# `domains` — project memory

Per-topic knowledge files a repo authors **about itself**: proven workflows, conventions, and the
gotchas that cost someone an afternoon. Plus the manifest that says which of them a given task
should load, so an agent starts with the right context instead of rediscovering it.

## Skills

| Command | Does |
|---|---|
| `/domains:init` | Scaffold the knowledge system and register it in the config bus. Safe to re-run |
| `/domains:migrate` | Apply pending scaffolding migrations; re-stamp the `knowledge` row |

## What it owns

`domains/**` — the manifest, the maintenance guide, the scan guide, and every topic file — plus
the `knowledge` rows in the config bus (`.agent/PROJECT.md`) and the *Domain Knowledge System*
section of `CLAUDE.md`.

It owns **nothing else**. The bus itself is shared and sectioned; the ticket-flow overlay and
everything under `.agent/work/` belong to the delivery tool; `CLAUDE.md` belongs to the project,
so every edit there is insert-if-absent.

## Working with other tools

**Nothing needs this plugin installed to read a repo's knowledge** — the files are plain Markdown
in the repo, which is the point. What this plugin adds is the scaffolding, the maintenance path,
and a **published contract** so a tool can ask *what applies to what I am about to touch*
without knowing where any of it lives:

- [`contracts/DOC-SYSTEM.md`](contracts/DOC-SYSTEM.md) — `locate` · `record` · `taxonomy`, the
  capability tiers, and the floor (`locate` is required; `record` may be unsupported).
- [`adapters/markdown.md`](adapters/markdown.md) — the shipped zero-dependency fallback: per-topic
  Markdown files and a manifest, assuming only a filesystem.

If it is **absent**, a repo's `domains/` folder still sits there and a human still reads it; a
tool that wanted the contract gets no doc-system binding and says so once. Nothing hard-fails
because this is missing.
