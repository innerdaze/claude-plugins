---
name: migrate
description: >-
  Apply pending intent-scaffolding migrations to a repo whose `intent/` layer was set up against
  an older release. Reads the `intent scaffolding` row from the config bus's `## Versions`,
  applies only what is pending, and re-stamps that row alone. Use whenever the user says
  "intent migrate", "upgrade the intent layer", "my intent layer is behind", or when another
  tool's migrate reports that the `intent-layer` role is stale. Migrates the scaffolding — keys,
  headers, tables — and never a statement of intent.
user-invokable: true
---

# `/intent:migrate` — bring the intent layer's scaffolding up to date

**Intent scaffolding version: 2** · **Minimum supported version: 1**

These two integers are this plugin's and nobody else's. `init` stamps the first onto a new layer,
`capture` confirms it, `doctor` compares against it, and this skill raises a project to it. No
other tool may move them, and this plugin moves nobody else's.

**Coordinate before running.** A migration edits a committed doc set that people cite, and
re-stamps once. It is run by **one** developer, as **its own reviewed change** — never folded
into an unrelated branch.

## Procedure

1. **Locate the bus** at `.agent/PROJECT.md`. Absent → this project has no registered intent
   layer; say so, name `/intent:init`, and stop.

2. **Read your own stamp** — the `intent scaffolding` row in `## Versions`. Missing while an
   `intent-layer` artifact row exists → the layer predates registration: say so, name
   `/intent:init` (which stamps the floor), and stop. **Read no other row as authority over your
   work.**

3. **Decide.** At canonical → say so and stop. Below the floor → there is nothing below 1; this
   cannot happen yet, and if it does the stamp is wrong: report it. Otherwise continue.

4. **Check preconditions, then apply the pending files in order** — `${CLAUDE_PLUGIN_ROOT}/skills/migrate/migrations/v{stamp+1}.md` …
   `v{canonical}.md`, and only those. A migration whose preconditions are unmet **declines**:
   record what it was waiting for and move on. Declining is an ordinary outcome.

5. **Re-stamp only the `intent scaffolding` row**, and only after everything in range applied. If
   one declined, stamp the highest fully applied version and say which remain. **In the same
   write, repoint your own `## Commands` cell** if it still reads `n/a — no migrations yet`: the
   `intent-layer` row's Migrate cell becomes `/intent:migrate`. It is this role's row, its truth is
   what this payload ships, and leaving it stale would have the doctor report drift on the very
   project you just migrated.

6. **Report** — headline first (`intent 1 → 2`), then one line per thing applied or declined,
   and **end with what to do**: at most four commands, in order, or one line saying nothing is
   pending.

## Boundaries

- **Scaffolding only, never claims.** A migration may change a key, a header, a table's shape, a
  path the layer's own files use. It may not add, remove, reword or soften a statement of intent,
  a register row's content, a marker, or a `TODO — needs input`. The layer is dictated by a
  person; this skill reshapes the container it sits in.
- **Your rows and your folder.** The folder named by the `intent-layer` artifact row — never a
  guessed path — plus the `intent-layer` rows in the bus. Nothing else.
- **Deterministic, once per repo.** Two developers must produce the same diff, and the committed
  stamp makes the second run a no-op. Anything that needs a judgement is reported as a follow-up
  for `/intent:capture`, which runs with the maintainer present.

## Migrations

- `${CLAUDE_PLUGIN_ROOT}/skills/migrate/migrations/v1.md` — the floor: the layer as `init` first scaffolded it.
- `${CLAUDE_PLUGIN_ROOT}/skills/migrate/migrations/v2.md` — register rows keyed by content, never by ordinal.
