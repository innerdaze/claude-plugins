---
name: cadence-roadmap
description: Create or update a project's vision & roadmap — the north star. Drafts the pitch, pillars, and milestones (each with one goal + concrete exit criteria), and revisits them at milestone boundaries. Defines milestones; does not break them into tickets (that's /cadence:plan) or implement. Use when the user runs /cadence:roadmap, asks to draft or update a vision or roadmap doc, wants to define or re-cut milestones, or asks what the project should aim at next at a milestone boundary.
---

# /cadence:roadmap — own the vision & roadmap

Maintains the project's living north-star doc, from the plugin's `${CLAUDE_PLUGIN_ROOT}/templates/vision-and-roadmap.md`. Vision is **human-led**: this skill facilitates, structures, and drafts — the user owns the content. It proposes; it doesn't decide the vision.

## Load

- Read the config (for the doc location and `decision_rights`) and the flow.
- Find the roadmap doc (init scaffolds it; typically alongside the config or in the project's docs). If none exists, start from the template.

## Mode A — Create (no roadmap yet)

Fill the template by facilitating, section by section. Either interview the user, or draft a proposal from what's known and refine with them:

1. **One-line pitch** — what this is and why it's different.
2. **Purpose / fantasy** — what it's for; for a product, what the user feels or gains.
3. **Pillars** — 3–5 principles that can settle arguments.
4. **Core thesis / loop** — the central thing the first milestone must prove.
5. **Where we are** — honest built-vs-missing.
6. **Milestones** — sequence toward the nearest meaningful, de-risking outcome. **Each milestone gets exactly one goal, concrete exit criteria, and an explicit "cut" list.** The cut list matters as much as the scope.

Write the doc. Record any settled forks in the **Key decisions** table with their *why*, so they aren't relitigated.

## Mode B — Update (roadmap exists)

Read it first, then revisit — typically at a milestone boundary:
- Mark a finished milestone done; sharpen or add the next.
- Add newly-locked decisions to the Key decisions table.
- Move firmed-up "open questions" into milestones or hand them to `/cadence:plan`.

Keep it a **living doc, not a changelog** — no ticket IDs or dates in here; those live in the tracker.

## Registering milestones (optional)

If the flow/tracker uses milestones, offer to register each milestone in the tracker via the tracker adapter (`create` with `type: milestone`), so `/cadence:plan` and `/cadence:session` can scope to it. For a `markdown` tracker this is a milestone item file; for hosted trackers, a native milestone.

## Boundaries

- **Defines milestones; does not create tickets.** Breaking a milestone into epics/tickets is `/cadence:plan`.
- **Does not implement.** That's the execution skill.
- **Proposes, doesn't dictate.** Vision/roadmap edits are the user's call; the skill drafts and structures.
- **Works without a full setup.** The roadmap is a document, so this skill can run from the template alone before Cadence is configured — if there's no config, say so, draft the doc, and suggest `/cadence:init` for the rest. Only milestone *registration* needs a tracker; if that doesn't resolve, skip it and say why rather than stopping.

## Next

Point the user to `/cadence:plan <milestone>` to break the current milestone into work, then `/cadence:session start` to begin.
