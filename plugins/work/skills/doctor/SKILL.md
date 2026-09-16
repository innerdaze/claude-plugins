---
name: doctor
description: >-
  Read-only diagnostic ("work doctor") — scan a project's instruction layers
  (CLAUDE.md, memory, `.claude/rules/**`, the config bus, the workflow overlay,
  `domains/*.md`) for conflicts that would block or derail a ticket, and report +
  suggest fixes without editing anything. Use whenever the user says "work doctor",
  "scan for conflicts", "check my setup", or "why is my setup fighting itself". It only
  inspects and advises — it never changes files.
user-invokable: true
argument-hint: ""
---

# work:doctor

Detect instruction conflicts in the project's config/knowledge layers. Report and suggest
only — never edit files.

This skill's procedure lives in the shared directory next to this skill. Read
**`../_shared/doctor.md`** (path relative to this SKILL.md's own directory) and follow it.

$ARGUMENTS
