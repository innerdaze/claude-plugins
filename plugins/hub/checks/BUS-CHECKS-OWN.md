# When a caller runs several doctors in one report

**One spec, vendored by every plugin.** This file is the authority; each plugin ships a
byte-identical copy at `checks/BUS-CHECKS-OWN.md`. A doctor reads it **only** when its arguments
carry one of the two flags below. Run alone, with no flag, a doctor never opens this file and runs
`checks/BUS-CHECKS.md` in full, exactly as it always has.

## Why it exists

A caller that collates several doctors into one report (`hub:doctor`) would otherwise have every
doctor read the same ~17 KB spec and run the same checks, then throw away all but one copy of the
answer. So under such a caller the shared checks run **once per report**: the first doctor runs
them in full, and the others rely on that result and run only what depends on who they are.

Nothing here lets a doctor read another plugin's files. The caller passes arguments to the
commands the bus's `## Commands` table names, and each doctor hashes **its own** vendored copies.

## The two flags

| Flag | Given to | The doctor does |
|---|---|---|
| `--shared-checks-lead` | the first doctor | runs `checks/BUS-CHECKS.md` in full, as if run alone, then ends its report with the line `shared-checks-digest: <digest>` |
| `--shared-checks-done=<digest> --shared-checks-by=<role>` | every other doctor | compares digests (below); on a match, skips the shared spec and runs only **What you still check** |

`<digest>` is what `python3 "${CLAUDE_PLUGIN_ROOT}/checks/bus_facts.py" --digest` prints: one hash
over this plugin's vendored `BUS-CHECKS.md`, `bus_facts.py` and `DOD-ANCHOR.md`. Equal digests
mean the two doctors hold the same rules, so the lead's answer is this doctor's answer too.
`<role>` is the role whose doctor ran the shared checks.

## Before skipping: compare digests

Run `python3 "${CLAUDE_PLUGIN_ROOT}/checks/bus_facts.py" --digest` and compare its output with the
`--shared-checks-done` value.

- **Equal** → skip `checks/BUS-CHECKS.md`. Start your report with the line
  `shared checks: run by <role>` and continue at **What you still check**.
- **Different** → your copy of the shared rules is not the lead's. Run `checks/BUS-CHECKS.md` in
  full, and start your report with `shared checks: digest mismatch (mine <a>, caller's <b>) — ran
  them in full`. One of the two copies is from an older release; the caller reports which.
- **`python3` missing, or the script errors** → you cannot tell whether the rules match. Run
  `checks/BUS-CHECKS.md` in full and say why in one line.

A fallback is never a failure. It costs a duplicate read, and the answer is still correct.

## What you still check

Some shared checks depend on which role is asking. The lead answered them for **its** role, so
answer them for yours. Use the bus facts already gathered in this conversation. Run
`checks/bus_facts.py` yourself only when they are not there.

- **§1, no bus at all:** name your own role's re-scaffold command.
- **§3b:** a `## Artifacts` row owned by the `--shared-checks-by` role whose role has no
  `## Versions` row. The lead skipped it as its own; report it unless it is also yours.
- **§4:** sections whose owner marker is your role. Drifted when you cannot parse them.
- **§5:** your own `## Versions` rows: current, behind (your migrate command) or below your floor
  (your re-scaffold command). Rows owned by other roles were reported by the lead; do not repeat
  them.
- **§6:** bindings for the seams your plugin consumes or provides. Already scoped to you.
- **§7:** every finding you raise names exactly one command that would act.

Then run your plugin's own checks as usual. Report in the same three bands.

## What the caller does with the result

The caller reports the lead's shared findings **once**. It keeps every finding above attributed
to the doctor that raised it. A digest mismatch is a finding in itself, raised against the stale
copy: two plugins in one stack vendor different shared rules. Its remedy is the command that
brings the stack to one release, `/hub:upgrade`, with the older plugin named as context.

If the lead's report has no `shared-checks-digest:` line, it is a release that predates this file.
The caller then runs every other doctor with no flag, so they run the spec in full, and says so
once.
