---
name: doctor
description: >-
  Check a repo's project memory and report what is broken, drifted or disabled — the manifest,
  the topic files, the scan guide, the `knowledge` rows in the config bus, and whether the
  doc-system binding resolves. Also reports every other component's version so one run shows the
  whole picture. Read-only: it never fixes anything, and every finding names the one command
  that would. Use when the user runs `/domains:doctor`, asks why knowledge is not loading, asks
  whether the setup is right, or after upgrading the plugin.
user-invokable: true
---

Read `${CLAUDE_PLUGIN_ROOT}/checks/BUS-CHECKS.md` and run **every** check in it. Those are the
shared config-bus checks that all four tools in this stack run identically — do not reinterpret
them, and do not skip one because it looks like another tool's business.

Then run the knowledge-specific checks below. Report in the three bands the shared spec defines:
**broken** · **disabled** · **drifted**.

## Knowledge-specific checks

**The artifact.** The `knowledge` row in `## Artifacts` and the folder it names:

- Row present, folder present → pass.
- Row present, folder gone → **drifted**. Report it absent; do not look for a replacement and do
  not delete the row.
- **Folder present, no row → drifted, and this one matters more than it looks.** Nothing outside
  this plugin can find unregistered knowledge, so it is invisible to every tool while being
  perfectly visible to a human. Name `/domains:init` — it is safe to re-run and adds the row.

**The manifest.** Present, parses, and its rows point at files that exist. A row naming a missing
file → **drifted** (name the file). A topic file with **no row** → **drifted**: it will never be
loaded by anything that goes through the manifest, which is everything.

**Dangling paths in knowledge content.** A path reference inside `domains/**` that does not
resolve → **drifted**, listed as `file:line`. This is the common state after a migration moved
something out from under the knowledge system: check the referenced path against `## Artifacts`,
and when a registered row names where that artifact went, the finding is *repointable* — name
`domains migrate`. When nothing registered explains it, report the reference and leave it to a
human; a path may simply have been deleted.

Report these every run, and do not treat "the migration mentioned it" as dealt with. A line in a
migration report scrolls past once; a finding comes back until the reference is fixed, which is
the difference between a reminder and a check.

**Stale beats absent.** A topic file whose content contradicts what is obviously in the repo now
is worse than no file: it costs the same to load and returns something false. You cannot judge
this mechanically, so report only the cheap signal — a file not touched since before a large
structural change — as **drifted**, and say it is a judgement for a human.

**The binding.** The `Doc system` row should name a kind whose adapter or fallback exists. `none`
while a knowledge folder is present → **broken**: the knowledge is there and nothing can reach
it through the contract. That is the upgrade regression, and it is the single most useful thing
this doctor says.

**Pays for itself.** Report the count and rough token weight of the always-load set. This is a
principle with no instrument, so the number is the finding — not a pass or a fail.

## Boundaries

- **Never write.** No fixing, no re-stamping, no adding a missing row "while you are here".
- **Judge only what you own.** `domains/**` and the `knowledge` rows. Another role's sections get
  reported, never assessed — their owner is authoritative and your reading is advisory.
