# `work migrate` — apply pending migrations, whoever owns them

Brings a project's scaffolding up to date. Two jobs, and the second is new:

1. **Apply `work`'s own pending migrations** — the ones `work init` would produce today that
   this project never received.
2. **Act as the orchestrator** for every other stale component in the config bus, by invoking
   the command its owner declared. `work` never learns another tool's name: it reads
   `## Versions` for what is stale and `## Commands` for who to call, and the *repo* is the
   join.

Any tool's `migrate` can play the orchestrator; this one does it when it is what the user ran. It runs the migrations `work init` would produce today
but that this project — set up against an older release — never received. It does **not**
re-interview, re-scan, or regenerate domain knowledge (that's `prep refresh`); it applies
targeted, additive upgrades from the registry.

**Coordinate before running.** A migration edits shared, committed repo files
(`CLAUDE.md`, the config bus, and any other scaffolding) and re-stamps the version
once. It should be run by **one** developer, on a **dedicated branch/PR, merged on its
own** — not folded into an unrelated feature branch. If several people migrate the same
project in parallel they produce conflicting edits and duplicate re-stamps. Before
starting, confirm with the user that this is the coordinated migration (and, ideally, that
the working tree is clean so the migration lands as its own reviewable change).

## Procedure — `work`'s own components

1. **Locate the project.** Derive the repo path the same way `work on` does:
   `git rev-parse --show-toplevel`, else the session working directory. Confirm
   the config bus exists — `.agent/PROJECT.md`, else the legacy `domains/PROJECT.md`. If
   neither exists the project isn't set up; tell the user to run
   `work init` and stop.

2. **Read the stamped versions.** Prefer the **`## Versions`** section: take the rows owned by
   `delivery` — `ticket-flow overlay` and `delivery scaffolding`. If that section does not exist
   yet, fall back to the legacy single `Domain system version` row. Either missing ⇒ treat as
   **1**. Call the scaffolding one `stamp`.

   Read the rows, not a global number: **there is no one version a project is behind on.** Each
   owner stamps and floors its own components, so a project can be current on the overlay and
   behind on scaffolding, or the reverse.

3. **Read the two canonical integers** from `templates.md` (same directory as this file):
   the **Domain system version** (`canonical`) and the **Minimum supported version**
   (`floor`).

4. **Decide:**
   - `stamp >= canonical` → report "domain system is up to date (v{stamp})" and stop. No
     changes.
   - `stamp < floor` → too far behind to chain safely. Tell the user to **re-scaffold instead
     of migrating**, naming the command from `## Commands` for *this* role (`delivery` →
     re-scaffold) rather than a generic "run init". A component owned by someone else that is
     below *their* floor is **their** answer to give: report it and let their command speak.
     Stop without changing anything.
   - otherwise (`floor <= stamp < canonical`) → continue.

5. **Read only the pending migration files.** Read `${CLAUDE_PLUGIN_ROOT}/migrations/v{stamp+1}.md` …
   `${CLAUDE_PLUGIN_ROOT}/migrations/v{canonical}.md` — **only those**, never the whole `migrations/` history.
   Show the user the list (versions + titles) before applying.

6. **Check preconditions, then apply in ascending order.** A migration may declare
   **Preconditions**; if they are unmet it **declines** — record what it was waiting for and
   carry on to the next. Declining is an ordinary outcome, not an error, and a later pass may
   find it ready (step 10).

   For the rest, follow each file's **Apply** steps exactly. They are idempotent — "insert if
   absent, skip if present" — so re-running is safe; still, report per migration what you
   changed vs. skipped. Where a step says to *ask first*, honour it: pause, surface it, act only
   on an explicit go-ahead.

7. **Re-stamp.** Write the new versions into the `delivery` rows of **`## Versions`** (creating
   the section if a migration has just introduced it, else updating the legacy row in place).
   Stamp **only the components you actually migrated** — never another owner's row, even to
   correct it. This is the last step — only stamp after every migration
   in the range succeeded. If one failed or was declined, stamp to the highest fully
   applied version instead and tell the user which migrations remain.

8. **Report — short, and ending in what to do.** One line of headline (`delivery 2 → 12`), then
   only what changes what the reader does next: any migration that **declined** and what it is
   waiting for, any that **changed behaviour rather than location**, and the files that moved.
   Migrations that applied cleanly are the headline's business, not a table of their own — ten
   applied migrations is one line, not ten.

   End with the commands to run next, in order, or one line saying nothing is pending. A reader
   who has to work the next step out of a list of findings has been handed homework.

   The per-migration detail from step 6 stays in the transcript above, where anyone who wants it
   can read it.

## Procedure — orchestrating the rest

Run this **after** step 8: `work`'s own migrations are the ones most likely to create the bus
another migration needs.

9. **Read `## Artifacts`, `## Versions` and `## Commands`** from the config bus.

   **Start with the roles that are present but unversioned.** A role that owns a row in
   `## Artifacts` and has **no** row in `## Versions` is registered on disk and unregistered as a
   component — the state every project reaches when its artifact predates the plugin that owns it.
   It is invisible if you read `## Versions` alone, so read the artifact table first and handle
   each such role explicitly: name the role, the artifact it owns, and that **the plugin owning
   that role registers itself by running its own init**. Do not name a command for it — you do
   not know one, and `## Commands` has no row to read.

   Then **ask the user to run it, and continue afterwards.** Reporting alone leaves the project
   half-migrated at the exact moment someone is paying attention to it: the delivery scaffolding
   is current, that role's is not, and the person now has to notice a line in a report and start
   a second procedure of their own accord. Ask instead — *"role `knowledge` owns `domains/` and
   is not registered as a component; if you have its plugin, run its init and I'll pick up from
   there"* — and when they do, **re-run the orchestration pass** (step 10). The role will have
   rows by then, so it orchestrates like any other.

   Asking is not the same as guessing. The user supplies the command, or runs it themselves; you
   never invent the name, and you never assume which plugin owns the role. If there is nobody to
   answer — an unattended run — report it as above and stop, which is the honest outcome rather
   than a stall.

   Then, for every `## Versions` row whose owner is
   not `delivery`, you cannot know its canonical version — only its owner can. So:

   - **Look up the role in `## Commands`.** No row, or a command not available in this session
     → **report it and move on.** "`knowledge` is stamped v2 and its migrate command is not
     available here" is a complete, actionable answer. Never guess a command name, never
     substitute one that looks similar, and never edit another owner's components yourself.
   - **Invoke the declared command.** It decides whether anything is pending; "already up to
     date" is a normal answer.

10. **Loop while progress is being made.** A migration may **decline** because its preconditions
    are unmet — the bus does not exist yet, another component has not moved. That is an ordinary
    answer, not a failure. So:

    - Run a pass over every pending component.
    - If anything applied, run another pass — something that declined may now proceed.
    - **Stop when a whole pass applies nothing**, and report each remaining component with
      *what it said it was waiting for*.

    **No fixed iteration cap.** Stop on lack of progress, not on a count.

    ⚠️ **Do not sequence them yourself.** You do not know the right order and must not infer
    one: ordering knowledge lives in each migration's preconditions, which is the only place
    that has it. A `work migrate` hardcoding "bus before extraction" would be encoding a
    sibling's business.

11. **Report the whole picture**, not just your own half: what `work` applied, what each other
    owner reported, what remains and why, and — if a role is stale with no available command —
    the one thing the user has to install or run.

    **Every remaining item names an action, or says plainly that none exists.** A component that
    declined and never became ready, a contradiction you stopped on, a reference nothing could
    repoint: each one gets the next step beside it. Where the thing that needs changing is
    outside this repo — a memory store, someone's notes — name the file, the line and the
    replacement rather than telling them to go looking. A migration report that ends in a list
    of problems with no routes is the state that makes people stop running migrations.

## Boundaries

- **Your own components, plus the structural move.** You apply `work`'s migrations and
  orchestrate others; you never edit another owner's *content*. One exception: a migration that
  moves whole sections into the bus may relocate sections whose owner is not installed, because
  the alternative leaves a repo half-migrated for as long as one tool is missing. That covers
  **moving** a section, never editing what is inside it.
- **Scaffolding only.** This touches the init artifacts (`PROJECT.md`, `INDEX.md`,
  `meta.md`, `prep-refresh-guide.md`) and the CLAUDE.md sections. It does **not** upgrade
  the workflow overlay — that has its own version and its own upgrade path
  (`work update-workflow refresh`). If the overlay is also stale, mention it, but don't
  migrate it here.

  Two things a migration may still do to the overlay *file*, because the alternative is a repo
  that no longer works: **move it**, and **repoint references to paths the same migration
  moved** (v4 does both). Neither reads or rewrites what the steps say — after a repoint, every
  line that is not one of those paths is byte-identical. Anything beyond that is the overlay's
  own upgrade path, not this one's.
- **Destructive steps are permitted, because the diff is reviewed** — a migration may delete
  and restructure what `work` owns. Three limits: never touch user-authored content outside
  `work`'s own sections; keep deletions **legible** (never bury one in reflowing or renaming —
  one kind of change per migration, or review becomes skimming); and stop at anything the
  migration marks *ask first*.
- **Deterministic, and once per repo.** Two developers migrating the same project must produce
  the **same** diff, or review is worthless and whoever merges second gets a conflict in a file
  they did not choose to touch. The committed stamp is what makes a second run a no-op rather
  than a competing change — read it before applying, write it after.
