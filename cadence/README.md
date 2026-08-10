# Cadence

*A configurable project-management methodology, as a plugin.*

Cadence gives an AI-assisted project a **spine**: a vision and roadmap, broken into epics and tickets, worked in bounded **sessions** that each have one concrete goal — so "what do I do now?" always has a better answer than "fix more bugs." It carries the *method* and adapts to *your* tools and *your* team's process, rather than forcing one workflow.

> Status: **early / work in progress** (`0.1.0`). The architecture is settled (see `DESIGN.md`); skills are being built against it.

## The idea in one picture

Cadence reads **two layers** of per-project configuration and drives the same skills against both:

- **Bindings** — *where and with what* you work: issue tracker, VCS, doc system, execution skill. Resolved through **adapters**. Change these → different toolchain.
- **Flow** — *how* you work: solo vs team, pre-release vs live; the states, gates, cadence, priority policy, and decision rights. Resolved through a **flow spec**. Change this → different process.

Neither is hardcoded. A solo builder on Linear + git and a live-product team on Jira + GitHub run the *same skills*, configured differently.

## What's in the box

- **Skills** — `/cadence init` (setup), `/session` (start/end a work session), `/plan` (break a milestone into work), `/roadmap` (vision & roadmap). *(Cadence does not ship a ticket-execution skill or a commit skill — it integrates with yours.)*
- **Flows** — three shipped presets: `solo-greenfield`, `team-sprints`, `live-oncall`. Fork one, or author your own.
- **Adapters** — trackers (Linear, GitHub, markdown), VCS (git, Diversion), doc systems (domains, none). Add more against the documented contracts.
- **Hooks** — a named extension surface (`HOOKS.md`) so a custom flow can override any step with your own authored instructions. This is what makes Cadence a platform, not three canned workflows.

## Configurable, three ways

1. **Pick a preset** and go.
2. **Override axes** — copy a preset flow and change values (cadence, priority policy, gates).
3. **Author stages** — point any hook at your own instruction doc; the skill runs it in place of the default. See `HOOKS.md`.

## Quick start

Install the plugin, then in your project run:

```
/cadence init
```

It detects your conventions (tracker, VCS, doc system, an existing execution skill), asks you to confirm them, helps you pick or author a flow (including your Definition of Done), writes the config, and scaffolds your vision/roadmap docs.

## Docs

- `DESIGN.md` — architecture & rationale (the spec).
- `config.example.md` — the bindings config, annotated.
- `flows/solo-greenfield.flow.md` — a preset, and the flow-spec schema by example.
- `flows/HOOKS.md` — the hook surface and each hook's contract.

## License

Apache-2.0 (recommended for a platform others build on; change before first publish if you prefer MIT).

---

*Author: Lee — complete author/repository/homepage fields before publishing.*
