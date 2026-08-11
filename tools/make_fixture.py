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

PLUGIN = Path(__file__).resolve().parent.parent / "cadence"


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
    """Assemble a config from the pieces a fixture varies."""
    return f"""
    # Cadence config — {kw['name']}

    ```yaml
    project:
      name: {kw['name']}
      ticket_prefix: {kw['prefix']}

    tracker:
      kind: markdown
      path: .claude/cadence/backlog
      status_map:
    {textwrap.indent(kw['status_map'].strip(), '    ' * 2)}

    vcs:
      kind: git
      checkpoint: commands

    execution:
      skill: {kw['exec_skill']}
      owns: {kw['exec_owns']}

    doc_system:
      kind: none
      notes: .claude/cadence/notes.md
      roadmap: docs/ROADMAP.md

    session_state:
      file: .claude/cadence/SESSION.local.md
      format: markdown

    models:
      mechanical: haiku
      reasoning: inherit

    flow: {kw['flow']}

    dod_gates: {kw['dod']}
    ```
    """


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
    print(f"\n{root}\n")
    print(textwrap.indent(note, "  "))
    print("\n  Run the skills against it, then delete it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
