# Cadence Ceremonies — default behaviours

> ## ⚠️ Documented, not yet invokable
>
> **No skill currently fires a `ceremony.*` hook, and no command runs a standup,
> review, retro, or incident review.** Everything below specifies what those
> ceremonies *will* do, so the contracts are settled and a flow can declare
> `cadence.ceremonies` without asserting something false. Today, declaring them
> is a description of your team's process, not an automation of it.
>
> **The one exception is planning**, and only partly: when a flow sets
> `decision_rights.commit_scope: human`, `/cadence:plan` writes a planning pack
> to `.claude/cadence/planning-pack-<date>.md` for your meeting, and stops. That
> is the `planning.prepare` behaviour below, reached through `/cadence:plan`
> rather than through a ceremony hook.
>
> Setting a `ceremony.*` hook in a flow is legal and has no effect. This section
> will be removed when the ceremony layer becomes invokable.

*A flow that lists a ceremony in `cadence.ceremonies` gets the defaults below, unless it overrides them with a `ceremony.<name>.prepare` or `.capture` hook (see `HOOKS.md`). These honour the core principle: **Cadence prepares the inputs a human ceremony needs and records what was decided — it never runs the meeting or makes the decisions.** Every `prepare` receives `{board, history, window}` and returns a prep artifact; every `capture` receives `{decisions}` and records them via the tracker/memory adapters. Ceremonies are mechanical-tier collation (delegate to the `mechanical` subagent); the judgment stays with the humans in the room.*

*Solo flows list no ceremonies, so none of this applies to `solo-greenfield`. These matter for `team-sprints` and `live-oncall`.*

## planning

- **prepare** → a **planning pack**: the ranked candidate backlog for the milestone, each item with its estimate (if the flow estimates) and its Definition-of-Done gates; last cycle's throughput if history has it; a *proposed* sprint sized to that throughput; and the open questions blocking commitment. Presented for the team to decide — never auto-committed (`decision_rights.commit_scope: human`).
- **capture** → record the **committed sprint**: move the agreed items to `Sprint Backlog`, tag them to the cycle, and note anything explicitly deferred. This is the outcome of `plan.commit_scope` when the approver is human.

## standup

- **prepare** → a **standup digest**: what moved since the last standup (Done, newly In Progress), what's in flight per owner, and — surfaced first — anything **blocked or at risk** (stuck in review, past its estimate, gate-failing). Keep it scannable; it's a prompt for the humans, not a status verdict.
- **capture** → record surfaced **blockers and reassignments** as comments/updates on the affected items, and file any new blocker that needs its own ticket.

## review

- **prepare** → a **review pack**: what shipped this cycle vs what was committed, a demo list (items now `Done`), and the carryover (committed-but-incomplete, with why). 
- **capture** → record **outcomes and feedback** — accepted vs needs-more-work — as item updates, and file follow-up tickets for feedback that becomes new work.

## retro

- **prepare** → **retro inputs**: the cycle's numbers (committed vs completed, carryover), plus signal Cadence can see — gate-failure patterns, bug influx vs closure, items that blew their estimate — as neutral prompts. Not conclusions; the team draws those.
- **capture** → record the **action items** the team agrees on as tickets (usually under a `Maintenance`/process epic), so retro decisions become tracked work instead of good intentions.

## incident-review  *(live-oncall)*

- **prepare** → a **postmortem draft scaffold**: the timeline reconstructed from the incident item's history, the impact/severity as recorded, and prompts for the human sections (contributing factors, what caught it, what didn't). Cadence assembles facts; people write the analysis.
- **capture** → record the **finished postmortem** on the incident (satisfying `gate.postmortem`) and file its **follow-up/prevention tickets**, linked back to the incident.

## Authoring your own

Override any of these by pointing a `ceremony.<name>.prepare` / `.capture` hook at your own doc in your flow's `hooks:` map — e.g. your team's specific planning-pack format or postmortem template. The hook receives the same Input and must return the same shape (see `HOOKS.md`). Add a *new* ceremony simply by listing it in `cadence.ceremonies` and providing its hooks.
