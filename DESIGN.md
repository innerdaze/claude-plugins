# Methodology Plugin — Architecture & Init Design

*Working name: **Cadence** (placeholder — see Open Decisions). A portable plugin that carries the project-management methodology we built for MachineGame54 and adapts it to any project's tools **and** any team's process.*

---

## What it is

A **methodology engine**, not a toolchain and not a single opinionated workflow. It ships an invariant *skeleton* — vision → roadmap → epics → tickets → gates, worked in bounded sessions with cross-session state — and then reads two layers of project-specific configuration:

- **Bindings** — *where and with what* you work: issue tracker, VCS, doc system, execution skill. Resolved through **adapters**.
- **Flow** — *how* you work: the process posture (solo vs team, pre-release vs live), the states, the gates, the cadence, the priority policy, the decision rights. Resolved through a **flow spec**.

Change the bindings and the same skills drive a different toolchain. Change the flow and the same skills drive a different *process* — from a solo greenfield builder to a live-product team with on-call.

## Principles (the non-negotiables)

1. **Environment-agnostic.** No skill assumes Linear, Diversion, a `domains/` system, GitHub, or any MCP. Everything tool-specific comes from bindings/adapters. `/cadence:session` assumes *nothing*.
2. **Process-agnostic.** No skill hardcodes a workflow. Solo-continuous, team-sprints, kanban, live-incident-first are all *flows*, not code paths. The methodology skeleton is invariant; the policies inside it are configured.
3. **Decision-support scales inversely to autonomy.** The more people and the more live the product, the more the plugin shifts from *making* decisions to *preparing and recording* them. A solo greenfield dev lets the skill propose goals and break down epics; a team lets it prepare the planning pack and record what the meeting decided. **It never tries to run the meeting or override human prioritization.**
4. **It owns neither execution nor the commit.** No bundled "work-on-a-ticket" skill; no bundled VCS commit logic. Both are the project's, reached via bindings. **Session state is the one exception** (Layer 1) — the only part of the skeleton with no external tool behind it, so the plugin owns that file and nothing else; everything else it touches, it reaches through an adapter.
5. **Detect, then confirm — never assume.** Init inspects the repo and *proposes*; the user confirms or corrects. This holds for the **whole lifecycle, not just init**: a binding that is missing or unset when a skill needs it is a question for the user, never a gap to fill by inference — then offer to write the answer into config so the next session doesn't re-ask. ⚠️ The specific failure to guard is **cross-project substitution**. Skills are installed once and serve every project, so another project's config is often already in context, and its values will look entirely plausible in this one — a ticket prefix, a DoD doc, an MCP namespace. Nothing is stored wrongly; the substitution happens in the *reasoning*, which is what makes it silent and confident. No project's configuration is ever a default for another's.
6. **Everything specific is data, and everything shipped is just a filled-in instance.** Adapters, flows, presets, DoD gates — the plugin ships instances of open contracts; users author their own against the same contracts. There is no "built-in vs custom" divide at the mechanism level.

## Generic vs project-specific

| Layer | Invariant (plugin ships) | Project-specific |
|---|---|---|
| Methodology skeleton | vision → roadmap → epics → tickets → gates; bounded sessions; session state | — |
| Templates | epic, ticket, spike, gate skeletons | which gates apply |
| Skills | `/cadence:session`, `/cadence:plan`, `/cadence:roadmap`, `/cadence:init` as *interpreters* | the flow they interpret + the ops they call |
| Bindings | adapter *contracts* | tracker/VCS/docs/execution + IDs + namespaces |
| Flow | flow-spec *vocabulary* + hook surface | the flow: states, gates, cadence, priority, decision rights, hooks |

---

## Layer 1 — Bindings (config + adapters)

One config file per project; **location detected** (if a domains system is present → `domains/PROJECT.md`, else `.claude/cadence/config.md`). It names the bindings and points at the flow:

```markdown
project:   { name: MachineGame54, ticket_prefix: MACH }
tracker:   { kind: linear, mcp_namespace: linear-uft, team_id: ..., project_id: ...,
             epic_convention: label:"Epic", statuses: {...} }
vcs:       { kind: diversion, checkpoint: skill:/commit, gotchas: "dv add for new files" }
execution: { skill: /work-on, owns: [domains, implement, test, docs, commit] }
doc_system:{ kind: domains, index: domains/INDEX.md, ticket_to_docs: "labels == domain names" }
session_state: { file: .claude/cadence/SESSION.local.md, format: markdown, vcs_ignored: true }
models:    { mechanical: haiku, reasoning: inherit }   # 3rd binding: which model tier does which work
flow:      solo-greenfield            # a shipped preset, OR .claude/cadence/my-flow.flow.md
```

