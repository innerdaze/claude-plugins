#!/usr/bin/env python3
"""Build a throwaway project in a known configuration shape.

Cadence's defect surface is the cross-product of its configurations, and the
default shape — solo-greenfield, every lane mapped, one in-flight lane, the only
gate on the final transition, no execution skill — is the one cell where most
failures are invisible. Every behavioural defect found so far needed a *different*
shape to become visible (see docs/VERIFICATION.md, "Coverage").

These fixtures are those shapes, built identically every time so a verification
run is repeatable rather than reassembled by hand.

    python tools/make_fixture.py --list
    python tools/make_fixture.py reduced-lane
    python tools/make_fixture.py execution-owns-commit --into /tmp/scratch

Each prints the path it built and what the shape is for. They are scratch
projects: build them, run the skills against them, throw them away.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent / "plugins" / "cadence"


def write(root: Path, rel: str, body: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(body).lstrip("\n"), encoding="utf-8")


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def init_repo(root: Path, message: str) -> None:
    git(root, "init", "-q")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "user.name", "Fixture")
    git(root, "add", "-A")
    git(root, "commit", "-qm", message)


def config(**kw: str) -> str:
    """Assemble a config from the pieces a fixture varies.

    Built flat, with no leading indentation on any line. An earlier version was
    an indented template run through textwrap.dedent, with the status_map block
    spliced in via textwrap.indent — which left the first mapped lane at a
    different depth from the rest and produced YAML that would not parse. The
    fixture then tested nothing except the config loader's error path.
    """
    lanes = "\n".join("    " + line.strip()
                      for line in kw["status_map"].strip().splitlines())
    return (
        f"# Cadence config — {kw['name']}\n"
        "\n"
        "```yaml\n"
        "project:\n"
        f"  name: {kw['name']}\n"
        f"  ticket_prefix: {kw['prefix']}\n"
        "\n"
        "tracker:\n"
        "  kind: markdown\n"
        "  path: .claude/cadence/backlog\n"
        "  status_map:\n"
        f"{lanes}\n"
        "\n"
        "vcs:\n"
        "  kind: git\n"
        "  checkpoint: commands\n"
        "\n"
        "execution:\n"
        f"  skill: {kw['exec_skill']}\n"
        f"  owns: {kw['exec_owns']}\n"
        "\n"
        "doc_system:\n"
        "  kind: none\n"
        "  notes: .claude/cadence/notes.md\n"
        "  roadmap: docs/ROADMAP.md\n"
        "\n"
        "session_state:\n"
        "  file: .claude/cadence/SESSION.local.md\n"
        "  format: markdown\n"
        "\n"
        "models:\n"
        "  mechanical: haiku\n"
        "  reasoning: inherit\n"
        "\n"
        f"flow: {kw['flow']}\n"
        "\n"
        f"dod_gates: {kw['dod']}\n"
        "```\n"
    )


SESSION_STATE = """
# Session state — {name}
updated: 2026-01-01

## Goal
current: {current}
next:    none

## Traps

