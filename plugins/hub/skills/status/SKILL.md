---
name: status
description: >-
  Report what state a project's plugin stack is in — which plugins are installed, enabled and
  current, every component's version from the config bus, which roles own an artifact without
  being registered, whether each binding resolves, and any knowledge folder nobody registered.
  Read-only; every finding names the command that would change it. Use when the user runs
  `/hub:status`, asks what is installed or what is out of date, asks what they would need to run
  before migrating, or wants one answer instead of running four plugins' doctors.
user-invokable: true
---

Follow `${CLAUDE_PLUGIN_ROOT}/skills/_shared/status.md` exactly.

It reads `${CLAUDE_PLUGIN_ROOT}/skills/_shared/detect.md` for the detection step — installed
**and enabled**, payload currency, what the bus says, and unregistered knowledge folders.

**This command writes nothing.** Not a fix, not a stamp, not a missing row. If something needs
changing, name the command that changes it and stop.
