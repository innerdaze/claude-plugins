---
name: migrate
description: >-
  Apply pending knowledge-scaffolding migrations to a repo whose `domains/` system was set up
  against an older release. Reads the `knowledge scaffolding` row from the config bus's
  `## Versions`, applies only what is pending, and re-stamps that row alone. Use whenever the
  user says "domains migrate", "upgrade the knowledge system", "my domains are behind", or when
  another tool's migrate reports that the `knowledge` role is stale. Migrates the scaffolding,
  never the knowledge inside it.
user-invokable: true
---

Read `../_shared/migrate.md` and follow it, plus only the pending
`../_shared/migrations/v{N}.md` files it names.
