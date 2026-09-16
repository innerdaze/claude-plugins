#!/usr/bin/env python3
"""Mirror the public plugins out of the private `agent` monorepo and open a PR.

Why this exists
---------------
The five plugins are developed in a private GitLab monorepo (`agent`) that
publishes them to a company npm registry. They also need to reach a *public*
GitHub marketplace, and that mirroring behaviour cannot live in the private
repo. So it lives here, pulling rather than being pushed: this repo is the
downstream, and nothing upstream knows it exists.

What it does, in order
----------------------
1. Fetches `agent` and resolves the ref to sync (default `origin/main`) - it
   reads the *committed* upstream tree, never the working copy, so it cannot be
   disturbed by, and cannot disturb, whatever you have checked out over there.
2. Copies each plugin's PUBLISHED file set into `plugins/<name>/`, scrubbing the
   company's identity out of the manifests as it goes.
3. Regenerates `.claude-plugin/marketplace.json` from what it just wrote.
4. Audits the result for leaked internal identifiers and REFUSES to continue if
   it finds any.
5. Branches, commits, pushes, and opens the PR. Merging it publishes, because
   this marketplace serves plugins straight out of the repo.

Usage
-----
    python tools/sync_from_agent.py                 # sync, push, open the PR
    python tools/sync_from_agent.py --dry-run       # write nothing, report what would change
    python tools/sync_from_agent.py --no-pr         # write and commit locally, stop there
    python tools/sync_from_agent.py --ref <sha>     # pin a specific upstream commit

Exit codes: 0 = done (or nothing to do), 1 = refused / failed.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# What gets mirrored, and who it belongs to once it lands here.
# ---------------------------------------------------------------------------

# The five that go public. `create-bug-ticket-for-is` is deliberately absent: it
# encodes an internal Jira workflow and has no meaning outside the company.
PLUGINS = ["hub", "cadence", "domains", "work", "intent"]

# Two upstream files that are not plugin payload but have to arrive with it.
#
# The validator, because it must track what it validates: it is written against
# `plugins/cadence`, which is exactly the layout here, and a validator a release
# older than the Markdown it checks is worse than none - it reports confidently
# on rules that have moved. The changelog, because the validator reads it to
# refuse a version that ships undescribed, and because it is the only record of
# what changed between two mirrors.
#
# Each entry may carry substitutions beyond the global ones. They are REQUIRED to
# match: a vendored patch that silently stops applying is how a file ends up
# looking maintained while doing nothing.
VENDORED_FILES = [
    ("scripts/validate_cadence.py", "tools/validate_cadence.py", [
        # Upstream files cadence's changelog under its own intent layer. Here it
        # is the repository's changelog, at the root, where a visitor looks.
        (re.compile(r'ROOT / "intent" / "cadence" / "CHANGELOG\.md"'),
         'ROOT / "CHANGELOG.md"'),
    ]),
    ("intent/cadence/CHANGELOG.md", "CHANGELOG.md", []),
]

GITHUB_REPO = "innerdaze/claude-plugins"
GITHUB_URL = f"https://github.com/{GITHUB_REPO}"
MARKETPLACE_NAME = "innerdaze"   # not "claude-plugins": Claude Code rejects
                                 # marketplace names containing "claude".
OWNER_NAME = "Lee Driscoll"
LICENSE = "Apache-2.0"

UPSTREAM_REMOTE_MARKER = "acresoftware/skunkworks/agent"
DEFAULT_AGENT_PATH = Path.home() / "Projects" / "agent"
DEFAULT_REF = "origin/main"

# Textual substitutions applied to every mirrored text file. These cover prose
# and links; the manifests are rewritten structurally below, which is what
# actually guarantees the identity fields are right.
REWRITES = [
    (re.compile(r"https://gitlab\.com/acresoftware/skunkworks/agent/-/issues"),
     f"{GITHUB_URL}/issues"),
    (re.compile(r"(git\+)?https://gitlab\.com/acresoftware/skunkworks/agent(\.git)?"),
     GITHUB_URL),
    (re.compile(r"git@gitlab\.com:acresoftware/skunkworks/agent\.git"), GITHUB_URL),
    (re.compile(r"@acresoftware/"), "@innerdaze/"),
    (re.compile(r"@acresoftware\b"), "@innerdaze"),
    (re.compile(r"\bacre-software\b"), MARKETPLACE_NAME),
    (re.compile(r"engineering@acresoftware\.com"), OWNER_NAME),
    (re.compile(r"Acre Software"), OWNER_NAME),
]

# Install instructions are the one place where a mirrored README is not merely
# differently-branded but *wrong*: upstream's describe two auth gates - an SSH
# clone of a private repo and an ~/.npmrc mapping a scope to a token-gated
# registry - and neither exists here, where the marketplace serves plugins out
# of a public repo with no credential of any kind.
#
# So the block is regenerated rather than find-and-replaced. The rule is written
# against the *shape* (a fenced block containing `/plugin marketplace add`)
# rather than against any plugin's wording, so a sixth plugin is covered the day
# it is added. If upstream reshapes the section past recognition, the block
# stops matching, the private URLs survive, and the audit below refuses the run
# - which is the failure this should have, rather than publishing instructions
# that send a stranger at a repo they cannot read.
INSTALL_BLOCK = re.compile(
    r"```\n(?:(?!```)[^\n]*\n)*?/plugin marketplace add[^\n]*\n"
    r"(?:(?!```)[^\n]*\n)*?```\n"
)
INSTALL_PREAMBLE = re.compile(
    r"The repo is private, so two auth gates apply[^\n]*\n"
    r"(?:(?!\n\n)[^\n]*\n)*?In short:\n"
)
LOCAL_CLONE_HINT = re.compile(r"/plugin marketplace add /path/to/agent")


def rewrite_install_block(match: re.Match) -> str:
    """Restate a README's install block for this public marketplace."""
    installed = re.search(r"/plugin install\s+(\S+?)@", match.group(0))
    lines = [f"/plugin marketplace add {GITHUB_REPO}"]
    if installed:
        lines.append(f"/plugin install {installed.group(1)}@{MARKETPLACE_NAME}")
    return "```\n" + "\n".join(lines) + "\n```\n"

