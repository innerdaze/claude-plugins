# Tracker adapter: `markdown`

*A zero-dependency tracker. Work items are Markdown files in the repo — greppable, diffable, no external service. Implements the tracker contract from `ADAPTERS.md`.*

## Config

```yaml
tracker:
  kind: markdown
  path: .cadence/backlog        # directory holding item files (default)
```

## On-disk format

One file per item at `<path>/<id>.md`:

```markdown
---
id: <PREFIX>-<n>
title: <one line>
type: milestone | epic | ticket | bug | spike | chore
status: <a status name from config.tracker.statuses / flow states, e.g. Backlog>
milestone: <milestone id or "">
epic: <parent epic id or "">      # set on tickets that belong to an epic
labels: [<label>, ...]
---

<description in Markdown>

## Comments
- <YYYY-MM-DD> <comment>
```

`<PREFIX>` is `config.project.ticket_prefix`. IDs are allocated as `max(existing numeric suffix) + 1` (scan the directory — no counter file to drift).

## Operations

- **`list_open(milestone?)`** — glob `<path>/*.md`, parse each front-matter block, keep items whose `status` is not the flow's terminal state (e.g. `Done`); if `milestone` is given, also filter by it. Return `{id,title,type,status,epic,milestone,labels}` for each. (Use Glob + Read; don't load bodies unless needed.)
- **`get(id)`** — Read `<path>/<id>.md`; return front-matter fields + description + the Comments list.
- **`create(fields)`** — compute the next id; Write `<path>/<id>.md` from the template with `fields` (title, type, description, and optional epic/milestone/labels); create `<path>/` if absent. Return the new id.
- **`comment(id, text)`** — Edit the file: append `- <today> <text>` under `## Comments` (add the heading if missing). Get today's date from the environment.
- **`set_status(id, status)`** — Edit the file's front-matter `status:` field to the new value.

## Concept mapping

- **epic** — an item with `type: epic`. A ticket "belongs to" it via its `epic:` field.
- **milestone** — an item with `type: milestone` (or just a string used in others' `milestone:` field).
- **label** — entries in the `labels:` list; these are what the execution/doc adapter uses to load context.
- **status** — the literal `status:` string; valid values are `config.tracker.statuses` / the flow's `states.lanes`.

## Notes

- It's plain files, so `/session`'s reads/writes are Read/Write/Edit/Glob — no MCP.
- Because items are in the repo, they're versioned by the VCS adapter alongside code — a nice property for solo/greenfield work.
- To migrate to a hosted tracker later, switch `config.tracker.kind`; the item files can be imported or left as history.