**Session state is the one store Cadence owns, and it owns nothing else.** `/cadence:session start` reads `session_state.file`; `/cadence:session end` writes it. It is **local, not committed** — hence `.local.md` plus an entry in the project's ignore file, added through the VCS adapter's `ignore()` so it lands in `.gitignore` / `.dvignore` / whatever the `kind` implies. Rationale: it is a working scratchpad of goal, milestone state and per-ticket hooks — high-churn, single-author, and a guaranteed merge conflict on any shared branch.

⚠️ **Do not own or depend on a project's memory files.** Some projects keep an always-loaded convention file (a `CLAUDE.md`, an agent `MEMORY.md`); that is the *project's*, not Cadence's. The plugin must never write to one, never require one to exist, and never read one **at run time** — a skill that works only when a memory file is present has a hidden dependency on a file it does not control, and fails confusingly where that file is absent. If a project wants a pointer from its own memory to the session-state file, the project writes that pointer once, by hand. Cadence never *writes* outside `.claude/cadence/`.

**Init is the deliberate exception, and the distinction is dependency, not reading.** `/cadence:init` already reads READMEs, manifests and skill files to work out what a project does; a convention file is the same kind of evidence and is frequently the best available. It carries what an interface cannot — which operations are irreversible, which recovery steps destroy local work. Reading it once, confirming with the user, and writing the result into Cadence's own config or adapter leaves nothing depending on the original. Reading it on every session would be a dependency. The first is fine; the second is the thing this rule forbids.

An **adapter** is an instruction doc a skill loads based on `kind`. The plugin ships only the **contracts** plus the near-universal **fallbacks** (`markdown`/`git`/`none`); environment adapters (`linear`, `diversion`, a `domains` doc-system, …) are **project-local, generated by `/cadence:init`** from the tool actually present — the plugin assumes no environment (see `adapters/ADAPTERS.md`). Contracts:
- **Tracker:** `list_open(milestone)` · `get(id)` · `create(fields)` · `comment(id,text)` · `set_status(id,status)` + epic/milestone/label mapping.
- **VCS:** `status()` · `diff()` · `checkpoint(msg, ticket_ref)` · `add_untracked(paths)` · `ignore(paths)` — appends to the ignore file the `kind` implies (`.gitignore`, `.dvignore`, …), idempotently; used at init to keep the session-state file out of the repo.
- **Doc system:** `locate(topics)` · `record(gotcha)` · `taxonomy()` — the label vocabulary that lets an item's labels resolve to context docs; may be empty.
- **Execution integration** is not implemented by the plugin — it's a pointer to the project's skill plus `execution.owns`, the contract that tells `/cadence:session end` what to *verify* rather than repeat.
- **Adapters are the cheap tier.** Their operations are mechanical, so skills delegate *batchy* adapter work to the `mechanical` subagent running on `config.models.mechanical` (default `haiku`). Model tiers are a third binding — config, never hardcoded, since available models differ per user.

---

## Layer 2 — Methodology (profiles & flows)

This is what makes the same skeleton serve a solo hobbyist and a 30-person live-product team. A **flow spec** is a declarative document; the skills *interpret* it. The three presets are flow specs we ship; a **custom flow** is one you author against the same vocabulary.

### The flow-spec vocabulary

A flow declares:

- **Work hierarchy** — the levels and names (milestone→epic→ticket, or initiative→story→task, or flat "issue"). Not hardcoded.
- **States & transitions** — the status lanes an item moves through, and which transitions are *gated*.
- **Gates** — named checkpoints, each with a *condition* and an *approver* (AI-auto / AI-proposes-human-decides / human-only). The DoD is one gate; design-review, QA sign-off, release approval are others.
- **Cadence & ceremonies** — continuous / sprint / kanban, and for each ceremony (planning, standup, review, retro) what the plugin does: prepare inputs, capture the outcome, or nothing.
- **Intake & priority policy** — how new work enters and the ordering rule `/cadence:session start` consults (`incident > customer bug > sprint > roadmap`, or just `next roadmap ticket`).
- **Decision rights** — the autonomy dial per step.
- **Session definition** — what a work session is and how its goal is chosen.