# The audit. Anything here surviving into the tree is a leak of a private
# repo's identity into a public one, so it fails the run rather than warning:
# a warning in a script that ends in `git push` is a leak with a paper trail.
FORBIDDEN = [
    ("acresoftware", "the company npm scope / GitLab namespace"),
    ("Acre Software", "the company as a named author"),
    ("skunkworks", "the private GitLab group"),
    ("80012274", "the private GitLab project id"),
    ("gitlab.com/api/v4", "the private package registry endpoint"),
    # The identity tokens above are not enough on their own. Rewriting
    # "@acresoftware" to "@innerdaze" inside a paragraph about wiring a scope to
    # a token-gated registry produces text that passes every check and still
    # sends a reader somewhere they cannot go. These three catch the *shape* of
    # private-install prose, whatever the names in it have been changed to.
    ("The repo is private", "install prose written for the private repo"),
    ("read_registry", "a private registry token scope"),
    (".npmrc", "an npm auth file no install here needs"),
]

TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".txt", ".toml"}


def fail(msg: str):
    sys.stderr.write(f"\nsync: {msg}\n")
    sys.exit(1)


def run(args: list[str], cwd: Path | None = None) -> str:
    """Run a command, failing loudly. Git and gh are the only callees."""
    try:
        p = subprocess.run(args, cwd=cwd, check=True, text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        fail(f"`{args[0]}` is not installed or not on PATH.")
    except subprocess.CalledProcessError as e:
        detail = (e.stderr or e.stdout or "").strip()
        fail(f"command failed: {' '.join(args)}\n{detail}")
    return (p.stdout or "").strip()


# ---------------------------------------------------------------------------
# 1. Upstream
# ---------------------------------------------------------------------------

def resolve_agent(path: Path) -> Path:
    if not (path / ".git").exists():
        fail(f"no git repository at {path}.\n"
             f"Pass --agent <path> or set AGENT_REPO.")
    remotes = run(["git", "remote", "-v"], cwd=path)
    if UPSTREAM_REMOTE_MARKER not in remotes:
        fail(f"{path} is a git repo, but its remotes do not mention "
             f"{UPSTREAM_REMOTE_MARKER}:\n{remotes}\n"
             f"Refusing to mirror a repository that may not be the one intended.")
    return path


def read_upstream(agent: Path, ref: str, path: str) -> bytes:
    """One file out of the upstream tree at `ref` - no checkout involved."""
    try:
        return subprocess.run(["git", "show", f"{ref}:{path}"], cwd=agent,
                              check=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).stdout
    except subprocess.CalledProcessError as e:
        fail(f"{path} is missing from {ref} upstream.\n{e.stderr.decode().strip()}")


def extract_upstream_dir(agent: Path, ref: str, path: str) -> dict[str, bytes]:
    """Every file under an upstream directory at `ref`, keyed by relative path."""
    proc = subprocess.run(["git", "archive", "--format=tar", ref, "--", path],
                          cwd=agent, check=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    out: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(proc.stdout)) as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            fh = tar.extractfile(member)
            if fh is not None:
                out[member.name] = fh.read()
    return out


# ---------------------------------------------------------------------------
# 2. Scrub
# ---------------------------------------------------------------------------

def to_lf(data: bytes) -> bytes:
    """Normalise to LF before anything reads the text.

    `git archive` and `git show` honour core.autocrlf, so on Windows the bytes
    arriving from upstream have CRLF endings while the repository stores LF.
    Every rule below is anchored on "\\n", and against CRLF they do not error -
    they quietly match nothing, which is how a README shipped a page of
    private-registry install instructions through a scrub that reported clean.
    Normalising once, here, is what makes those rules mean what they say.
    """
    return data.replace(b"\r\n", b"\n")


def rewrite_text(data: bytes) -> bytes:
    text = to_lf(data).decode("utf-8")
    for pattern, replacement in REWRITES:
        text = pattern.sub(replacement, text)
    return text.encode("utf-8")


def rewrite_plugin_manifest(data: bytes, plugin: str) -> bytes:
    """Restate ownership in `.claude-plugin/plugin.json`.

    Structural, not textual: these four fields are the ones that say who
    published this and under what terms, and getting them right by regex would
    be getting them right by luck.
    """
    manifest = json.loads(rewrite_text(data))
    manifest["author"] = {"name": OWNER_NAME}
    manifest["homepage"] = f"{GITHUB_URL}/tree/main/plugins/{plugin}"
    manifest["repository"] = GITHUB_URL
    manifest["license"] = LICENSE
    return (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def rewrite_readme(data: bytes) -> bytes:
    text = to_lf(data).decode("utf-8")
    text = INSTALL_PREAMBLE.sub("Install it from the public marketplace:\n", text)
    text = INSTALL_BLOCK.sub(rewrite_install_block, text)
    text = LOCAL_CLONE_HINT.sub("/plugin marketplace add /path/to/claude-plugins", text)
    return rewrite_text(text.encode("utf-8"))


def transform(rel_path: str, data: bytes, plugin: str) -> bytes:
    if rel_path == ".claude-plugin/plugin.json":
        return rewrite_plugin_manifest(data, plugin)
    if rel_path == "README.md":
        return rewrite_readme(data)
    if Path(rel_path).suffix in TEXT_SUFFIXES:
        return rewrite_text(data)
    return data   # anything else is an opaque asset: copy it byte for byte


def audit(paths: list[Path]) -> None:
    hits: list[str] = []
    for path in paths:
        if path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token, why in FORBIDDEN:
            for n, line in enumerate(text.splitlines(), 1):
                if token in line:
                    hits.append(f"  {path.relative_to(ROOT)}:{n}  {token}  ({why})")
    if hits:
        fail("internal identifiers survived the scrub - nothing was committed:\n"
             + "\n".join(hits)
             + "\n\nAdd a rule to REWRITES in this script, then re-run.")


# ---------------------------------------------------------------------------
# 3. Mirror
# ---------------------------------------------------------------------------

def sync_plugin(agent: Path, ref: str, plugin: str, dry_run: bool) -> dict:
    """Mirror one plugin. Returns its provenance record."""
    pkg = json.loads(read_upstream(agent, ref, f"plugins/{plugin}/package.json"))
    version = pkg["version"]

    # `files` is upstream's own answer to "what does this plugin consist of",
    # already maintained because it governs what npm publishes. Reusing it means
    # a new directory reaches this marketplace the moment it reaches the
    # registry, with nothing here to remember to update. What it leaves out -
    # evals/, .npmrc, package.json - is exactly what should not be mirrored.
    published = pkg.get("files")
    if not published:
        fail(f"plugins/{plugin}/package.json upstream has no `files` list, so "
             f"there is no way to tell what it publishes.")

    tree = extract_upstream_dir(agent, ref, f"plugins/{plugin}")
    prefix = f"plugins/{plugin}/"
    wanted: dict[str, bytes] = {}
    for entry in published:
        found = {
            name[len(prefix):]: blob
            for name, blob in tree.items()
            if name == prefix + entry or name.startswith(prefix + entry + "/")
        }
        if not found:
            fail(f"plugins/{plugin}/package.json lists `{entry}`, but it is not "
                 f"in the upstream tree at {ref}.")
        wanted.update(found)

    dest = ROOT / "plugins" / plugin
    if dry_run:
        return {"version": version, "files": len(wanted), "written": []}

    # Replace wholesale rather than merge: a mirror that only ever adds files
    # keeps serving a skill upstream deleted, and a deleted skill is usually
    # deleted because following it now does the wrong thing.
    if dest.exists():
        shutil.rmtree(dest)
    written: list[Path] = []
    for rel_path, blob in sorted(wanted.items()):
        target = dest / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(transform(rel_path, blob, plugin))
        written.append(target)
    return {"version": version, "files": len(wanted), "written": written}


def sync_vendored_files(agent: Path, ref: str, dry_run: bool) -> list[Path]:
    written = []
    for src, dst, patches in VENDORED_FILES:
        text = rewrite_text(read_upstream(agent, ref, src)).decode("utf-8")
        for pattern, replacement in patches:
            text, applied = pattern.subn(replacement, text)
            if not applied:
                fail(f"vendoring {src}: the patch {pattern.pattern!r} no longer "
                     f"matches anything upstream. Check what changed and update "
                     f"VENDORED_FILES in this script.")
        target = ROOT / dst
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8", newline="\n")
        written.append(target)
    return written


def write_marketplace(dry_run: bool) -> Path:
    """Rebuild the marketplace manifest from the plugins actually present.

    Generated, never hand-edited: the manifest and the directories are two
    statements of the same fact, and the failure mode of maintaining both is a
    marketplace advertising a plugin that is not there.
    """
    entries = []
    for plugin in PLUGINS:
        manifest_path = ROOT / "plugins" / plugin / ".claude-plugin" / "plugin.json"
        if not manifest_path.exists():
            if dry_run:
                continue
            fail(f"{manifest_path.relative_to(ROOT)} is missing after the sync.")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entry = {
            "name": manifest["name"],
            "source": f"./plugins/{plugin}",
            "version": manifest["version"],
            "description": manifest["description"],
            "author": {"name": OWNER_NAME},
            "homepage": f"{GITHUB_URL}/tree/main/plugins/{plugin}",
            "repository": GITHUB_URL,
            "license": LICENSE,
        }
        if manifest.get("keywords"):
            entry["keywords"] = manifest["keywords"]
        entries.append(entry)

    marketplace = {
        "name": MARKETPLACE_NAME,
        "owner": {"name": OWNER_NAME, "url": f"{GITHUB_URL}/issues"},
        "metadata": {
            "description": "Claude Code plugins by Lee Driscoll: an interoperating "
                           "stack of hub, cadence, domains, work and intent.",
        },
        "plugins": entries,
    }
    target = ROOT / ".claude-plugin" / "marketplace.json"
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(marketplace, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
    return target


def write_provenance(sha: str, ref: str, records: dict[str, dict], dry_run: bool) -> Path:
    """Record where this tree came from.

    Without it the only answer to "is the mirror current?" is to eyeball five
    version numbers against a repo you may not have cloned.
    """
    state = {
        "note": "Generated by tools/sync_from_agent.py. The plugins in this "
                "repository are mirrored from their source monorepo; edit them "
                "there, then re-run the sync.",
        "upstream_ref": ref,
        "upstream_commit": sha,
        "plugins": {name: rec["version"] for name, rec in records.items()},
    }
    target = ROOT / ".upstream.json"
    if not dry_run:
        target.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return target


# ---------------------------------------------------------------------------
# 4. Publish
# ---------------------------------------------------------------------------

def git_is_clean() -> bool:
    return run(["git", "status", "--porcelain"], cwd=ROOT) == ""


def open_pr(branch: str, sha: str, records: dict[str, dict], previous: dict) -> None:
    lines = [
        f"Mirrors `agent@{sha[:12]}` into this marketplace.",
        "",
        "| plugin | version |",
        "| --- | --- |",
    ]
    for name, rec in records.items():
        was = previous.get("plugins", {}).get(name)
        version = rec["version"]
        shown = version if was in (None, version) else f"{was} -> {version}"
        lines.append(f"| `{name}` | {shown} |")
    lines += [
        "",
        "Generated by `tools/sync_from_agent.py` - review the diff, don't edit the "
        "plugins here. Merging this publishes them: the marketplace serves each "
        "plugin straight out of `plugins/<name>/`.",
        "",
        "\U0001F916 Generated with [Claude Code](https://claude.com/claude-code)",
    ]
    body = "\n".join(lines)

    if shutil.which("gh") is None:
        print(
            "\ngh is not installed, so the PR was not opened. The branch is pushed;\n"
            "open it here:\n"
            f"  {GITHUB_URL}/compare/main...{branch}?expand=1\n\n"
            "To have future runs open it for you:\n"
            "  winget install --id GitHub.cli\n"
            "  gh auth login\n"
        )
        return

    url = run(["gh", "pr", "create",
               "--repo", GITHUB_REPO,
               "--base", "main",
               "--head", branch,
               "--title", f"sync: mirror plugins from agent@{sha[:12]}",
               "--body", body], cwd=ROOT)
    print(f"\nPR opened: {url}")


# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--agent", type=Path,
                    default=Path(os.environ.get("AGENT_REPO", DEFAULT_AGENT_PATH)),
                    help=f"path to the agent monorepo (default: {DEFAULT_AGENT_PATH})")
    ap.add_argument("--ref", default=DEFAULT_REF,
                    help=f"upstream ref to mirror (default: {DEFAULT_REF})")
    ap.add_argument("--branch", help="branch name (default: sync/agent-<sha>)")
    ap.add_argument("--no-fetch", action="store_true",
                    help="skip `git fetch` upstream; mirror what is already local")
    ap.add_argument("--no-pr", action="store_true",
                    help="commit locally, but do not push or open a PR")
    ap.add_argument("--skip-validate", action="store_true",
                    help="mirror even if the payload fails validation")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would change; write nothing")
    args = ap.parse_args()

    if not args.dry_run and not git_is_clean():
        fail("this repository has uncommitted changes. Commit or stash them "
             "first - the sync rewrites plugins/ wholesale.")

    agent = resolve_agent(args.agent.expanduser())
    if not args.no_fetch:
        print(f"fetching {agent} ...")
        run(["git", "fetch", "--quiet", "origin"], cwd=agent)
    sha = run(["git", "rev-parse", args.ref], cwd=agent)
    print(f"upstream: {args.ref} = {sha[:12]}")

    state_path = ROOT / ".upstream.json"
    previous = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}

    records: dict[str, dict] = {}
    written: list[Path] = []
    for plugin in PLUGINS:
        rec = sync_plugin(agent, args.ref, plugin, args.dry_run)
        records[plugin] = rec
        written.extend(rec["written"])
        was = previous.get("plugins", {}).get(plugin)
        change = "" if was in (None, rec["version"]) else f"  (was {was})"
        print(f"  {plugin:<9} v{rec['version']:<8} {rec['files']:>3} files{change}")

    written.extend(sync_vendored_files(agent, args.ref, args.dry_run))
    write_marketplace(args.dry_run)
    write_provenance(sha, args.ref, records, args.dry_run)

    if args.dry_run:
        print("\ndry run - nothing written.")
        return 0

    audit(written)
    print("scrub audit: clean")

    # Validate before the commit, not after the push. CI runs the same script,
    # so skipping it here would only move the same failure to a place where it
    # costs a round trip and a force-push to find out about.
    validator = ROOT / "tools" / "validate_cadence.py"
    if validator.exists() and not args.skip_validate:
        print("\nvalidating the payload ...")
        result = subprocess.run([sys.executable, str(validator)], cwd=ROOT)
        if result.returncode != 0:
            fail("the mirrored payload does not validate (above). Nothing was "
                 "committed. Fix it upstream and re-run, or pass --skip-validate "
                 "if you are deliberately mirroring a known-broken tree.")

    if git_is_clean():
        print(f"\nalready in sync with agent@{sha[:12]} - nothing to do.")
        return 0

    branch = args.branch or f"sync/agent-{sha[:12]}"
    run(["git", "checkout", "-B", branch], cwd=ROOT)
    run(["git", "add", "-A"], cwd=ROOT)
    summary = ", ".join(f"{n} v{r['version']}" for n, r in records.items())
    run(["git", "commit", "-m",
         f"sync: mirror plugins from agent@{sha[:12]}\n\n{summary}\n\n"
         f"Generated by tools/sync_from_agent.py.\n\n"
         f"Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"],
        cwd=ROOT)
    print(f"\ncommitted on {branch}")

    if args.no_pr:
        print("--no-pr: stopping before push.")
        return 0

    run(["git", "push", "--force-with-lease", "-u", "origin", branch], cwd=ROOT)
    open_pr(branch, sha, records, previous)
    return 0


if __name__ == "__main__":
    sys.exit(main())
