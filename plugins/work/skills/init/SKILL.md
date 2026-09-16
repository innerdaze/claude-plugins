---
name: init
description: >-
  Bootstrap the portable "domain system" for a repo — detect the environment,
  version-control system, and ticket tracker, then write the `domains/` operational-
  knowledge files, `PROJECT.md` config, and the `prep` commands into the project's
  `CLAUDE.md`. Use whenever the user says "work init", "set up the domain system",
  "set up domains", "bootstrap domains", or "prep refresh"/"prep one time init" when no
  domain system exists yet. Run once per repo (then re-run `prep refresh` after major
  changes). This is SETUP — for actually delivering a ticket, that's the `work:on` skill.
user-invokable: true
argument-hint: "[refresh]"
---

# work:init

Set up (or refresh) the domain system for THIS project. Detect reality; never assume the
environment.

This skill's procedure lives in the shared directory next to this skill. Do not do the
work from this file:

1. First read **`../_shared/overview.md`** — the domain-system mental model and the
   cardinal rule.
2. Then read **`../_shared/init.md`** and follow it. It drives detection and file
   generation, and pulls skeletons from `../_shared/templates.md`, detection signals from
   `../_shared/environments.md`, and runs the conflict scan in `../_shared/doctor.md`.

Both paths are relative to this SKILL.md's own directory. If `$ARGUMENTS` is `refresh`
(or the user says "prep refresh"), follow init.md's re-scan path.

$ARGUMENTS
