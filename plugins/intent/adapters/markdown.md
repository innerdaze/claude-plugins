# `markdown` — the shipped intent-read fallback

*The zero-dependency binding: the intent folder as Markdown documents in the repo. Assumes a
filesystem. Read-only by construction, which is the point rather than a limitation.*

## Capabilities

```markdown
## Capabilities
supports:    locate(topics), locate(paths)
costly:      —
unsupported: check()
```

`check()` is **unsupported here**, and it should be said plainly why: comparing a plan against
stated intent is a judgement, and this fallback is a file reader. A caller that wants it falls
back to `locate` and does the comparison where the judgement belongs — in the Planner, whose
output a human reads.

## Where it reads

The intent folder registered in the config bus's `## Artifacts` under owner role `intent-layer`
— **never a hardcoded path.** No row, or a path that does not exist, means no intent layer is
registered: return empty and say nothing.

That silence is deliberate. Most projects have no intent layer, and an unregistered one is
**invisible by design** — it becomes visible when its owner runs and registers it, not when
someone guesses at a folder that looks like design documentation.

## `locate(topics, paths?)`

1. **Read the folder's index** if it has one; otherwise treat each document as a topic.
2. **Always include the standing order** — whatever the index marks as the rules of the doc set.
   Intent has a spine that applies to everything, unlike knowledge, where nothing is universal.
3. **Match topics** against document titles, headings and index entries.
4. **Match paths**, when given, against any paths a document names.
5. **Rank** the matches, most specific first, ties in index order so two callers see the same
   list.
6. **Carry the attribution markers through, verbatim.** A statement marked as unratified
   inference is *not* the same as a dictated one, and a caller that flattens the distinction is
   reporting a guess as a decision. If the layer marks it, pass it on.

## What it must never do

- **Never write.** No operation, no exception, no "recording that a gap was found". The register
  is written by the capture workflow with a human present.
- **Never soften.** Return statements as they are. A contradiction is the caller's to report, not
  this adapter's to smooth over by paraphrasing.
- **Never infer intent from code**, even when a document is thin. Empty is the honest answer, and
  the whole layer exists because reading code produces a different artifact.
