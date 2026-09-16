# Flow: Solo / Greenfield

*A shipped Cadence preset. One builder, no live users yet — maximize momentum, let the skill decide. Fork this file to customize; any hook you don't set uses the built-in default. The schema every key here comes from is `FLOW-SPEC.md`.*

> **The lanes below are process vocabulary, not columns you must create.** Only
> `backlog` and `done` are structurally required; `In Progress` is a refinement —
> if your tracker has two columns, map those two in `config.tracker.status_map`,
> leave the rest unmapped, and Cadence will skip the steps that need them. It will
> never add a column to your board.
>
> This preset deliberately declares **three** lanes, not five. An earlier version
> listed `Todo` and `In Review` as well, and nothing could ever put an item in
> either — a flow should not name parts of a process it does not perform.

```yaml
meta:
  name: solo-greenfield
  summary: One builder, pre-release. High autonomy, continuous flow, ship-nothing-yet.
  cadence_version: "0.6"
  autonomy: high            # documentation only — orients a flow author

hierarchy:
  levels: [milestone, epic, ticket]

states:
  lanes: [Backlog, In Progress, Done, Won't Do]
  roles:
    backlog: Backlog        # required — where /cadence:plan creates
    active:  In Progress    # omit this and sessions won't mark work in flight
    done:    Done           # required
    abandoned: [Won't Do]   # terminal, not success — map a won't-fix column here
    # no `review` role: solo work has no separate review step
  wip_limit: none
  gated_transitions:
    "In Progress -> Done": [gate.dod]
    "Backlog -> Won't Do":  []   # a decision, taken by a person

gates:
  dod:
    approver: ai            # ai | ai-proposes | human
    checks:                 # a project ADDS to this via config.dod_gates
      - tests
      - check: docs
        applies_when: "the change alters a documented surface - a command, a config key,
          a published contract, or prose that describes one"

cadence:
  model: continuous
  ceremonies: []            # solo continuous flow has none

intake:
  new_work: roadmap-driven
  bug_triage: defer         # file it, keep going — don't fix on sight
  priority_policy:
    - blocker-for-current-ticket
    - current-epic
    - next-roadmap-ticket

decision_rights:
  select_goal:     ai
  plan_breakdown:  ai
  commit_scope:    ai
  release:         ai

session:
  goal: one ticket (or a clean slice of one) from the current milestone

hooks: {}
```

## Why the gate sits on `In Progress -> Done`

An earlier version gated `"In Review -> Done"` — but this flow declares no
`review` role, so nothing ever entered `In Review`, and the only gate in the
preset was attached to a transition that never happened. The gate now sits on the
transition this flow actually makes. If you add a review step, add the lane role,
its `status_map` entry, and the transition together — all three, or the gate
goes back to being decorative.

## How the other presets differ

Same schema, different values — this is what "configurable methodology" means:

- **Team / Sprints:** `cadence.model: sprint`; `decision_rights` shift to `ai-proposes` (the skill drafts, a human ceremony commits); a `code_review` gate and a real `review` role; `intake.new_work` becomes the committed cycle rather than the raw roadmap.
- **Live Product / On-call:** adds an incident lane above the hierarchy and `intake.bug_triage: preempt` — a customer incident interrupts the roadmap; more gates, and `decision_rights.release: human`.

## Authoring your own

1. **Override axes** — copy this file, change values.
2. **Edit the spec** — restructure states and gates for a bespoke process.
3. **Authored stages** — point a `hooks:` entry at your own instruction doc.

`FLOW-SPEC.md` is the schema; `HOOKS.md` is the hook surface and each hook's
input→output contract.