## Milestone note
"""


# ---------------------------------------------------------------------------

def reduced_lane(root: Path) -> str:
    """A board with fewer columns than the flow declares."""
    write(root, "README.md", """
    # tide-table
    Next high tide for a handful of harbours.
    """)
    write(root, "lib/tides.py", """
    from datetime import time

    HIGHS = {"oban": [time(4, 12), time(16, 38)], "ullapool": [time(5, 2), time(17, 30)]}


    def next_high(harbour, now):
        for t in HIGHS.get(harbour, []):
            if t > now:
                return t
        return None
    """)
    write(root, "docs/ROADMAP.md", """
    # tide-table — Vision & Roadmap

    ## Roadmap

    ### M0 — answer from a terminal *(current focus)*

    **Goal:** `tide-table <harbour>` prints the next high tide.

    **Exit criteria:**
    - a known harbour prints the next high tide after now
    - an unknown harbour exits non-zero
    - after the last tide of the day the behaviour is defined and tested
    """)
    write(root, ".claude/cadence/config.md", config(
        name="tide-table", prefix="TIDE", flow="solo-greenfield", dod="[tests, docs]",
        exec_skill="none", exec_owns="[]",
        # solo-greenfield declares five lanes. This board has two.
        status_map="Backlog: Backlog\nDone: Done"))
    write(root, ".claude/cadence/backlog/TIDE-1.md", """
    ---
    id: TIDE-1
    title: "CLI entry point: harbour in, next high tide out"
    type: feature
    status: Backlog
    milestone: M0
    epic: ""
    labels: [feature]
    order: 1
    depends_on: []
    updated: 2026-01-01
    ---

    ## Comments
    """)
    write(root, ".claude/cadence/SESSION.local.md",
          SESSION_STATE.format(name="tide-table", current="none"))
    write(root, ".gitignore", ".claude/cadence/SESSION.local.md\n__pycache__/\n")
    init_repo(root, "initial: tides and Cadence setup")
    return ("The flow declares five lanes; status_map has two. `In Progress` is "
            "unmapped.\nExercises: sessions must not invent a column, and "
            "gate.dod must still run\non a path whose intermediate lane cannot be "
            "represented.")


def intermediate_gate(root: Path) -> str:
    """A gate on a transition that is NOT the final hop, into an unmapped lane."""
    src = PLUGIN / "examples" / "author-your-own-flow"
    (root / ".claude/cadence/hooks").mkdir(parents=True, exist_ok=True)
    shutil.copy(src / "manuscript.flow.md", root / ".claude/cadence/manuscript.flow.md")
    for h in (src / "hooks").glob("*.md"):
        shutil.copy(h, root / ".claude/cadence/hooks" / h.name)

    write(root, "README.md", """
    # field-notes
    A researched essay. Claims tracked as work items.
    """)
    write(root, "essay.md", """
    # Working title

    ## First section
    A claim that will need sourcing.
    """)
    write(root, "docs/ROADMAP.md", """
    # field-notes — Vision & Roadmap

    ## Roadmap

    ### essay — first draft *(current focus)*
    **Goal:** every claim in the first section is supported.
    """)
    write(root, ".claude/cadence/config.md", config(
        name="field-notes", prefix="CLAIM", flow=".claude/cadence/manuscript.flow.md",
        dod="[]", exec_skill="none", exec_owns="[]",
        # manuscript declares six lanes. `Reviewed` is deliberately absent, and
        # gate.citations sits on the transition INTO it.
        status_map=("Outline: Outline\nDrafting: Drafting\n"
                    "Needs-Support: Needs-Support\nSupported: Supported\nFinal: Final")))
    write(root, ".claude/cadence/backlog/CLAIM-1.md", """
    ---
    id: CLAIM-1
    title: "A claim resting on nothing yet"
    type: claim
    status: Needs-Support
    milestone: essay
    epic: "first-section"
    labels: [claim]
    order: 1
    depends_on: []
    updated: 2026-01-01
    ---

    Sources recorded: none.

    ## Comments
    """)
    write(root, ".claude/cadence/SESSION.local.md",
          SESSION_STATE.format(name="field-notes", current="none"))
    write(root, ".gitignore", ".claude/cadence/SESSION.local.md\n")
    init_repo(root, "initial: essay draft and Cadence setup")
    return ("Project-local flow with authored hooks. `Reviewed` is unmapped, and\n"
            "gate.citations sits on `Supported -> Reviewed` — an INTERMEDIATE hop.\n"
            "Exercises: gates collected along the whole path; a `human` approver\n"
            "(gate.editorial) that must not auto-clear; a terminal lane named\n"
            "`Final` rather than `Done`; pipeline lanes that must not run backwards.")


def execution_owns_commit(root: Path) -> str:
    """execution.owns includes commit - and execution did not do it."""
    write(root, "README.md", """
    # unit-convert
    A unit conversion library with a project execution skill.
    """)
    write(root, "src/convert.py", """
    FACTORS = {("m", "ft"): 3.280839895, ("kg", "lb"): 2.20462262}


    def convert(value, frm, to):
        if (frm, to) in FACTORS:
            return value * FACTORS[(frm, to)]
        raise ValueError(f"no conversion from {frm} to {to}")
    """)
    write(root, "src/__init__.py", "")
    write(root, "docs/ROADMAP.md", """
    # unit-convert — Vision & Roadmap

    ## Roadmap

    ### M0 — conversions that are not simple factors *(current focus)*
    **Goal:** temperature converts correctly.
    """)
    write(root, ".claude/skills/do-ticket/SKILL.md", """
    ---
    name: do-ticket
    description: Work a ticket end to end in this project - implement, test, document and commit it.
    ---
    # /do-ticket
    Implement the named ticket, add tests, update docs, then commit referencing
    the ticket id. This skill owns the checkpoint; nothing downstream re-commits.
    """)
    write(root, ".claude/cadence/config.md", config(
        name="unit-convert", prefix="UC", flow="solo-greenfield", dod="[tests, docs]",
        exec_skill="/do-ticket", exec_owns="[implement, test, docs, commit]",
        status_map="Backlog: Backlog\nIn Progress: In Progress\nDone: Done"))
    write(root, ".claude/cadence/backlog/UC-1.md", """
    ---
    id: UC-1
    title: "Support temperature conversion, which is not a simple factor"
    type: feature
    status: In Progress
    milestone: M0
    epic: ""
    labels: [feature]
    order: 1
    depends_on: []
    updated: 2026-01-01
    ---

    ## Comments
    - 2026-01-01 Session goal: bring UC-1 to Done. Handed off to /do-ticket.
    """)
    write(root, ".claude/cadence/SESSION.local.md",
          SESSION_STATE.format(name="unit-convert", current="UC-1 — temperature conversion"))
    write(root, ".gitignore", ".claude/cadence/SESSION.local.md\n__pycache__/\n")
    init_repo(root, "initial: convert() and Cadence setup")

    # The point of the fixture: /do-ticket "ran" and left the work UNCOMMITTED.
    write(root, "src/convert.py", """
    FACTORS = {("m", "ft"): 3.280839895, ("kg", "lb"): 2.20462262}
    OFFSETS = {("c", "f"): (1.8, 32.0), ("f", "c"): (1 / 1.8, -32.0 / 1.8)}


    def convert(value, frm, to):
        if (frm, to) in FACTORS:
            return value * FACTORS[(frm, to)]
        if (frm, to) in OFFSETS:
            factor, offset = OFFSETS[(frm, to)]
            return value * factor + offset
        raise ValueError(f"no conversion from {frm} to {to}")
    """)
    write(root, "tests/__init__.py", "")
    write(root, "tests/test_convert.py", """
    import unittest

    from src.convert import convert


    class TestConvert(unittest.TestCase):
        def test_temperature(self):
            self.assertAlmostEqual(convert(100, "c", "f"), 212.0)
            self.assertAlmostEqual(convert(32, "f", "c"), 0.0)
    """)
    return ("execution.owns includes `commit`, so session end must VERIFY rather\n"
            "than perform. The fixture leaves the work uncommitted and the tree\n"
            "dirty — execution claimed the job and didn't do it.\n"
            "Exercises: the verify branch, and its failure path — report the\n"
            "discrepancy, don't silently commit, don't abandon the work, and don't\n"
            "leave the item advanced with no checkpoint.")


FIXTURES = {
    "reduced-lane": reduced_lane,
    "intermediate-gate": intermediate_gate,
    "execution-owns-commit": execution_owns_commit,
}


def self_check(root: Path) -> bool:
    """Confirm the fixture is the shape it claims, before anything tests it."""
    import re

    try:
        import yaml
    except ImportError:
        print("note: PyYAML not installed; skipping fixture self-check",
              file=sys.stderr)
        return True

    ok = True
    cfg_path = root / ".claude/cadence/config.md"
    if not cfg_path.exists():
        print(f"FIXTURE BROKEN: no config at {cfg_path}", file=sys.stderr)
        return False

    m = re.search(r"```yaml\n(.*?)```", cfg_path.read_text(encoding="utf-8"), re.S)
    if not m:
        print("FIXTURE BROKEN: config has no yaml block", file=sys.stderr)
        return False
    try:
        cfg = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        print(f"FIXTURE BROKEN: config yaml does not parse: {e}", file=sys.stderr)
        return False

    if not (cfg.get("tracker") or {}).get("status_map"):
        print("FIXTURE BROKEN: no tracker.status_map", file=sys.stderr)
        ok = False

    # Every backlog item's front-matter must parse, or the tracker is unreadable.
    for item in (root / ".claude/cadence/backlog").glob("*.md"):
        fm = re.match(r"^---\n(.*?)\n---\n", item.read_text(encoding="utf-8"), re.S)
        if not fm:
            print(f"FIXTURE BROKEN: {item.name} has no front-matter", file=sys.stderr)
            ok = False
            continue
        try:
            yaml.safe_load(fm.group(1))
        except yaml.YAMLError as e:
            print(f"FIXTURE BROKEN: {item.name} front-matter: {e}", file=sys.stderr)
            ok = False

    # A project-local flow must actually be there, with any hooks it names.
    flow = str(cfg.get("flow", ""))
    if flow.endswith(".flow.md"):
        fp = root / flow
        if not fp.exists():
            print(f"FIXTURE BROKEN: flow {flow} missing", file=sys.stderr)
            ok = False
        else:
            fm = re.search(r"```yaml\n(.*?)```", fp.read_text(encoding="utf-8"), re.S)
            for hook_doc in re.findall(r":\s*(\./hooks/\S+\.md)", fm.group(1) if fm else ""):
                if not (fp.parent / hook_doc).exists():
                    print(f"FIXTURE BROKEN: hook {hook_doc} missing", file=sys.stderr)
                    ok = False
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fixture", nargs="?", choices=sorted(FIXTURES))
    ap.add_argument("--into", help="parent directory (default: a temp dir)")
    ap.add_argument("--list", action="store_true", help="list fixtures and exit")
    args = ap.parse_args()

    if args.list or not args.fixture:
        print("Fixtures - each is a configuration shape the default cannot expose:\n")
        for name, fn in sorted(FIXTURES.items()):
            first = (fn.__doc__ or "").strip().splitlines()[0]
            print(f"  {name:24} {first}")
        print("\nSee docs/VERIFICATION.md for the coverage table.")
        return 0

    parent = Path(args.into) if args.into else Path(tempfile.mkdtemp(prefix="cadence-fixture-"))
    root = parent / args.fixture
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    note = FIXTURES[args.fixture](root)

    # Check the fixture is the shape it claims before anyone tests against it.
    # A fixture that silently fails to apply produces a run that "finds" defects
    # in the harness rather than the plugin - which has happened here twice.
    if not self_check(root):
        return 1

    print(f"\n{root}\n")
    print(textwrap.indent(note, "  "))
    print("\n  Run the skills against it, then delete it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
