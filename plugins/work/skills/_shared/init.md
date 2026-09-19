# `work init` — bootstrap the domain system

You are setting up the domain system for the current project so that `work on` (and
any future agent) can pick up tickets with full context. Run this once per repo;
it's safe to re-run (Step 0 makes it idempotent).

Work through the four steps in order. The first three are the user's mandate:
**(1) determine the environment, (2) learn the VCS and ticket tracker, (3) create
the domain system + update CLAUDE.md + run the first project scan (`prep refresh`).**
Step 0 protects anything that's already there.

Throughout, obey the cardinal rule from SKILL.md: **never assume the environment.**
Establish facts by reading the repo, confirm with the user, and only then write —
using *this* project's real vocabulary.

---

## Step 0 — Look before you touch

Before anything, see what already exists so you extend rather than clobber:

1. Read the project root listing and note the obvious signal files.
2. Check for an existing setup: a config bus (`.agent/PROJECT.md`, or the legacy
   `domains/PROJECT.md`), a `domains/` directory,
   `domains/INDEX.md`, or a plugin/framework that ships general domains under its
   own resources directory with a `prep-init-guide.md` (or equivalent).
3. Check for an existing `CLAUDE.md`.

If a domain system already exists: **do not overwrite it.** Tell the user what you
found and ask whether to (a) refresh/extend it in place, or (b) leave it alone. If a
plugin ships general domain files, the project files you write *layer on top* of
them (two-layer loading) — record that in INDEX.md rather than duplicating their
content. If `CLAUDE.md` exists, you will *insert* a section, never replace the file.

Read these references now so you have the patterns and skeletons ready:
- `environments.md` — detection signals, topic ideas, verification/VCS/tracker tables.
- `templates.md` — the skeletons for PROJECT.md, INDEX.md, the CLAUDE.md section, and the prep guide.

---

## Step 1 — Determine the environment

Never assume it. Build evidence, then confirm.

1. From the root listing, match against the detection signals in
   `environments.md`. Gather *all* matches — a repo can be several things.
   If the root has a monorepo manifest (see Step 1.3), the manifest names the
   workspace directories — descend into those, not a guessed set.
2. Pin the precise label **and version**: read the manifest that proves it
   (`package.json` framework dep; `pyproject.toml` `python_requires`; `go.mod` `go`
   directive; `Cargo.toml` `edition`; etc.). Don't guess a version — read it.
3. If it's a monorepo or polyglot repo, **exhaustively enumerate every workspace
   member from the monorepo's root config** — don't sample, eyeball, or guess from
   directory names. Read whichever root manifest the monorepo type uses:
   `pnpm-workspace.yaml` `packages:`, `package.json` `workspaces`, `nx.json` /
   `workspace.json` `projects`, `turbo.json`, `lerna.json` `packages`, `Cargo.toml`
   `[workspace] members`, `go.work` `use(...)`. Expand any glob (`apps/*`,
   `packages/*`) so the final list contains concrete project paths. The enumerated
   list seeds the per-project deep-inspection lines later; missing one here means
   it's missing from every domain file downstream.
4. **Confirm with the user** via `AskUserQuestion`: present the environment you
   detected (with the evidence) as the recommended option, plus "something else".
   This is the one assumption you must never get wrong — everything downstream
   inherits the vocabulary you settle on here.

Record the confirmed environment label; it goes into PROJECT.md and shapes every
later choice (domain topics, verification commands, the language you write in).

---

## Step 2 — Learn the VCS and the ticket tracker

Both feed PROJECT.md and determine how `work on` will commit and talk to the tracker.

**2a — Version control.** Detect from `.git/` / `.diversion/` / `.hg/` / `.svn/`
(see the VCS table in `environments.md`). Note the commit workflow: does
the project have a `/commit` skill, a Diversion-only rule, a conventional-commits
convention? If detection is ambiguous, ask. Capture the VCS and the commit workflow.

**2b — Ticket tracker.** This is the one `work on` most depends on, so get it right:

