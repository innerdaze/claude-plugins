# Feature Process — templates

*Generic, tool-agnostic templates Cadence scaffolds into a project. Wherever this says "your tracker / VCS / docs," the actual mechanism comes from the project's config + flow. The hierarchy names (milestone / epic / ticket) are the defaults; a flow may rename them.*

## Hierarchy

```
MILESTONE  → a roadmap milestone with a goal + exit criteria
  └─ EPIC   → one coherent feature/system slice
     └─ TICKET → one shippable unit of work (~0.5–2 sessions)
        └─ (optional) sub-task
```

Rules (defaults; a flow may adjust): every ticket belongs to an epic; every epic to a milestone; bugs may attach to the epic they regressed or a standing `Maintenance` epic. Labels should mirror the project's doc/context taxonomy so the execution skill can load the right context deterministically.

## Epic template

```markdown
## Epic: <name>

**Milestone:** <milestone>
**Outcome:** <the one capability this delivers, one sentence>
**Why now:** <what it unblocks or de-risks>

### Story
<2–4 sentences: what changes for the user / what the system gains. Experience, not implementation.>

### Acceptance criteria (epic-level)
- [ ] <observable capability>
- [ ] <the "you can now demo X" statement>

### Context/domains touched
<labels the execution skill should load>

### Tickets
<smallest set that delivers the outcome, incl. the standard tickets below>

### Definition of Done (epic)
- [ ] All member tickets Done.
- [ ] Demonstrable end-to-end.
- [ ] Every flow gate that applies is satisfied (see the flow's `gates`).
- [ ] Cross-cutting concerns handled or scheduled (see standard tickets).
- [ ] Checkpointed via the project's VCS, referencing the epic.

### Out of scope
<explicit cuts>
```

**Standard tickets to create during planning** (adapt to the flow's gates):
- **A "cross-cutting requirement" ticket per gate the flow demands but the work doesn't do inline** — e.g. a multiplayer/replication ticket, a security-review ticket, an accessibility pass. This is how a project-specific quality bar (a `dod_gate`) becomes tracked work instead of an afterthought. It may be scheduled to a later milestone but exists from planning.
- **An "integration + verify + docs" ticket** — wire the pieces together, run the epic DoD, update docs, checkpoint. Prevents "all tickets done but nothing works together."

## Ticket template

```markdown
**Epic:** <epic>
**Type:** feature | bug | tech-debt | spike | chore
**Context:** <labels the execution skill should load>

### What
<one paragraph; concrete enough that "done" is unambiguous>

### Acceptance criteria
- [ ] <testable statement>

### Definition of Done (ticket)
- [ ] Meets acceptance criteria.
- [ ] Satisfies the flow's ticket-level gates (from `config.dod_gates`), or explicit N/A + reason for each.
- [ ] Checkpointed via the project's VCS, referencing this ticket.
```

## Spike template

```markdown
**Type:** spike
**Timebox:** <n sessions — stop at the box; a partial answer is an answer>

### The question
<one question, answerable yes/no/with-caveats>

### Scope / Not in scope
<what to try; what's explicitly excluded>

### Deliverable
A written verdict + a recommendation + a decision recorded in the roadmap. Throwaway code is discarded or flagged behind a toggle.
```

## On the Definition of Done

The DoD is **configured, not fixed.** `config.dod_gates` lists the gates that apply (e.g. `tests`, `docs` universally; `mp-safe`, `persistence`, `accessibility`, `changelog` per project). Universal defaults + project additions + a "define your own" option are chosen at `/cadence init`. The point is that quality bars can't be skipped silently: an item either meets a gate or records an explicit, reasoned N/A.
