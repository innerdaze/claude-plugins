---
name: cadence-session
description: Start or end a bounded work session in a project configured with Cadence. Start loads context, picks one goal per the flow's priority policy, and hands off to the project's execution skill; end runs the flow's gates, advances the item, verifies or performs the checkpoint, prunes the session scratchpad, and sets the next goal. Environment- and process-agnostic. Use when the user runs /cadence:session, says "start a session", "begin a work session", "wrap up", "end my session", "what should I work on next", or asks to close out the ticket they were working on.
---

# /cadence:session — Cadence session interpreter

This skill assumes **nothing** about the environment or the process. It reads the project's **config** (bindings: tracker, VCS, docs, execution skill) and its **flow** (methodology: states, roles, gates, priority, decision rights), and executes the session ritual by interpreting them. Where the flow sets a **hook**, run that instruction doc; otherwise use the default described here.

## Load order (do this first, every time)

1. **Read the config** at `.claude/cadence/config.md` — one location, always. If it isn't there, tell the user to run `/cadence:init` and stop. (A config at some other path is a pre-0.2 layout; say so and point at `/cadence:doctor`.)
2. **Load the flow spec** named in `config.flow` — a shipped preset at `${CLAUDE_PLUGIN_ROOT}/flows/<name>.flow.md`, or a project-local path resolved relative to the config file.
3. **Resolve adapters** from `config.tracker.kind`, `config.vcs.kind`, `config.doc_system.kind`. For each family, look first for a project-local adapter at `.claude/cadence/adapters/<family>/<kind>.md`, else the shipped fallback at `${CLAUDE_PLUGIN_ROOT}/adapters/<family>/<kind>.md`. Read each adapter's **Capabilities** block — it tells you which operations and fields actually exist here.
4. **Resolve the lane roles.** Every status this skill sets comes from `flow.states.roles.<role>` mapped through `config.tracker.status_map` to a real status. Never write a literal status name.
5. **Note `config.execution`** — the project's execution skill and what it `owns`.

