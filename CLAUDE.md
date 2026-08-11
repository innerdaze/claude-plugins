# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code / Cowork **plugin marketplace** containing one plugin, **Cadence** (`cadence/`). The shipped payload is entirely Markdown — the "programs" are skill/adapter/flow/hook instruction docs that a Claude agent loads and follows at run time, so a change to a doc *is* a change to behaviour.

Two things at the repo root are **not** part of the payload and must never move into `cadence/`:

- **`DESIGN.md`** — architecture, rationale, and history. Internal notes. No shipped file may cite it; anything an adopter needs belongs in the contracts.
- **`tools/`** — the repo's own validator and CI. This is the only executable code in the repo, and it exists to enforce the invariants below mechanically. Keeping it outside `cadence/` is what lets the shipped plugin stay pure Markdown.

Run the validator before committing (it is what CI runs):

```
python tools/validate_cadence.py
```

Beyond that there is no build or test suite. The only full exercise loop is installing and running the plugin:

```
/plugin marketplace add C:\Users\Lee\Projects\claude-plugins
/plugin install cadence@innerdaze
```

Then, in a *separate* consumer project (never here), run `/cadence:init`, `/cadence:roadmap`, `/cadence:plan`, `/cadence:session start|end`. `cadence.zip` at the repo root is a packaging artifact and is gitignored (`*.zip`); it is not a source of truth — regenerate it from `cadence/` rather than editing it.

## Architecture: two configurable layers over an invariant skeleton

The one thing worth understanding before editing anything. Cadence ships an invariant methodology **skeleton** — vision → roadmap → epics → tickets → gates, worked in bounded sessions — and reads two independent layers of per-project configuration:

- **Bindings** (`config.example.md`) — *where and with what* you work: tracker, VCS, doc system, execution skill, **and model tiers**. Resolved through **adapters** (`adapters/ADAPTERS.md`). Change these → same process, different toolchain.
- **Flow** (`flows/*.flow.md`) — *how* you work: hierarchy, states, gates, cadence/ceremonies, intake & priority policy, decision rights, session definition. Change this → same tools, different process.

The five skills (`skills/{init,session,plan,roadmap,doctor}/SKILL.md`) are **interpreters** of those two layers. Only `init` writes configuration; `doctor` is strictly read-only, which is what makes it safe to run anywhere. They must never hardcode a tool or a workflow. Where a step can vary, it is a named **hook** (`flows/HOOKS.md`): unset → the skill's built-in default; set → the skill loads the project's instruction doc and follows it instead.

Division of labour, in one line: **hooks decide and describe; adapters perform side-effects; skills orchestrate and own the writes.** A hook returns "create these three tickets"; the skill calls the tracker adapter's `create`.

`flows/solo-greenfield.flow.md` doubles as the flow-spec schema by worked example — read it before touching the flow vocabulary. `examples/author-your-own-flow/` is the level-3 proof (a non-software "manuscript" flow with two authored hooks) and should keep working as a demonstration of the same contracts.

## Contracts are public API

Three files are **versioned interfaces**, documented for strangers to build against:

- `adapters/ADAPTERS.md` — tracker / VCS / doc-system operation contracts, and the three-tier adapter model (contracts shipped · `markdown`/`git`/`none` fallbacks shipped · **environment adapters generated project-locally by `/cadence:init`**).
- `flows/HOOKS.md` — the hook catalog with each hook's Input → Output contract, plus the coherence rules `/cadence:init` enforces.
- The flow-spec vocabulary, defined by example in `flows/solo-greenfield.flow.md`.

Renaming a hook, or changing an Input/Output shape or an adapter operation, is a **breaking change** (see the Versioning section of `HOOKS.md`). Additive changes are minor.

## Editing rules (these are what actually constrain work here)

`DESIGN.md` (repo root, not shipped) carries the rationale; read it before any non-trivial change. Its six principles are the standing constraints:

