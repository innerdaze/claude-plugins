# Flow: Team / Sprints

*A shipped Cadence preset. A team working in fixed sprints: the skill **prepares and records**, humans **decide scope**. Mixed autonomy. Demonstrates the flow schema at a team posture — different hierarchy names, sprint cadence with ceremonies, a human commit gate, and a code-review gate. Fork to customize.*

```yaml
meta:
  name: team-sprints
  summary: A team on fixed sprints. Skill proposes + records; the team commits scope at planning.
  autonomy: mixed            # high | mixed | low

hierarchy:
  levels: [milestone, epic, story, task]   # note: renamed vs solo's ticket — the hierarchy is declared, not fixed
  spikes: allowed

states:
  lanes: [Backlog, Sprint Backlog, In Progress, In Review, Done]
  wip_limit: per-person      # sprints bound WIP; a flow may set a number
  gated_transitions:
    "In Review -> Done": [gate.dod, gate.code_review]

gates:
  dod:
    approver: ai-proposes    # the skill checks and recommends; a human accepts
    checks: [tests, docs]
  code_review:
    approver: human          # a peer must approve — never auto-cleared
    checks: [peer-approved]

cadence:
  model: sprint
  sprint_length: "2 weeks"   # adjust to taste
  ceremonies: [planning, standup, review, retro]   # the plugin prepares inputs + captures outcomes for each

intake:
  new_work: sprint-driven    # the top of the committed sprint, not the raw roadmap
  bug_triage: file           # file to backlog; triaged into a sprint at planning unless it blocks committed work
  priority_policy:
    - blocker-for-current-story
    - committed-sprint
    - backlog-by-rank

decision_rights:
  select_goal:    ai-proposes  # skill suggests today's item; the dev confirms
  plan_breakdown: ai-proposes
  commit_scope:   human        # the TEAM commits the sprint at planning — the skill never decides scope
  release:        ai-proposes

session:
  goal: one story/task from the committed sprint
  start: load memory -> show committed sprint items -> propose the top one -> the dev confirms -> hand to execution skill
  end: run gate.dod + gate.code_review -> verify (not repeat) the checkpoint -> update the board -> set next

hooks: {}     # override any step via HOOKS.md; e.g. ceremony.planning.prepare for your team's planning-pack format
```

## What this preset demonstrates

- **Hierarchy is declared, not fixed** (`story`/`task` instead of `ticket`).
- **Ceremonies are first-class.** `/cadence:plan` under this flow *is* sprint planning — it proposes a sprint and, because `commit_scope: human`, produces a planning pack and defers the actual commitment to the team. `ceremony.*.prepare`/`.capture` hooks (defaults, overridable) drive standup/review/retro support.
- **Human gates can't be auto-cleared.** `code_review` needs a person; the skill won't advance a story past it on its own.