Hook resolution, for any step named below: if `flow.hooks[<step>]` is set, load and follow that doc (passing it the step's Input, expecting its Output — the contracts are at `${CLAUDE_PLUGIN_ROOT}/flows/HOOKS.md`); else use the default here.

## Resolving a role to a status — read this once

Three things must line up before this skill changes an item's status:

1. the flow declares the **role** (`roles.active`, `roles.done`, …),
2. that role names a **lane**, and
3. `config.tracker.status_map` maps that lane to a **status the tracker really has**.

If any link is missing, **do not perform that transition.** Say so once, in one
sentence, and carry on with the rest of the session. A flow with no `active` role
is a legitimate process — it means "don't mark work in flight." A lane with no
`status_map` entry means the tracker cannot represent that step, which is normal
on a two-column board.

What you must never do is substitute a plausible-looking status. Moving an item
to a column that doesn't exist, or to a nearby one that does, is worse than not
moving it: the first fails loudly at best, and the second silently puts the
user's board into a state they never chose.

`roles.done` is the exception worth stating: if it is missing or unmapped, an
item cannot be completed, so **stop and ask** rather than ending the session
with the work in limbo.

## `/cadence:session start`

1. **`session.start`** (default): read the session-state file (`config.session_state.file`) — Cadence's own local scratchpad, *not* the project's memory. Determine the current milestone from the roadmap (`config.doc_system.roadmap`) and the tracker.
2. **`session.select_goal`** (default): walk `flow.intake.priority_policy` in order, gathering candidates via the tracker adapter. **Skip any token whose required field the adapter declares unsupported** (see the token table in `${CLAUDE_PLUGIN_ROOT}/flows/FLOW-SPEC.md`) and say which you skipped — a policy that silently does nothing is worse than a shorter one that works. If the flow has `hierarchy.first_class.incident`, check `states.incident_lanes` first. Where more than one candidate survives, run **`intake.prioritize`**. Respect `flow.decision_rights.select_goal`:
   - `ai` → pick it and state the choice.
   - `ai-proposes` → present the top 1–3 and let the user choose.
   - `human` → present the board; the user decides; don't pre-empt.
3. **Frame the goal** in one sentence ("By end of session, `<id> <title>` is `<done role>`") and name the **session type**. If it can't be said in one sentence, it's too big — offer to split it first.
4. **Move the item to `roles.active`**, per the resolution rules above, and fire **`transition.<from>_to_<to>`**. If the role or its mapping is absent, skip this and note it once. Check `states.wip_limit`: if the active lane already holds more than the limit, say so before adding to it.
5. **Record the goal** via the tracker adapter (`comment`) as the anti-drift anchor.
6. **State the bug rule** for this session (`flow.intake.bug_triage`), and mean it: if a bug surfaces later, fire **`bug.triage`** rather than deciding on impulse. New work arriving mid-session goes through **`intake.classify`** first.
7. **Hand off** to `config.execution.skill`. Do not implement here.

### When `config.execution.skill` is `none`

This is a normal, fully supported setup — the zero-dependency default, not a degraded one. It means **there is no execution skill to hand off to: the work happens in this session, with the user, in the open conversation.** `execution.owns` is empty, so nothing is owned elsewhere, and `/cadence:session end` performs the checkpoint itself rather than verifying someone else's.

## `/cadence:session end`

The order of these steps matters and is explained below — do not reorder them.

1. **Gate(s).** For the transition to `roles.done`, run each `gate.<name>.check` the flow attaches. The **effective DoD** is `flow.gates.dod.checks` ∪ `config.dod_gates` — a union; a project may raise the flow's bar, never lower it. Honour each gate's approver: a `human` gate is never auto-cleared. If a gate fails, leave the item where it is, record an honest note, and stop here.
2. **Advance the item** to `roles.done` (via `roles.review` first if the flow declares that transition), firing `transition.<from>_to_<to>`.
3. **Checkpoint.** If `config.execution.owns` includes `commit`, *verify* rather than repeat: use the VCS adapter's `log()` to confirm a checkpoint referencing this item exists, and `status()` to confirm the tree is clean. Otherwise — including whenever `execution.skill` is `none` — run the checkpoint yourself via the `checkpoint` hook / VCS adapter. Record any durable gotcha through the doc adapter's `record()`.
4. **Prune the session state** — run `session_state.prune`. The default rule lives in `${CLAUDE_PLUGIN_ROOT}/flows/HOOKS.md`; in short, reconcile the scratchpad **against the tracker** (not against what the file claims) and drop anything the tracker already tells you, keeping only non-obvious traps.
5. **`session.end`** (default): write the pruned session state to `config.session_state.file`, per the schema in `${CLAUDE_PLUGIN_ROOT}/adapters/ADAPTERS.md` — the next goal plus any **cross-cutting** note the tracker can't hold. Drop the next goal into a tracker `comment` too.

### Why status is set *before* the checkpoint

Under a tracker whose items live in the repo (the `markdown` fallback commits its
backlog deliberately), **the item file is part of the change set.** Committing
first therefore captures the item still open, and then step 2 re-dirties the tree
— so the commit's own backlog contradicts its message, and the `status()`-clean
check in step 3 can never pass again for any later session.

Setting status first is also correct for hosted trackers, where the two are
independent. So this order is universally right, and the reverse is quietly
wrong in exactly the configuration Cadence ships as its default.

**If the checkpoint fails after the status change**, say so plainly and offer to
revert the status. Do not leave the item advanced with the work uncommitted — a
tracker that claims work is done when it isn't committed is the one state worse
than either failure alone.

## When something doesn't resolve

Cadence is a chain of lookups — config → flow → adapters → roles → tracker — and a stranger's project will break that chain in ways yours never does. The rule at every link is the same: **surface the gap, don't fill it by inference.** A wrong guess here produces confident work against the wrong tool, the wrong process, or another project's conventions.

- **No config** → route to `/cadence:init` and stop.
- **`config.flow` names a file that isn't there** → stop. Name the missing path; offer to re-point `flow:` at a shipped preset or re-run init. Never silently substitute a preset — the flow *is* the process.
- **An adapter `kind` resolves to nothing** → stop and route to `/cadence:init`, which generates it.
- **A tracker is configured but unreachable** → say so and stop. Do not fall back to the `markdown` tracker: a second, empty backlog looks like a working system while forking the project's state.
- **A hook doc named in `flow.hooks` is missing** → report which, use the built-in default for that step, and continue. A flow author mid-authoring is better served by a working session and a warning.
- **A role or `status_map` entry is missing** → see the resolution rules above: skip the transition and note it, except for `roles.done`, where you stop and ask.
- **The tracker returns no open items** → not an error. Say the backlog is empty for this milestone and offer `/cadence:plan`.

## Notes

- **Honour decision rights.** Never auto-decide a step the flow marks `human`.
- **Never repeat execution-owned work.** `config.execution.owns` is the seam that keeps this skill and the execution skill from duplicating commit/doc steps — and it cuts both ways: what execution doesn't own, this skill must do.
- **Stay fast.** ~5 minutes each end. The value is the goal in and the verified close out, not ceremony.
- **Delegate the grunt work.** Batchy adapter reads/writes can go to the `mechanical` subagent, spawned per the calling convention in `${CLAUDE_PLUGIN_ROOT}/adapters/ADAPTERS.md`. The goal *decision* and gate *judgment* stay on the session model.
- **Session state is Cadence's own local file.** Read and write only `config.session_state.file`. Never read, write, or depend on the project's own memory (`CLAUDE.md`, agent `MEMORY.md`), and never reach outside `.claude/cadence/`.
