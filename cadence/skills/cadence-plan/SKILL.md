---
name: cadence-plan
description: Break a roadmap milestone into epics and tickets in a project already configured with Cadence, using the feature-process templates and the flow's decision rights. Under a solo flow it creates the work directly; under a team flow it proposes a plan and defers the commit to a planning ceremony. Use when the user runs /cadence:plan, or asks to break a milestone, epic, or sprint into tracked work items. Not for ad-hoc planning of a single task — this writes to the project's tracker.
---

# /cadence:plan — break a milestone into work

Turns a milestone from the roadmap into concrete epics and tickets in the tracker. Uses the plugin's `${CLAUDE_PLUGIN_ROOT}/templates/feature-process.md` for shapes and the flow for how much the skill may decide.

## Load

- Config: tracker adapter, `dod_gates`, `execution.owns`, and the doc adapter (for `taxonomy()`).
- Flow: `hierarchy`, `gates`, `decision_rights`, `cadence`, and the `plan.*` hooks.
- The roadmap doc (for the milestone's goal + exit criteria).

## Steps

1. **Pick the milestone** — from the argument, else the current one in the roadmap. Restate its goal + exit criteria.

2. **`plan.breakdown`** (default): propose the smallest set of **epics** that together deliver the milestone's exit criteria. Break each epic into **tickets** using the epic/ticket templates. For every epic, include the standard tickets:
   - a **cross-cutting-requirement ticket per applicable `dod_gate`** that the work doesn't satisfy inline (e.g. a security-review ticket, an accessibility pass) — created during planning, schedulable later, so a project quality bar becomes tracked work;
   - an **integration + verify + docs ticket**.
   Label each item from the doc adapter's `taxonomy()` (so the execution skill can load the right context from labels alone), and set `milestone`/`epic` links. If `taxonomy()` is empty — the `none` doc system — skip context labels rather than inventing a scheme, and apply only the flow's own type labels.

3. **`plan.estimate`** (optional) — size items if the flow uses estimates.

4. **`plan.commit_scope`** — respect `decision_rights.commit_scope`:
   - **`ai`** (solo/greenfield) → create the items directly.
   - **`ai-proposes`** → present the full proposal, get the user's approval, then create.
   - **`human`** (team) → produce a **planning pack** for the planning ceremony and **stop** — do not auto-create scope. What the ceremony commits is recorded later via `ceremony.planning.capture`.

5. **Create the items** via the tracker adapter (`create`), linking tickets → epics → milestone and setting the initial status per the flow's `states` (e.g. `Backlog`/`Todo`). For a large breakdown, hand the bulk item-creation to the `mechanical` subagent — the decisions are already made; only the tracker writes remain. Spawn it per the calling convention in `${CLAUDE_PLUGIN_ROOT}/adapters/ADAPTERS.md` (pass `config.models.mechanical` as a model override when it isn't `haiku`).

## Cadence note

- **Continuous / solo:** `/cadence:plan` populates the milestone's backlog.
- **Sprint / team:** `/cadence:plan` *is* sprint planning — it proposes a sprint's worth of work and, for `human` commit rights, defers the actual commitment to the ceremony rather than deciding scope for the team.

## Boundaries

- **Creates (or proposes) work items; does not implement.** Working a ticket is the execution skill, entered via `/cadence:session`.
- **Does not set vision.** Milestones and their exit criteria come from `/cadence:roadmap`.
- **Honours decision rights.** Never commits team scope the flow reserves for a human.
- **Surfaces gaps instead of filling them.** If the config, flow, tracker, or doc adapter doesn't resolve, stop and say which link broke — see "When something doesn't resolve" in `${CLAUDE_PLUGIN_ROOT}/skills/cadence-session/SKILL.md`. Creating items against a guessed tracker or a substituted flow is the expensive failure here, because the items persist.

## Next

Hand off to `/cadence:session start`, which will pick the first item per the flow's priority policy.
