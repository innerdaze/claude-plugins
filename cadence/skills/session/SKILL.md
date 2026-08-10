---
name: session
description: Start or end a bounded work session, interpreting this project's Cadence config and flow. `/session start` loads context, picks one goal per the flow's priority policy, and hands off to the project's execution skill. `/session end` runs the flow's gates, verifies (never repeats) the checkpoint, and sets the next goal. Environment- and process-agnostic. Use when the user runs /session, /session start, /session end, or asks to begin or wrap up a work session.
---

# /session — Cadence session interpreter

This skill assumes **nothing** about the environment or the process. It reads the project's **config** (bindings: tracker, VCS, docs, execution skill) and its **flow** (methodology: states, gates, cadence, priority, decision rights), and executes the session ritual by interpreting them. Where the flow sets a **hook**, run that instruction doc; otherwise use the default described here.

## Load order (do this first, every time)

1. **Locate & read the config.** If the repo has a `domains/` doc system, the config is `domains/PROJECT.md`; otherwise `.claude/cadence/config.md`. If neither exists, tell the user to run `/cadence init` and stop.
2. **Load the flow spec** named in `config.flow` — a shipped preset in the plugin's `flows/`, or a project-local path.
3. **Resolve adapters** from `config.tracker.kind`, `config.vcs.kind`, `config.doc_system.kind` (load each adapter doc; it tells you which tools/commands to use).
4. **Note `config.execution`** — the project's execution skill and what it `owns`. This is what `/session end` must **verify, not repeat**.

Hook resolution, for any step named below: if `flow.hooks[<step>]` is set, load and follow that doc (passing it the step's Input, expecting its Output — see `flows/HOOKS.md`); else use the default here.

## `/session start`

1. **`session.start`** (default): read memory; determine the current milestone from the roadmap / tracker.
2. **`session.select_goal`** (default): using `flow.intake.priority_policy`, gather candidates via the tracker adapter (`list_open`) — plus the incident queue first if the flow has an incident lane — and choose one goal. Respect `flow.decision_rights.select_goal`:
   - `ai` → pick it and state the choice.
   - `ai-proposes` → present the top 1–3 and let the user choose.
   - `human` → present the board; the user decides; don't pre-empt.
3. **Frame the goal** in one sentence ("By end of session, `<id> <title>` is Done", or a concrete observable) and the **session type** per the flow's vocabulary. If it can't be said in one sentence, it's too big — offer to split (a planning action) first.
4. **Record it** via the tracker adapter (`comment`) as the anti-drift anchor.
5. **State the bug rule** for this session = `flow.intake.bug_triage` (`defer` / `file` / `preempt`), so mid-session bugs are handled per the flow, not on impulse.
6. **Hand off** to `config.execution.skill` for the actual work. Do not implement here. If `config.execution.skill` is `none`, proceed manually but remember `/session end` will then have to do the checkpoint itself.

## `/session end`

1. **Gate(s).** For the item's gated transition to Done, run each `gate.<name>.check` the flow attaches (default `gate.dod`: confirm `config.dod_gates` are met or explicitly N/A'd, honouring each gate's approver). If a gate fails, keep the item in progress with an honest note — do not advance it.
2. **Verify the checkpoint — don't repeat it.** If `config.execution.owns` includes `commit`/`docs`, confirm the execution skill already did them (VCS adapter `status` clean; last checkpoint references the item; any gotcha recorded via the doc adapter). Only run the checkpoint yourself (VCS adapter / `checkpoint` hook) if execution doesn't own it or left work uncommitted.
3. **Advance state** via the tracker adapter (`set_status` → Done) once gates pass and the checkpoint exists.
4. **`session.end`** (default): set the next session's goal (one line, recorded via tracker `comment` or memory), and capture any **cross-cutting** decision to memory — not the per-item gotchas the execution skill already filed.

## Notes

- **Honour decision rights.** Never auto-decide a step the flow marks `human` (e.g. committing sprint scope, releasing).
- **Never repeat execution-owned work.** The `config.execution.owns` contract is the seam that keeps `/session` and the execution skill from duplicating commit/doc steps.
- **Stay fast.** ~5 minutes each end. The value is the goal in and the verified close out, not ceremony.
- **Delegate the grunt work.** Batchy adapter reads/writes (scanning the tracker via `list_open`, updating many items) can go to the `mechanical` subagent per `config.models.mechanical`; the goal *decision* and gate *judgment* stay on the session model.
- If the config or flow is missing or incoherent, stop and route the user to `/cadence init`.
