# `markdown` — stated intent as Markdown documents in the registered artifact

*The consumer-side fallback for an `Intent` binding of `markdown`. It exists so cadence can
satisfy the intent-read seam **from repo artifacts alone**, with no other plugin installed and
nothing read out of another plugin's payload.*

That is the whole reason this file is here rather than borrowed. The intent tool ships a
`markdown` adapter describing the format from the *provider* side; reading it would mean reaching
into another plugin's install path, which the seam rules forbid without exception. So the
consumer ships its own reading of the same repo artifact, and the two never have to agree on
anything except what is written in the repo.

## Capabilities

```
supports:    locate(topics), locate(paths)
costly:      —
unsupported: check()
```

`check()` is unsupported, and the reason is worth stating: comparing a milestone against stated
intent is a judgement, and this fallback is a file reader. The skill falls back to `locate` and
does the comparison itself, in the proposal a person reads — never here.

## Resolving the artifact

**Read the path from the bus, never by scanning.** `## Artifacts` has a row whose **Owner** is
`intent-layer`; its path is the folder. Match on the owner role id, not on the artifact's name or
path — the role id survives renames and handovers, and the name does not. No row, or a path that
does not exist → this binding cannot resolve: say so **once** and behave as [`none`](./none.md).
Do **not** go looking for a likely folder — finding one by name is the path-detection the registry
exists to remove.

## `locate(topics, paths?)`

1. **Read the folder's index** if it has one; otherwise treat each document as a topic.
2. **Always include the standing order** — whatever the index marks as the rules of the doc set.
   Intent has a spine that applies to everything, unlike knowledge, where nothing is universal.
3. **Match topics** against document titles, headings and index entries. For a milestone, the
   topics are the nouns of its scope and exit criteria; for a proposed item, its title and the
   systems it names.
4. **Match paths**, when given, against any paths a document names.
5. **Rank** the matches, most specific first, ties in index order so two callers see the same
   list.
6. **Carry the attribution markers through, verbatim.** A statement marked as unratified
   inference is *not* the same as a dictated one, and a caller that flattens the distinction is
   reporting a guess as a decision. If the layer marks it, pass it on — the proposal says which
   kind of statement a milestone collided with.

## What it must never do

- **Never write.** No operation, no exception, no "recording that a milestone disagreed". The
  layer's register is written by its own capture workflow with a human present. A contradiction
  cadence finds is reported outward, in the proposal, and a person moves it.
- **Never soften.** Return statements as they are. A contradiction is the skill's to report, not
  this adapter's to smooth over by paraphrasing.
- **Never infer intent from code or from the roadmap.** Empty is the honest answer. The roadmap
  is the thing being checked; it cannot also be the source of what it is checked against.
