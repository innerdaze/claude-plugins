---
name: cadence-init
description: Set up Cadence in a project. Detects the project's conventions (doc system, VCS, execution skill, issue tracker), confirms them, and GENERATES a project-local adapter for each non-fallback tool it finds; then helps you pick or author a flow (including your Definition of Done), writes the config, and scaffolds your vision/roadmap docs. Use when the user runs /cadence init, says "set up Cadence", "initialize Cadence", or wants to start using the methodology in a project.
---

# /cadence init — set up Cadence in a project

Produce: a **config** (bindings), a **flow** selection (methodology), any **project-local adapters** the environment needs, and the starter docs. The governing rule is **detect, then confirm — never assume.** Nothing is written until the user approves.

Cadence ships no integration for a specific external tool (see `adapters/ADAPTERS.md`). Where a project uses a real tracker/VCS/doc-system, init **generates a project-local adapter** tailored to it. The plugin's `flows/`, `templates/`, and the adapter **contracts** are the sources to read; the plugin itself is never modified.

If a Cadence config already exists, this is an **update**: read it first, propose changes, back it up before overwriting.

## Phase 1 — Detect the environment, and generate its adapters (propose → confirm)

Inspect the repo and connected tools, present findings as one summary the user confirms or corrects, and **for each non-fallback tool, generate a project-local adapter** at `.claude/cadence/adapters/<family>/<kind>.md` implementing that family's contract against what you actually find. Never assume a tool or its interface.

- **Doc system.** If `domains/` + `INDEX.md` exists → propose `doc_system: domains`, **generate `adapters/docs/domains.md`** implementing the doc-system contract against that INDEX (label→doc mapping), and set the config location to `domains/PROJECT.md`. Else if `docs/` → generate a `docs` adapter. Else → the shipped `none` fallback.
- **VCS.** Detect `.git` / `.diversion` / `.jj` / `.hg`. `git` → use the shipped `git` fallback. Anything else (e.g. `diversion`) → **inspect its CLI and generate `adapters/vcs/<kind>.md`** implementing the vcs contract against the tool's real commands, capturing only **tool-generic** gotchas; put **machine/workspace-specific** quirks in `config.vcs.gotchas`, not the adapter. Detect an existing commit skill to delegate to.
- **Execution skill.** Scan `.claude/skills/`, enabled plugins, and global skills for a ticket-execution skill (`work-on`, `implement`, `do-ticket`, …). **Propose the best candidate but ask the user to confirm** it's the right one, how it's invoked, and what it `owns` (implement/test/docs/commit) — this drives the verify-don't-repeat seam in `/session end`. If none, `execution.skill: none`.
- **Tracker.** Detect connected tracker MCPs. For one found → **inspect the tools/verbs it actually exposes and generate `adapters/trackers/<kind>.md`** implementing the tracker contract against those exact operations; collect its `mcp_namespace`, IDs, and `ticket_prefix` into config (namespaces differ per project). If none is connected → the shipped `markdown` fallback (no MCP needed).

Show the generated adapters + assembled bindings and get explicit confirmation. Adapters are stored **in the project**; the plugin is untouched.

## Phase 2 — Choose the flow (pick or author)

Offer two paths:

**A) Pick a preset**, then optionally override axes (level 1):
- `solo-greenfield` — one builder, pre-release; high autonomy, continuous flow, bugs deferred.
- `team-sprints` — sprint cadence + ceremonies; the skill proposes, the team commits scope; goals come from the committed sprint.
- `live-oncall` — an incident lane that preempts the roadmap; release/regression/changelog gates; releases human-approved.

Summarize each; let the user pick, then ask about tweaking any axis (cadence, priority policy, gates).

**B) Author a custom flow** — walk the flow-spec vocabulary (hierarchy, states, gates, cadence/ceremonies, intake/priority policy, decision rights, session definition). For any step the vocabulary can't express, author a **hook doc** (level 3) at the relevant hook from `flows/HOOKS.md`. Write to a project-local `./cadence/<name>.flow.md` (+ `hooks/*.md`).

**Definition of Done** (either path): present a multi-select menu, always ending in **"define your own"** — `tests` · `docs` · `no-warnings` · `multiplayer` · `persistence` · `accessibility` · `perf-budget` · `changelog` · `security-review` · *define your own…* The selection becomes `config.dod_gates`. Settle milestone mechanism, epic convention, and memory location as needed.

**Model tiers.** Set `config.models` — default `mechanical: haiku`, `reasoning: inherit`. If the user lacks the default cheap tier or prefers a different one, rebind it. This is what lets the skills delegate batchy mechanical work (adapter ops, scaffolding) to the cheap `mechanical` subagent while judgment stays on the session model.

## Phase 3 — Coherence check

Before writing, validate config + flow + adapters and **warn on any contradiction** (don't silently accept):
- No step whose decision right is `human` may have a hook that returns an autonomous decision.
- Every gated transition references a gate that exists.
- Every `hooks:` entry names a real hook from `HOOKS.md` and points at a readable doc.
- Every ceremony in `cadence.ceremonies` has at least a `.prepare` default or hook.
- **Every `config.<family>.kind` resolves** — to a project-local adapter just generated, or a shipped fallback. If not, generate or fall back before finishing.

## Phase 4 — Write the config

Write to the location chosen in Phase 1, per `config.example.md`. **Never write secrets or credentials.** For the `markdown` tracker, create its `path` directory. If updating, back up the prior config first.

## Phase 5 — Scaffold the docs

From the plugin's `templates/`, create any absent, pre-filled with the project name and chosen flow:
- `vision-and-roadmap.md` (always — the north star).
- Offer `feature-process.md` and `session-goals.md` as in-repo references.
Do not overwrite existing docs — only fill gaps.

## Phase 6 — Dry-run

Resolve config + flow + adapters and show what `/session start` would surface now (e.g. "current milestone: none yet; no open items — run `/plan`"). This proves the bindings, adapters, *and* process resolve before the user relies on them. Finish by naming the next moves: `/roadmap`, then `/plan`, then `/session start`.

## Notes

- **What init does NOT do:** create tickets (that's `/plan`) or implement anything. It configures, generates adapters, and scaffolds.
- **Idempotent:** safe to re-run; updates and backs up rather than clobbering. Re-running can regenerate an adapter if a tool's interface changed.
- **Zero-dependency default:** if nothing is detected, `markdown` + `git` + `none` + `solo-greenfield` is a complete, runnable setup with no external service and no generated adapters.
