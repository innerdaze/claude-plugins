# `hub doctor` — one report from every doctor

Invokes each role's declared doctor and collates what comes back. Read-only, and it runs **no
checks of its own**.

## Why it does not implement checks

The shared config-bus checks are vendored identically into every plugin
(`${CLAUDE_PLUGIN_ROOT}/checks/BUS-CHECKS.md` here too) precisely so every doctor answers the
same questions the same way. A `hub` that ran its own copy would be a second opinion on files it
does not own — and when the two disagreed, nobody could say which was right. Collation is
presentation, not analysis.

## Procedure

1. **Detect** — [`detect.md`](./detect.md), because a report from a stale plugin is a stale
   report, and that has to be said at the top rather than discovered later.

2. **Invoke each doctor the bus declares.** Read `## Commands`; for every role with a `Doctor`
   cell whose plugin is installed and enabled, run it. A role with an empty `Doctor` cell has
   none declared — report that, and do not go looking for one by name.

3. **Collate.**
   - **De-duplicate the shared bands.** Every doctor runs the same config-bus checks, so four
     doctors produce four copies of the same bus findings. Report each shared band **once**.
   - **Keep every plugin-specific finding attributed** to the doctor that raised it. A finding
     without its source cannot be followed up.
   - **Two doctors disagreeing on a shared band is itself a finding.** They vendor the same
     checks, so a disagreement means one of them is reading the file differently — report both
     verbatim and say they disagree. Do not average them and do not pick.

4. **Attribute against a recent migration, when there was one.** Ask each doctor, or check the
   pre-migration file out of git yourself, and mark each finding *caused by the migration* or
   *predates it*. This is the difference between a readable report and a list: on a real
   rehearsal it separated eleven pre-existing problems from the one that was actually new.

5. **Report** every finding with the one command that would change it, or a plain statement that
   none exists — including, explicitly, findings about things **outside the repo** (memories,
   notes) which no command here can reach.

   **One line per finding, and end with what to do.** Headline, the findings grouped by band,
   then the commands to run in order — at most four, copy-pasteable. If it does not change what
   the reader does next, it is not in the report; the detail is already above it for anyone who
   wants it. De-duplicating the shared bands is what makes this possible, so spending the space
   you saved on prose gives it straight back.

## Never

- **Never write.** No doctor in this stack writes, and an aggregator least of all.
- **Never suppress a plugin-specific finding** to keep the report short. De-duplicate the shared
  bands; keep everything else.
- **Never report a component's version as current while its owner's payload is behind.**
