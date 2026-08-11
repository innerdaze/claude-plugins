# Cadence

*A configurable project-management methodology, as a plugin.*

Cadence gives an AI-assisted project a **spine**: a vision and roadmap, broken into epics and tickets, worked in bounded **sessions** that each have one concrete goal — so "what do I do now?" always has a better answer than "fix more bugs." It carries the *method* and adapts to *your* tools and *your* team's process, rather than forcing one workflow.

> Status: **early** (`0.1.0`). The four skills and three preset flows are implemented; `team-sprints` and `live-oncall` depend on tracker capabilities not every adapter provides, and the ceremony layer is documented but not yet invokable — see `flows/CEREMONIES.md`.

## The idea in one picture

Cadence reads **two layers** of per-project configuration and drives the same skills against both:

- **Bindings** — *where and with what* you work: issue tracker, VCS, doc system, execution skill. Resolved through **adapters**. Change these → different toolchain.
- **Flow** — *how* you work: solo vs team, pre-release vs live; the states, gates, cadence, priority policy, and decision rights. Resolved through a **flow spec**. Change this → different process.

Neither is hardcoded. A solo builder on Linear + git and a live-product team on Jira + GitHub run the *same skills*, configured differently.

## What's in the box

- **Commands** — `/cadence:init` (setup), `/cadence:session start|end` (a work session), `/cadence:plan` (break a milestone into work), `/cadence:roadmap` (vision & roadmap), `/cadence:doctor` (check your setup; read-only). Each is backed by a skill (`cadence-init`, `cadence-session`, …) that Claude can also engage on its own when you just say "let's wrap up the session." *(Cadence does not ship a ticket-execution skill or a commit skill — it integrates with yours.)*
- **Flows** — three shipped presets: `solo-greenfield`, `team-sprints`, `live-oncall`. Fork one, or author your own.
- **Adapters** — the plugin ships the **contracts** plus three zero-dependency fallbacks: `markdown` (tracker), `git` (VCS), `none` (docs). Adapters for real tools — Linear, GitHub, Jira, whatever you use — are **generated into your project by `/cadence:init`** against the interface that tool actually exposes, because those interfaces vary per install. Cadence assumes no environment.
- **Hooks** — a named extension surface (`HOOKS.md`) so a custom flow can override any step with your own authored instructions. This is what makes Cadence a platform, not three canned workflows.

## Configurable, three ways

1. **Pick a preset** and go.
2. **Override axes** — copy a preset flow and change values (cadence, priority policy, gates).
3. **Author stages** — point any hook at your own instruction doc; the skill runs it in place of the default. See `HOOKS.md`.

## Quick start

Install the plugin:

```
/plugin marketplace add innerdaze/claude-plugins
/plugin install cadence@claude-plugins
```

Then, in your project:

```
/cadence:init
```

It detects your conventions (tracker, VCS, doc system, an existing execution skill), asks you to confirm them, helps you pick or author a flow (including your Definition of Done), writes the config, and scaffolds your vision/roadmap docs.

## Docs

- `flows/FLOW-SPEC.md` — the flow-spec schema: every key, its type, and which skill reads it.
- `config.example.md` — the bindings config, annotated.
- `flows/solo-greenfield.flow.md` — a preset; a worked instance of the schema.
- `flows/HOOKS.md` — the hook surface and each hook's contract.
- `flows/CEREMONIES.md` — ceremony defaults (documented; not yet invokable).

## Contributing and bugs

Issues and pull requests: <https://github.com/innerdaze/claude-plugins/issues>.

The contracts — `adapters/ADAPTERS.md`, `flows/HOOKS.md`, `flows/FLOW-SPEC.md` — are treated as public API. Renaming a hook, changing its Input/Output, removing an adapter operation, or changing a config key's meaning is a breaking change. See `CONTRIBUTING.md` at the repository root before proposing one.

## License

Apache-2.0 — see `LICENSE`. Copyright 2026 Lee Driscoll.
