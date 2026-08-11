---
description: Set up Cadence in this project — detect the tracker/VCS/doc-system/execution bindings, generate their adapters, pick or author a flow, map your tracker's real statuses to it, write the config, and scaffold the roadmap.
argument-hint: "[--defaults for a non-interactive zero-dependency setup]"
---

Set up Cadence in this project by following the `cadence-init` skill at
`${CLAUDE_PLUGIN_ROOT}/skills/cadence-init/SKILL.md`. Read that skill and follow it exactly.

The governing rule is **detect, then confirm — never assume**: propose what you find, write nothing
until the user approves, and treat a missing binding as a question for the user rather than a gap to
fill by inference. Assemble the config from the user's answers — never copy one from anywhere.

If the argument is `--defaults`, run the non-interactive path described at the end of that skill:
the zero-dependency stack only, and no MCP-backed tracker.

$ARGUMENTS
