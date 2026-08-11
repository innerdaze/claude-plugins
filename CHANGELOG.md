# Changelog

All notable changes to the plugins in this marketplace are recorded here. This
file covers **Cadence**; if the marketplace gains a second plugin, it gets its
own section.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
Cadence uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html) with one
project-specific rule: **the contracts are the public API.** Renaming a hook,
changing a hook's Input/Output, removing an adapter operation, or changing the
meaning of a config key is a *major* change. Adding an optional hook, operation,
field, or config key is *minor*.

## [Unreleased]

### Added

- `commands/` — `/cadence:init`, `/cadence:session`, `/cadence:plan`,
  `/cadence:roadmap`. Plugin skills are addressed `plugin:skill`, so the
  previously documented `/cadence init` was never a form Claude Code could
  parse. Each command is a thin wrapper; behaviour stays in the skill.
- `taxonomy()` on the doc-system contract — the label vocabulary that lets an
  item's labels resolve to context docs. Returning empty is valid and means
  items carry no context labels.
- A "When something doesn't resolve" section in `/cadence:session`, covering
  the six ways the config → flow → adapter → tracker chain breaks in a project
  that isn't the author's.
- A documented calling convention for the `mechanical` subagent, so
  `config.models.mechanical` is actually honoured and an unavailable tier
  degrades visibly instead of failing silently.

### Changed

- **Marketplace renamed** `cadence-marketplace` → `claude-plugins`, so the
  documented install command resolves.
- **All skills namespaced `cadence-*`**, with directory names matching their
  frontmatter `name`. Installing Cadence can no longer shadow a `session`,
  `plan`, or `roadmap` skill an adopter already has.
- Every reference from a skill to a bundled file is now anchored with
  `${CLAUDE_PLUGIN_ROOT}`. A skill's working directory is the *consumer's*
  repo, so bare paths resolved to nothing and the model improvised — silently.
- Cadence's data now lives under one root, `.claude/cadence/`. The `markdown`
  tracker's backlog and the `none` adapter's notes previously wrote to
  `.cadence/`, outside the root the design declares inviolable.
- `DESIGN.md` moved to the repository root. It is internal design notes and
  history, not part of the shipped plugin payload.

### Fixed

- The shipped Definition-of-Done menu and templates no longer carry
  game-development-specific gates.
- The `session_state.prune` default rule was stated verbatim in three files and
  had begun to drift; `flows/HOOKS.md` is now its sole owner.

[Unreleased]: https://keepachangelog.com/en/1.1.0/
