# Templates — the knowledge system

Skeletons `domains init` fills in. Read with [`environments.md`](environments.md) for topic
seeding hints.

## Knowledge scaffolding version

**Knowledge scaffolding version: 2**
**Minimum supported version: 1**

This is the canonical version of the knowledge system's scaffolding — `INDEX.md`, `meta.md`,
the scan guide, and the domain-file shape. `domains init` stamps it into the config bus's
`## Versions` table as the **`knowledge scaffolding`** row, owned by role `knowledge`;
`domains migrate` reads it back and applies what is pending.

**It is this plugin's number and nobody else's.** `work` has its own for its own components,
and neither may raise the other's — that independence is the whole reason the stamp is per
component rather than one shared integer.

(History: v1 = the scaffolding as extracted from `work` 0.1.x, unchanged in shape so an
existing project is already at v1 rather than needing a conversion.)

---

## `domains/INDEX.md`

```markdown
# Domain Index — {ProjectName}

Manifest used by `work on` to map ticket topics to domain files. Each row lists a
domain, what it covers, and trigger keywords/symbols that should pull it in. See
`meta.md` for how loading works and how to add/maintain domains.
{If a plugin or framework also ships general domain files, note the two-layer
arrangement here and give both the plugin path and the project path.}

## Always-load

Loaded for every ticket regardless of topic:

| Domain | Path | Covers |
|---|---|---|
| {code} | `domains/{code}.md` | {1-line scope} |
| {…} | `domains/{…}.md` | {1-line scope} |

## Topic-triggered

Pull in when ticket text matches any trigger (case-insensitive against title,
description, comments, and any file paths/symbols surfaced during analysis):

| Domain | Scope | Path | Trigger keywords / symbols |
|---|---|---|---|
| {routing} | {what it covers} | `domains/{routing}.md` | {real keywords, dir names, symbol/file prefixes from THIS repo} |
| {…} | … | … | … |

## Loading rules

1. Always include the always-load domains.
2. Include a topic-triggered row if any of its triggers appears in the combined
   ticket text or in file paths the work will touch.
3. Don't load a domain "just in case" — extra files cost context. Three to five
   domains is typical; eight+ signals the ticket is too broad and should be split.
4. Pass the final list to the Domain Loader as explicit file paths.
```

---

## `domains/meta.md`

The domain-system guide *for this project* — how loading works, how to add and
maintain domains, and the hard rules. Tailor the vocabulary and the hard rules to the
detected environment. This is scaffolding `work init` writes (not scan output), so a
future agent or human can extend the system without re-reading the skill.

```markdown
# Meta — Domain System Guide ({ProjectName})

This project carries its operational knowledge in `domains/`. This file explains how
that system works here and how to keep it healthy.

## The pieces

- `PROJECT.md` — project config (environment, version control, ticket tracker, how
  "done" is proven). The single source of truth `work on` reads every run.
- `INDEX.md` — the manifest mapping topics → domain files, with trigger keywords.
- `prep-refresh-guide.md` — the re-runnable scan that (re)writes the topic files.
- `<topic>.md` — per-topic operational knowledge (the files listed in INDEX.md).
- `meta.md` — this guide.

## Loading domains (`prep`)

- `prep <domain>` → read `domains/<domain>.md` before starting work on that topic.
  {If two-layer: read the general/plugin file first, then the project file.}
- `prep X + Y` → load several at once.
- Load proactively as work reveals new topics; don't wait to be asked.

## Adding a new domain

1. Create `domains/<name>.md`. Use the house structure: **what it is + where it lives**
   (real paths/symbols) → **proven patterns & naming conventions** → **gotchas** →
   **pointers** to deeper docs rather than duplicating them.
2. Register it in `INDEX.md`: pick always-load (rare — only if every ticket needs it)
   or topic-triggered, and give **real** trigger keywords (directory names, symbols,
   file prefixes from this repo) so domain selection is accurate.
3. Respect the token budget (target 500–1500, ceiling ~2000). Summarize, don't dump.

## Maintaining domains

- Re-run `prep refresh` after major structural changes (new subsystem, big
  refactor, framework upgrade) to refresh the topic files.
- When work surfaces a broadly-useful gotcha or convention, promote it into the right
  domain file (this is what `work on`'s wrap-up does automatically) — keep edits scoped
  and match the file's existing style.
- Keep `PROJECT.md` in sync if the VCS or tracker changes.

## Hard rules

{Environment-specific invariants every domain assumes. Examples to adapt:
- Never read generated/vendored trees (node_modules, build output, binaries).
- Run the project's codegen/build prerequisite before type-checking where required.
- Don't commit environment-specific config files.
- Query/verify real values instead of speculating.
- Domains point at existing convention docs (e.g. `.claude/rules/`) rather than copying them.}
```

