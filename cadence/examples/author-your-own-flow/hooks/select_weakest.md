# Hook: `session.select_goal` — "weakest claim first"

*Authored override for the `manuscript` flow. Implements the `session.select_goal` contract from `flows/HOOKS.md`.*

**Input** (provided by `/session`): `{backlog, sprint_or_cycle, incident_queue, priority_policy, roadmap}`.
For this flow, `backlog` is the set of claims and sections; there is no sprint or incident queue.

**Do:**
1. Take the claims currently in state `Needs-Support`.
2. Score each by support strength, weakest first:
   - `none` — no source recorded,
   - `weak` — a single non-authoritative source,
   - `contested` — sources disagree and the claim doesn't acknowledge it.
3. The weakest such claim is the goal. If every claim is at least `Supported`, fall back to the next `Drafting` section that still has open questions; failing that, the next `Outline` item.

**Output:** `{goal_item, rationale, session_type}` —
- `goal_item`: the chosen claim (or section),
- `rationale`: one line on why it's the weakest link,
- `session_type`: `research` for a claim, `draft` for a section.

**Approver note:** `decision_rights.select_goal` is `ai-proposes`, so present the pick to the author for a nod rather than starting unilaterally.
