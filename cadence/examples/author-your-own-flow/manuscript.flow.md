# Flow: Manuscript (worked example — author-your-own)

*A **custom** flow, not a shipped preset — the worked example for authoring your own. It runs Cadence for a **non-software** project: writing a long-form researched document (paper, report, book). It shows the flow-spec vocabulary bent to a new domain, plus two **level-3 authored hooks** (in `./hooks/`) that override behaviour the vocabulary can't express declaratively. Read `WALKTHROUGH.md` alongside this. To use it in a project: `flow: ./manuscript.flow.md`.*

```yaml
meta:
  name: manuscript
  summary: Writing a long-form researched document. Author-led; Cadence tracks claims and their support.
  cadence_version: "0.2"
  autonomy: mixed

hierarchy:
  levels: [work, section, claim]     # the piece → its sections → individual claims/arguments

states:
  lanes: [Outline, Drafting, Needs-Support, Supported, Reviewed, Final]
  roles:
    backlog: Outline                 # new claims start life as outline entries
    active:  Drafting
    review:  Reviewed
    done:    Final                   # note: NOT "Done" — the terminal lane is named by the flow
  gated_transitions:
    "Outline -> Drafting":     []
    "Drafting -> Needs-Support": []
    "Needs-Support -> Supported": []
    "Supported -> Reviewed":   [gate.citations]
    "Reviewed -> Final":       [gate.editorial]

gates:
  citations:
    approver: ai-proposes            # Cadence checks; the author accepts
    checks: [every-claim-cited]
  editorial:
    approver: human                  # the author's own read
    checks: [reads-aloud-cleanly, structure-holds]

cadence:
  model: continuous
  ceremonies: []

intake:
  new_work: weakest-claim-first
  bug_triage: file                   # a "bug" = a factual error or broken argument; file it as a claim in Needs-Support
  priority_policy:
    - unsupported-claim
    - section-with-open-questions
    - next-outline-item

decision_rights:
  select_goal:    ai-proposes
  plan_breakdown: ai-proposes
  commit_scope:   human              # the author owns the outline/scope
  release:        human              # publishing is the author's call

session:
  goal: bring one claim from Needs-Support to Supported (or draft one section)

# --- Level-3 authored hooks: override behaviour the vocabulary can't express ---
hooks:
  session.select_goal:  ./hooks/select_weakest.md
  gate.citations.check: ./hooks/citations.md
```

## What this example demonstrates

- **Cadence generalizes past software.** Hierarchy (`work/section/claim`), states (`Needs-Support`, `Supported`), and the "bug" concept (a broken argument) are all domain-specific — declared, not hardcoded.
- **Nothing assumes a lane called `Done`.** This flow's success terminal is `Final`, declared through `states.roles.done`. Skills ask for the *role*, so renaming the whole vocabulary costs nothing — which is the test of whether the design is really process-agnostic.
- **A novel priority policy.** `unsupported-claim` is not one of the documented tokens. That is legal — unknown tokens are interpreted as prose — and the validator warns, because a token nothing recognises silently does nothing. Here the authored `session.select_goal` hook is what gives it meaning.
- **Two real level-3 hooks.** `session.select_goal` and `gate.citations.check` are authored in `./hooks/`, each honouring its Input→Output contract from the plugin's `flows/HOOKS.md` — the escape hatch, end to end.
