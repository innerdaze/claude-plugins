# Cadence Hooks — the extension API

*This is the public contract that makes level-3 custom flows possible. A **hook** is a named seam in a skill's execution where the default behaviour can be replaced by your own authored instructions. This file is a **versioned interface** — changing a hook's name or contract is a breaking change.*

## How hooks work

Every skill (`/cadence:session`, `/cadence:plan`, …) runs as a sequence of steps. At each step it looks up the corresponding hook in the active flow spec:

```yaml
# in a flow spec
hooks:
  session.select_goal: ./hooks/select_goal.md
  gate.dod:            ./hooks/dod.md
```

- **Unset** → the skill uses the built-in default for that hook (usually the behaviour baked into the preset).
- **Set** → the skill loads your instruction doc and follows it *in place of* the default, passing it the hook's declared **Input** and expecting its declared **Output**.

A hook doc is plain Markdown instructions. It receives a context block (the Input) and must end by producing the Output in the specified shape, so the skill can act on it deterministically. Think of it as "you write this one step; Cadence wires it in."

## Contract conventions

- **Input** is what the skill guarantees to hand the hook (already-resolved data — the skill has done tracker/VCS reads for you).
- **Output** is what the hook must return. Keep it to the declared fields; extra prose is fine as `notes`.
- **Approver** (on gates and decisions): `ai` = the hook/skill may decide autonomously · `ai-proposes` = produce a recommendation for a human to accept · `human` = stop and require explicit human sign-off. A hook must honour the approver level the flow declares.
- **Purity** — hooks decide and describe; the *skill* performs side-effects (creating tickets, committing) through adapters. A hook returns "create these three tickets," it doesn't call the tracker itself.

## The hook catalog

**Every hook names the skill step that fires it.** A hook with no firing site is
a defect, not a feature — it is a promise of extensibility that silently does
nothing. Where a hook is catalogued but not yet wired, it says so explicitly, and
the validator holds that line.

### Session

**`session.start`** — fires at the top of `/cadence:session start`, after config + session state are loaded.
*Fired by:* `cadence-session`, start step 1.
Input: `{config, flow, session_state, current_milestone}` → Output: `{session_frame}` (what to show the user; any setup notes).

**`session.select_goal`** — chooses the session's one goal. The heart of how flows differ.
*Fired by:* `cadence-session`, start step 2.
Input: `{backlog, cycle, incident_queue, priority_policy, roadmap}` → Output: `{goal_item, rationale, session_type}`.
Defaults: *solo-greenfield* → next roadmap ticket; *team-sprints* → top committed cycle item; *live-oncall* → highest incident, else cycle, else roadmap.

**`session.end`** — the wrap sequence.
*Fired by:* `cadence-session`, end step 6.
Input: `{active_item, execution_owns, dod_result}` → Output: `{ordered close actions}`. Must *verify* work the execution skill owns rather than repeat it — except where `execution.skill` is `none`, in which case there is nothing to verify and the session performs the checkpoint itself.

**`session_state.prune`** — fires at `/cadence:session end`, before session state is written. Keeps the local scratchpad from silently becoming a stale second copy of the backlog.
*Fired by:* `cadence-session`, end step 5.
Input: `{session_state, tracker}` → Output: `{pruned_session_state}`.
Default (all presets): check each entry's item state via the **tracker adapter** — never from what the file itself claims — then delete: entries whose item is closed (unless a *non-obvious trap* survives — the shipped work deliberately departs from the ticket text and restoring it would reintroduce a bug), notes that merely restate their item's title, cross-references within the file, and bare item IDs carrying no note (a list of IDs is a tracker query, not a memory). Flows may tune how aggressively this runs by overriding the hook. The file's schema is in `${CLAUDE_PLUGIN_ROOT}/adapters/ADAPTERS.md`.

### Intake & triage

**`intake.classify`** — a new work item arrives mid-session and its type/severity/lane must be decided.
*Fired by:* `cadence-session`, on any new item raised during a session.
Input: `{raw_item}` → Output: `{type, severity, lane}`.

**`intake.prioritize`** — order a queue of candidates.
*Fired by:* `cadence-session`, start step 2, when `priority_policy` yields more than one candidate.
Input: `{queue, priority_policy}` → Output: `{ordered_queue}`.

**`bug.triage`** — a bug is found *mid-session*. The rule that flips solo↔live.
*Fired by:* `cadence-session`, whenever a bug surfaces while a session is open.
Input: `{bug, current_goal, flow}` → Output: `{decision: defer | file | preempt, target}`.
Defaults: *solo* → `defer` (file it, keep going); *live* → `preempt` if customer-impacting.
This hook is the difference between a bug rule that is *stated* and one that is *applied* — the flow's `intake.bug_triage` value is its default, not a substitute for firing it.

### Planning

**`plan.breakdown`** — turn a milestone into the levels below it.
*Fired by:* `cadence-plan`, step 2.
Input: `{milestone, templates, tracker_shape}` → Output: `{proposed_items}` (not yet created — the skill creates them via the tracker adapter, respecting decision rights).

**`plan.estimate`** *(optional)* — attach estimates/sizing.
*Fired by:* `cadence-plan`, step 3, when the flow uses estimates.
Input: `{items}` → Output: `{items_with_estimates}`.

