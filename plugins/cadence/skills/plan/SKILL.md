---
name: plan
description: Break a roadmap milestone into epics and tickets in a project already configured with Cadence, using the feature-process templates and the flow's decision rights. Under a solo flow it creates the work directly; under a team flow it writes a planning pack and defers the commitment to the team. Use when the user runs /cadence:plan, or asks to break a milestone, epic, or sprint into tracked work items. Not for ad-hoc planning of a single task — this writes to the project's tracker.
---

# /cadence:plan — break a milestone into work

Turns a milestone from the roadmap into concrete items in the tracker. Uses `${CLAUDE_PLUGIN_ROOT}/templates/feature-process.md` for shapes and the flow for how much this skill may decide.

## Load

- **Config**: the tracker adapter (and its **Capabilities** block), `dod_gates`, `execution.owns`, the doc adapter, `doc_system.roadmap`.
- **Flow**: `hierarchy.levels`, `states.roles`, `gates`, `decision_rights`, `cadence`, and the `plan.*` hooks.
- **The roadmap doc** at `config.doc_system.roadmap` — for the milestone's goal and exit criteria.

## Steps

1. **Pick the milestone** — from the argument, else the current one in the roadmap. Restate its goal and exit criteria; if they aren't concrete enough to tell when the milestone is finished, say so and offer `/cadence:roadmap` first. Planning against vague exit criteria produces vague tickets.

2. **`plan.breakdown`** (default): propose the smallest set of items at the flow's `hierarchy.levels` that together deliver the exit criteria. For each level-2 item (epic, or whatever the flow calls it), include:
   - a **cross-cutting-requirement item per applicable effective DoD gate** that the work doesn't satisfy inline — a security review, an accessibility pass. Create these only for gates that genuinely need separate scheduled work; a gate like `tests` that every item satisfies inline does **not** get its own ticket, or you generate ceremony;
   - an **integration + verify + docs item** — wire the pieces together, run the epic's DoD, update docs, checkpoint. This is what prevents "all tickets done, nothing works together."

3. **Label from `taxonomy()`.** Ask the doc adapter for the project's label vocabulary and label items from it, so the execution skill can load the right context from labels alone. If `taxonomy()` is empty or unsupported — the `none` doc system — apply only the flow's type labels and **do not invent a scheme**.

4. **Set the fields the priority policy needs.** Read the flow's `priority_policy`, look up each token's required field, and populate it: `order` for `backlog-by-rank`, `depends_on` for `blocker-for-current-ticket`, `milestone` for `next-roadmap-ticket`, `epic` for `current-epic`, `cycle` for `committed-sprint`. A policy token whose field nobody writes is a token that silently does nothing — this step is what makes `flow.intake.priority_policy` real rather than decorative.

   **Check each field is actually settable here, not merely listed as supported.** Some are conditional: a Linear milestone needs a *project* to exist first, so `milestone` can be "supported" by the adapter and still unsettable on a board with no projects. Where you cannot set a field the policy depends on, **say which token that disables** and either create the missing prerequisite or tell the user what to create. Silently omitting it produces the worst outcome — a backlog full of work that goal selection cannot see.

5. **`plan.estimate`** (optional) — size items if the flow uses estimates.

6. **`plan.commit_scope`** — respect `decision_rights.commit_scope`:
   - **`ai`** → create the items directly.
   - **`ai-proposes`** → present the full proposal, get approval, then create.
   - **`human`** → **write a planning pack** to `.agent/cadence/planning-pack-<YYYY-MM-DD>.md` and stop. Do not create scope.

     **Then say what happens next**, because the pack is an input to a meeting rather than the end
     of one: the team commits the cycle **in the tracker** — starting the sprint, or setting the
     cycle field on the agreed items — and cadence reads it from there. Nothing reads this pack
     back, and nothing needs to: a sprint committed on the board is the real commitment. The pack holds the ranked candidates with their estimates and DoD gates, last cycle's throughput if the tracker can supply it, a *proposed* cycle sized to that throughput, and the open questions blocking commitment. Tell the user to take it to their planning meeting and re-run `/cadence:plan` — or edit the board — once scope is agreed. (Cadence has no ceremony layer yet; this file is what stops "defer to the planning ceremony" from being a dead end.)

   **Whenever scope is actually committed — by any branch — it means two things, not one**: writing the `cycle` onto the items, *and* moving them to `roles.committed` if the flow declares that role and its lane is mapped. A sprint flow with a "committed but not started" lane that never receives anything is describing a process it does not perform.

7. **Create the items** via the tracker adapter (`create`), linking children to parents and setting the initial status to **`flow.states.roles.backlog`** resolved through `config.tracker.status_map`. If that role is unmapped, ask which status new work should start in rather than guessing. For a large breakdown, hand the bulk creation to the `mechanical` subagent — the decisions are already made; only the tracker writes remain. Spawn it per the calling convention in `${CLAUDE_PLUGIN_ROOT}/adapters/ADAPTERS.md`.

   **Set the assignee when the owner is unambiguous.** On a single-developer project with a
   tracker that supports the field, every new item is that developer's — create them assigned,
   rather than leaving a backlog of unassigned tickets that says nothing about who will do them.

   On a team the owner is usually not knowable yet, and empty is then the honest value: the
   planning meeting assigns, or whoever takes an item assigns it then. Do not guess — a wrong
   assignee reads as somebody's decision. `ADAPTERS.md` § *Ownership* has the reasoning.

8. **Checkpoint the new items.** If the tracker stores items in the repo, a breakdown just created a pile of files. Commit them via the VCS adapter (`add_untracked` + `checkpoint`, message referencing the milestone) so they are versioned as their own change. Leaving them untracked means the next `/cadence:session end` sweeps a whole backlog into an unrelated item's commit — and `/cadence:doctor` will rightly flag it. If the tracker is hosted, there is nothing to commit; say so and skip.

## Cadence note

- **Continuous / solo:** `/cadence:plan` populates the milestone's backlog.
- **Sprint / team:** `/cadence:plan` *is* planning preparation — it proposes a cycle's worth of work and, for `human` commit rights, produces the pack and defers rather than deciding scope for the team.

## Boundaries

- **Creates (or proposes) work items; does not implement.** Working an item is the execution skill, entered via `/cadence:session`.
- **Does not set vision.** Milestones and their exit criteria come from `/cadence:roadmap`.
- **Honours decision rights.** Never commits team scope the flow reserves for a human.
- **Surfaces gaps instead of filling them.** If the config, flow, tracker, or doc adapter doesn't resolve, stop and say which link broke — see "When something doesn't resolve" in `${CLAUDE_PLUGIN_ROOT}/skills/session/SKILL.md`. Creating items against a guessed tracker or a substituted flow is the expensive failure here, because the items persist.

## Next

Hand off to `/cadence:session start`, which will pick the first item per the flow's priority policy.

Keep the report to what changes what the reader does next — one line per item created or changed, one line per thing you could not do and why. The workings are already in the transcript above.
