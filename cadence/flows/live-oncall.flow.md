# Flow: Live Product / On-call

*A shipped Cadence preset. A team shipping to real users: **incidents preempt the roadmap**, releases are **gated and human-approved**, and anything customer-facing is low-autonomy. Demonstrates the schema at its most constrained — an incident lane above the hierarchy, extra gates, and a `preempt` bug rule. Fork to customize.*

```yaml
meta:
  name: live-oncall
  summary: Shipping to real users. Incidents interrupt the roadmap; releases are human-approved.
  autonomy: low              # customer-facing decisions stay with humans

hierarchy:
  levels: [milestone, epic, story, task]
  spikes: allowed
  first_class:
    incident: above-all      # incidents outrank the normal hierarchy

states:
  lanes: [Backlog, Sprint Backlog, In Progress, In Review, Done]
  incident_lanes: [Triage, Mitigating, Resolved, Postmortem]
  gated_transitions:
    "In Review -> Done":      [gate.dod, gate.code_review, gate.regression]
    "Resolved -> Postmortem": [gate.postmortem]
  release_pipeline:           [gate.changelog, gate.release_approval]

gates:
  dod:              { approver: ai-proposes, checks: [tests, docs] }
  code_review:      { approver: human,       checks: [peer-approved] }
  regression:       { approver: ai-proposes, checks: [no-regression, monitoring-in-place] }
  changelog:        { approver: ai,          checks: [changelog-entry] }
  release_approval: { approver: human }       # a person signs off every release
  postmortem:       { approver: human,        checks: [postmortem-written] }

cadence:
  model: sprint
  ceremonies: [planning, standup, review, retro, incident-review]

intake:
  new_work: incident-first
  bug_triage: preempt        # a customer-impacting bug interrupts the roadmap and becomes the goal
  priority_policy:
    - active-incident
    - customer-bug-by-severity
    - committed-sprint
    - backlog-by-rank

decision_rights:
  select_goal:    ai-proposes
  plan_breakdown: ai-proposes
  commit_scope:   human
  release:        human       # releasing is never autonomous

session:
  goal: the highest-priority item — an active incident if one exists, else the committed sprint item
  start: check the incident queue FIRST -> if an incident is above threshold, that's the goal (open its lane) -> else the committed sprint
  end: run gate.dod + gate.code_review + gate.regression -> verify the checkpoint -> if this is a release, run the release pipeline (human-approved) -> update the board -> next

hooks: {}     # e.g. override bug.triage for your severity rubric, or ceremony.incident-review.capture for your postmortem template
```

## What this preset demonstrates

- **A lane above the hierarchy.** Incidents are first-class and preempt everything — the `bug.triage: preempt` rule and the incident-first priority policy are what flip solo's "defer the bug" into "drop the roadmap."
- **More gates, more human sign-off.** Regression, changelog, and a human-approved release pipeline encode the reality that mistakes now reach customers.
- **`/session start` consults the incident queue first**, so the same start ritual behaves like on-call triage here and like roadmap-work under the solo flow — one skill, driven entirely by the flow.