1. Look at which MCP servers are loaded in this session (a `*linear*`, Jira, or
   Notion server is a strong signal) and at repo hints (`.github/` → GitHub Issues;
   `.gitlab-ci.yml` / a GitLab remote → GitLab Issues).
2. **Confirm with the user**, and capture three things precisely:
   - the tracker (Linear / Jira / GitHub / GitLab / Notion / none),
   - how to reach it (the MCP namespace like `mcp__linear-uft`, or a CLI like `gh` /
     `glab`),
   - the ticket-id prefix (e.g. `MACH`, `RD`), if the tracker uses one.
3. If a Linear/Jira/Notion MCP server *should* be there but isn't loaded, tell the
   user it must be connected (and Claude Code restarted) for `work on` to use it —
   but you can still finish init now.
4. If there's no tracker, that's fine: record `none`. `work on` will run in
   describe-the-task-inline mode.

Record only those three in the bus's `## Tracker` — `Kind`, `Access`, `Prefix` — and **omit a
row you have nothing for** (no `Access` when `Kind` is `none`; no `Prefix` when the tracker has
none). Never write `n/a`. **Do not write operations into the bus:** how `work on` fetches,
comments and sets status is in `tracker-ops.md`, by `Kind`.

---

## Step 3 — Write the bus, seed CLAUDE.md's Rules, scan for conflicts

Now write the apparatus. Order matters: write the config, manifest, meta guide, and
scan procedure first, wire up CLAUDE.md, then run the scan that fills in the
knowledge files.

**3a — Write the config bus at `.agent/PROJECT.md`.** One place, always — no alternative path,
no private copy. **On a bus that already exists, a `shared` row that is present but blank counts
as absent**: ask for that one value, write it, and change nothing else — not the rows around it,
not another role's sections. This is the only thing re-running init does to a live bus's shared
sections, and it is why a doctor may name this command for a blank row without sending someone
through a full re-scaffold. If a legacy `domains/PROJECT.md` is present, do **not** write a second bus:
stop and tell the user to run `work migrate`, which moves it. Fill the template from
`templates.md`
with the confirmed environment, VCS + commit workflow, tracker + access +
prefix, and the verification method (no repo path — it's machine-specific; `work on`
derives it at runtime) (pick the commands the repo actually supports —
check `package.json` scripts / Makefile / CI). **Look for a written Definition of Done** — a
file or heading so named, a feature-process or contributing doc that lists what every change
must satisfy — propose it, confirm, and write `## Verification → Definition of Done` as its path;
none found → ask once, and omit the row if the project has not written one down. Set the `## Artifacts` `Ticket flow` row to
`none` and write no `Ticket flow rules` row (a fresh project has no extracted rules yet).

**Add `.agent/local/` to the project's ignore file** while you are creating `.agent/` — one entry,
idempotent. It is where anything uncommitted goes: a plugin's runtime state, and the values for
settings a project's own overlay steps declare. Doing it now costs a line and removes the failure
where the first tool to need it forgets, and someone commits their local state — that registry row is the *only* place the overlay's path is recorded, so there is no
`Workflow overlay` row to write; don't create `.agent/work/workflow.md` here either — that's
`update-workflow`'s job once a project actually customizes the flow. Delete rows that
don't apply.

**Write the three shared sections too** — `## Artifacts`, `## Versions`, `## Commands` — from
`templates.md`. They are not optional decoration; they are how any other tool finds what exists
here, what is stale, and who to ask:

- **`## Artifacts`** — register only what **`work`** owns (the ticket-flow row). Add the
  knowledge row only while `work` still owns the knowledge system; once a separate tool owns it,
  that row is *its* to write. Never register an artifact you do not own — that would mean
  detecting its path, which is what the table exists to avoid.
- **`## Versions`** — stamp the `delivery` rows from the canonical integers in `templates.md`.
  This replaces the old single `Domain system version` row: one row per component, each with its
  owner, because each owner sets its own floor. If you are editing a project that still has the
  old single row, leave it alone — `work migrate` moves it.
