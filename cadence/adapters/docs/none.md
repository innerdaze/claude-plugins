# Doc-system adapter: `none`

*For projects without a structured knowledge-doc system. Implements the doc-system contract from `ADAPTERS.md` with the lightest possible footprint — so durable lessons still aren't lost.*

## Config

```yaml
doc_system:
  kind: none
  notes: .cadence/notes.md       # where record() appends (default)
```

## Operations

- **`locate(topics)`** — returns nothing structured. Suggest the skill glance at `README`/`CONTRIBUTING` if present, otherwise proceed. There is no context-pack mapping under `none`.
- **`record(note)`** — append the note to `<notes>` (default `.cadence/notes.md`) under a dated bullet, creating the file if absent. This is the minimal fallback so a hard-won gotcha survives even without a doc system.

## When to move off `none`

`none` keeps overhead at zero, but as a project grows, a real doc system pays for itself: it lets the execution skill load *only* the relevant context per item (via label→doc mapping) instead of re-deriving it. When that time comes, switch `config.doc_system.kind` to `domains` (or another doc adapter) and migrate the accumulated `notes.md` entries into the structured docs. Cadence's `record()` calls then land in the right place automatically.

## Note

Even under `none`, the DoD's "docs updated" gate (if the flow includes it) is satisfied by a meaningful `record()` — the bar is "the lesson is written down somewhere durable," not "a specific doc system exists."
