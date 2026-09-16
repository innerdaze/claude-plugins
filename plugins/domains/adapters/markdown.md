# `markdown` — the shipped doc-system fallback

*The zero-dependency binding: per-topic Markdown files in the repo, with a manifest. Assumes a
filesystem and nothing else. This is what runs before any project-local adapter is generated,
and for most projects it is all they will ever need.*

## Capabilities

```markdown
## Capabilities
supports:    locate(topics), locate(paths), record(), taxonomy()
costly:      —
unsupported: —
```

All four, because everything here is a file read or a file write. Nothing about this binding is
expensive at repo scale; a project whose knowledge has outgrown a directory scan generates an
adapter with a real index and declares `costly` where it applies.

## Where it reads

The knowledge folder registered in the config bus's `## Artifacts` table under owner role
`knowledge` — **not** a hardcoded path. No row, or a path that does not exist, means there is no
knowledge system: return empty results and say so once. Do not scan for a likely folder.

## `locate(topics, paths?)`

1. **Read the manifest** in the knowledge folder. It maps topics → files, with trigger keywords
   and an always-load set.
2. **Always include the always-load rows.**
3. **Match topics** against trigger keywords and symbols, case-insensitively, in the caller's
   topics.
4. **Match paths**, when given, against each row's path patterns. A row whose patterns cover a
   path the caller named is included even when no keyword matched — this is the whole reason
   `paths` exists.
5. **Rank** what matched: always-load first, then by how specifically it matched — an exact
   path or symbol hit above a keyword substring, a keyword in the title above one in the body.
   Ties keep manifest order, so the ranking is deterministic and two callers see the same list.
6. **Return digests**, and bodies only for entries the caller asked to expand.

Err toward inclusion when ambiguous, but say so if the result exceeds roughly five topics: that
usually means the caller's scope is too broad to answer usefully, and the honest answer is to
say so rather than to return everything.

## `record(note)`

Append to the topic file that owns the subject; **mint a new topic file and add its manifest row**
when none fits. Two rules from the knowledge system's own design:

- **Timeless.** Strip ticket ids, dates and commit refs — provenance lives in the tracker and the
  VCS, not in the knowledge. What stays is the present-tense rule or gotcha.
- **Pays for itself.** An entry that will not save more than it costs to load should not be
  written. Say what you dropped and why.

## `taxonomy()`

The manifest's topic slugs, verbatim. It is a controlled vocabulary only to the extent the
project has kept one — return what is there, and empty when the manifest has no topics.
