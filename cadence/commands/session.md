---
description: Start or end a bounded Cadence work session — start picks one goal per the flow's priority policy and hands off to the project's execution skill; end runs the gates, verifies the checkpoint, and sets the next goal.
argument-hint: "start | end"
---

Run a Cadence work session by following the `cadence-session` skill at
`${CLAUDE_PLUGIN_ROOT}/skills/cadence-session/SKILL.md`. Read that skill and follow it exactly.

The argument selects the half of the ritual to run:

- `start` (or no argument, when no session is currently open) → the start sequence.
- `end` → the end sequence.

If the argument is missing and the session state file records an open goal, assume `end` and say so
before proceeding, so the user can correct you.

$ARGUMENTS
