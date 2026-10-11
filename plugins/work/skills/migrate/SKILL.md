---
name: migrate
description: >-
  Apply pending scaffolding migrations to a project initialised against an older `work`
  release, and orchestrate any other stale component in the config bus by invoking the
  command its owner declared. Reads the stamped versions from the bus
  (`.agent/PROJECT.md`, or the legacy `domains/PROJECT.md`), applies each pending
  migration from the registry, and re-stamps only what it migrated. Use whenever the user
  says "work migrate", "apply migrations", "upgrade the domain system", "move the config
  bus", "my domain system is behind", or acts on the stale-scaffolding warning `work on`
  prints. Also brings the workflow overlay current by running `update-workflow`'s refresh mode
  when its schema stamp is behind, so one run covers both of `delivery`'s components.
user-invokable: true
argument-hint: ""
---

# work:migrate

Bring a project's domain-system scaffolding up to the skill's current version by applying
the pending migrations. Additive and idempotent — safe to re-run.

This skill's procedure lives in the shared directory next to this skill. Read
**`../_shared/migrate.md`** (path relative to this SKILL.md's own directory) and follow
it. The migrations it applies live one-file-per-version in **`../_shared/migrations/`**
(read only the pending `v{N}.md` files — see `../_shared/migrations/README.md`).

$ARGUMENTS
