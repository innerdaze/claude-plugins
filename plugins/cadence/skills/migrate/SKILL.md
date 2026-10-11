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

**Then bring the config's contract current — every run, whatever the stamp said.**
`cadence_version` in `.agent/cadence/config.md` is a second number with its own question
(`${CLAUDE_PLUGIN_ROOT}/migrations/README.md` § *The stamp*), so "scaffolding up to date" does not answer it. Compare it
with `${CLAUDE_PLUGIN_ROOT}/flows/CONTRACT-VERSION.md`:

| Config says | Do |
|---|---|
| same as the contract | nothing |
| **same major, older minor** | raise it to the contract and name, from `CONTRACT-VERSION.md`, what each skipped minor added. Every minor is additive by that file's own rule, so the config still means what it said — the raise is a true statement, not a guess. Touch no other key |
| **older major** | decline: something the config relies on was renamed or changed meaning. List what changed and name `/cadence:init`, which re-asks only what the change affects |
| newer than the contract | decline: the plugin is behind, not the config. Name `claude plugin update` |
| absent | decline: the config predates 0.3. Name `/cadence:init` |

**Never raise a project-local flow's `meta.cadence_version`.** A flow is its author's statement
about what they wrote against; a minor behind is informational (`/cadence:doctor` § 2), and
rewriting it would claim a review nobody did. Report it in one line.

Found on a real upgrade: scaffolding migrated, contract at 0.6, config left at 0.5 — and the only
remedy anything named was a full `/cadence:init`.

**One developer, one reviewed change.** A migration edits shared committed files and re-stamps
once; run it on its own branch, not folded into unrelated work.
