---
description: Check this project's Cadence setup and report what is broken, disabled, or drifted — config, flow validity, adapter coverage, tracker reachability and ownership, lane mappings, and session state. Read-only; fixes nothing.
argument-hint: "(no arguments)"
---

Check this project's Cadence setup by following the `cadence-doctor` skill at
`${CLAUDE_PLUGIN_ROOT}/skills/cadence-doctor/SKILL.md`. Read that skill and follow it exactly.

This is a **read-only** diagnosis. Do not write, fix, rebind, or "helpfully"
repair anything you find — report it and name the remedy. `/cadence:init` is the
only skill that writes configuration, and keeping one writer is what makes this
safe to run anywhere.

$ARGUMENTS
