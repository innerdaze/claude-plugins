# Templates

Starting points, not forms to fill. Match the project's own voice and drop
sections that don't apply.

## `intent/README.md`

```markdown
# <Project> — Design Docs

The **intent** layer for <project>: what it is for, how it is meant to be built,
and how it is meant to be worked on. Written from the maintainer's stated design,
not read off the code.

## Rules of this doc set

1. **The maintainer is the source of truth.** These docs record stated intent.
2. **Code does not get a vote.** Where the implementation contradicts a statement
   here, the doc stays as written and the contradiction is logged in
   [`alignment.md`](./alignment.md) as work to do.
3. **No duplication of the "how".** <existing docs> describe how the thing is
   built. They point *up* at these docs for the why; these docs do not restate
   file layouts, schemas, or checklists.
4. **Unstated is not assumed.** Anything not stated is marked
   `TODO — needs input` rather than inferred.

## Contents

| Doc | Covers |
|---|---|
| [purpose.md](./purpose.md) | ... |
| [alignment.md](./alignment.md) | Register of code-vs-intent gaps |

## Status

<per-doc state: settled / what's still open>
```

Keep the status table current — it's how the maintainer sees progress, and it stops
a half-captured folder reading as finished.

## A topic stub (phase 2)

```markdown
# <Topic>

> **Status:** TODO — needs input.

## <First question this doc answers>

_TODO_

## <Second>

_TODO_

---

### Needed from you

- <specific, answerable question>
- <another — aim for 4–6, concrete not open-ended>
```

Good `Needed from you` questions name the decision, not the area. "What is the
unit of a record — per run, per release, per day?" beats "tell me about the data
model."

## `intent/alignment.md`

```markdown
# Alignment register

Where the implementation contradicts stated intent in `intent/`. The design docs
are not edited to match code — the code gets fixed, or the intent gets restated
deliberately.

Severity: **blocker** (intent unachievable as built) · **drift** (works, wrong
shape) · **cosmetic** (naming/docs only).

<ticket table, once filed>

## Open

| # | Intent | What the code does | Severity | Status |
|---|---|---|---|---|
| 1 | <claim + link to the doc> | <specific: file, symbol, line> | blocker | <open / fix decided / needs your decision> |

## Resolved

- **<claim>** — <why it turned out not to be a gap, or how it was fixed>

## Decided, not yet checked against code

- **<claim>** (<doc>). <what would have to be true, and what nobody has verified>

## Still open in the intent docs

<the remaining TODO — needs input markers, by doc>
```

Two things make rows useful: **specificity** on the code side (name the file and
symbol, not "the collectors"), and a **status** that says what happens next rather
than restating the problem.

Number rows so they can be cited in tickets and commits. When a gap spawns a
dependency, `2a`-style sub-rows keep the numbering stable.

## Commit messages

Put the *decisions* in the log, not just the file list. Someone reading `git log` in
a year should see what was settled without opening the docs.

```
docs: add intent/ as the intent layer

<one paragraph on what the layer is for and the code-gets-no-vote rule>

<one paragraph listing the substantive decisions recorded>

<one paragraph on what the register opens with, blockers named>
```

## The conflict pattern

When two of the maintainer's own answers don't compose, write it into the relevant
doc as a named, unresolved conflict with options — then log it in the register.
Something like:

```markdown
### <Thing> conflicts with <rule> — unresolved

<Why they collide, concretely.>

One of the two has to give:

- **<Option A>.** <What it costs.>
- **<Option B>.** <What it costs.>

> **TODO — needs decision.** Tracked in [alignment.md](./alignment.md).
```

Surfacing the collision *is* the deliverable. Picking silently destroys the thing
that makes the docs trustworthy.
