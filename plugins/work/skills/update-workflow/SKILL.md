---
name: update-workflow
description: >-
  Customize the ticket workflow by folding a skill or custom steps into the three
  phases as a lean overlay at `.agent/work/workflow.md` — never mutating the phases
  themselves. Use whenever the user says "update-workflow", "integrate <skill> into the
  workflow", "use <skill> when working tickets", "add a <step> step", "modify phase N",
  or wants to change how `work:on` runs tickets. Pass `refresh` (or "upgrade the
  workflow to the new schema", "my overlay is stale") to regenerate the overlay into the
  current schema without re-interviewing.
user-invokable: true
argument-hint: "[refresh]"
---

# work:update-workflow

Fold a workflow skill / custom steps into the `work:on` three-phase spine as an overlay
at `.agent/work/workflow.md`. The spine is invariant — the overlay only adds around it.

This skill's procedure lives in the shared directory next to this skill. Read
**`../_shared/update-workflow.md`** (path relative to this SKILL.md's own directory) and
follow it. It reads the canonical spine from `../_shared/on.md` and the overlay schema
version from `../_shared/templates.md`. If `$ARGUMENTS` is `refresh`/`--refresh`, follow
that file's **Refresh mode** instead of the interview.

$ARGUMENTS
