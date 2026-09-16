# Migrations — domain-system scaffolding

One file per version: `v{N}.md` describes the change that bumped the canonical **Domain
system version** (declared in `templates.md`) to N, and exactly how to bring a project at
`v{N-1}` up to it. Splitting per version keeps context bounded — a reader loads only the
files it needs, never the whole history.

## Who reads what (keep it this way — it's the context budget)

- **`work on`** reads **nothing here**. Its stale-scaffolding warning is a pure integer
  compare: project stamp (`PROJECT.md` → `Domain system version`, missing ⇒ 1) vs the
  canonical + floor in `templates.md`. Never make `work on` open a migration file — that's
  the leak this layout exists to prevent.
- **`work migrate`** reads **only the pending files** — `v{stamp+1}.md` … `v{canonical}.md`
  — never the applied ones. Cost scales with the gap to close, not the total history.
- **Other owners' migrations are not here and never will be.** `work migrate` orchestrates them
  by invoking the command each owner declares in the bus's `## Commands`; it does not read, hold
  or vendor anybody else's migration files.

## Versions and the floor

`templates.md` declares two integers:

- **Domain system version** (canonical) — the newest version; the highest `vN.md` here (**v13**).
- **Minimum supported version** (floor) — the oldest version `work migrate` will migrate
  *from*. A project stamped below the floor is too far behind to chain safely: it re-scaffolds
  instead of migrating.

**These integers govern `work`'s own components only.** The bus's `## Versions` carries one row
per component with its owner, and **each owner sets its own floor** — so there is no single
number a project is behind on, and `work` never answers a floor question about a component it
does not own.

When the history gets long, raise the floor and delete the now-below-floor `vN.md` files
(git keeps them). That's the only pruning ritual, and it's optional — nothing breaks if
you never prune; the files just accumulate (and only `work migrate` ever pays for them).

## Authoring a migration (on every version bump)

1. Bump **Domain system version** in `templates.md` by one (N → N+1).
2. Make the scaffolding change in `templates.md` / `init.md`.
3. Add `v{N+1}.md` here (copy the skeleton below).
4. **Destructive steps are allowed, because a migration is a reviewed change** — its diff is
   read by a person before it lands. Three limits, and they are what make that true:
   - **Only what `work` owns.** User-authored content outside `work`'s own sections is never
     deleted or rewritten.
   - **Deletions stay legible.** Never bury one in reflowing, renaming or reordering — **one
     kind of change per migration**, or the review is skimming rather than reading.
   - **Anything ambiguous still asks.** Where the right answer depends on intent the file
     cannot know, the Apply step must **report and ask**, not act.
5. **Declare `Preconditions` when the migration depends on something outside itself** — the bus
   existing, another component having moved. An unmet precondition makes the migration
   **decline**, which is an ordinary outcome: the orchestrator re-runs it on a later pass once
   something else has applied. This is also *the only place* ordering is expressed — no
   orchestrator sequences migrations, because knowing the order would mean knowing about
   siblings.
6. **Keep it deterministic and once-per-repo.** Two developers migrating the same project must
   produce the same diff; the committed stamp is what makes the second run a no-op.
7. **A contradiction stops the step and offers the resolutions.** Where a migration cannot
   proceed without guessing — two config buses, two real paths for one artifact, a row that
   disagrees with the file it names — stopping is right and stopping *alone* is not. State the
   contradiction in full (both values, and where each came from), then offer the resolutions you
   could apply, each with exactly what it would do to the repo, and apply the one the user picks.

   A migration that only reports leaves someone holding a half-migrated repo and no route
   forward, which is how a migration becomes a thing people avoid running. The doctors are held
   to this already — every finding names one command, and *"a finding with no next action is a
   complaint"*. A migration that has stopped mid-chain owes at least as much.

   **This does not break determinism.** The same-diff rule governs choices a migration makes on
   its own; a contradiction is by definition not one of those — it is a decision only a person
   can take, and surfacing it is what keeps the diff honest rather than plausible. Record the
   decision and its reason in the report, so the reviewer reads a choice rather than an
   inexplicable edit.

   Where the conflicting thing is **outside the repo** — a memory store, personal notes — you
   cannot offer to fix it. Name the file, the line and the replacement, so the instruction is
   something the user can act on in one step rather than a warning to go looking.

**Skeleton (`v{N}.md`):**

```markdown
# v{N} — {short title}

**What changed:** {one line, author-facing}

**Preconditions:** {what must already be true, or "none". Unmet ⇒ decline and say which one —
the orchestrator will retry after something else applies. This is where ordering lives.}

**Apply (v{N-1} → v{N}):**
1. {imperative, idempotent step — name file + section + exact text}
2. {…}
```
