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

### Session

**`session.start`** — fires at the top of `/cadence:session start`, after config + session state are loaded.
Input: `{config, flow, session_state, current_milestone}` → Output: `{session_frame}` (what to show the user; any setup notes).

**`session.select_goal`** — chooses the session's one goal. The heart of how flows differ.
Input: `{backlog, sprint_or_cycle, incident_queue, priority_policy, roadmap}` → Output: `{goal_item, rationale, session_type}`.
Defaults: *solo-greenfield* → next roadmap ticket; *team-sprints* → top committed sprint item; *live-oncall* → highest incident, else sprint, else roadmap.

**`session.end`** — the wrap sequence.
Input: `{active_item, execution_owns, dod_result}` → Output: `{ordered close actions}` (e.g. verify-commit, set-status, next-goal). Must *verify* work the execution skill owns rather than repeat it.

**`session_state.prune`** — fires at `/cadence:session end`, before session state is written. Keeps the local scratchpad from silently becoming a stale second copy of the backlog.
Input: `{session_state, tracker}` → Output: `{pruned_session_state}`.
Default (all presets): check each entry's item state via the **tracker adapter** — never from what the file itself claims — then delete: entries whose item is closed (unless a *non-obvious trap* survives — the shipped work deliberately departs from the ticket text and restoring it would reintroduce a bug), notes that merely restate their item's title, cross-references within the file, and bare item IDs carrying no note (a list of IDs is a tracker query, not a memory). Flows may tune how aggressively this runs by overriding the hook.

### Intake & triage

**`intake.classify`** — a new work item arrives.
Input: `{raw_item}` → Output: `{type, severity, lane}`.

**`intake.prioritize`** — order a queue.
Input: `{queue, priority_policy}` → Output: `{ordered_queue}`.

**`bug.triage`** — a bug is found *mid-session*. The rule that flips solo↔live.
Input: `{bug, current_goal, flow}` → Output: `{decision: defer | file | preempt, target}`.
Defaults: *solo* → `defer` (file to Maintenance, keep going); *live* → `preempt` if customer-impacting.

### Planning

**`plan.breakdown`** — turn a milestone into epics/tickets.
Input: `{milestone, templates, tracker_shape}` → Output: `{proposed_items}` (not yet created — the skill creates them via the tracker adapter, respecting decision rights).

**`plan.estimate`** *(optional)* — attach estimates/sizing.
Input: `{items}` → Output: `{items_with_estimates}`.

**`plan.commit_scope`** — decide what actually enters a sprint/cycle.
Input: `{proposal, decision_rights}` → Output: `{committed_set}` **or** `{defer_to: "planning ceremony"}` when the approver is human.

### Gates

**`gate.<name>.check`** — evaluate a gate on a gated transition. Names are flow-defined: `dod`, `design_review`, `qa`, `release_approval`, ….
Input: `{item, context, checks}` → Output: `{result: pass | fail | needs-human, notes}`.
`gate.dod` default: verify the flow's `dod_gates` (tests, docs, + project gates) are satisfied or explicitly N/A'd.

### Ceremonies

**`ceremony.<name>.prepare`** — produce the inputs a human ceremony needs (planning pack, standup summary, review notes, retro prompts).
Input: `{board, history, window}` → Output: `{prep_artifact}`.

**`ceremony.<name>.capture`** — record a ceremony's outcome back into the tracker/memory.
Input: `{decisions}` → Output: `{recorded changes}`.

The **default** behaviours for planning / standup / review / retro / incident-review are spelled out in `CEREMONIES.md`; override them per flow by pointing these hooks at your own docs.

### Transitions & release

**`transition.<from>_to_<to>`** — side-effects/guards when an item changes state.
Input: `{item, from, to}` → Output: `{side_effects}`.

**`checkpoint`** — how work is committed. Delegates to the VCS adapter; the hook can add changelog/version steps.
Input: `{changes, ticket_ref, vcs_adapter}` → Output: `{commit actions}`.

**`release`** — a gated release (mostly for live-product flows).
Input: `{candidate, gates, approver}` → Output: `{release plan}` or `{blocked_by}`.

## Authoring a hook

1. In your flow spec, add `hooks: { <hook.name>: ./hooks/<file>.md }`.
2. Write `<file>.md` as instructions that consume the declared **Input** and end by emitting the declared **Output**.
3. Honour the approver level — never auto-decide something the flow marks `human`.
4. Keep side-effects in the skill: describe the action, don't perform it.

## Coherence rules (checked at `/cadence:init` and on flow edits)

- A step whose `decision_rights` is `human` must not have a hook that returns an autonomous decision.
- Every `gated_transition` must reference a gate that exists.
- Every `hooks:` entry must name a real hook from this catalog and point at a readable doc.
- A ceremony referenced in `cadence.ceremonies` should have at least a `.prepare` default or hook.

## Versioning

Hook names and contracts are public API. Additive changes (new optional hooks, new optional Output fields) are minor; renames or Input/Output changes are breaking and bump the major version. Flows declare the Cadence version they target.
