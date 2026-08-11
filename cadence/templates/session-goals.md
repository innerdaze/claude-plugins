# Session Goals — template

*Why a project works in bounded sessions, each with one goal. Tool- and process-agnostic; the specifics (how the goal is chosen, how bugs are handled) come from the project's flow. Cadence's `/cadence:session` skill automates this ritual.*

## Why sessions have goals

Without a defined goal, a session drifts to the nearest well-shaped task — usually the bug list — and calls it progress. The fix isn't discipline, it's removing the vacuum: every session starts by naming one goal that ladders up to a milestone, so there's nothing for the drift reflex to fill. **Never start a session without naming its goal first.**

## Session types

Pick one per session (the flow may define its own set): **Advance** (move an epic forward by finishing a ticket — the default), **Spike** (a timeboxed question), **Bug-batch** (a deliberately chosen burn-down), **Design/Plan** (no code — resolve an open question, break down an epic), **Polish** (tuning already-working work).

## Start ritual (~5 min)

1. Load the session scratchpad and the current milestone.
2. Choose one goal via the flow's **priority policy** — not on impulse. (`/cadence:session start` does this by the flow's rules.)
3. State it in one sentence and pick the session type. If it won't fit one sentence, split it first.
4. Move the item to the flow's *active* lane, if the flow declares one and the tracker has a column for it.
5. Record the goal (a tracker comment) as the anti-drift anchor.
6. Note the flow's **bug rule** for the session (`defer` / `file` / `preempt`) so mid-session bugs are handled by policy rather than reflex.

## Sizing a good goal

One session ≈ one ticket. A good goal is **observable** ("the X event fires when Y"), **ladders up** (ticket → epic → milestone), and is slightly smaller than you think you can do.

## The bug rule

How a found bug is handled is set by the flow, not habit:
- **defer** (pre-release/solo default) — file it, keep going; schedule a bug-batch session deliberately.
- **file** — record and continue, no batching assumption.
- **preempt** (live-product default) — a customer-impacting bug becomes the goal, over the roadmap.

## End ritual (~5 min)

1. **Gate:** run the flow's gates for reaching the *done* lane. Pass → continue; fail → leave the item where it is, with an honest note.
2. **Advance the item** in the tracker.
3. **Set the next session's goal** (one line, recorded) so the next start opens loaded.
4. **Checkpoint:** if an execution skill owns `commit`, *verify* it happened; otherwise do it yourself.
5. **Scratchpad:** keep only cross-cutting notes the tracker can't hold — not per-item gotchas, which belong on the item or in the docs.

**Commit last.** If your work items live in the repo — a file-based tracker —
then *every* tracker write is a repo write: the status change, the next-goal
note, all of it. Anything you write after committing leaves the tree dirty and
contradicts the commit you just made. Moving only the status earlier and still
commenting afterwards reproduces the same problem one step later.

The scratchpad is the exception: it's ignored, so it can be written last.

## The responsibility split (why nothing duplicates)

- **Execution skill** (the project's own, if it has one) owns an item end-to-end: implement, test, docs, checkpoint.
- **`/cadence:session`** owns the envelope: goal in, gate + advance + checkpoint + next-goal out.

The seam is `execution.owns`, and it cuts both ways. **What execution owns, the
session verifies rather than repeats** — if end finds itself re-committing work
an execution skill already committed, that's duplication.

**What execution does not own, the session must do itself.** With
`execution.skill: none` — the zero-dependency default — nothing is owned
elsewhere: the work happens in the session, and end performs the checkpoint. That
is the correct behaviour, not an exception to the rule.
