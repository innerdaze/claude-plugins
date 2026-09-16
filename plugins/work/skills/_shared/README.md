# `work` — a portable domain-system + ticket-workflow skill

`work` is a Claude Code skill that brings a lightweight **"domain system"** to any
codebase and then **works tickets** against it. It's deliberately project-agnostic:
it figures out what your project *is*, how it's version-controlled, and how its
tickets are tracked — then sets itself up to match, instead of assuming.

It has two subcommands:

| Command | What it does |
|---|---|
| `/work init` | One-time setup: detect the environment, learn the VCS + ticket tracker, and create the domain system (knowledge files + config + the `prep` commands) tailored to this project. |
| `/work on <TICKET>` | Pick up a tracked ticket and deliver it end-to-end — analyse → plan (you approve) → implement → verify → commit → comment → follow-ups. |
| `/work update-workflow` | Fold an existing workflow skill or custom steps into `/work on`'s three phases — without ever losing them. Maps each step to a phase + model + effort level, shows you the merged flow for sign-off, then records a lean `.agent/work/workflow.md` overlay. |
| `/work doctor` | Read-only diagnostic: scan the project's config layers (memories, CLAUDE.md, rules, settings, domain files) for instructions that contradict or would block a workflow step. Reports conflicts with severity and suggests resolutions — never edits anything. |

---

## Why it exists

Two recurring problems on any codebase:

1. **Agents start cold.** Every new session re-learns the same things — where the code
   lives, the conventions, the gotchas, how to test. `work` captures that as plain
   files in the repo so the knowledge is reused, not rediscovered.
2. **Workflows are project-specific but mostly the same shape.** "Pick up a ticket and
   ship it" looks similar everywhere, but the details (git vs Diversion, Jira vs Linear,
   `yarn test` vs a game-engine compile) differ. `work` keeps the *shape* and reads the
   *details* from a per-project config.

The result: the operational knowledge and the working process travel **with the repo**,
and the same skill works in every project you drop it into.

---

## The domain system

`/work init` creates a `domains/` folder and wires a section into your `CLAUDE.md`.
Here's what lands in the project:

```
<project root>/
├── domains/
│   ├── PROJECT.md          # config: environment, VCS, ticket tracker, how "done" is proven
│   ├── INDEX.md            # manifest: topic → domain file, with trigger keywords
│   ├── meta.md             # the system's own guide: how loading works, how to ADD & MAINTAIN domains
│   ├── prep-refresh-guide.md # the re-runnable scan procedure that (re)generates the topic files
│   ├── code.md             # per-topic operational knowledge…
│   ├── <topic>.md          # …one file per major subsystem (names depend on YOUR project)
│   └── …
└── CLAUDE.md               # gains a "Domain Knowledge System" section documenting the prep commands
```

- **`PROJECT.md`** is the single source of truth. `/work on` reads it on every run and
  adapts its behaviour (which VCS commands to use, how to fetch/comment on a ticket,
  how to verify a change) to whatever it finds there.
- **`INDEX.md`** maps topics to domain files using real trigger keywords from your repo
  (directory names, symbols, file prefixes), so the right knowledge loads for the right
  ticket without loading everything.
- **`meta.md`** documents the system itself — most importantly, **how to add a new
  domain and how to keep existing ones current** — so a future agent or teammate can
  extend it without ever reading the skill.
- **`<topic>.md`** files are the actual operational knowledge: what a subsystem is,
  where it lives, the proven patterns, and the gotchas.

### The `prep` commands

`/work init` documents two commands into your `CLAUDE.md`:

- **`prep <domain>`** — load the matching domain file(s) before starting a task
  (e.g. `prep code`, `prep graphql + forms`). Load proactively as work reveals topics.
- **`prep refresh`** — (re)scan the project and (re)write the topic domain files. Run
  once at setup (done for you by `work init`), then re-run after major changes (new
  subsystem, big refactor, framework upgrade). `prep one time init` is a legacy alias.

---

## Key features

- **Never assumes the environment.** Step 1 of `init` detects what the project is and
  *confirms with you* before writing anything. It uses your project's real vocabulary —
  no terms from one ecosystem leaking into another.