**`plan.commit_scope`** — decide what actually enters a cycle.
*Fired by:* `cadence-plan`, step 4.
Input: `{proposal, decision_rights}` → Output: `{committed_set}` **or** `{defer_to: "planning ceremony"}` when the approver is `human` — in which case the skill writes a planning pack for the meeting rather than deciding scope.

### Roadmap

**`roadmap.milestone_progress`** — decide whether a milestone's exit criteria have advanced, and how to say so.
*Fired by:* `cadence-roadmap`, Mode C.
Input: `{milestone, open_items, closed_items, exit_criteria}` → Output: `{progress_note, met_criteria, milestone_complete}`.
Vision drafting deliberately has **no** hook: Principle 3 reserves it for the human, and a hook there would invite automating the one thing the design says not to automate.

### Gates

**`gate.<name>.check`** — evaluate a gate on a gated transition. Names are flow-defined: `dod`, `code_review`, `qa`, `release_approval`, ….
*Fired by:* `cadence-session`, end step 1, for each gate on the transition being made.
Input: `{item, context, checks}` → Output: `{result: pass | fail | needs-human, notes}`.
`gate.dod` default: verify the **effective DoD** is satisfied or explicitly N/A'd. The effective DoD is `flow.gates.dod.checks` ∪ `config.dod_gates` — a union, so a project may raise the bar above the flow's baseline and can never silently lower it. (`dod_gates` is a **config** key; `checks` is the flow's.)

### Ceremonies — ⚠️ deferred, not yet invokable

> **No skill currently fires any `ceremony.*` hook.** The contracts and the
> default behaviours in `CEREMONIES.md` are specified so the shape is settled and
> a flow can declare ceremonies without lying about them — but there is no
> command that runs a standup, review, retro, or incident review. Planning is the
> exception, and only partly: `/cadence:plan` writes a planning pack for a human
> meeting when `decision_rights.commit_scope` is `human`.
>
> Setting one of these hooks in a flow is legal and has no effect today.

**`ceremony.<name>.prepare`** — produce the inputs a human ceremony needs.
*Fired by:* **nothing yet — deferred.**
Input: `{board, history, window}` → Output: `{prep_artifact}`.

**`ceremony.<name>.capture`** — record a ceremony's outcome back into the tracker.
*Fired by:* **nothing yet — deferred.**
Input: `{decisions}` → Output: `{recorded changes}`.

### Transitions & release

**`transition.<from>_to_<to>`** — side-effects/guards when an item changes state. Lane names are used verbatim, including spaces: `transition.Backlog_to_In Progress`.
*Fired by:* `cadence-session`, on every status change it makes (start's move to `roles.active`, end's move to `roles.done`).
Input: `{item, from, to}` → Output: `{side_effects}`.

**`checkpoint`** — how work is committed. Delegates to the VCS adapter; the hook can add changelog/version steps.
*Fired by:* `cadence-session`, end step 3.
Input: `{changes, item_ref, vcs_adapter}` → Output: `{commit actions}`.

**`release`** — a gated release (mostly for live-product flows).
*Fired by:* **nothing yet — deferred.** `states.release_pipeline` is declarable but no skill walks it.
Input: `{candidate, gates, approver}` → Output: `{release plan}` or `{blocked_by}`.

## Authoring a hook

1. In your flow spec, add `hooks: { <hook.name>: ./hooks/<file>.md }`.
2. Write `<file>.md` as instructions that consume the declared **Input** and end by emitting the declared **Output**.
3. Honour the approver level — never auto-decide something the flow marks `human`.
4. Keep side-effects in the skill: describe the action, don't perform it.

## Coherence rules

Checked mechanically by `tools/validate_cadence.py` for the shipped flows, and by
`/cadence:doctor` for a project's own flow. `/cadence:init` applies them before
writing.

- Every `hooks:` entry names a real hook from this catalog — literal, or matching
  a documented wildcard (`gate.<name>.check`, `ceremony.<name>.prepare|capture`,
  `transition.<from>_to_<to>`) — and points at a readable doc.
- Every hook in this catalog has a *Fired by* line naming a real skill step, or
  is explicitly marked deferred. A hook nothing fires is a defect.
- Every gate named by a `gated_transitions` entry or by `release_pipeline` exists
  in `gates:`.
- Both lanes of every `"<from> -> <to>"` transition key are members of
  `states.lanes`, and every `states.roles` value is a member of `states.lanes`.
- **Lane reachability**: a lane on the right-hand side of a gated transition that
  nothing declared reaches is reported. This is how a gate attached to a
  transition that never occurs gets caught, rather than quietly never firing.
- A step whose `decision_rights` is `human` must not have a hook that returns an
  autonomous decision.
- A ceremony in `cadence.ceremonies` has a section in `CEREMONIES.md` — and, for
  now, is understood to be non-invokable.

## Versioning

Hook names and contracts are public API. Additive changes (new optional hooks,
new optional Output fields) are minor; renames or Input/Output changes are
breaking and bump the major version.

Every flow declares the contract version it targets in `meta.cadence_version`
(see `FLOW-SPEC.md`). `/cadence:doctor` compares that against the installed
plugin and reports a mismatch — which is what makes an upgrade detectable rather
than a source of silent misbehaviour.
