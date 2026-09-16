# `markdown` — knowledge as markdown files in the registered artifact

The consumer-side fallback for a `Doc system | markdown` binding. It exists so `work` can satisfy
the doc-system seam **from repo artifacts alone**, with no other plugin installed and nothing read
out of another plugin's payload.

That is the whole reason this file is here rather than borrowed. The knowledge system's own plugin
ships a `markdown` adapter describing the format from the *provider* side; reading it would mean
reaching into another plugin's install path, which the seam rules forbid without exception. So the
consumer ships its own reading of the same repo artifact, and the two never have to agree on
anything except what is written in the repo.

## Capabilities

```markdown
## Capabilities
supports:    locate(), taxonomy()
costly:      —
unsupported: record()
```

## Resolving the artifact

**Read the path from the bus, never by scanning.** `## Artifacts` has a row whose owner is
`knowledge`; its path is the folder. No row, or a path that does not exist → this binding cannot
resolve: say so once and behave as [`none`](./none.md). Do **not** go looking for a likely folder
— finding one by name is the path-detection the registry exists to remove.

## Behaviour

- **`locate(topics, paths?)`** — read the manifest in that folder (the file the knowledge system
  keeps as its index), match `topics` against its rows, and return the files those rows name. Rank
  by the manifest's own ordering; where it distinguishes always-load rows from topic-triggered
  ones, always-load comes first. A row naming a file that does not exist is skipped and reported
  once, not repaired.
- **`taxonomy()`** — the manifest's topic names, verbatim. Do not normalise, re-case or invent
  slugs; a vocabulary that disagrees with the file it came from is worse than none.
- **`record(note)` — `unsupported`.** Writing knowledge belongs to the role that owns the folder.
  `work` reading it is a repo artifact; `work` writing it would be one tool editing another's
  artifact. The Curator's findings stay in session memory and are reported, exactly as under
  `none`.

## What the caller must do with that

**Say what loaded, once.** *"Loaded N knowledge files for these topics."* Not per step.

**Treat a stale entry as information, not an error.** A manifest row pointing at a moved file is
that owner's to fix, and its doctor reports it. Working from the rest is the right response;
stopping is not.

**Declare `docs: costly` rather than `supports`** if the folder is large enough that loading it
dominates a phase. The binding resolving says nothing about it being cheap.
