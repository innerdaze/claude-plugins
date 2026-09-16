---
name: on
description: >-
  Pick up and deliver a tracked ticket end-to-end via subagent orchestration —
  read-only Context/Plan (with user approval), then Execute, then Wrap up. Use this
  whenever the user says "work on <TICKET>", "pick up ticket X", "let's do X",
  "start X", or names a bare ticket ID (e.g. "MACH-42",
  "RD-4981", or just "42"). Works in ANY project — it reads `.agent/PROJECT.md` to
  adapt to the project's environment, version control, and ticket tracker rather than
  assuming them. (Setup is a separate skill: use `work:init` if there is no
  `domains/` system yet.)
user-invokable: true
argument-hint: <ticket-id>
---

# work:on

Deliver one tracked ticket end-to-end. The ticket id is `$ARGUMENTS` (a bare number
like `42` is normalized to `<PREFIX>-42` using the prefix in `.agent/PROJECT.md`).

This skill's procedure lives in the shared directory next to this skill. Do not do the
work from this file:

1. First read **`../_shared/overview.md`** — the domain-system mental model, the
   invariant spine ("every phase, every domain step, every ticket"), and the cardinal
   rule (never assume the environment).
2. Then read **`../_shared/on.md`** and follow it exactly — the three-phase orchestration
   (Context & Planning → Execute → Wrap up). It is the spine; run every phase on every
   ticket regardless of size. Phase 1 is not done until the plan carries its **Domain
   integration** block (domains picked from `INDEX.md` + Domain Loader summary obtained);
   no shortcut for "small" or already-familiar tickets.

Both paths are relative to this SKILL.md's own directory.

$ARGUMENTS
