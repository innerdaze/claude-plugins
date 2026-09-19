# Cadence config — the annotated reference

*This file documents the **shape** of a Cadence config. It is a reference, not a
template: `/cadence:init` assembles your config from your answers and writes only
the keys you actually answered. **Nothing here is copied into your project.***

That distinction is deliberate and load-bearing. An earlier version of this file
carried a filled-in example from a real project, and init was told to write
configs "per" this file — with the result that a key present only in that example
leaked into unrelated projects. A worked example that gets copied is a
contamination channel, so this file has none.

**Location:** `.agent/cadence/config.md`. One place, always. If you want the
config visible from your doc system, add a pointer to it by hand — Cadence writes
only inside `.agent/cadence/`.

---

## Two files, and the split is by *who else needs the value*

**Changed at 0.5.0.** Cadence's config used to hold everything. It now holds only its
**methodology**; the **bindings** live in the shared config bus at `.agent/PROJECT.md`, because
another tool needs the same values and the whole point of the bus is that a project states them
once.

| Where | What | Why there |
|---|---|---|
| **`.agent/PROJECT.md`** (shared, sectioned) | tracker · VCS · doc-system · execution bindings | a second tool would legitimately use each one. Stating them twice is how they drift |
| **`.agent/cadence/config.md`** (cadence's own root) | flow, session state, gates, model tiers, `cadence_version` | only cadence can use them. A flow spec is meaningless to a ticket engine |

**The test, stated once:** *if only one tool could use a value, it does not belong in the bus.*

`## Tracker` is the interesting case, and the answer changed: **it belongs to no role, and
cadence does not take it over.** The old design had cadence claim the section on install,
rewriting its owner marker. That conflated two different things — **which tracker this project
uses** is an environment fact that `work`, `domains` and `cadence` all read and any of them may
have asked about, while **what to work on next** is the methodology decision, and only the second
is cadence's. It already lives in `## Execution` and the flow. Claiming the section claimed the
fact rather than the decision.

So `## Tracker` is `shared`: read it, write a row that is absent, never overwrite a value another
tool wrote. What stays in cadence's own config is the part only cadence can use — the
`status_map`, which maps *this flow's* lanes onto the tool's real statuses. The tracker's `kind`,
access and prefix are the bus's.

## The shape

```yaml
cadence_version: "0.5"             # the contract version this config is written against

# `project` is gone: name and ticket prefix are the bus's `## Project` -> Name and
# `## Tracker` -> Prefix. Two copies of one fact is what the bus exists to prevent.

# --- Bindings: WHERE and WITH WHAT you work (resolved via adapters) ---

tracker:  # kind/access/prefix ⇒ the bus's `## Tracker` (a `shared` section — read it, never
          # take it over). Only `status_map` stays here, because only cadence can use it.
  hands_off:                        # columns cadence takes NO action in
    - status: In Dev Review
      note: "MR is with a peer. I take no action; the item is not stalled."
    - status: Awaiting Release
      note: "Release train picks it up. Nothing for me to do."
  notes: >                          # anything the board cannot tell you
    Bugs found in QA come back to In Progress rather than a new ticket.
  # --- how this project's process lanes map to the tool's REAL statuses ---
  status_map:                       # lane (from the flow) -> the tool's status
    Backlog: Backlog
    In Progress: Doing
    Done: Done
    # Where two of the tool's statuses share a display name - which Linear, Jira
    # and GitHub Projects all permit - a bare name is ambiguous and the entry
    # must qualify it:
    #   Backlog: { name: Queued, category: backlog }
    #   Todo:    { name: Queued, category: unstarted }

vcs:      # ⇒ MOVED to the bus's `## Version control` section (read, not owned)
  kind: <git | diversion | jj | hg>
  checkpoint: <commands | skill:/your-commit-skill>
  gotchas: "<optional: quirks specific to THIS machine or workspace>"

execution:  # ⇒ MOVED to the bus's `## Execution` section
  skill: <e.g. /work-on | none>           # the project's own ticket-execution skill
  owns: [implement, test, docs, commit]   # what /cadence:session END must VERIFY, not repeat
                                          # `status` is deliberately absent: the done transition
                                          # is the session's, gated by the DoD. A project may add
                                          # it — the execution skill then closes items itself and
                                          # the gate runs after the fact; the doctor says so

doc_system: # ⇒ MOVED to the bus's `Doc system` binding row
  kind: <none | docs | ...>
  notes: .agent/cadence/notes.md   # required for kind: none — where record() appends
  index: <e.g. docs/INDEX.md | omit>
  ticket_to_docs: "<rule mapping labels to docs | omit>"
  roadmap: docs/ROADMAP.md          # where /cadence:roadmap reads and writes

# There is no `intent` key, and there will not be one. Stated design is read from the bus's
# `Intent` binding row and the `intent-layer` artifact row — another role writes both; cadence
# reads them and stops planning a milestone that contradicts what they point at. `none`, or no
# row, means milestones go unchecked, and cadence says so once at init's dry-run.

session_state:
  file: .agent/local/cadence-session-<worktree>.md   # Cadence's OWN scratchpad — LOCAL, ignored
         # `.agent/local/` is ignored as a directory and is meant to be SHARED across
         # worktrees (a symlink you create), so the worktree key in the filename is
         # what stops two checkouts sharing one session
  format: markdown

# --- Models: WHICH tier does WHICH work (a third binding) ---

models:
  mechanical: haiku      # cheap tier: adapter file/CLI ops, scaffolding, collating
  reasoning:  inherit    # judgment stays on the session model

# --- Methodology: HOW you work ---

flow: <solo-greenfield | team-sprints | live-oncall | ./my-flow.flow.md>

dod_gates:                 # ADDS to the flow's own gates.dod.checks — never replaces
  - tests                  # a bare entry always applies
  - check: comment quality
    applies: infer         # the session judges, per change, and shows its evidence
  - check: security-review
    applies: always        # inference is unreliable here — absence of evidence is not evidence
  - check: migration-rehearsed
    applies_when:
      changed_paths: ["migrations/**", "templates/**"]
```

---

## Notes on the keys that cause trouble

**`cadence_version` exists so an upgrade mismatch is detectable.** Flows have
always declared the contract version they target; configs did not — which meant a
config using a newer contract feature than the installed plugin was invisible.
That is a real ordering hazard, not a theoretical one: it happened here, when a
config was written with the qualified `status_map` form against a plugin that
predated it. The older skill reads a mapping where it expects a string and has no
way to know why. `/cadence:doctor` compares this against the installed version and
says so.

**`tracker.status_map` is the whole reason lanes are safe.** A flow declares
*process* lanes; your tracker has whatever columns it has. This map is the only
place the two meet, and init builds it by asking your tracker what statuses it
actually has (`statuses()`) and showing you the answer — never by copying a
preset's lane names.

A lane with **no entry here is fine.** It means your tool can't represent that
step, so Cadence skips it and says so once. If your board is just Backlog and
Done, map those two and leave the rest out; sessions simply won't mark work
in-flight. Cadence never creates a column in your tracker.

**`dod_gates` adds, it never replaces.** The effective Definition of Done is the
flow's `gates.dod.checks` **∪** this list. You can raise the bar for your project;
you cannot silently lower what the flow requires.

An entry takes the same forms a flow's `checks` do (`flows/FLOW-SPEC.md` §
*Declaring what makes a check applicable*): a bare string (always), `applies:
always`, `applies: infer`, or `applies_when` with globs or one prose sentence.
`infer` is what `/cadence:init` writes for a check you add, because a check that
fires at changes it has nothing to say about is how a Definition of Done becomes
a toll. **Declaring a looser mode here cannot loosen a check the flow pinned**;
where both name the same check the stricter wins — `always` > `applies_when` >
`infer` — because the union may only raise the bar. And every check
that does not apply is named in the session's report with its reason, so a
condition you regret is visible rather than quiet.

**`execution.owns` is a seam, not a wish list.** It tells `/cadence:session end`
what to *verify* rather than repeat. If `execution.skill` is `none`, leave `owns`
empty — the session then performs the checkpoint itself, which is the normal
zero-dependency path, not a degraded one.

**Models are a binding, not an assumption.** Available tiers differ per user and
IDs differ on Bedrock/Vertex, so this is config. `mechanical` names the cheap
model Cadence delegates *batchy* mechanical work to; `reasoning: inherit` keeps
judgment on the session model. If a configured tier isn't available, Cadence says
so and runs inline rather than substituting a tier you didn't choose.

**One root, two kinds of file.** Everything Cadence owns lives under
`.agent/cadence/` — config, generated adapters, a custom flow, the `markdown`
tracker's `backlog/`, the `none` adapter's `notes.md`. All of it is **committed**
except the `.local.md` session scratchpad, which init adds to your ignore file.
See "Where adapter data lives" in `adapters/ADAPTERS.md`.

**What is *not* here.** `epic_convention` lives in the tracker adapter's Concept
mapping, because how a tool represents an epic is a fact about the tool, not
about your project. Terminal statuses are not configured either — they are
derived from the flow's `states.roles`.

## The zero-dependency setup

If nothing is detected, this is a complete, runnable config with no external
service:

```yaml
tracker:   { status_map: { Backlog: Backlog, Done: Done },
             hands_off: [], notes: "" }   # kind/path live in the bus
vcs:       { kind: git, checkpoint: commands }
execution: { skill: none, owns: [] }
doc_system:{ kind: none, notes: .agent/cadence/notes.md, roadmap: docs/ROADMAP.md }
session_state: { file: .agent/local/cadence-session-<worktree>.md, format: markdown }
models:    { mechanical: haiku, reasoning: inherit }
flow:      solo-greenfield
dod_gates: [tests, docs]
```

Note the two-entry `status_map`: even the default doesn't pretend to have five
columns.