- **VCS- and tracker-agnostic.** Works with git, Diversion, Mercurial, SVN — and Linear,
  Jira, GitHub Issues, GitLab Issues, Notion, or no tracker at all. The specifics are
  captured once in `PROJECT.md`; the workflow reads them.
- **One adaptive workflow, not a copy per project.** There's a single `/work on`
  procedure. It adapts via `PROJECT.md` rather than being regenerated, so there's one
  thing to maintain.
- **Looks before it touches.** If a domain system (or a `CLAUDE.md`, or a `.claude/rules/`
  setup) already exists, `init` *extends* it rather than overwriting — it inserts into
  `CLAUDE.md`, layers on plugin-provided domains, and asks before clobbering anything.
- **Self-documenting & maintainable.** The `meta.md` it writes explains how to grow the
  system, and `/work on`'s wrap-up automatically promotes recurring gotchas into the
  right domain file.
- **Subagent orchestration with right-sized models.** `/work on` keeps the main session
  lean and delegates each phase to a subagent on the cheapest model that can do the job
  (Haiku for transforms, Sonnet for synthesis, Opus for architectural judgement).

---

## How `/work init` works

Run it once per repo (it's safe to re-run — it detects and preserves existing setup).

1. **Look before you touch.** Scan the root, note signal files, and check for an existing
   `domains/`, `CLAUDE.md`, or plugin-provided domains. Anything found is extended, not
   overwritten.
2. **Determine the environment.** Match detection signals (`package.json`,
   `pyproject.toml`, `go.mod`, `Cargo.toml`, …), pin the precise label *and version*, and **confirm
   with you**. Everything downstream inherits this.
3. **Learn the VCS and the ticket tracker.** Detect git/Diversion/etc. and the commit
   workflow; detect the tracker (from loaded MCP servers + repo hints) and capture how
   to reach it (MCP namespace or CLI) plus the ticket-id prefix. Confirms with you.
4. **Create the system + run the scan.** Write `PROJECT.md`, `INDEX.md`, `meta.md`, and a
   project-tailored `prep-refresh-guide.md`; insert the "Domain Knowledge System" section
   into `CLAUDE.md`; then run the first project scan (`prep refresh`) over the project (reading files +
   safe, read-only commands) and write the per-topic domain files. Finally it reconciles
   the manifest with what the scan found and reports everything it created.

---

## How `/work on <TICKET>` works

Its **first action** is to read the config bus (`.agent/PROJECT.md`) — if that's missing or incomplete,
it tells you to run `/work init` first rather than guessing.

- **Phase 1 — Context & Planning (read-only).** Enters plan mode. Picks relevant domains
  from `INDEX.md`, then in parallel a Domain Loader summarises them and a Ticket Analyst
  studies the ticket + comments + the code it touches. A Planner drafts an implementation
  plan, which is presented to you for approval. **No changes happen until you approve.**
- **Phase 2 — Execute.** After approval, it tracks each plan step as a task and an
  Implementer makes the changes, running your project's verification (from `PROJECT.md`)
  as it goes.
- **Phase 3 — Wrap up.** Captures learnings (promoting broadly-useful ones into the
  domain docs and your memory), commits using your project's VCS workflow, posts a
  summary comment on the ticket, and — with your sign-off — files any follow-up tickets
  and updates the ticket's status.

A bare ticket id (`MACH-42`, `RD-4981`, or just `42`) is treated as `work on <that id>`.

---

## How `/work update-workflow` works

The three phases above are the invariant spine — `/work on` always runs them, always
keeps domain integration inside them. `update-workflow` lets a project *customize how*
they run without losing any of that.

Trigger it explicitly (`/work update-workflow`) or just ask — "use the resolve-bug skill
when working tickets", "add a reproduce-the-bug step", "modify phase 2 to write the test
first". It then:

1. **Investigates** the workflow skill you named (reads its `SKILL.md` + step files) or
   takes the step you described.
2. **Maps** each step onto the spine — which phase, where it slots relative to the core
   steps, and which model + effort (same transform→haiku / synthesis→sonnet / judgment→opus
   model rule, plus a low/medium/high effort dial, that `/work on` uses everywhere).
   Overlapping steps are *merged*, not duplicated.
3. **Shows you the full merged flow** phase by phase — core steps + injected steps, each
   tagged with its model + effort — and asks you to approve, reorder, or drop injections.
4. **Records a lean overlay** at `.agent/work/workflow.md` that *references* the source skill
   rather than copying its steps, so the skill stays the single source of truth. `/work
   on` reads this overlay and weaves the steps in on every run. The overlay carries an
   **`Overlay schema version`** stamp; when the skill's overlay format moves ahead of a
   project's stamped overlay, `/work on` prints a one-line warning telling you to run
   `/work update-workflow refresh` (it never blocks — the core flow stays current
   regardless). **Refresh** is a migration, not a re-interview: it re-expresses your
   existing steps/scenarios in the new schema (back-filling new fields like effort levels
   and parallel-group marks) and re-stamps the version, leaving your workflow choices intact.

The phases and the domain-integration steps are never removed — overlays only add around
them.

> **Note on skill upgrades.** The procedure itself (`on.md`, `update-workflow.md`) is
> installed by symlink, so changes take effect on the next run with no per-project step.
> The generated files a project holds *are* snapshots, tracked by two independent version
> stamps in `templates.md`:
> - **Overlay schema version** → the `.agent/work/workflow.md` overlay. When it moves ahead of
>   a project's stamp, `/work on` tells you to run `/work update-workflow refresh`.
> - **Domain system version** → the init scaffolding (`PROJECT.md`, `INDEX.md`, `meta.md`,
>   `prep-refresh-guide.md`, and the CLAUDE.md sections). When it moves ahead of a
>   project's stamp (in `PROJECT.md`), `/work on` tells you to run `/work migrate`, which
>   applies the pending `${CLAUDE_PLUGIN_ROOT}/migrations/v{N}.md` files additively and re-stamps.
>
> Both warnings are one-line and non-blocking; the core flow stays current regardless.
> Neither propagates automatically — the stamp is what surfaces the pending upgrade the
> next time you run `/work on` in that project.

---

## Using it

```text
# First time in a repo
/work init

# Load knowledge before a task (optional — work on does this for you)
prep code
prep graphql + forms

# Pick up a ticket
/work on RD-4981
/work on 4981          # bare number → normalised with the project's prefix

# Refresh the knowledge files after big changes
prep refresh
```

### Requirements & limits

- **Subagents** — `/work on` orchestrates subagents; it's designed for an environment
  that supports them.
- **A ticket tracker is optional.** If `PROJECT.md` records `none`, `/work on` runs in
  "describe the task inline" mode (you paste the task; it skips fetch/comment/status).
- **MCP-based trackers must be connected.** For Linear/Jira/Notion, the relevant MCP
  server has to be loaded in the session for automatic fetch/comment/status; otherwise
  `/work on` falls back to asking you to paste ticket details.

---

## Extending it

To add a new domain to a project: create `domains/<name>.md` in the house structure
(what it is + where it lives → patterns & conventions → gotchas → pointers), register it
in `domains/INDEX.md` with real trigger keywords, and keep it within the token budget.
The full conventions live in the project's `domains/meta.md` — that file is the contract
for keeping the system healthy over time.

---

## What's inside the skill

```
work/
├── SKILL.md                    # router + the shared mental model
├── README.md                   # this file (for humans)
└── 
    ├── init.md                 # the /work init procedure
    ├── on.md                   # the /work on orchestration procedure
    ├── update-workflow.md      # the /work update-workflow procedure (fold skills/steps into the phases)
    ├── doctor.md               # the /work:doctor procedure (detect instruction conflicts)
    ├── environments.md         # detection signals + per-ecosystem conventions
    └── templates.md            # the file skeletons init fills in (PROJECT/INDEX/meta/CLAUDE/prep-guide/workflow)
```

## Installing

`work` is distributed as a `.skill` file (a zip). There's no native installer — extract
it into a skills directory:

```bash
# Personal (all your projects)
unzip work.skill -d ~/.claude/skills/
```
```powershell
# Windows
tar -xf work.skill -C "$env:USERPROFILE\.claude\skills\"
```

To share with a team, commit the `work/` folder into a repo's `.claude/skills/` — it's
then available to everyone on clone, no install needed. Claude Code picks up skills live
(restart only if `.claude/skills/` didn't exist when the session started).