### Presets (shipped flow specs)

- **Solo / Greenfield** — today's MachineGame flow. High autonomy: the skill proposes goals and breaks down epics; continuous cadence; bug rule = defer to bug-batch; gates = DoD only; priority = next roadmap ticket.
- **Team / Sprints** — sprint cadence with planning/standup/review/retro; `/cadence:plan` *proposes* a sprint but a human ceremony commits it; goals come from the committed sprint, not invented; gates add code-review; decision rights mostly propose-then-human.
- **Live Product / On-call** — adds an **incident/hotfix lane** above everything; bug rule *inverts* (a customer incident preempts the roadmap); gates add regression, changelog, release-approval; checkpoint becomes gated/versioned release.

### Custom, graduated (levels 1–3 — level 3 in scope)

1. **Override axes.** Start from the nearest preset, change individual values (cadence, priority policy, DoD gates). Covers most "custom."
2. **Edit the flow spec.** Fork a preset and rewrite its states/gates/ceremonies for a bespoke process.
3. **Authored stages (the escape hatch).** For behavior the vocabulary can't express, point any **hook** at your own instruction doc, which the skill loads and follows in place of the default — full power, without forking the plugin.

### The hook surface (what makes level 3 real)

The skills expose named **hooks** — the seams where behavior can be overridden. A flow spec maps `hook → instruction doc`; unset hooks use the active preset's default. Each hook has a **contract**: declared inputs it receives and the output it must return, so an authored stage plugs in predictably.

| Hook | Fires when | Input → Output contract |
|---|---|---|
| `session.select_goal` | `/cadence:session start`, after context load | {backlog, sprint, incident queue, priority policy, roadmap} → {chosen goal, rationale} |
| `session.start` / `session.end` | session open / close | {config, flow, session state} → {session frame} / {close actions} |
| `session_state.prune` | `/cadence:session end`, before writing session state | {session state, tracker} → {pruned session state} |
| `intake.classify` | a new item arrives | {raw item} → {type, severity, lane} |
| `intake.prioritize` | queue needs ordering | {queue, policy} → {ordered queue} |
| `bug.triage` | a bug is found mid-session | {bug, context, flow} → {defer \| file \| preempt} |
| `plan.breakdown` | `/cadence:plan` on a milestone | {milestone, templates, tracker} → {proposed items} |
| `plan.commit_scope` | scope enters a sprint/cycle | {proposal, decision rights} → {committed set \| "needs meeting"} |
| `gate.<name>.check` | a gated transition (dod, design_review, qa, release_approval, …) | {item, context} → {pass \| fail \| needs-human, notes} |
| `ceremony.<name>.prepare` / `.capture` | planning/standup/review/retro | {board, history} → {prep pack} / {recorded outcome} |
| `transition.<from>_to_<to>` | a state change | {item, from, to} → {side-effects} |
| `checkpoint` / `release` | work is committed / released | {changes, ticket, vcs adapter} → {commit/release actions} |

That table *is* the extension API. A custom flow can override one hook (e.g. a bespoke `session.select_goal`) and inherit everything else from a preset.

**`session_state.prune` — why it exists.** Session state is a scratchpad for what the *tracker cannot tell you*; left unpruned it silently becomes a stale second copy of the backlog, and a second copy of a backlog is worse than none — it disagrees with the real one while looking authoritative. The default prune rule (what gets deleted, what earns a keep) is specified once, in `flows/HOOKS.md`; it is a hook contract, not a design decision to restate here.

The load-bearing part is *where the truth comes from*: the default reconciles against the **tracker adapter, never against what the file itself claims.** That distinction is not a nicety. In the first project to run this, two entries sat in the open list as live work while a paragraph three lines above already recorded them closed — pruning from the file's own assertions would have preserved both. Flows may tune how aggressively this runs — a scratchpad in solo-continuous, a shared record under team-sprints — by overriding the hook.

### Coherence & portability

