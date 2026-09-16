---
name: doctor
description: >-
  Check a repo's intent layer and report what is broken, drifted or disabled — whether it is
  registered in the config bus, whether its index and alignment register are intact, and whether
  unratified inference has been left unmarked. Also reports every other component's version so
  one run shows the whole picture. Read-only, always: this layer is dictated by a human and a
  tool that edited it would be the failure the layer exists to prevent. Use when the user runs
  `/intent:doctor` or asks whether the design docs are in good order.
user-invokable: true
---

Read `${CLAUDE_PLUGIN_ROOT}/checks/BUS-CHECKS.md` and run **every** check in it — the shared
config-bus checks all four tools in this stack run identically. Then the intent-specific ones
below, reported in the same three bands: **broken** · **disabled** · **drifted**.

## Intent-specific checks

**Registration.** The `intent-layer` row in `## Artifacts`:

- Row and folder present → pass.
- **Folder present, no row → drifted.** An unregistered layer is invisible to every tool, by
  design — nothing may guess at a folder that looks like design documentation. Name
  `/intent:capture`, which registers it.
- Row present, folder gone → **drifted**: report absent, change nothing.

**The register exists.** A layer with topic docs but no `alignment.md` → **drifted**, and say
why it matters rather than just naming it: without a register there is nowhere for a
contradiction to go, so the docs get quietly edited to match the code instead. That is the one
failure this whole layer exists to prevent.

**Attribution is intact.** Report counts of unratified inference markers and of
`TODO — needs input` markers. These are **not defects** — they are the layer being honest, and a
doc set with none is more suspicious than one with many. Report them as *numbers*, never as
findings to clear.

⚠️ **A statement with no marker is not automatically dictated.** You cannot tell the difference
mechanically, so do not try: report that markers exist and how many, and leave the judgement to
the person who dictated the docs.

**Open gaps.** Count the register's open rows by severity, and name any that have been open
longest. A gap that nobody has looked at in months is a finding about the *process*, not about
the code.

**The binding.** The `Intent` row should name a kind whose adapter or fallback exists. `none`
while an intent layer is present → **disabled**: the layer is readable by humans and unreachable
through the contract, so nothing checks a plan against it.

**The `## Commands` migrate cell matches what this payload ships.** Compare the `intent-layer`
row's migrate command against whether a `migrate` skill exists in this plugin:

- cell says `n/a — no migrations yet` and the plugin **now ships one** → **drifted**, and it is
  the consequential direction: an orchestrator reads the bus, so the migration will never be
  invoked and the project will sit at an old stamp reporting itself current. The fix is
  `/intent:init`, which repoints the cell.
- cell names a command that **does not exist here** → **broken**: something will try to run it.
- **A version row with no matching artifact, or an artifact with no version row** → **drifted**,
  the same finding every other doctor makes, reported for this role only.

This is the one comparison only this plugin may make — the bus is the authority for callers, and
the payload is the authority for what exists, and nobody else may read both.

## Reporting

One line per finding, grouped by band. **End with the next steps** — what to run or decide, in
order, at most four — or one line saying nothing needs doing. Where a finding is a person's
judgement rather than a command (an unratified inference somebody must confirm or strike), say
so and say what the decision is between. A doctor that ends in counts has told the reader the
weather; they need to know whether to take a coat.

## Boundaries

- **Never write. Not ever, not even the register.** The layer is dictated by a human, and the
  code gets no vote — a tool that edited it could soften the very statement it was found to
  contradict. Findings go in the report, and a person moves them into the register.
- **Judge only what you own.** The intent folder and the `intent-layer` rows. Another role's
  sections are reported, never assessed.
