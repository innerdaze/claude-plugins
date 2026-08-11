# Tracker adapter: `markdown`

*A zero-dependency tracker. Work items are Markdown files in the repo — greppable, diffable, no external service. Implements the tracker contract from the plugin's `adapters/ADAPTERS.md`.*

## Capabilities

```
supports:    statuses, list_open, get, create, comment, update, list_closed,
             epic, milestone, labels, order, depends_on, severity, updated_at
unsupported: cycle, assignee
```

`cycle` and `assignee` are unsupported by choice, not oversight: this tracker
exists for one person working in one repo. A flow whose priority policy uses
`committed-sprint` will skip that token here and say so — if you need cycles,
you need a hosted tracker.

## Config

```yaml
tracker:
  kind: markdown
  path: .claude/cadence/backlog     # directory holding item files
  status_map:                       # flow lane -> the status written to disk
    Backlog: Backlog
    Done: Done
```

Because this tracker is free-form, **`status_map` is the vocabulary** — the
values on the right are exactly the statuses that exist. That is what
`statuses()` returns. Map only the lanes you want; a flow lane with no entry is
simply not represented, and the skills skip the step that needs it.

## On-disk format

One file per item at `<path>/<id>.md`:

```markdown
---
id: <PREFIX>-<n>
title: "<one line — ALWAYS quoted>"
type: milestone | epic | ticket | bug | spike | chore
status: <a value from status_map>
milestone: <milestone id or "">
epic: <parent epic id or "">
labels: []
order: <integer or omit>
depends_on: [<item id>, ...]
severity: <optional, for bugs>
updated: <YYYY-MM-DD>
---

<description in Markdown>

## Comments
- <YYYY-MM-DD> <comment>
```

**Quote `title:` always.** A title containing a colon — `"Perf budget: p95 under
200ms"` — is invalid YAML unquoted, and it silently breaks front-matter parsing
for that item. The same applies to any value containing `:`, `#`, or a leading
`[`.

`<PREFIX>` is `config.project.ticket_prefix`. IDs are allocated as
`max(existing numeric suffix) + 1` by scanning the directory — no counter file to
drift.

`updated:` is maintained explicitly by `update()`. Do **not** infer it from file
mtime: mtime is not preserved across clones, checkouts, or most sync tools, so an
inferred value would be confidently wrong.

## Operations

- **`statuses()`** — return the distinct values of `config.tracker.status_map`. The one mapped from the flow's `done` role (plus any `abandoned`) is terminal.
- **`list_open(filter?)`** — glob `<path>/*.md`, parse each front-matter block, keep items whose `status` is not in the caller-supplied terminal set. Apply any of `milestone`, `epic`, `type`, `status_in`, `status_not_in`, `updated_since`, `limit` that are given; ignore `cycle`/`assignee` and report that you did. Return the item record for each. (Glob + Read; don't load bodies unless asked.)
- **`list_closed(filter?)`** — the same, inverted: items whose `status` *is* in the terminal set.
- **`get(id)`** — Read `<path>/<id>.md`; return front-matter + description + comments.
- **`create(fields)`** — compute the next id; Write `<path>/<id>.md` from the template above; create `<path>/` if absent. Set `updated`. Return the new id.
- **`comment(id, text)`** — Edit the file: append `- <today> <text>` under `## Comments` (add the heading if missing). Take today's date from the environment.
- **`update(id, fields)`** — Edit the named front-matter fields and refresh `updated`. **`set_status(id, status)`** is this with one field — and it must reject a status that is not in `statuses()` rather than writing it.

## Concept mapping

- **epic** — an item with `type: epic`; a ticket belongs to it via its `epic:` field. (This is this tracker's `epic_convention`; there is no config key for it.)
- **milestone** — an item with `type: milestone`, or a bare string used in others' `milestone:` field.
- **label** — entries in `labels:`, drawn from the doc adapter's `taxonomy()`. With `doc_system: none` the taxonomy is empty and items carry no context labels.
- **status** — the literal `status:` string; valid values are exactly `statuses()`.

## Notes

- It's plain files, so reads and writes are Read/Write/Edit/Glob — no MCP.
- **Items are committed, deliberately.** They live under `.claude/cadence/backlog/` and are versioned alongside the code, so the backlog diffs and reviews like everything else — the main reason to pick this over a hosted tracker on a small project. Only `SESSION.local.md` is ignored; see "Where adapter data lives" in the plugin's `adapters/ADAPTERS.md`.
- Because items are committed, **the order of operations at session end matters**: the status change must land *before* the checkpoint, or the commit captures the item still open and leaves the tree dirty.
- To migrate to a hosted tracker later, switch `config.tracker.kind`; these files can be imported or left as history.
