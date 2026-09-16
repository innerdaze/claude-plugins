# The seam catalog — `work`'s hooks and slots

*Where behaviour may be changed, what each seam receives, and what it must return. This table
**is** the extension surface: an overlay that names something not here is naming nothing.*

**Catalog version: 1.** A new optional seam or output field is minor. Renaming a seam, or
changing an Input/Output, is breaking — an overlay was written against it.

## Two primitives, and the difference is enforceable

| | Means | May target |
|---|---|---|
| **hook** | *replaces* a step's default behaviour | only a step marked hookable below |
| **slot** | *inserts* a new step beside existing ones | any anchor below |

**A hook over a gate or a domain-integration step is rejected**, not warned about — that is what
"an overlay only adds" means in a form something can check. A slot running beside one is fine.
The distinction exists so *weakening* is structural rather than a judgement about a step's
prose.

## Purity — what a seam may and may not do

**Seams decide and describe; the skill performs.** A hook returns *"create these three items"*;
it does not call the tracker. Adopted from `cadence`, for the same reason: a seam that performs
its own side-effects cannot be reasoned about, retried, or run in a fresh context.

## Hookable steps

Every row names the step that fires it. **A catalogued seam with no firing site is a defect**,
not a feature — a promise of extensibility that silently does nothing.

| Hook | Fired by | Input → Output |
|---|---|---|
| `ticket.analyse` | Step 1.1 (Ticket Analyst) | `{ticket, domain summary}` → `{goal, what the ticket says, comment history, relevant code, ambiguities, hidden complexity}` |
| `question.decide` | Step 1.2 | `{ambiguities, assumptions available}` → `{ask \| assume}` + the question or the assumption recorded |
| `plan.produce` | Step 1.3 (Planner) | `{ticket analysis, domain context, assumptions, intent layer}` → a plan carrying `Goal · Approach · Steps · Parallelisation · Files · Risks · Out of scope · Verification · Intent conflicts` |
| `task.split` | Step 2.1 | `{approved plan}` → `{ordered tasks, parallel groups}` |
| `implement.task` | Step 2.2 (Implementer) | `{task, plan, domain context, verification}` → `{what changed, verification run, STOP?}` |
| `rescope.classify` | Step 2.3 | `{STOP report, current plan}` → `{additive \| invalidating}` + rationale |
| `checkpoint` | Step 3.2 (Commit) | `{changes, ticket ref, VCS binding}` → `{commit actions}` — same seam name as `cadence`'s, because it is the same concept |
| `ticket.comment` | Step 3.3 | `{outcome, curator items}` → `{comment text}` |
| `followup.file` | Step 3.4 | `{deferred items, tracker binding}` → `{items to create, status transition}` |

## Not hookable, and why

| Step | Why |
|---|---|
| Step 1.0 · 1.0b · Domain re-check · 3.1a Curator · 3.1b Doc Updater | **domain integration** — the context guarantee is the promise; a hook here removes it silently |
| Step 1.4 `ExitPlanMode` | **the approval gate.** Nothing may replace the human stop before the first write |
| The project's verification | **the proof-of-done gate.** A ticket closing without the project's own proof makes the wrap-up decoration |
| Step 3.1a-i | it is already a *seam* — replace the **binding**, not the step |

An overlay may still `slot` a step immediately before or after any of these. That is the
supported way to add behaviour around a guarantee without removing it.

## Slot anchors

| Anchor | Position |
|---|---|
| `phase1.start` · `phase2.start` · `phase3.start` | first in that phase |
| `phase1.end` · `phase2.end` · `phase3.end` | last in that phase |
| `before <step-id>` · `after <step-id>` | adjacent to any step above, hookable or not |

A slot declaring `Parallel: independent` may be grouped with an adjacent independent slot, and
the two run concurrently. Grouping a slot that depends on its neighbour is a defect the overlay's
own schema rejects.

## What an overlay may not do, restated for authors

1. **The three phases are never removed or reordered.**
2. **Domain integration always runs.**
3. **No gate is weakened** — no `hook` targets a gate or a domain-integration step.
4. **A ticket matching no scenario runs the plain spine**, which is valid rather than an error.

Written in enforceable terms so the validator can check them, and so an author knows before
writing rather than after being refused.