---

## CLAUDE.md — the "Domain Knowledge System" section

`domains init` appends this section (create `CLAUDE.md` if it is missing) and inserts **one**
bullet into the project's `## Rules` list. Nothing else in that file is ours.

**Insert-if-absent, always.** `CLAUDE.md` belongs to the project, not to this plugin: match by
intent rather than verbatim text, skip a bullet the project already states in its own words, and
never reformat, reorder or remove anything around what you add.

### The one Rules bullet

```markdown
- **Proactively load domains** — run `prep <domain>` for relevant domains without being asked; use the user's prompt for initial discovery, then load more domains as the work reveals new topics.
```

If the project has no `## Rules` heading at all, **report it and ask** before creating one — a
missing heading is as likely to be deliberate as accidental.

### Domain Knowledge System section (append)

```markdown
## Domain Knowledge System

This project keeps its operational knowledge in `domains/` — per-topic files of
proven workflows, conventions, and gotchas for working in this codebase. The
manifest at `domains/INDEX.md` maps topics to files; `.agent/PROJECT.md` holds the
project config (environment, version control, ticket tracker, how "done" is proven).

### `prep <domain>`

When the user says `prep <domain>` (e.g. `prep {code}`, `prep {x} + {y}`), load the
matching domain file(s) before starting work:

- Read `domains/<domain>.md`. {If two-layer: read the plugin/general file first,
  then the project file.}
- For combined preps (`prep X + Y`), load all requested domains.

Proactively `prep` relevant domains without being asked — use the user's prompt for
initial discovery, then load more as the work reveals new topics.

### `prep refresh`

When the user says `prep refresh` (or the legacy alias `prep one time init`), read
the full procedure at `domains/prep-refresh-guide.md` and follow it step by step. It
(re)scans the project and (re)writes the per-topic domain files. Run once at setup,
then re-run after major changes.

To add a domain or understand how the system is maintained, see `domains/meta.md`.
```

---

## `domains/prep-refresh-guide.md` (project-local, environment-specific)

The re-runnable scan procedure. `work init` writes this so `prep refresh`
works later even without the `work` skill installed. **Tailor the whole thing to
the detected environment** — the structure below is the constant; the tools and
targets are not. See `init.md` "Writing the scan guide" for how to
fill it.

```markdown
# `prep refresh` — project scan for {ProjectName}

Read this file in full before starting. The goal is token-efficient domain files
that capture how THIS project is structured and worked — not raw dumps.

## Phase 1 — Discovery (read-only, breadth-first)

{Environment-specific discovery steps. For each: what to read or which safe,
read-only command to run, and what to extract. Examples by environment:
- web/node: read package.json (scripts, deps, workspaces), tsconfig, the app entry
  and routing setup; `yarn/npm list --depth=0`; the test runner config.
- python: read pyproject/requirements, the package layout, settings/urls; `pip list`.
- go/rust: read go.mod / Cargo.toml, the package layout, the main entry; `go list ./...` / `cargo metadata`.
Never run mutating commands.}

## Phase 2 — Deep inspection (depth on the few things that matter most)

{Identify the project's core subsystems (entry points, the main feature areas) and
read enough of each to describe its real shape — key modules, the dominant patterns,
naming conventions, the seams other code plugs into. Cap the depth; summarize the
long tail by grouping.

**Monorepos:** the unit of deep inspection is the **workspace member**, not a
guessed subsystem. Re-read the root monorepo config (the same one used at init —
`pnpm-workspace.yaml`, `package.json` `workspaces`, `nx.json`, `turbo.json`,
`Cargo.toml [workspace]`, `go.work`, etc.) and expand its globs to the concrete
list of projects. Every entry in that list gets a line here — none get dropped. If
the list is large, you may *summarize* trailing entries (group by kind, one-line
each) but you may not *omit* them. List the monorepo's enumerated projects below
so this guide is self-contained:

- {project-path-1}
- {project-path-2}
- ...}

## Phase 3 — Write the domain files

Write one file per always-load + major topic into `domains/`. Token budget per file:
target 500–1500, ceiling ~2000; summarize aggressively past that. Each file: what
the subsystem is, where it lives (paths), the proven patterns and naming
conventions, and the known gotchas. Keep the environment's real vocabulary.

## Scaling rules

{Group when counts explode: "147 components → 1 app shell, 12 feature modules, …".
Top-level only for big trees. List the most important N, summarize the rest.}
```

---

