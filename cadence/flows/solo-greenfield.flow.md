# Flow: Solo / Greenfield

*A shipped Cadence preset. One builder, no live users yet — maximize momentum, let the skill decide. Fork this file to customize (levels 2–3); any hook you don't set uses the built-in default. This file is also the worked example of the flow-spec vocabulary — every section below is part of the schema.*

```yaml
meta:
  name: solo-greenfield
  summary: One builder, pre-release. High autonomy, continuous flow, ship-nothing-yet.
  autonomy: high            # high | mixed | low  (the through-line: how much the skill may decide)

# --- Work hierarchy: the levels an item can be, top-down ---
hierarchy:
  levels: [milestone, epic, ticket]
  spikes: allowed           # timeboxed investigations attach under a milestone or epic

# --- States an item moves through, and which transitions are gated ---
states:
  lanes: [Backlog, Todo, In Progress, In Review, Done]
  wip_limit: none
  gated_transitions:
    "In Review -> Done": [gate.dod]

# --- Gates: named checkpoints with a condition + an approver ---
gates:
  dod:
    approver: ai            # ai | ai-proposes | human
    checks: [tests, docs]   # baseline; a project extends via config.dod_gates
  # no design_review / qa / release gates in this preset

# --- Cadence & ceremonies ---
cadence:
  model: continuous         # continuous | sprint | kanban
  ceremonies: []            # solo continuous flow has none

# --- Intake & prioritization: how work enters, and what /session start picks ---
intake:
  new_work: roadmap-driven  # the next open ticket in the current milestone's active epic
  bug_triage: defer         # defer | file | preempt   (solo bug-batch rule: file, don't fix on sight)
  priority_policy:
    - blocker-for-current-ticket
    - current-epic
    - next-roadmap-ticket

# --- Decision rights: the autonomy dial per step ---
decision_rights:
  select_goal:     ai
  plan_breakdown:  ai
  commit_scope:    ai
  release:         ai

# --- Session definition: what a work session is, how its goal is chosen ---
session:
  goal: one ticket (or a clean slice of one) from the current milestone
  start: load memory -> propose 1-3 next tickets -> name one goal + type -> hand to execution skill
  end: run gate.dod -> verify (not repeat) the execution skill's commit + domain-doc update -> set next goal

# --- Hooks: level-3 overrides map a hook name to your instruction doc. ---
# None here — this preset uses all built-in defaults. To override:
#   hooks:
#     session.select_goal: ./hooks/select_goal.md
hooks: {}
```

## How the other presets differ from this one

Same schema, different values — this is what "configurable methodology" means in practice:

- **Team / Sprints:** `cadence.model: sprint` with `ceremonies: [planning, standup, review, retro]`; `decision_rights` shift to `ai-proposes` (the skill drafts, a human ceremony commits); `gates` add `code_review`; `intake.new_work` becomes "the top item of the committed sprint," not "next roadmap ticket."
- **Live Product / On-call:** adds an `incident` lane above everything and `intake.bug_triage: preempt` (a customer incident interrupts the roadmap); `gates` add `regression`, `changelog`, `release_approval`; `decision_rights.release: human`; checkpoint becomes a gated, versioned release.

## Authoring your own (levels 1–3)

1. **Override axes** — copy this file, change values (e.g. `cadence.model: kanban`, a different `priority_policy`, extra `gates`).
2. **Edit the spec** — rewrite `states`/`gates`/`ceremonies` for a bespoke process.
3. **Authored stages** — set a `hooks:` entry pointing at your own instruction doc; the skill loads it at that hook instead of the default. See `HOOKS.md` for the full hook surface and each hook's input→output contract.