1. **Environment-agnostic.** Nothing in `cadence/` may assume Linear, Diversion, GitHub, a `domains/` doc system, or any MCP. Tool specifics arrive only via bindings/adapters.
2. **Process-agnostic.** Solo, sprints, kanban, incident-first are *flows*, never code paths.
3. **Decision support scales inversely to autonomy.** More people / more live → the plugin shifts from *making* decisions to *preparing and recording* them. It never runs the meeting or overrides human prioritization (see `flows/CEREMONIES.md`).
4. **It owns neither execution nor the commit.** No ticket-execution skill and no VCS commit skill are shipped; both belong to the consumer project, reached via `config.execution` / the VCS adapter. `/cadence:session end` **verifies** execution-owned work rather than repeating it. The single exception is the local session-state file (`config.session_state.file`) — the one store Cadence owns.
5. **Detect, then confirm — never assume**, across the whole lifecycle, not just init. The specific hazard called out in DESIGN: **cross-project substitution** — skills are installed once and serve every project, so another project's ticket prefix / MCP namespace / DoD will be in context and will look plausible. A missing binding is a question for the user, never an inference.
6. **Everything specific is data.** Adapters, flows, presets, gates are instances of open contracts; there is no "built-in vs custom" divide at the mechanism level.

Two more, load-bearing in practice:

- **Cadence never touches a project's own memory** (`CLAUDE.md`, an agent `MEMORY.md`) and never reaches outside `.claude/cadence/`. Any pointer from a project's memory to Cadence's session state is written by that project, by hand.
- **No leaked specifics.** MachineGame54 appears throughout DESIGN as consumer #1 / a worked example — it is never a dependency, and real IDs, workspace GUIDs, or MCP namespaces must not land in shipped files. Presets and examples use placeholders.

## Cross-file consistency is the main maintenance hazard

The same facts are stated in several places by design (spec, contract, skill, README). A behavioural change usually has to land in more than one of them, or the docs start contradicting each other. Known coupling:

- A hook change → `flows/HOOKS.md` **and** the skill that fires it **and** any preset flow that documents its default **and** DESIGN's hook table.
- An adapter-contract change → `adapters/ADAPTERS.md` **and** the shipped fallback implementing it (`adapters/trackers/markdown.md`, `adapters/vcs/git.md`, `adapters/docs/none.md`) **and** `skills/init/SKILL.md`, which generates adapters against the contract.
- A config-shape change → `config.example.md` **and** every skill that reads that key **and** DESIGN's Layer 1 block.
- A new default behaviour → the skill, the relevant preset flow, and `flows/CEREMONIES.md` if it is a ceremony.

`CHANGELOG.md` is the release record and the place a breaking change must be declared — and under this project's rule, *the contracts are the public API*: renaming a hook, changing its Input/Output, removing an adapter operation, or changing a config key's meaning are all major changes.

## Conventions

- **One skill, one surface. There is no `commands/` directory.** A plugin skill is *both* typeable as `/cadence:<name>` and selectable by Claude from its description, so a command wrapper adds nothing but a duplicate entry. Learned the hard way: an earlier version shipped both, and every capability registered twice.
- **Skill names are bare** — `init`, `session`, `plan`, `roadmap`, `doctor` — with the directory name matching the frontmatter `name` exactly. Do **not** prefix them `cadence-`: the plugin namespace already prefixes everything with `cadence:`, so a prefix yields `/cadence:cadence-session`. That namespacing is also what stops a bare `session` here from shadowing an adopter's own `session` skill.
- **Bundled-file references need `${CLAUDE_PLUGIN_ROOT}`.** A skill's working directory is the *consumer's* repo, so `flows/HOOKS.md` resolves to nothing there. Any path from a skill into the plugin must be written `${CLAUDE_PLUGIN_ROOT}/flows/HOOKS.md`. The failure mode is silent — the model improvises rather than erroring — so this is easy to reintroduce and hard to notice.
- **Descriptions are the dispatch surface.** Each SKILL.md `description` must name the trigger phrases; that is how the skill gets selected.
- Flow specs and configs are **Markdown with a YAML block**, read as prose by the skills — human-editable, not machine-validated. Keep them readable over strict.
- Prose style throughout is deliberate: em-dashes, bolded lead-ins, a rationale for every rule. Match it — these docs are read by both people and models, and the rationale is what makes a rule survive contact with a novel case.
