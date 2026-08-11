---
name: cadence-session
description: Start or end a bounded work session in a project configured with Cadence. Start loads context, picks one goal per the flow's priority policy, and hands off to the project's execution skill; end runs the flow's gates, verifies (never repeats) the checkpoint, prunes the session scratchpad, and sets the next goal. Environment- and process-agnostic. Use when the user runs /cadence:session, says "start a session", "begin a work session", "wrap up", "end my session", "what should I work on next", or asks to close out the ticket they were working on.
---

# /cadence:session — Cadence session interpreter

This skill assumes **nothing** about the environment or the process. It reads the project's **config** (bindings: tracker, VCS, docs, execution skill) and its **flow** (methodology: states, gates, cadence, priority, decision rights), and executes the session ritual by interpreting them. Where the flow sets a **hook**, run that instruction doc; otherwise use the default described here.

## Load order (do this first, every time)

1. **Locate & read the config.** If the repo has a `domains/` doc system, the config is `domains/PROJECT.md`; otherwise `.claude/cadence/config.md`. If neither exists, tell the user to run `/cadence:init` and stop.
2. **Load the flow spec** named in `config.flow` — a shipped preset at `${CLAUDE_PLUGIN_ROOT}/flows/<name>.flow.md`, or a project-local path resolved relative to the config file.
3. **Resolve adapters** from `config.tracker.kind`, `config.vcs.kind`, `config.doc_system.kind`. For each family, look first for a project-local adapter at `.claude/cadence/adapters/<family>/<kind>.md`, else the shipped fallback at `${CLAUDE_PLUGIN_ROOT}/adapters/<family>/<kind>.md`. Load each adapter doc; it tells you which tools/commands to use.
4. **Note `config.execution`** — the project's execution skill and what it `owns`. This is what `/cadence:session end` must **verify, not repeat**.

Hook resolution, for any step named below: if `flow.hooks[<step>]` is set, load and follow that doc (passing it the step's Input, expecting its Output — the contracts are at `${CLAUDE_PLUGIN_ROOT}/flows/HOOKS.md`); else use the default here.

## `/cadence:session start`

1. **`session.start`** (default): read the session-state file (`config.session_state.file`) — Cadence's own local scratchpad, *not* the project's memory; determine the current milestone from the roadmap / tracker.
2. **`session.select_goal`** (default): using `flow.intake.priority_policy`, gather candidates via the tracker adapter (`list_open`) — plus the incident queue first if the flow has an incident lane — and choose one goal. Respect `flow.decision_rights.select_goal`:
   - `ai` → pick it and state the choice.
   - `ai-proposes` → present the top 1–3 and let the user choose.
   - `human` → present the board; the user decides; don't pre-empt.
3. **Frame the goal** in one sentence ("By end of session, `<id> <title>` is Done", or a concrete observable) and the **session type** per the flow's vocabulary. If it can't be said in one sentence, it's too big — offer to split (a planning action) first.
4. **Record it** via the tracker adapter (`comment`) as the anti-drift anchor.
5. **State the bug rule** for this session = `flow.intake.bug_triage` (`defer` / `file` / `preempt`), so mid-session bugs are handled per the flow, not on impulse.
6. **Hand off** to `config.execution.skill` for the actual work. Do not implement here. If `config.execution.skill` is `none`, proceed manually but remember `/cadence:session end` will then have to do the checkpoint itself.

## `/cadence:session end`

1. **Gate(s).** For the item's gated transition to Done, run each `gate.<name>.check` the flow attaches (default `gate.dod`: confirm `config.dod_gates` are met or explicitly N/A'd, honouring each gate's approver). If a gate fails, keep the item in progress with an honest note — do not advance it.
2. **Verify the checkpoint — don't repeat it.** If `config.execution.owns` includes `commit`/`docs`, confirm the execution skill already did them (VCS adapter `status` clean; last checkpoint references the item; any gotcha recorded via the doc adapter). Only run the checkpoint yourself (VCS adapter / `checkpoint` hook) if execution doesn't own it or left work uncommitted.
3. **Advance state** via the tracker adapter (`set_status` → Done) once gates pass and the checkpoint exists.
4. **Prune the session state** — run `session_state.prune`. The default rule is specified in `${CLAUDE_PLUGIN_ROOT}/flows/HOOKS.md`; in short, reconcile the scratchpad **against the tracker** (not against what the file claims) and drop anything the tracker already tells you, keeping only non-obvious traps.
5. **`session.end`** (default): write the pruned session state to `config.session_state.file` — the next goal plus any **cross-cutting** note the *tracker can't tell you* (not the per-item gotchas the execution skill already filed). Also drop the next goal into a tracker `comment` for visibility. This file is Cadence's own local, git-ignored scratchpad.

## When something doesn't resolve

Cadence is a chain of lookups — config → flow → adapters → hooks → tracker — and a stranger's project will break that chain in ways yours never does. The rule at every link is the same one that governs init: **surface the gap, don't fill it by inference.** A wrong guess here is worse than a stop, because it produces confident work against the wrong tool, the wrong process, or another project's conventions.

- **No config** → route to `/cadence:init` and stop. Don't offer to work without one.
- **`config.flow` names a file that isn't there** → stop. Name the missing path and offer either to re-point `flow:` at a shipped preset or to re-run init. Never silently substitute a preset: the flow *is* the process, and picking one for the user changes what the session does.
- **An adapter `kind` resolves to nothing** (no project-local adapter, no shipped fallback) → stop and route to `/cadence:init`, which generates it. This is the documented resolution error in `${CLAUDE_PLUGIN_ROOT}/adapters/ADAPTERS.md`.
- **A tracker is configured but unreachable** (MCP disconnected, auth expired) → say so plainly and stop. Do not fall back to the `markdown` tracker — a second, empty backlog looks like a working system and quietly forks the project's state.
- **A hook doc named in `flow.hooks` is missing** → report which hook and use the built-in default for that step, saying that you did. A flow author who pointed at a file they haven't written yet is better served by a working session and a warning than by a hard stop.
- **The tracker resolves but returns no open items** → this is not an error. Say the backlog is empty for the current milestone and offer `/cadence:plan`.

## Notes

- **Honour decision rights.** Never auto-decide a step the flow marks `human` (e.g. committing sprint scope, releasing).
- **Never repeat execution-owned work.** The `config.execution.owns` contract is the seam that keeps `/cadence:session` and the execution skill from duplicating commit/doc steps.
- **Stay fast.** ~5 minutes each end. The value is the goal in and the verified close out, not ceremony.
- **Delegate the grunt work.** Batchy adapter reads/writes (scanning the tracker via `list_open`, updating many items) can go to the `mechanical` subagent, spawned per the calling convention in `${CLAUDE_PLUGIN_ROOT}/adapters/ADAPTERS.md` (pass `config.models.mechanical` as a model override when it isn't `haiku`). The goal *decision* and gate *judgment* stay on the session model.
- **Session state is Cadence's own local file.** Read and write only `config.session_state.file` (git-ignored). Never read, write, or depend on the project's own memory (`CLAUDE.md`, agent `MEMORY.md`), and never reach outside `.claude/cadence/`.
- If the config or flow is missing or incoherent, stop and route the user to `/cadence:init`.
