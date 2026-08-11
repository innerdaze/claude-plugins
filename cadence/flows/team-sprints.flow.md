# Flow: Team / Sprints

*A shipped Cadence preset. A team working in fixed cycles: the skill **prepares and records**, humans **decide scope**. Demonstrates the schema at a team posture — renamed hierarchy levels, cycle cadence, a human commit gate, and a review lane that is actually reachable. Schema: `FLOW-SPEC.md`.*

> **This preset asks more of your tracker than the solo one.** `committed-sprint`
> in the priority policy needs a `cycle` field on items, and the shipped
> `markdown` fallback declares `cycle` unsupported — on that tracker the token is
> skipped and goal selection falls through to `backlog-by-rank`. Use a hosted
> tracker whose generated adapter supports cycles, or drop the token.
>
> **Ceremonies are declared but not yet invokable** — see `CEREMONIES.md`. The
> one with a real path today is planning: with `commit_scope: human`,
> `/cadence:plan` writes a planning pack for your meeting instead of deciding
> scope for you.

```yaml
meta:
  name: team-sprints
  summary: A team on fixed cycles. Skill proposes and records; the team commits scope.
  cadence_version: "0.4"
  autonomy: mixed

hierarchy:
  levels: [milestone, epic, story, task]   # the hierarchy is declared, not fixed

states:
  lanes: [Backlog, Sprint Backlog, In Progress, In Review, Done]
  roles:
    backlog:   Backlog
    committed: Sprint Backlog   # accepted into the cycle, not yet started
    active:    In Progress
    review:    In Review        # this flow DOES review, so the role is declared
    done:      Done
  wip_limit: per-person
  gated_transitions:
    "Backlog -> Sprint Backlog":     []   # the team committing scope at planning
    "Sprint Backlog -> In Progress": []
    "In Progress -> In Review":      []
    "In Review -> Done":             [gate.dod, gate.code_review]

gates:
  dod:
    approver: ai-proposes    # the skill checks and recommends; a human accepts
    checks: [tests, docs]
  code_review:
    approver: human          # a peer must approve — never auto-cleared
    checks: [peer-approved]

cadence:
  model: sprint
  cycle_length: "2 weeks"
  ceremonies: [planning, standup, review, retro]   # documented; not yet invokable

intake:
  new_work: cycle-driven
  bug_triage: file           # triaged into a cycle at planning unless it blocks committed work
  priority_policy:
    - blocker-for-current-ticket
    - committed-sprint
    - backlog-by-rank

decision_rights:
  select_goal:    ai-proposes  # skill suggests today's item; the dev confirms
  plan_breakdown: ai-proposes
  commit_scope:   human        # the TEAM commits the cycle — the skill never decides scope
  release:        ai-proposes

session:
  goal: one story or task from the committed cycle

hooks: {}
```

## What this preset demonstrates

- **Hierarchy is declared, not fixed** — `story`/`task` instead of `ticket`.
- **A reachable review lane.** This flow declares a `review` role *and* a transition into it, so `In Review` is somewhere items actually go — which is what makes `gate.code_review` meaningful rather than decorative. Declaring the gate without the transition would give you a checkpoint that never fires.
- **Human gates can't be auto-cleared.** `code_review` needs a person; the skill won't advance a story past it.
- **The skill never commits team scope.** `commit_scope: human` means `/cadence:plan` produces a planning pack and stops.
