# Migrations — knowledge scaffolding

One file per version: `v{N}.md` describes the change that bumped **Knowledge scaffolding
version** (declared in `templates.md`) to N, and exactly how to bring a project at `v{N-1}` up to
it. Per-version files keep context bounded — a reader loads only what it needs.

**These are this plugin's migrations and nobody else's.** `work` has its own registry for its own
components. Neither reads, holds or vendors the other's files: an orchestrating `migrate`
invokes the command each owner declares in the bus's `## Commands`, which is the only coupling
there is.

## Authoring one

1. Bump **Knowledge scaffolding version** in `templates.md` by one.
2. Make the scaffolding change in `templates.md` / `init.md`.
3. Add `v{N+1}.md` from the skeleton below.
4. **Declare `Preconditions`** when the change depends on something outside this plugin — the bus
   existing, another component having moved. Unmet ⇒ decline and name what you are waiting for.
   This is the only place ordering is expressed; no orchestrator sequences migrations, because
   knowing the order would mean knowing about siblings.
5. Keep it **deterministic** and safe to re-run.

**Skeleton:**

```markdown
# v{N} — {short title}

**What changed:** {one line, author-facing}

**Preconditions:** {what must already be true, or "none".}

**Apply (v{N-1} → v{N}):**
1. {imperative, idempotent step — name file + section + exact text}
```

## The floor

`templates.md` declares the canonical version and the **Minimum supported version** — the oldest
this plugin will migrate *from*. Below it, a project re-scaffolds with `domains init` instead.
Raising the floor lets you delete the below-floor files; git keeps them.
