#!/usr/bin/env python3
"""Validate the Cadence plugin payload.

Everything Cadence ships is Markdown that an agent executes at run time, so
there is no compiler between what we write and what happens. This script is the
substitute: it enforces the invariants that have actually drifted or broken in
practice, each one traceable to a real defect. See tools/README.md for the
reasoning behind each rule.

Usage:
    python tools/validate_cadence.py [--quiet]

Exit codes: 0 = clean (warnings allowed), 1 = at least one error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "PyYAML is required: pip install pyyaml\n"
        "(It is the only dependency; the plugin payload itself has none.)\n"
    )
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "cadence"

ERRORS: list[str] = []
WARNINGS: list[str] = []


def err(rule: str, msg: str) -> None:
    ERRORS.append(f"[{rule}] {msg}")


def warn(rule: str, msg: str) -> None:
    WARNINGS.append(f"[{rule}] {msg}")


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(p)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def payload_md() -> list[Path]:
    return sorted(PLUGIN.rglob("*.md"))


def yaml_blocks(text: str) -> list[str]:
    return re.findall(r"```ya?ml\n(.*?)```", text, re.S)


def frontmatter(text: str) -> dict | None:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None


# --------------------------------------------------------------------------
# 1. Manifests parse, and their versions agree with the changelog
# --------------------------------------------------------------------------
def check_manifests() -> None:
    mp = ROOT / ".claude-plugin" / "marketplace.json"
    pp = PLUGIN / ".claude-plugin" / "plugin.json"
    data = {}
    for p in (mp, pp):
        if not p.exists():
            err("manifest", f"missing {rel(p)}")
            continue
        try:
            data[p] = json.loads(read(p))
        except json.JSONDecodeError as e:
            err("manifest", f"{rel(p)} is not valid JSON: {e}")

    plugin = data.get(pp)
    if plugin:
        for field in ("name", "version", "description", "author", "license",
                      "homepage", "repository"):
            if not plugin.get(field):
                err("manifest", f"plugin.json is missing '{field}'")

    market = data.get(mp)
    if market:
        # Claude Code refuses to load a marketplace whose name looks like an
        # official Anthropic source, and the error only appears at install time -
        # long after the name was chosen. Catch it here instead.
        mname = str(market.get("name", ""))
        if not mname:
            err("manifest", "marketplace.json has no 'name'")
        elif re.search(r"claude|anthropic", mname, re.I):
            err("manifest",
                f"marketplace name {mname!r} contains 'claude'/'anthropic' - Claude Code "
                f"rejects it as impersonating an official marketplace. It need not match "
                f"the repository name.")

    if market and plugin:
        entries = {e.get("name"): e for e in market.get("plugins", [])}
        if "cadence" not in entries:
            err("manifest", "marketplace.json does not list the cadence plugin")
        elif entries["cadence"].get("version") != plugin.get("version"):
            err("manifest",
                f"version mismatch: plugin.json {plugin.get('version')!r} vs "
                f"marketplace entry {entries['cadence'].get('version')!r}")

    # The changelog must know about the current version, so a release can never
    # ship without a note saying what changed.
    ch = ROOT / "CHANGELOG.md"
    if not ch.exists():
        err("manifest", "missing CHANGELOG.md")
    elif plugin:
        v = plugin.get("version", "")
        body = read(ch)
        if v and v not in body and "[Unreleased]" not in body:
            err("manifest", f"CHANGELOG.md mentions neither {v} nor [Unreleased]")


# --------------------------------------------------------------------------
# 2. Skills and commands are wired correctly
# --------------------------------------------------------------------------
def check_skills_and_commands() -> set[str]:
    skills: set[str] = set()
    skills_dir = PLUGIN / "skills"
    for d in sorted(p for p in skills_dir.iterdir() if p.is_dir()) if skills_dir.exists() else []:
        sk = d / "SKILL.md"
        if not sk.exists():
            err("skill", f"{rel(d)} has no SKILL.md")
            continue
        fm = frontmatter(read(sk))
        if fm is None:
            err("skill", f"{rel(sk)} has no parseable YAML frontmatter")
            continue
        name = fm.get("name")
        if not name:
            err("skill", f"{rel(sk)} frontmatter has no 'name'")
        elif name != d.name:
            # Directory and name must match so the skill resolves the same way
            # however the harness looks it up.
            err("skill", f"{rel(sk)} declares name {name!r} but lives in {d.name!r}")
        elif name.startswith("cadence-") or name.startswith("cadence_"):
            # The plugin namespace already prefixes everything with `cadence:`,
            # so a prefixed name registers as /cadence:cadence-<n>.
            err("skill", f"{rel(sk)} name {name!r} repeats the plugin namespace - "
                         f"it would register as /cadence:{name}. Use the bare name.")
        else:
            skills.add(name)
        if not fm.get("description"):
            err("skill", f"{rel(sk)} frontmatter has no 'description'")
        elif len(fm["description"]) < 80:
            warn("skill", f"{name}: description is short; it is the only dispatch surface")

    # A commands/ directory would double the registered surface: a plugin skill
    # is already typeable as /cadence:<name>, so a command wrapper adds a second
    # entry for the same capability. This shipped once and was only visible on a
    # real install.
    if (PLUGIN / "commands").exists():
        err("command", "cadence/commands/ exists - plugin skills are already typeable as "
                       "/cadence:<name>, so a command wrapper registers every capability "
                       "twice. Delete it and rely on the skill.")
    return skills


# --------------------------------------------------------------------------
# 3. Every ${CLAUDE_PLUGIN_ROOT} path resolves; bundled files are anchored
# --------------------------------------------------------------------------
def check_plugin_root_paths() -> None:
    """The highest-value rule here.

    A skill's working directory is the *consumer's* repo, so an unanchored
    bundled path resolves to nothing and the model improvises instead of
    erroring. That failure is silent, which is what makes it worth a rule.
    """
    for p in payload_md():
        text = read(p)
        for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./<>-]+)", text):
            if "<" in ref:  # a documented placeholder like flows/<name>.flow.md
                continue
            target = PLUGIN / ref
            if not target.exists():
                err("plugin-root", f"{rel(p)} references ${{CLAUDE_PLUGIN_ROOT}}/{ref} which does not exist")

    # Inside a skill or command, a bundled file must be anchored.
    bundled = re.compile(r"`((?:flows|adapters|templates|agents|skills)/[A-Za-z0-9_./-]+\.md)`")
    for p in sorted((PLUGIN / "skills").rglob("*.md")) + sorted((PLUGIN / "commands").glob("*.md")):
        text = read(p)
        for m in bundled.finditer(text):
            start = max(0, m.start() - 30)
            if "CLAUDE_PLUGIN_ROOT" not in text[start:m.start()]:
                err("plugin-root",
                    f"{rel(p)} references bundled `{m.group(1)}` without ${{CLAUDE_PLUGIN_ROOT}}")


# --------------------------------------------------------------------------
# 4. No project-specific terms leak into the shipped payload
# --------------------------------------------------------------------------
BANNED = {
    "machinegame": "a private project name",
    "unreal": "an engine specific to one consumer",
    "linear-uft": "a private MCP namespace",
    "mp-safe": "a game-specific DoD gate",
    "domains/PROJECT.md": "one consumer's config location, not a general default",
}


def check_banned_terms() -> None:
    """Cadence is installed once and serves every project, so a real project's
    name or namespace in the payload is a live contamination source, not a
    cosmetic blemish. This has leaked before."""
    for p in payload_md():
        low = read(p).lower()
        for term, why in BANNED.items():
            if term.lower() in low:
                err("banned-term", f"{rel(p)} contains {term!r} ({why})")


# --------------------------------------------------------------------------
# 5. Flow specs validate against FLOW-SPEC.md
# --------------------------------------------------------------------------
TOP_KEYS = {"meta", "hierarchy", "states", "gates", "cadence", "intake",
            "decision_rights", "session", "hooks"}
APPROVERS = {"ai", "ai-proposes", "human"}


def flow_files() -> list[Path]:
    return sorted(PLUGIN.rglob("*.flow.md"))


def check_flows(hook_names: set[str], wildcards: list[str]) -> None:
    plugin_minor = ""
    pj = PLUGIN / ".claude-plugin" / "plugin.json"
    if pj.exists():
        try:
            v = json.loads(read(pj)).get("version", "")
            plugin_minor = ".".join(v.split(".")[:2])
        except json.JSONDecodeError:
            pass

    spec = PLUGIN / "flows" / "FLOW-SPEC.md"
    if not spec.exists():
        err("flow", "flows/FLOW-SPEC.md is missing - it is the schema")
        return
    documented_tokens = set(re.findall(r"^\|\s*`([a-z-]+)`\s*\|", read(spec), re.M))

    for p in flow_files():
        blocks = yaml_blocks(read(p))
        if not blocks:
            err("flow", f"{rel(p)} has no yaml block")
            continue
        try:
            d = yaml.safe_load(blocks[0]) or {}
        except yaml.YAMLError as e:
            err("flow", f"{rel(p)} yaml does not parse: {e}")
            continue

        name = rel(p)
        for k in set(d) - TOP_KEYS:
            err("flow", f"{name}: unknown top-level key {k!r} (not in FLOW-SPEC.md)")

        meta = d.get("meta") or {}
        for k in ("name", "summary", "cadence_version"):
            if not meta.get(k):
                err("flow", f"{name}: meta.{k} is required")
        # A shipped flow must target the version it ships with, or /cadence:doctor
        # reports contract drift on a pristine install.
        if plugin_minor and meta.get("cadence_version"):
            if str(meta["cadence_version"]) != plugin_minor:
                err("flow", f"{name}: meta.cadence_version is {meta['cadence_version']!r} "
                            f"but this plugin is {plugin_minor!r} - a shipped flow that targets "
                            f"an older contract makes doctor report drift on a clean install")

        st = d.get("states") or {}
        lanes = st.get("lanes") or []
        roles = st.get("roles") or {}
        if not lanes:
            err("flow", f"{name}: states.lanes is required")
        for req in ("backlog", "done"):
            if req not in roles:
                err("flow", f"{name}: states.roles.{req} is required")
        for role, lane in roles.items():
            for v in (lane if isinstance(lane, list) else [lane]):
                if v and v not in lanes:
                    err("flow", f"{name}: roles.{role} = {v!r} is not in states.lanes")

        all_lanes = set(lanes) | set(st.get("incident_lanes") or [])
        gates = set((d.get("gates") or {}).keys())
        reached = {roles.get("backlog")}
        transitions = st.get("gated_transitions") or {}
        for key, glist in transitions.items():
            if "->" not in key:
                err("flow", f"{name}: transition {key!r} is not '<from> -> <to>'")
                continue
            frm, to = (s.strip() for s in key.split("->", 1))
            for side in (frm, to):
                if side not in all_lanes:
                    err("flow", f"{name}: transition {key!r} names lane {side!r} not in states.lanes")
            reached.add(to)
            for g in glist or []:
                gname = g[5:] if g.startswith("gate.") else g
                if gname not in gates:
                    err("flow", f"{name}: transition {key!r} references undefined gate {gname!r}")
        for g in (st.get("release_pipeline") or []):
            gname = g[5:] if g.startswith("gate.") else g
            if gname not in gates:
                err("flow", f"{name}: release_pipeline references undefined gate {gname!r}")

        # Lane reachability: a gate on a transition nothing reaches never fires.
        # This is the shape of a real defect - a preset gated "In Review -> Done"
        # while declaring no review step.
        #
        # Entry points are lanes work can appear in without a transition: the
        # backlog role (where /cadence:plan creates) and the first incident lane
        # (an incident is raised straight into triage, not moved there).
        active = roles.get("active")
        if active:
            reached.add(active)
        incident_lanes = st.get("incident_lanes") or []
        if incident_lanes:
            reached.add(incident_lanes[0])
        for key in transitions:
            if "->" not in key:
                continue
            frm = key.split("->", 1)[0].strip()
            if frm not in reached:
                warn("flow-reachability",
                     f"{name}: transition {key!r} starts in {frm!r}, which nothing declared reaches "
                     f"- any gate on it will never fire")

        for gname, g in (d.get("gates") or {}).items():
            ap = (g or {}).get("approver")
            if ap not in APPROVERS:
                err("flow", f"{name}: gate {gname!r} has approver {ap!r}, expected one of {sorted(APPROVERS)}")

        for step, right in (d.get("decision_rights") or {}).items():
            if right not in APPROVERS:
                err("flow", f"{name}: decision_rights.{step} = {right!r} is not a valid level")

        for tok in ((d.get("intake") or {}).get("priority_policy") or []):
            if tok not in documented_tokens:
                warn("flow", f"{name}: priority-policy token {tok!r} is not documented in FLOW-SPEC.md "
                             f"- it will be read as prose and may silently do nothing")

        for hk, doc in (d.get("hooks") or {}).items():
            known = hk in hook_names or any(re.fullmatch(w, hk) for w in wildcards)
            if not known:
                err("flow", f"{name}: hooks entry {hk!r} is not a hook in HOOKS.md")
            target = (p.parent / doc).resolve()
            if not target.exists():
                err("flow", f"{name}: hook {hk!r} points at {doc}, which does not exist")

        for ceremony in ((d.get("cadence") or {}).get("ceremonies") or []):
            cer = PLUGIN / "flows" / "CEREMONIES.md"
            if cer.exists() and not re.search(rf"^##\s+{re.escape(ceremony)}\b", read(cer), re.M):
                err("flow", f"{name}: ceremony {ceremony!r} has no section in CEREMONIES.md")


# --------------------------------------------------------------------------
# 6. Every catalogued hook is fired by something, or explicitly deferred
# --------------------------------------------------------------------------
def check_hooks() -> tuple[set[str], list[str]]:
    hooks_md = PLUGIN / "flows" / "HOOKS.md"
    if not hooks_md.exists():
        err("hook", "flows/HOOKS.md is missing")
        return set(), []
    text = read(hooks_md)
    names: set[str] = set()
    wildcards: list[str] = []

    entries = re.findall(r"^\*\*`([^`]+)`\*\*(.*?)(?=^\*\*`|\Z)", text, re.M | re.S)
    for name, body in entries:
        if "<" in name:
            # re.escape leaves < and > alone on modern Python, so substitute the
            # bare placeholders rather than escaped ones.
            wildcards.append(re.escape(name).replace("<name>", r"[a-z_-]+")
                             .replace("<from>", r".+").replace("<to>", r".+"))
        else:
            names.add(name)
        m = re.search(r"^\*Fired by:\*\s*(.+)$", body, re.M)
        if not m:
            err("hook", f"HOOKS.md: `{name}` has no *Fired by:* line "
                        f"- a hook nothing fires is a defect, not a feature")
            continue
        site = m.group(1).strip()
        if "deferred" in site.lower():
            continue
        skill = re.search(r"`([a-z][a-z0-9-]*)`", site)
        if not skill:
            err("hook", f"HOOKS.md: `{name}` Fired-by does not name a skill: {site[:60]!r}")
        elif not (PLUGIN / "skills" / skill.group(1) / "SKILL.md").exists():
            err("hook", f"HOOKS.md: `{name}` is fired by {skill.group(1)!r}, which does not exist")
    return names, wildcards


# --------------------------------------------------------------------------
# 7. Shipped fallback adapters cover the contract they claim
# --------------------------------------------------------------------------
def check_adapters() -> None:
    contract = PLUGIN / "adapters" / "ADAPTERS.md"
    if not contract.exists():
        err("adapter", "adapters/ADAPTERS.md is missing")
        return
    text = read(contract)

    families = {
        "tracker": (PLUGIN / "adapters" / "trackers", r"## Tracker contract(.*?)^## "),
        "vcs": (PLUGIN / "adapters" / "vcs", r"## VCS contract(.*?)^## "),
        "doc": (PLUGIN / "adapters" / "docs", r"## Doc-system contract(.*?)^## "),
    }
    for fam, (d, pattern) in families.items():
        m = re.search(pattern, text, re.S | re.M)
        if not m:
            err("adapter", f"ADAPTERS.md has no '{fam}' contract section")
            continue
        ops = set(re.findall(r"\*\*`([a-z_]+)\(", m.group(1)))
        if not d.exists():
            continue
        for a in sorted(d.glob("*.md")):
            body = read(a)
            if "## Capabilities" not in body:
                err("adapter", f"{rel(a)} has no Capabilities block "
                               f"- degradation must be declared, not silent")
            for op in ops:
                if op not in body:
                    err("adapter", f"{rel(a)} never mentions contract op '{op}()' "
                                   f"(implement it or declare it unsupported)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quiet", action="store_true", help="only print failures")
    args = ap.parse_args()

    if not PLUGIN.exists():
        sys.stderr.write(f"No plugin payload at {PLUGIN}\n")
        return 2

    check_manifests()
    check_skills_and_commands()
    check_plugin_root_paths()
    check_banned_terms()
    hook_names, wildcards = check_hooks()
    check_flows(hook_names, wildcards)
    check_adapters()

    for w in WARNINGS:
        print(f"warning: {w}")
    for e in ERRORS:
        print(f"ERROR:   {e}")

    if ERRORS:
        print(f"\n{len(ERRORS)} error(s), {len(WARNINGS)} warning(s)")
        return 1
    if not args.quiet:
        print(f"ok - payload valid ({len(WARNINGS)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