- **`## Commands`** — declare `work`'s own migrate and re-scaffold commands. Do **not** invent
  rows for tools that are not installed: an absent row is the correct answer, and it is what
  makes "stale, and its command is not available here" a complete finding rather than a guess.

### `work init` does not create the knowledge system

**It used to, and it no longer does.** Project memory belongs to the knowledge tool, which owns
`domains/**` and registers itself in the bus. Two tools scaffolding one artifact is what disjoint
ownership forbids, and it is the reason installing this plugin no longer drags a knowledge system
in.

So:

- **If `domains/` already exists**, leave it entirely alone — do not reformat it, do not
  re-register it, do not touch `domains/INDEX.md`. Its rows in the bus are the knowledge role's
  to write.
- **If it does not exist**, say so **once** and carry on: *"no knowledge system here — install
  the knowledge tool and run its init if you want one; ticket delivery works without it."* Do not
  offer to create one, and do not name a specific package as a requirement — that would make one
  plugin depend on another.
- **Never write a `knowledge` row** into `## Artifacts`, `## Versions` or `## Commands`. An
  absent row is the correct state until its owner runs.

⚠️ **This is a real capability change for an upgrading repo**, not just a refactor: a project
that had knowledge loading yesterday gets none today until the knowledge tool is installed. Say
it plainly rather than letting it be discovered.

**3b — Update `CLAUDE.md`.** Add the **Rules** section from `templates.md`:
(1) the **Rules** section — project-agnostic working-agreement defaults. First scan
the whole file for any existing `## Rules` heading; if one exists, merge the missing
bullets into it (skip bullets already covered) rather than adding a second `## Rules`
heading. Only insert a fresh section (just after the project overview/title) if none
exists. (2) the **Domain Knowledge System** section, appended, documenting
`prep <domain>` and `prep refresh` and pointing at `domains/meta.md` for
adding/maintaining domains. If `CLAUDE.md` exists, insert and preserve everything
else; if not, create it with a one-line project overview, then these sections. Use
the environment's real vocabulary — no cross-ecosystem leakage.

**3c — Conflict scan.** Run the procedure in `doctor.md` against the
project's newly-written and pre-existing config layers. Present the structured
conflict report to the user: each finding with its location, quoted text,
severity, and suggested resolution. If there are no conflicts, say so in one
sentence.

This step is **report and suggest only** — do not edit any file based on the
findings, and do not queue fixes automatically. Tell the user: *"These are
suggestions only. Ask me to act on any finding if you want to resolve it now,
or come back to `work doctor` at any time."* The domain system is live regardless
of whether the user acts on the findings.

Because `work on` is the single adaptive orchestrator that reads PROJECT.md, writing
a correct PROJECT.md *is* "re-creating work:on for this setup" — there is nothing
further to generate.

---

## Show what you wrote, and have it confirmed

**Every init ends by presenting the configuration it produced.** Not a summary — the content, or a
faithful rendering of it. A summary is where a wrong assumption survives: *"configured your
tracker"* reads as correct whatever actually got written.

**Mark what you inferred, separately from what you were told.** The lines the user supplied need no
scrutiny. The inferred ones are the whole reason to ask, and separating them turns "does this look
right?" — whose honest answer is usually "I suppose so" — into a short list of specific claims
somebody can check.

Say two more things while you have their attention: **what this configuration switched off** (a
binding left `none`, anything the tool cannot do here) and **how to change each part** — the file
to edit, or the command to re-run. A confirmation nobody can act on is a notification.

Running non-interactively: print the same thing and say plainly that it was **not confirmed**.

**Then end with what to do** — the commands that make the setup useful, in order, at most four
(`prep <domain>`, `work on <TICKET>`, whatever is still unbound), or one line saying nothing is
pending. The configuration above is content the user must check, so it stays in full; everything
*around* it is only worth writing if it changes what they do next.