- **Coherence check.** A custom flow can contradict itself ("team-consensus decisions" + "AI auto-approves sprint scope"). The authoring step validates the spec and warns — it doesn't silently accept.
- **Portability.** A flow spec (and its hook docs) is a self-contained artifact. Teams version and share theirs; an org can publish a house flow; the three presets are just the seed library. The DoD "define your own" is the same idea one level down — the *whole flow* gets a "define your own," not only the DoD.

---

## Skills the plugin ships

All are *interpreters* of the config + flow; none assume a tool or a process.

- **`/cadence:init`** — detect bindings → confirm/interview → pick or author a flow → write config + flow → scaffold docs → dry-run.
- **`/cadence:session`** (start/end) — runs the flow's `session.*` and gate hooks; pulls the goal via `session.select_goal`; delegates execution to `execution.skill`; verifies (not repeats) the checkpoint.
- **`/cadence:plan`** — runs `plan.*` hooks to turn a milestone into epics/tickets via the tracker adapter, respecting decision rights (propose vs commit).
- **`/cadence:roadmap`** — create/update the vision & roadmap doc from templates.

Not shipped: a ticket-execution skill, a VCS-specific commit skill.

---

## The init flow (detect → confirm → choose/author flow → scaffold)

1. **Detect bindings and propose** — doc system (`domains/`? → config at `domains/PROJECT.md`), execution skill (scan skills/plugins/global; **propose a candidate but ask the user to confirm** it and what it owns), VCS (`.git`/`.diversion`/`.jj` + any commit skill), tracker (connected MCPs + IDs + prefix).
2. **Choose the flow:**
   - **Pick a preset** (Solo/Greenfield · Team/Sprints · Live/On-call), then optionally override axes (level 1).
   - **or Author custom** — the interview walks the flow-spec vocabulary (hierarchy, states, gates, cadence, intake/priority, decision rights), and for any step the vocabulary can't capture, offers to author a **hook doc** (level 3). The DoD menu (with "define your own") is just the `gate.dod` slice of this.
3. **Coherence-check** the resulting flow; warn on contradictions.
4. **Write** config + flow spec (+ any hook docs).
5. **Scaffold** vision/roadmap/feature-process docs from templates, pre-filled, if absent.
6. **Dry-run** — show what `/cadence:session start` surfaces under the chosen flow, so the bindings *and* the process resolve before the user trusts them.

---

## Plugin anatomy

```
cadence/
  .claude-plugin/plugin.json
  skills/                          # one entry per capability; typed AND model-selected
    init/SKILL.md                  #   -> /cadence:init
    session/SKILL.md               #   -> /cadence:session start|end
    plan/SKILL.md                  #   -> /cadence:plan
    roadmap/SKILL.md               #   -> /cadence:roadmap
    doctor/SKILL.md                #   -> /cadence:doctor
  agents/
    mechanical.md                  # cheap-tier subagent (model: haiku) for mechanical work
  adapters/
    ADAPTERS.md                    # the bindings contract
    trackers/markdown.md           # shipped fallbacks only; env adapters are project-local (init-generated)
    vcs/git.md
    docs/none.md
  flows/
    solo-greenfield.flow.md
    team-sprints.flow.md
    live-oncall.flow.md
    HOOKS.md                       # the hook surface + contracts (the extension API)
  templates/
    vision-and-roadmap.md
    feature-process.md
    session-goals.md
  config.example.md
  README.md
```

A custom flow lives with the project (e.g. `.claude/cadence/my-flow.flow.md` + `hooks/*.md`) and is referenced from `config.flow`.

**Why there is no `commands/` directory.** A first attempt shipped one, on the assumption that skills could only be model-selected and a command was needed to give users something to type. That assumption was wrong: a plugin skill is *both* typeable as `/cadence:<name>` and selectable from its description. Shipping both registered every capability twice — `/cadence:init` from the command and `/cadence:cadence-init` from the skill — which only became visible on a real install.

Two lessons worth keeping. **The plugin namespace is the namespace**: everything is already `cadence:<name>`, so prefixing skill names `cadence-` produces a stutter, and a bare `session` inside this plugin cannot shadow an adopter's own `session` skill. And **the surface a plugin presents is not verifiable from its source** — nothing in the repo could have shown the doubling. That is the argument for `docs/VERIFICATION.md` existing at all.

