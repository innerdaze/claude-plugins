# Environments — typical topics

Seeding hints for `domains init`: what an environment's knowledge usually divides into. They are
a **starting point, not an answer** — the topics that matter are this codebase's actual
subsystems, which only reading the repo reveals.

Detection of the environment itself is not here. That is the config bus's business, and whoever
writes the bus has already done it: read the `Environment` row rather than re-deriving it.

## Typical domain topics by environment

Use these to seed `INDEX.md`, then **replace them with the project's real
subsystems** discovered during the prep scan. The goal is topics that map to how
*this* codebase is actually divided, with trigger keywords that are real symbols,
directories, and file prefixes from the repo.

| Environment | Always-load topics | Common topic-triggered domains |
|---|---|---|
| React / frontend | code, components | routing, state management, data-fetching/api, styling/design-system, forms, testing, build/tooling |
| Node service | code, api | data/persistence, auth, jobs/queues, integrations, testing, deployment |
| Python | code | api/web, data/models, tasks, integrations, testing, packaging |
| Go / Rust | code | api, persistence, concurrency, cli, testing, build |
