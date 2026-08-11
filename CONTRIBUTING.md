# Contributing

Thanks for looking. This repository is a Claude Code plugin marketplace; almost
all of it is **Markdown that an AI agent executes at run time**. That makes
contributing here a little different from a normal codebase, and it's worth
understanding the two consequences before you start.

**A change to a doc is a change to behaviour.** There is no compiler between
what you write and what happens. An ambiguous sentence in a `SKILL.md` becomes
an improvising agent, and the failure is usually silent — the model guesses
rather than erroring. Prefer prose that says *why*, because a rule with a reason
survives contact with situations you didn't anticipate; a bare imperative
doesn't.

**The contracts are public API.** `adapters/ADAPTERS.md`, `flows/HOOKS.md`, and
`flows/FLOW-SPEC.md` are versioned interfaces that strangers author against.
Renaming a hook, changing a hook's Input/Output, removing or renaming an adapter
operation, or changing what a config key means are all **breaking** changes and
need a major version bump plus a `CHANGELOG.md` entry under a `BREAKING`
heading. Adding an optional hook, operation, field, or config key is minor.

## Before you open a PR

```
python tools/validate_cadence.py
```

CI runs exactly this. It checks the invariants that have historically drifted —
that every `${CLAUDE_PLUGIN_ROOT}/…` path resolves, that skill directory names
match their frontmatter, that every flow key exists in the schema, that every
hook in the catalog has a firing site, and that no project-specific term has
leaked back into the payload. `tools/README.md` explains the reason behind each
rule; if a rule seems wrong, that file is the argument to engage with.

## What lives where

The single most common way this repository degrades is the same fact being
written in three files and then drifting apart. Each fact has exactly one owner.
Change it there, and make the other files *point* rather than restate:

| Fact | Owner |
|---|---|
| Flow-spec keys, lane roles, priority-policy tokens | `cadence/flows/FLOW-SPEC.md` |
| Hook names, Input/Output contracts, firing sites | `cadence/flows/HOOKS.md` |
| Adapter operations, item fields, capability declarations | `cadence/adapters/ADAPTERS.md` |
| Config keys and their semantics | `cadence/config.example.md` |
| Where Cadence writes; committed vs local | `cadence/adapters/ADAPTERS.md` |
| Ceremony defaults | `cadence/flows/CEREMONIES.md` |
| Architecture rationale and history | `DESIGN.md` (root — **not** shipped) |

## Changes that must land together

- **A hook change** → `flows/HOOKS.md`, the skill that fires it, and any preset
  documenting its default.
- **An adapter-contract change** → `adapters/ADAPTERS.md`, every shipped
  fallback (`trackers/markdown.md`, `vcs/git.md`, `docs/none.md`) either
  implementing it or declaring it unsupported, and `skills/init/` which
  generates adapters against the contract.
- **A config-shape change** → `config.example.md` and every skill reading that key.
- **A flow-vocabulary change** → `flows/FLOW-SPEC.md`, all three presets, the
  `examples/` flow, and the validator rule that enforces it.

## Adding a preset flow, an adapter, or a hook

All three are instances of open contracts — there is no "built-in vs custom"
divide at the mechanism level, so the bar is the same for a shipped preset and
one you keep in your own project.

- **A flow** must validate against `FLOW-SPEC.md` and declare
  `meta.cadence_version`. Its `lanes` are *process vocabulary* and must never be
  presented as columns a user's tracker is required to have.
- **An adapter** must implement every required operation of its family or
  explicitly declare it unsupported, and must not read the flow — adapters
  perform, they don't decide.
- **A hook** must have a firing site in a skill, or be marked deferred in the
  catalog. A hook nothing fires is a bug, not a feature.

## The rules that are not negotiable

These come from `DESIGN.md` and exist because violating them produces failures
that are silent and confident rather than loud:

1. **No shipped file may assume a specific tool** — not Linear, GitHub, Jira,
   Diversion, or any MCP. Tool specifics arrive only through generated adapters.
2. **No shipped file may hardcode a process.** Solo, sprints, kanban and
   incident-first are flows, never code paths.
3. **Never substitute one project's configuration for another's.** Skills are
   installed once and serve every project, so another project's ticket prefix or
   MCP namespace will be in context and will look plausible. A missing binding is
   a question for the user, never an inference.
4. **No real project names, workspace IDs, or credentials in the payload.** Use
   fictional placeholders. The validator enforces a banned-term list because this
   has leaked before.
5. **Cadence writes only inside `.claude/cadence/`**, plus one line in the
   project's ignore file. It never reads or writes a project's own memory files.

## Reporting a bug

<https://github.com/innerdaze/claude-plugins/issues>. The most useful report
names which skill or contract you were exercising, what you expected from the
docs, and what the agent actually did — the gap between those two is usually the
defect.