**Referring to bundled files.** A skill runs with the *consumer project* as its working directory, so a bare path like `flows/HOOKS.md` resolves into the user's repo, where it doesn't exist. Every reference from a skill to a file shipped inside the plugin must be written `${CLAUDE_PLUGIN_ROOT}/flows/HOOKS.md`. This is not cosmetic: adapter resolution and hook resolution both depend on the skill actually finding those docs, and the failure is silent — the model guesses instead of erroring.

---

## Migration: MachineGame54 as consumer #1

- `domains/PROJECT.md` becomes the config; `flow: solo-greenfield`.
- Bindings: `tracker: linear` (linear-uft, MACH) · `vcs: diversion` (delegates to `/commit`) · `doc_system: domains` · `execution: /work-on` (owns implement/test/docs/commit).
- The current hardcoded `/cadence:session` is replaced by the interpreter reading config+flow. Your recent seam fix (verify, don't repeat the commit) becomes the general `session.end` behaviour driven by `execution.owns`. Your bug-batch rule is just the Solo/Greenfield `bug.triage` default.
  - ⚠️ **Retire the consumer's own `/session` skill at cutover.** Cadence's is named `cadence-session`, so the two no longer *collide* — but they do overlap, and two live session rituals is worse than one. MachineGame's copy lives at `~/.claude/skills/session/`; its substance is already captured here (the `session_state` binding, the `session_state.prune` hook and its default, Principles 4 and 5), so deleting it loses no reasoning. **Namespacing is the general rule:** every shipped skill is prefixed `cadence-` precisely so installing this plugin can never shadow a skill the adopter already relies on.
  - MachineGame's existing session-state file moves to `.claude/cadence/SESSION.local.md` and gets ignored via `vcs.ignore()`. Any pointer to it from the project's own memory file is updated **by the project, by hand, once** — the plugin does not perform that migration and must not read the project's memory.
- Nothing game-side changes; MachineGame becomes the reference implementation. A second, deliberately different consumer (GitHub + git + no docs, Team/Sprints flow) proves both layers generalize.

---

## Decisions

- **Name:** **Cadence** — locked.
- **Audience:** **shareable / public from the start.** This raises the bar and reshapes the build (below), and forbids any MachineGame- or Unreal-specific detail from leaking into the plugin — MachineGame is a *consumer/example*, never a dependency.
- **Starter sets** (recommended): adapters Linear + GitHub + markdown, git + Diversion, domains + none; the three preset flows.
- **Config & flow format** (recommended): Markdown, human-editable, read as prose. Revisit only if machine validation is needed.

### What "shareable from the start" requires

- **Contracts are public API.** The adapter contracts, the flow-spec vocabulary, and `HOOKS.md` must be documented well enough for a stranger to author a new adapter, flow, or hook. Treat them as versioned interfaces.
- **No leaked specifics.** Shipped presets/adapters/examples use placeholders. Your real MachineGame config (real `linear-uft` IDs, workspace GUIDs) stays in *your* repo, never in the public plugin. Never publish credentials or workspace IDs.
- **Its own repo.** Cadence is a separate versioned project with a README, a `LICENSE` (recommend MIT or Apache-2.0 — decide before first publish), a marketplace manifest, and at least one worked "author-your-own-flow" example.
- **Onboarding is a feature.** `/cadence:init` and the docs are the first surface a new adopter meets; they get first-class effort.

## Build plan (phased — each phase independently useful)

1. **Config + flow schema; write MachineGame's config + `solo-greenfield` flow.** Proves both shapes on a real project.
2. **Env- and flow-agnostic `/cadence:session`** reading config+flow; dogfood on MachineGame.
3. **Bindings adapters** for MachineGame's stack (linear, diversion, domains).
4. **`HOOKS.md` + the hook surface**, wired into the skills as real extension points (this is what makes level 3 exist).
5. **`/cadence:init`** — detection + flow pick/author + coherence-check.
6. **Second consumer** — GitHub/git/none + Team/Sprints flow, to prove both layers.
7. **Package** — manifest, templates, flows, README → installable plugin.
8. **Shareable packaging** (first-class, not optional) — README + contract docs (adapters, flow-spec, `HOOKS.md`), a `LICENSE`, a marketplace manifest, an "author-your-own-flow" worked example, and versioning.

Phases 1–4 already give *you* a cleaner, fully configurable MachineGame setup; 5–8 make it adoptable by strangers. The hook surface (4) and the contract docs (8) are the difference between "three canned workflows" and "a platform others build on."
