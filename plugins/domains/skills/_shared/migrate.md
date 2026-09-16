# `domains migrate` — bring the knowledge system up to date

Applies the pending **knowledge scaffolding** migrations: the changes `domains init` would
produce today that this project, set up against an older release, never received.

**Coordinate before running.** A migration edits shared, committed files and re-stamps once. It
is run by **one** developer, as **its own reviewed change** — never folded into an unrelated
branch. Several people migrating in parallel produce conflicting edits and duplicate stamps.

## Procedure

1. **Locate the bus.** `.agent/PROJECT.md`, else the legacy `domains/PROJECT.md`. If neither
   exists, this project has no knowledge system to migrate — say so and stop.

2. **Read your own stamp.** The **`knowledge scaffolding`** row in `## Versions`. Missing ⇒ treat
   as the floor. **Read no other row as authority over your work** — a row owned by another role
   is theirs, including when it disagrees with yours.

3. **Read the canonical integers** from `templates.md`: `Knowledge scaffolding version` and
   `Minimum supported version`. These are this plugin's numbers; no other tool may raise them and
   this plugin raises nobody else's.

4. **Decide.** Up to date → say so and stop. Below the floor → tell the user to re-scaffold with
   `domains init` rather than migrate, and stop. Otherwise continue.

5. **Check preconditions, then apply the pending files in order** — `migrations/v{stamp+1}.md` …
   `v{canonical}.md`, and only those. A migration whose preconditions are unmet **declines**:
   record what it was waiting for and move on. Declining is an ordinary outcome, and an
   orchestrating `migrate` will retry after something else applies.

6. **Re-stamp only the `knowledge scaffolding` row**, and only after everything in range
   succeeded. If one failed or declined, stamp the highest fully applied version and say which
   remain.

7. **Report** what applied, what declined and why, and what is left — one line each, headline
   first (`knowledge 1 → 2`). A migration that changed behaviour rather than a path says so,
   marked as a change. **End with what to do**: the commands to run, in order, copy-pasteable — at most four — or one line saying nothing is pending. If it does not change what the reader does next, it does not belong in the report; the detail is already in the transcript above.

## Boundaries

- **Your rows and your folder.** `domains/**`, plus the `knowledge` rows in the bus. Never touch
  another role's sections, another tool's artifacts, or the user's own prose.
- **Destructive steps are permitted, because the diff is reviewed** — within `domains/`. Keep
  deletions legible: one kind of change per migration, never buried in reflowing or renaming.
- **Never rewrite a topic file's content to fit a new shape without asking.** The scaffolding is
  ours; the knowledge inside it is the project's, written by people about their own codebase.
- **Deterministic, once per repo.** Two developers must produce the same diff; the committed
  stamp makes the second run a no-op.
