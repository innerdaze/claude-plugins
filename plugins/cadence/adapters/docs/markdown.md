# Doc-system adapter: `markdown` — knowledge as markdown files in the registered folder

*The consumer-side fallback for a `Doc system | markdown` binding — the kind the knowledge
tool's own init writes into the bus. It exists so cadence can satisfy the doc-system seam **from
repo artifacts alone**, with no other plugin installed and nothing read out of another plugin's
payload.*

That is the whole reason this file is here rather than borrowed. The knowledge tool ships a
`markdown` adapter describing the format from the *provider* side; reading it would mean reaching
into another plugin's install path, which the seam rules forbid without exception. So the
consumer ships its own reading of the same repo artifact, and the two never have to agree on
anything except what is written in the repo.

## Capabilities

```
supports:    locate(), record(), taxonomy()
costly:      —
unsupported: —
```

## Resolving the artifact

**Read the path from the bus, never by scanning.** `## Artifacts` has a row whose **Owner** is
`knowledge`; its path is the folder. No row, or a path that does not exist → this binding cannot
resolve: say so once and behave as [`none`](./none.md). Do **not** go looking for a likely folder
— finding one by name is the path-detection the registry exists to remove.

## Operations

- **`locate(topics, paths?)`** — read the manifest in that folder (the file the knowledge system
  keeps as its index), match `topics` against its rows' trigger keywords, and `paths` against any
  path patterns a row names; return the files those rows point at. Always-load rows come first,
  then the rest in manifest order. A row naming a file that does not exist is skipped and reported
  once, never repaired — the folder is another role's.
- **`record(note)`** — append the note to cadence's **own** notes file, `.agent/cadence/notes.md`,
  under a dated bullet, exactly as `none` does. Cadence may not write into the knowledge folder:
  that is the knowledge role's artifact, and the execution skill's wrap-up is what promotes a
  session's learnings into it. Say once where the note landed. The DoD's docs gate is satisfied
  by a meaningful `record()` here as under `none` — the bar is *the lesson is written down
  somewhere durable*, not *in a particular folder*.
- **`taxonomy()`** — the manifest's topic names, verbatim. Do not normalise, re-case or invent
  slugs; a vocabulary that disagrees with the file it came from is worse than none.

## Notes

- **The kind is the bus's, not cadence's.** An older `/cadence:init` invented adapter names for
  knowledge systems it recognised (`domains`), and a project could then carry a bus row saying
  `markdown` and an adapter file saying something else — which resolves to nothing on both sides.
  Migration v4 renames such a file to the bus's kind; init no longer invents one.
- **Declare `costly` in a generated adapter** if the folder is large enough that loading it
  dominates a session start. The binding resolving says nothing about it being cheap.
