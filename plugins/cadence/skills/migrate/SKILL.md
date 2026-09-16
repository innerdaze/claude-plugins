---
name: migrate
description: >-
  Apply pending migrations to cadence's own project-local scaffolding — its config location, the
  split between shared bindings and methodology, and where its root lives. Reads the
  `cadence methodology` row from the config bus's `## Versions`, applies only what is pending,
  and re-stamps that row alone. Use whenever the user says "cadence migrate", "upgrade cadence's
  config", "move cadence's root", or when another tool's migrate reports that the `methodology`
  role is stale.
user-invokable: true
---

Read `${CLAUDE_PLUGIN_ROOT}/migrations/README.md` for the rules and
`${CLAUDE_PLUGIN_ROOT}/migrations/MIGRATIONS-VERSION.md` for the canonical integers. Then, from
`${CLAUDE_PLUGIN_ROOT}/migrations/`, read **only the pending** per-version files — the ones
numbered above this project's stamp, up to and including the canonical version — and follow them
in ascending order. Never read the whole history: cost should scale with the gap to close.

**Read the stamp first.** The `cadence methodology` row in the bus's `## Versions`; a missing row
means **v0** (pre-versioning), not "up to date". Stamp only that row, only after everything in
range succeeded, and never another owner's row.

**Preconditions are a real answer.** A migration whose preconditions are unmet declines: record
what it was waiting for and report it. An orchestrating `migrate` will come back after something
else applies — declining is ordinary, not a failure.

**One developer, one reviewed change.** A migration edits shared committed files and re-stamps
once; run it on its own branch, not folded into unrelated work.
