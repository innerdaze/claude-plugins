# `work` — Claude Code plugin

Portable domain-system + ticket-workflow skill, packaged as a Claude Code plugin
and published to Acre's private GitLab npm registry as `@innerdaze/work`.

The plugin ships **four focused skills** (each with its own trigger surface), all sharing
the procedures under [`skills/_shared/`](skills/_shared/):

- **`work:on <TICKET>`** ([`skills/on/`](skills/on/SKILL.md)) — pick up and deliver
  a tracked ticket end-to-end via subagent orchestration (analyse → plan → implement →
  verify → commit → comment → follow-ups).
- **`work:init`** ([`skills/init/`](skills/init/SKILL.md)) — bootstrap a project's
  domain system (operational-knowledge files, `PROJECT.md` config, the `prep` commands),
  tailored to the project's actual environment, VCS, and ticket tracker.
- **`work:update-workflow [refresh]`** ([`skills/update-workflow/`](skills/update-workflow/SKILL.md))
  — fold custom steps / workflow skills into the three phases as an overlay.
- **`work:doctor`** ([`skills/doctor/`](skills/doctor/SKILL.md)) — read-only "doctor" that
  scans the project's instruction layers for conflicts.

Invoke plugin-namespaced: `/work:on <TICKET>`, `/work:init`, etc. A bare ticket id
routes to `work:on`. Shared procedures (`on.md`, `init.md`, `templates.md`, …) live once in
`skills/_shared/`; each skill's `SKILL.md` is a thin router into it.

## Install

Install it from the public marketplace:

```
/plugin marketplace add innerdaze/claude-plugins
/plugin install work@innerdaze
```
