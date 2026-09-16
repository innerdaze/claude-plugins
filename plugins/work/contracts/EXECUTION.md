# The execution contract

*What a caller invokes to have a tracked ticket delivered, and what it may therefore stop doing
itself. This is the contract `work` **exposes**; the ones it consumes are in
[`../adapters/`](../adapters/).*

**Contract version: 1.** A new optional field is minor. Changing what `deliver` does, or removing
a declared `owns` capability, is breaking — a caller was relying on not doing that work.

## `deliver(ticket) → outcome`

Hand over a ticket id; `work` runs its phases and reports. One operation, because **the phase
spine is `work`'s own business, not the caller's.**

| Input | Required | Meaning |
|---|---|---|
| `ticket` | **yes** | the ticket id, in the project's own scheme |

Per-phase entry points are deliberately **not** offered. Exposing Context / Execute / Wrap-up
separately would make the spine part of this contract, so a caller could run two of three — and
the spine's invariance is the promise being made. A caller wanting only analysis is asking for a
different tool.

**`declined` is a legitimate outcome, not an error.** `work` refuses a ticket it cannot plan —
too vague, or contradicting the project's stated intent — and a caller must handle that as an
answer rather than a failure.

## `owns` — the declaration that makes verifying possible

`work` declares what it handles, so a caller **verifies rather than repeats**:

```markdown
## Capabilities
supports:    implement, test, docs, commit
costly:      —
unsupported: —
```

`docs` means project memory, and it is `supports` **only when a doc-system binding exists**. With
none, `work` declares `docs: unsupported` for that project and says so once — because claiming to
handle documentation when nothing is bound is exactly the invented capability the prohibitions
below forbid.

**This list is declared by the plugin, not configured by the user.** A hand-maintained list in
every repo drifts from what the tool does, and the drift is invisible because both sides still
parse. A project may **narrow** it — "we do our own commits" — and that narrowing is a project
statement recorded in the config bus, not a redefinition of what `work` does.

## What a caller may assume

- **It may not drive the phases.** It invokes delivery and reads the outcome.
- **It may not assume the approval gate is skippable.** `deliver` stops for a human before
  anything is written. A caller wanting unattended delivery is asking for something not offered.
- **It must not repeat what `owns` claims.** That is the entire point of the declaration: a
  caller that commits again after `work` committed is the duplication this removes.

## Two prohibitions

- **Never work around a missing capability** by doing the work somewhere the contract does not
  model.
- **Never invent the data.** An outcome field `work` cannot fill is absent, not fabricated.
