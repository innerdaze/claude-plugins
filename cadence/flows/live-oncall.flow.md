# Flow: Live Product / On-call

*A shipped Cadence preset. A team shipping to real users: **incidents preempt the roadmap**, releases are **gated and human-approved**, and anything customer-facing is low-autonomy. Demonstrates the schema at its most constrained. Schema: `FLOW-SPEC.md`.*

> **The most demanding preset — read this before adopting it.** It needs a
> tracker that supports `severity` (for `customer-bug-by-severity`) and `cycle`
> (for `committed-sprint`); unsupported tokens are skipped with a note. Its
> `release_pipeline` and its ceremonies are **declared but not yet invokable** —
> no skill walks a release pipeline or runs an incident review today. Adopt this
> flow for its incident lane, its gates, and its decision rights; do not expect
> Cadence to drive your release.

```yaml
meta:
  name: live-oncall
  summary: Shipping to real users. Incidents interrupt the roadmap; releases are human-approved.
  cadence_version: "0.4"
  autonomy: low              # customer-facing decisions stay with humans

hierarchy:
  levels: [milestone, epic, story, task]
  first_class:
    incident: above-all      # incidents outrank the normal hierarchy

states:
  lanes: [Backlog, Sprint Backlog, In Progress, In Review, Done]
  roles:
    backlog:   Backlog
    committed: Sprint Backlog
    active:    In Progress
    review:    In Review
    done:      Done
  incident_lanes: [Triage, Mitigating, Resolved, Postmortem]
  gated_transitions:
    "Backlog -> Sprint Backlog":     []
    "Sprint Backlog -> In Progress": []
    "In Progress -> In Review":      []
    "In Review -> Done":        [gate.dod, gate.code_review, gate.regression]
    # the incident lane's own path — declared so gate.postmortem is reachable
    "Triage -> Mitigating":     []
    "Mitigating -> Resolved":   []
    "Resolved -> Postmortem":   [gate.postmortem]
  release_pipeline: [gate.changelog, gate.release_approval]   # declared; not yet walked

gates:
  dod:              { approver: ai-proposes, checks: [tests, docs] }
  code_review:      { approver: human,       checks: [peer-approved] }
  regression:       { approver: ai-proposes, checks: [no-regression, monitoring-in-place] }
  changelog:        { approver: ai,          checks: [changelog-entry] }
  release_approval: { approver: human }
  postmortem:       { approver: human,       checks: [postmortem-written] }

cadence:
  model: sprint
  cycle_length: "2 weeks"
  ceremonies: [planning, standup, review, retro, incident-review]   # not yet invokable

intake:
  new_work: incident-first
  bug_triage: preempt        # a customer-impacting bug interrupts the roadmap
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
  goal: the highest-priority item — an active incident if one exists, else the committed cycle

hooks: {}
```

## What this preset demonstrates

- **A lane above the hierarchy.** `first_class.incident` plus `incident_lanes` and the `preempt` bug rule are what flip solo's "defer the bug" into "drop the roadmap." `/cadence:session start` consults the incident lanes first, so the same start ritual behaves like on-call triage here and like roadmap work under the solo preset — one skill, driven entirely by the flow.
- **More gates, more human sign-off.** Regression, changelog, and a human-approved release encode the reality that mistakes now reach customers.
- **Declared ≠ automated.** `release_pipeline` and the ceremonies are part of the flow's description of your process, and Cadence will not pretend to run them. That honesty is deliberate: a plugin that half-runs a release is worse than one that doesn't.
