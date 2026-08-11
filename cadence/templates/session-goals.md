# Session Goals — template

*Why a project works in bounded sessions, each with one goal. Tool- and process-agnostic; the specifics (how the goal is chosen, how bugs are handled) come from the project's flow. Cadence's `/cadence:session` skill automates this ritual.*

## Why sessions have goals

Without a defined goal, a session drifts to the nearest well-shaped task — usually the bug list — and calls it progress. The fix isn't discipline, it's removing the vacuum: every session starts by naming one goal that ladders up to a milestone, so there's nothing for the drift reflex to fill. **Never start a session without naming its goal first.**

## Session types

Pick one per session (the flow may define its own set): **Advance** (move an epic forward by finishing a ticket — the default), **Spike** (a timeboxed question), **Bug-batch** (a deliberately chosen burn-down), **Design/Plan** (no code — resolve an open question, break down an epic), **Polish** (tuning already-working work).

## Start ritual (~5 min)

1. Load memory and the current milestone.
2. Choose one goal via the flow's **priority policy** — not on impulse. (`/cadence:session start` does this by the flow's rules.)
3. State it in one sentence and pick the session type. If it won't fit one sentence, split it first.
4. Record the goal (a tracker comment) as the anti-drift anchor.
5. Note the flow's **bug rule** for the session (`defer` / `file` / `preempt`) so mid-session bugs are handled by policy.

## Sizing a good goal

One session ≈ one ticket. A good goal is **observable** ("the X event fires when Y"), **ladders up** (ticket → epic → milestone), and is slightly smaller than you think you can do.

## The bug rule

How a found bug is handled is set by the flow, not habit:
- **defer** (pre-release/solo default) — file it, keep going; schedule a bug-batch session deliberately.
- **file** — record and continue, no batching assumption.
- **preempt** (live-product default) — a customer-impacting bug becomes the goal, over the roadmap.

## End ritual (~5 min)

Mind the seam: the **execution skill owns** implement → test → docs → checkpoint. The end ritual *verifies* that and closes the envelope — it does not repeat them.

1. **Gate:** run the flow's gates for the transition to Done. Pass → done; fail → keep in progress with an honest note.
2. **Verify the checkpoint** — confirm the execution skill committed and updated docs; only do it yourself if execution doesn't own it.
3. **Advance the item** to Done in the tracker.
4. **Set the next session's goal** (one line, recorded) so the next start opens loaded.
5. **Memory:** capture cross-cutting decisions only — not the per-item gotchas the execution skill already filed.

## The responsibility split (why nothing duplicates)

- **Execution skill** (the project's own) owns one item end-to-end: implement, test, docs, checkpoint.
- **`/cadence:session`** owns the envelope: goal in, gate + verify + next-goal out.

If `/cadence:session end` ever finds itself committing or editing docs on a normal execution session, that's duplication — the execution skill already did it. Verify, don't repeat.
