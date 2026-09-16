# `none` — no knowledge system bound

## Capabilities

```markdown
## Capabilities
supports:    —
costly:      —
unsupported: locate(), record(), taxonomy()
```

## Behaviour

Every operation returns **empty**, immediately, without touching the filesystem.

- `locate(...)` → no entries. `work` plans from the ticket and the code.
- `record(...)` → nothing persisted. The Curator's findings stay in session memory.
- `taxonomy()` → no vocabulary.

## What the caller must do with that

**Say it once, then carry on.** *"No project memory bound; working from the ticket and the code."*
Not per step, not per phase — once. A warning repeated is a warning ignored.

**Do not create the folder.** If knowledge would be useful here, that is the user's decision and
another tool's job. `work` scaffolding one to have somewhere to write would be two tools owning
one artifact.

**Declare `docs: unsupported`** for this project in the execution contract, so a caller verifying
`work`'s output knows documentation was not part of it. Claiming `docs` with nothing bound is
inventing a capability.

⚠️ **This binding is the correct state for a repo with no knowledge system — and also what an
upgrading repo gets if it has a `domains/` folder and has not installed the tool that now owns
it.** Those two look identical from here and are not the same situation, which is why the
diagnostic reports the folder-without-a-binding case specifically.
