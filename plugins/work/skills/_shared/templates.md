# Templates

Skeletons `work init` fills in and writes into the target project. Fill every
`{placeholder}` from what you detected and confirmed. Delete rows/sections that
don't apply to this project rather than leaving them blank — a half-filled config
is worse than an honest "none". Keep the environment's real vocabulary throughout;
strip anything that belongs to a different ecosystem.

## Domain system version

**Domain system version: 16**
**Minimum supported version: 1**

This is the canonical version of the init **scaffolding** — the shape of the files
`work init` writes into a project (`PROJECT.md`, `INDEX.md`, `meta.md`,
`.agent/work/**`) and the `## Rules` section it seeds. It is **separate from**
the Overlay schema version below (that one tracks only `.agent/work/workflow.md`) and from
the npm package version in `plugin.json` (that's release packaging, not artifact schema).

`work init` stamps the canonical number into the bus's `## Versions` rows (the `Domain system
version` row). `work on` compares the stamp against these two integers — **a pure integer
check; it reads no migration files** — and warns (one line, non-blocking) when a project
is behind: below the floor ⇒ "re-run `work init`", between floor and canonical ⇒ "run
`work migrate`". `work migrate` reads only the pending files `${CLAUDE_PLUGIN_ROOT}/migrations/v{stamp+1}.md` …
`${CLAUDE_PLUGIN_ROOT}/migrations/v{canonical}.md`, applies them, and re-stamps.

> **Changing at R1:** this single stamp is being **split per owner**. `## Versions` in the config
> bus carries one row per component with its owning role, and each owner sets its own floor — so
> `work` floors the overlay and its own bus sections, while the knowledge scaffolding is floored
> by whoever owns the `knowledge` role. A jointly-owned stamp would mean neither could raise it
> without the other, which is the lockstep the split exists to prevent.

**Minimum supported version** is the oldest version `work migrate` will migrate *from*.
Raise it (and delete the now-below-floor `${CLAUDE_PLUGIN_ROOT}/migrations/vN.md` files) only when the history
grows long enough to be worth pruning — see `${CLAUDE_PLUGIN_ROOT}/migrations/README.md`.

**Bump the canonical by one whenever you change the scaffolding in a way an existing
project should pick up** (e.g. add a Rules bullet, add a PROJECT.md field, change INDEX.md
shape). Every bump **must** add a matching `${CLAUDE_PLUGIN_ROOT}/migrations/v{N}.md` file describing the change
and how to apply it — that file is what `work migrate` runs. A canonical version with no
matching migration file is a bug: projects would warn as behind with nothing to apply.
(History: v1 = baseline — the pre-versioning format; a missing stamp is treated as v1.
v2 = added the "Keep memory current" + "Proactively load domains" Rules bullets to the
CLAUDE.md template.)

## Overlay schema version

**Overlay schema version: 4**

This is the canonical version of the `.agent/work/workflow.md` overlay format and its
conventions (step-library fields, scenario syntax, the model+effort and parallel-group
rules). `update-workflow` stamps this number into every overlay it writes (step 8); `work
on` reads it back from the overlay and compares against this declaration, warning the user
when a project's overlay is behind. **Bump it by one whenever you change the overlay
skeleton or its conventions below** — that's the signal that makes already-initialised
projects show as stale and prompt a re-run. (History: v1 = original; v2 = added per-step
effort levels + scenario parallel groups; v3 = the overlay now **carries its own step
schema** in a normative header section, so anything that can read the repo can write a valid
overlay without reading this skill; the spine gained two conditional steps — the intent-layer
resolve in Phase 1 and the shared-knowledge check in Phase 3, both no-ops when the project has
neither; and each step now declares `Kind: slot | hook`, with a hook over a gate or a
domain-integration step rejected outright. v3 is unreleased, so all three fold into it rather
than minting v4/v5 — **once it ships, it freezes.**)

---

## `.agent/PROJECT.md` — the config bus

> **The frozen core below is not `work`'s to define.** The schema marker, the six `shared`
> sections and the three `shared, additive` tables are specified in the vendored
> `${CLAUDE_PLUGIN_ROOT}/checks/BUS-CHECKS.md` § *Creating the bus, when nothing has*, which every plugin ships
> byte-identical — because any of them may be the first to run and write this file. What follows
> is that skeleton plus the rows `work` fills in. The two are compared mechanically by
> `scripts/validate_payloads.py`; if they disagree, the vendored spec is right.

**What goes in it, and what does not.** The bus is a map **for the plugins** — which tracker,
which VCS, which command proves done, who owns which artifact. Every plugin loads it blind, first,
on every run, and none of them reads prose. So:

- **Facts, not instruction.** A value is a name, a path, a kind, a command, a stamp. Not a
  sentence about how to use it. `git commit -m …` is a value; *"never commit to main"* is a
  working agreement and belongs in the project's `CLAUDE.md`. A procedure belongs in the skill
  that runs it. How `work on` drives the tracker is in `tracker-ops.md`, never here.
- **A section is a heading, a marker and a table.** No prose beside the table, nothing under the
  H1 but the schema marker. Write the file below **exactly** — the notes in this list are for you,
  not for the file.
- **Unknown is an absent row.** `none` is a fact and stays (*this project has no tracker* tells a
  tool something). Never write `n/a`.
- **Not an overflow for `CLAUDE.md`.** There is no notes section. Something worth stating once is
  the project's to place, and the bus is the one file where it costs every plugin.

**Writing rules the file itself does not carry** (they are here so two runs produce one diff):

- **The six `shared` sections** — `## Project`, `## Environment`, `## Version control`,
  `## Tracker`, `## Verification`, `## Bindings` — belong to no role, because any tool can be the
  one that asked the user. Write a row that is absent, never overwrite a value another tool
  wrote; a disagreement is a human's to resolve. `## Bindings` is additive (append rows); the
  other five are not.
- **Additive tables are appended to, never inserted into.** A new row goes after the last one.
- **Marker spacing:** a section you create from this file — copy its heading line **verbatim**,
  padding included. A marker you add to an existing heading — exactly one space. The whitespace
  is not significant to any check; the rule exists so two runs agree.
- **The `<!-- manifest schema: N -->` marker** under the H1 is frozen in presence and syntax; its
  value is not. The `| manifest schema |` row in `## Versions` is not a substitute.
- **`## Artifacts`: register only what `work` owns** — the ticket-flow rows. An absent row means
  not registered, never forbidden. Registering someone else's artifact means detecting its path,
  which is what the table exists to avoid. **Owner is a role id** (`knowledge` · `delivery` ·
  `methodology` · `intent-layer` · `shared-memory`), never a tool name. A row whose path has
  vanished is treated as absent and reported once — never guessed at.
- **`## Bindings`: a kind, not a product path.** A tool resolves it as: project-local adapter for
  that kind, else the kind's shipped fallback, else an error naming the command that generates
  one. `none` is a real binding with a real fallback.
- **`## Versions`: one row per component, stamped by its owner**, each owner with its own floor.
  `work` stamps its two rows from the canonical integers at the top of this file.
- **`## Commands`: each owner declares what migrates its own components.** The row shape is
  **not** frozen (the Doctor column was added after the table shipped). A role with no row, or a
  command not available in this session, is reported, never guessed.

```markdown
# Project Configuration — {ProjectName}

<!-- manifest schema: 1 -->

## Project              <!-- owner: shared -->

| Key | Value |
|---|---|
| Name | {ProjectName} |

## Environment          <!-- owner: shared -->

| Key | Value |
|---|---|
| Stack | {precise label + version, e.g. "React 18 (Vite + TypeScript)" or "Python 3.12 (Django 5)"} |

## Version control      <!-- owner: shared -->

| Key | Value |
|---|---|
| Kind | {git \| Diversion \| hg \| svn \| none} |
| Commit workflow | {the command that commits, e.g. "git commit -m …" \| "via /commit skill" \| "dv commit"} |

## Tracker              <!-- owner: shared -->

| Key | Value |
|---|---|
| Kind | {Linear \| Jira \| GitHub \| GitLab \| Notion \| none} |
| Access | {MCP namespace e.g. `mcp__linear-uft`, or CLI e.g. `gh` / `glab` — omit the row when Kind is none} |
| Prefix | {e.g. `MACH`, `RD` — omit the row when the tracker has no prefix} |

## Verification         <!-- owner: shared -->

| Key | Value |
|---|---|
| Proven by | {the commands that prove "done", e.g. "`yarn test` + `tsc --noEmit` + `yarn build`"} |
| Definition of Done | {path to the document that states the project's bar in its own words — items like "persistence", "no new warnings" — or omit the row when the project has not written one down. `Proven by` is what is automated; this is what must be true} |

## Bindings             <!-- owner: shared, additive -->

| Seam | Kind |
|---|---|
| Doc system | {`none`, or the binding for this project's knowledge system — `markdown` when it has the standard one} |
| Intent | {`none`, or the binding for an intent layer} |
| Shared knowledge | {`none` — or the binding for a shared-knowledge service, if the project has one} |

## Artifacts            <!-- owner: shared, additive -->

| Artifact | Path | Owner |
|---|---|---|
| Knowledge | `domains/` | knowledge |
| Ticket flow | {`.agent/work/workflow.md`, or "none"} | delivery |
| Ticket flow rules | {`.agent/work/rules/`, or omit the row when the overlay has no extracted rules} | delivery |

## Versions             <!-- owner: shared, additive -->

| Component | Version | Owner |
|---|---|---|
| manifest schema | 1 | shared |
| ticket-flow overlay | {stamp the canonical "Overlay schema version" from `templates.md`} | delivery |
| delivery scaffolding | {stamp the canonical "Domain system version" from `templates.md`} | delivery |
| knowledge scaffolding | {same stamp, until `domains` owns it and re-stamps} | knowledge |

## Commands             <!-- owner: shared, additive -->

| Role | Migrate | Re-scaffold | Doctor |
|---|---|---|---|
| delivery | `work migrate` | `work init` | `work doctor` |
| knowledge | {`domains migrate`} | {`domains init`} | {`/domains:doctor`} |
```

---

## CLAUDE.md — the "Rules" section

`work init` seeds this once. **The file is the project's**, so every edit is insert-if-absent,
matched by intent rather than verbatim, and nothing around what you add is reformatted, reordered
or removed. If a bullet's intent is already stated in the project's own words, skip it.

`[note]` The **Domain Knowledge System** section and the `prep`-related bullet are **not here** —
they belong to the knowledge system's own plugin, which inserts them itself. Do not seed them
from `work`: two tools writing the same section is what ownership rules exist to prevent.

Working-agreement defaults that keep the assistant honest and rigorous. These are
project-agnostic, so seed every project with them; the user can tune the list after.

**Merge, never duplicate.** First scan the whole file for an existing `## Rules`
heading (there may even be more than one). If one exists, add only the missing
bullets into that existing section — do not create a second `## Rules` heading.
Skip any bullet whose intent is already covered, so you don't restate a rule the
project already has in different words. Only when no `## Rules` heading exists at all
do you insert a fresh one, placed directly after the project overview / title and
before the deeper structure sections.

```markdown
## Rules

- Do not just reinforce what I believe, be honest and accurate
- **Prove before implementing** — validate uncertain theories with logging or automated tests before changing code
- **Challenge my approach** — if you know a better pattern, say so
- **Build for the future** — do not prefer a fix purely because it is simpler or avoids touching other files
- **Keep memory current** — proactively update your auto memory when you learn something worth remembering for future sessions (user preferences, project decisions, useful feedback, gotchas encountered). Don't wait to be asked.
- **Proactively load domains** — run `prep <domain>` for relevant domains without being asked; use the user's prompt for initial discovery, then load more domains as the work reveals new topics.
```


## `.agent/work/workflow.md` (OPTIONAL — only when the flow is customized)

Not written at `init`. Created/edited by `update-workflow` (see
`update-workflow.md`) when the user integrates a workflow skill, adds custom
steps, or defines a scenario. It is an **overlay**: it folds extra steps into `work on`'s
three phases and never removes them. Keep it lean — a **step library** defined once and
**scenarios** that sequence those steps; reference detail (in-repo skill § or extracted
`.agent/work/rules/*.md`), never copy step bodies.

```markdown
# Workflow overlay — {ProjectName}

> **Overlay schema version: {N}** — stamped by `work update-workflow` (use the canonical
> version from the skill's `templates.md`). If `work on` warns this is behind the
> skill's current schema, run `work update-workflow refresh` to regenerate this overlay
> (a migration that preserves your steps/scenarios — not a re-interview).

## Step schema — normative

This section is the **contract**, carried here so anything that can read this repo can write
a valid overlay without reading `work`'s own files. It travels with the file it describes, so
the two cannot drift.

**The seam names come from the published catalog**, `${CLAUDE_PLUGIN_ROOT}/contracts/SEAMS.md`: which
steps are hookable, what each hook receives and must return, and the slot anchors. An overlay
naming a seam that is not in the catalog is naming nothing.

**A step** is an `### {step-id}` heading under `## Step library`, with these fields:

| Field | Required | Value |
|---|---|---|
| `Kind` | yes | `slot` (inserts a new step) or `hook` (replaces a core step's behaviour). A `hook` **may not target a gate or a domain-integration step** — that is a weakening, and the overlay is rejected |
| `Intent` | yes | what the step produces, and why it matters |
| `Model + effort` | yes | `haiku\|sonnet\|opus` + `low\|medium\|high` |
| `Gate` | yes | `none`, or what must be true to proceed — a gate pauses for the user |
| `Parallel` | yes | `independent`, or `serial — depends on <step-id>` |
| `Detail` | yes | a pointer: `.agent/work/rules/<topic>.md` or `<skill> § "<section>"`. **Never an inlined step body** |
| `Settings` | no | options this step reads, one per line: `<name>: <boolean\|string\|number> = <default> — <what it does>`. Values live in `.agent/local/`, never here |

`step-id` is kebab-case and unique within the file. It is the only name a scenario may use.

### `Settings` — why a step declares its own options

A plugin declares its preferences in its manifest under `userConfig`, and the harness lists them
in `/plugin configure` and validates them. **A project's own step cannot use that**, because the
manifest belongs to whoever ships the plugin — so a step you added to your overlay would
otherwise have its options recorded nowhere, discoverable only by reading whatever code implements
it.

Declaring them here recovers what the manifest gives a plugin:

- **Discoverable** — the options are in the artifact anyone already reads to understand the step.
- **Checkable** — `work doctor` reads this file, so it can report a value set for an option no
  step declares, or a declared option whose value is the wrong type. Folklore cannot be checked.
- **Impossible to commit by accident** — the *declaration* is committed and the *value* is not.

The default is what applies when nobody has set anything, and a step must work with its defaults:
an option whose absence breaks the step is a required input, and a required input belongs in the
step's `Detail`, not in a setting somebody may never set.

**Values are read from `.agent/local/`** — one ignored directory for everything uncommitted, so a
preference cannot be committed and two worktrees do not share one. A step that reads a setting
from a committed file is misdeclared: that value is the project's, and it belongs in the config
bus or the plugin's own config.

**A scenario** is an `### {scenario-name}` heading under `## Scenarios`, with:

| Field | Required | Value |
|---|---|---|
| `Match` | yes | the condition that selects this scenario — issue type, branch pattern, keywords |
| `Sequence` | yes | an ordered list of `step-id` entries, each with a **slot** |

A **slot** says where the step lands: the phase (`Phase 1\|2\|3`) and an anchor —
`first`, `last`, `before <core-step>`, or `after <core-step>`. Two step-ids joined by `+` on
one line are a **parallel group**, permitted only when both are `Parallel: independent`.

**Four invariants a valid overlay may not break.** These are checkable rather than advisory: an
overlay that breaks one is **rejected before it runs**, naming the step and the rule.

1. **The three phases are never removed or reordered.** An overlay adds; it does not replace.
2. **Domain integration always runs** — the Step 1.0 domain pick, intent resolve, Domain Loader,
   Domain re-check, Memory Curator and Domain Doc Updater are not overridable, and no scenario
   may slot a step *in place of* one.
3. **No gate is weakened.** The plan-approval stop and the project's proof-of-done are not
   removable, and structurally: **no `hook` may target a gate or a domain-integration step.**
   A `slot` running beside one is fine.
4. **A ticket matching no scenario runs the plain spine.** Matching nothing is valid, never
   an error.

**Invariance is an artifact, not a word.** Each invariant step emits something that must be
present in the run — the plan's `## Domain integration` block is the existing example. The
validator checks the overlay cannot remove it; the artifact check catches a step that did not run
for any other reason. Both, because neither sees what the other sees.

`Detail` pointers are resolved by whoever runs the overlay. A step whose detail cannot be
resolved is reported, not skipped silently.

Read by `work on` after `PROJECT.md`. It customizes *how* the three phases run; it never
removes them. The spine is invariant:

- **Phase 1 — Context & Planning** — plan mode; domain pick → intent-layer resolve → Domain Loader + Ticket Analyst → Planner → ExitPlanMode.
- **Phase 2 — Execute** — Implementer + verification.
- **Phase 3 — Wrap up** — Curator → shared-knowledge check → Domain Doc Updater + Follow-up Filer → commit → comment → status.

Domain integration (Step 1.0 domain pick, Domain Loader, Memory Curator, Domain Doc
Updater) always runs. Everything below *adds to* the spine; it never replaces it. A ticket
that matches no scenario runs the plain spine.

## Integrated workflow skills (references, not copies)

| Skill | Where the detail lives | What it contributes |
|---|---|---|
| {skill-name} | {in-repo `.claude/skills/<name>/SKILL.md`, OR "extracted → `.agent/work/rules/*.md`" if the skill is external} | {1-line — why it's folded in} |

If a skill is external (not committed to this repo), its load-bearing detail is extracted
into `.agent/work/rules/*.md` so the overlay never depends on a skill teammates lack.

## Step library

Each injected step, defined once and reused by the scenarios below. Model + effort follow
the core two-dial rule: model — transform → haiku, synthesis → sonnet, judgment → opus;
effort — mechanical → low, synthesis → medium, search-over-alternatives → high (default one
notch lower than instinct on both).

### {step-id, e.g. `root-cause-gate`}
- **Kind:** {`slot` — inserts a new step | `hook` — replaces a core step's behaviour. A `hook` may not target a gate or a domain-integration step.}
- **Intent:** {what it produces and why it matters}
- **Model + effort:** {haiku|sonnet|opus} + {low|medium|high} {— note if it's a subagent pipeline, e.g. "sonnet/medium search → opus/high synthesis"}
- **Gate:** {does it pause for user confirmation? what must be true to proceed?}
- **Parallel:** {independent of its neighbours (disjoint files/outputs, no data dependency) → can run concurrently; or "serial — depends on <step-id>"}
- **Detail:** {`.agent/work/rules/<topic>.md`, or `<skill> § "<section>"`}

### {step-id, …}
- …

## Scenarios

Each scenario = a match condition + an ordered list of step-ids with slots. Core spine
steps are implicit (always run); list only injections and where they slot. Where adjacent
step-ids are mutually independent (per their **Parallel** flag), group them so `work on`
fans them out in one message instead of running them in series.

### {scenario-name, e.g. `bug`}
- **Match:** {issue type / branch pattern / keywords that select this scenario}
- **Sequence:**
  1. `{step-id}` — {slot, e.g. "Phase 1, first, before domain pick"}
  2. `{step-id}` — {slot, e.g. "Phase 1, after Ticket Analyst, before Planner"}
  3. `{step-id}` + `{step-id}` — {parallel group: both in Phase 3 after commit, independent}

### {scenario-name, e.g. `hotfix`}
- **Match:** {…}
- **Sequence:** {may reuse the same step-ids in a different order, or a subset}

## Merges & notes

- {Where an injected step overlaps a core step, record the merge — e.g. "<skill>'s
  'analyse ticket' merges into the Ticket Analyst, not run separately".}
- {Any project working agreement about the workflow.}
```
