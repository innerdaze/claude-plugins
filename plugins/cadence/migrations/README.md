# Migrations — cadence's own components

One file per version: `v{N}.md` brings a project at `v{N-1}` up to N. Cadence had none before
0.5.0, because nothing it owned had ever moved. The config split and the root move are its first.

**These are cadence's migrations and nobody else's.** Every tool in the stack keeps its own
registry; an orchestrating `migrate` invokes the command each owner declares in the bus's
`## Commands`, which is the only coupling there is. Nothing here reads, holds or vendors another
tool's migration files.

## The stamp

Cadence stamps **`cadence methodology`** in the bus's `## Versions`, owned by role
`methodology`, and reads it back to decide what is pending. It also keeps `cadence_version` in
its own config — the *contract* version a flow was authored against, which is a different number
answering a different question:

| Number | Answers |
|---|---|
| `cadence methodology` (bus) | has this project's cadence **scaffolding** been migrated? |
| `cadence_version` (its config) | which **hook/flow contract** was this flow written against? |

Conflating them would be easy and wrong: a flow authored against an older contract is a
compatibility question for the flow author, while a stale scaffolding stamp is a migration for
whoever runs one.

## Authoring one

1. Bump **Methodology scaffolding version** in `MIGRATIONS-VERSION.md`.
2. Make the change in the payload.
3. Add `v{N}.md` from the skeleton.
4. **Declare `Preconditions`** for anything outside cadence's control — the bus existing, another
   component having moved. Unmet ⇒ decline and name what you are waiting for. This is the only
   place ordering lives; no orchestrator sequences migrations, because knowing the order would
   mean knowing about siblings.
5. Keep it deterministic and safe to re-run: two developers must produce the same diff.

**Skeleton:**

```markdown
# v{N} — {short title}

**What changed:** {one line}

**Preconditions:** {or "none"}

**Apply (v{N-1} → v{N}):**
1. {imperative, idempotent step}
```
