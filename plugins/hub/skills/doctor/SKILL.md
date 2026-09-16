---
name: doctor
description: >-
  Run every installed plugin's doctor and collate the results into one report — de-duplicating
  the shared config-bus checks they all run, keeping each plugin-specific finding attributed to
  the doctor that raised it, and marking findings as caused by a recent migration or
  pre-existing. Read-only, and it runs no checks of its own. Use when the user runs
  `/hub:doctor`, asks whether the setup is healthy, or wants one report instead of running each
  plugin's doctor separately.
user-invokable: true
---

Follow `${CLAUDE_PLUGIN_ROOT}/skills/_shared/doctor.md` exactly.

**Run no checks of your own.** The shared config-bus checks are vendored identically into every
plugin in this stack — including `${CLAUDE_PLUGIN_ROOT}/checks/BUS-CHECKS.md` here — so that
every doctor answers the same questions the same way. Your job is to invoke each role's declared
doctor, de-duplicate the shared bands, and keep everything else attributed. A second opinion on
files this plugin does not own is worse than no opinion.
