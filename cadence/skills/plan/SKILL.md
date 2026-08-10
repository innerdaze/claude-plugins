---
name: cadence-plan
description: Break a roadmap milestone into epics and tickets in the project's tracker, using the feature-process templates and the flow's decision rights. Under a solo flow it creates the work directly; under a team flow it proposes a plan and defers the commit to a planning ceremony. Use when the user runs /plan, asks to plan a milestone or sprint, or to break down work.
---

# /plan — break a milestone into work

Turns a milestone from the roadmap into concrete epics and tickets in the tracker. Uses the plugin's `templates/feature-process.md` for shapes and the flow for how much the skill may decide.

## Load

- Config: tracker adapter, `dod_gates`, `execution.owns`, doc/context taxonomy.
- Flow: `hierarchy`, `gates`, `decision_rights`, `cadence`, and the `plan.*` hooks.
- The roadmap doc (for the milestone's goal + exit criteria).

## Steps

1. **Pick the milestone** — from the argument, else the current one in the roadmap. Restate its goal + exit criteria.

2. **`plan.breakdown`** (default): propose the smallest set of **epics** that together deliver the milestone's exit criteria. Break each epic into **tickets** using the epic/ticket templates. For every epic, include the standard tickets:
   - a **cross-cutting-requirement ticket per applicable `dod_gate`** that the work doesn't satisfy inline (e.g. a multiplayer/replication ticket, a security-review ticket) — created during planning, schedulable later, so a project quality bar becomes tracked work;
   - an **integration + verify + docs ticket**.
   Assign each item labels from the project's context taxonomy (so the execution skill loads the right context), and set `milestone`/`epic` links.

3. **`plan.estimate`** (optional) — size items if the flow uses estimates.

4. **`plan.commit_scope`** — respect `decision_rights.commit_scope`:
   - **`ai`** (solo/greenfield) → create the items directly.
   - **`ai-proposes`** → present the full proposal, get the user's approval, then create.
   - **`human`** (team) → produce a **planning pack** for the planning ceremony and **stop** — do not auto-create scope. What the ceremony commits is recorded later via `ceremony.planning.capture`.

5. **Create the items** via the tracker adapter (`create`), linking tickets → epics → milestone and setting the initial status per the flow's `states` (e.g. `Backlog`/`Todo`). For a large breakdown, hand the bulk item-creation to the `mechanical` subagent (on `config.models.mechanical`) — the decisions are already made; only the tracker writes remain.

## Cadence note

- **Continuous / solo:** `/plan` populates the milestone's backlog.
- **Sprint / team:** `/plan` *is* sprint planning — it proposes a sprint's worth of work and, for `human` commit rights, defers the actual commitment to the ceremony rather than deciding scope for the team.

## Boundaries

- **Creates (or proposes) work items; does not implement.** Working a ticket is the execution skill, entered via `/session`.
- **Does not set vision.** Milestones and their exit criteria come from `/roadmap`.
- **Honours decision rights.** Never commits team scope the flow reserves for a human.

## Next

Hand off to `/session start`, which will pick the first item per the flow's priority policy.
