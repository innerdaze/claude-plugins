# `work doctor` — detect instruction conflicts before they derail a ticket

`work doctor` is a **read-only diagnostic pass**. It reads the project's config
layers, surfaces instructions that contradict or would block a step the work
skill's workflow needs to run, and suggests resolutions. It does **not** edit any
file and does not plan or implement a fix — it reports and stops. State this to
the user at the start of every run: *"scan only reports and suggests; act on any
finding only if you ask me to."*

---

## Why it exists

A project accumulates instructions in many places: auto-memories, `CLAUDE.md`,
rules files, settings, and the domain system itself. Any one of them can silently
contradict a step the `work on` workflow expects to run — most dangerously when a
memory says "never do X" and the workflow's verification or TDD step needs to do X.
The conflict causes a workflow step to fail, stall, or produce an unreliable result,
and it's never obvious *why* until someone investigates. `work doctor` makes the
conflict visible before any ticket is picked up.

---

## Config layers to read

Read every layer in order. Don't skip a layer because it seems unlikely to have
conflicts — the interesting cases are often in the least-obvious place.

1. **Agent memory store** — the auto-memory index (if present) and each
   referenced memory file. The index is typically at
   `~/.claude/projects/<project-hash>/memory/MEMORY.md` or the session's
   memory path; follow any `@`-imports it references. This is the canonical
   source of "never do X" instructions that are invisible in the repo.

2. **`CLAUDE.md`** — the root file and every file it `@`-imports (they chain
   transitively; follow the full graph). This is the primary place for
   project-wide working agreements and constraints.

3. **`.claude/rules/**`** — every file in the rules tree (recurse; match
   `**/*.md`). Rules fire contextually based on the `paths:` frontmatter they
   carry; read them all to catch anything that fires during editing or test
   commands.

4. **`.claude/settings.json`** and **`.claude/settings.local.json`** — both
   files if they exist. Read:
   - `permissions.allow` and `permissions.deny` — tool/command allow lists and
     explicit denies. A deny on a command the workflow runs (e.g. a test runner,
     a VCS command, a tracker CLI) is a hard blocker.
   - `hooks` — pre/post-tool hooks. A hook that rewrites or suppresses a command
     can silently break a workflow step even without a `deny` entry.

5. **The config bus** (`.agent/PROJECT.md`, or the legacy path) — the workflow contract. Read it for:
   - blank or `TODO` fields (the workflow can't run without them),
   - the `Verification` commands — these are what the workflow will run to prove a
     step is done; any deny/hook/instruction that blocks them is a conflict,
   - the VCS and tracker adapter rows — any instruction contradicting the noted
     commands is a conflict.

6. **`.agent/work/workflow.md`** (if present) — the workflow overlay. Injected steps
   name their Detail refs; read those refs to understand what each step will
   attempt, and check those actions against the other layers.

7. **`domains/*.md`** (remaining domain files) — scan for instructions (often in
   "gotchas" sections) that forbid or alter the behavior of a workflow step —
   e.g. "never modify X", "always ask before running Y".

Read all layers before classifying conflicts. Cross-layer tension (a rule vs a
memory vs `CLAUDE.md`) won't surface unless you hold all layers at once.

---

## Conflict classes

Classify every finding into one of these five classes. Each finding gets its own
entry in the report.

### 1 — Workflow step contradiction
An instruction in any layer that forbids or materially alters an action a
workflow step needs to perform.

**Canonical example:** a memory entry "never run tests; the user runs tests" when
the bus's `Verification` command requires the test suite to run, or
when the workflow overlay's TDD contract step runs the test suite to confirm a
regression test fails.

Other examples: "never commit automatically", "always ask before pushing", "do not
call the tracker API directly" — each blocks a specific Phase 2 or Phase 3 step.

Detection heuristic: find every place the workflow *must* invoke a command or
make a call (verification commands from PROJECT.md, VCS commit from the VCS row,
tracker ops from the adapter, any step's Detail ref), then check all other layers
for an instruction that matches or contradicts it.

### 2 — Permission deny or blocking hook
A `permissions.deny` entry in settings that covers a command the workflow needs to
run; or a hook that rewrites or suppresses that command.

Check each entry against the verification commands, the VCS commit command, and the
tracker adapter commands from PROJECT.md. A deny on a broad pattern (e.g. `deny:
["Bash"]`) that would swallow a needed command is higher severity than a narrow
deny that only blocks an unrelated tool.

### 3 — Intra-project instruction contradiction
Two instructions from different layers that contradict each other, regardless of
the workflow — a rule file says "always run lint before committing" while a memory
says "never run lint automatically"; a `CLAUDE.md` constraint says "do not modify
file X" while a rules file for that path says to always update it on change.

Detection heuristic: look for polarity pairs — always/never, do/don't, run/skip —
on the same subject across different layers.

### 4 — Stale reference
An instruction naming a file, flag, command, path, or symbol that does not exist
in the repo. Stale references mislead both humans and agents — they create the
impression that a constraint or a tool is in place when it isn't.

Detection: for each instruction that names a concrete path, command, or symbol,
verify it exists (`find`, `which`, or a quick read). Flag those that don't.

### 5 — PROJECT.md gap
A blank, `TODO`, `TBD`, or missing required field in the config bus that
`work on` reads before proceeding. `work on` will either stall or fall back to
guessing if these are missing.

Required fields to check: project name, environment label, VCS row, tracker +
tracker prefix row, and the verification commands row. Flag each missing or
placeholder value separately.

---

## The shared config-bus checks come first

Read `${CLAUDE_PLUGIN_ROOT}/checks/BUS-CHECKS.md` and run **every** check in it before anything
below. Those are the checks all four tools in this stack run **identically** — vendored rather
than shared, because no plugin may read another's files and this is the only legal way to make
four tools agree.

Do not reinterpret them, and do not skip one because it looks like another tool's business:
reporting the whole `## Versions` table is the point, since it is the one place an adopter sees
every pending thing without running four tools.

The conflict classes below are `work`'s **own** additional checks — the instruction-layer scan
nothing else does.

## Pending work across the whole bus

Covered by check 5 of the shared spec — report the whole table, judge only your own rows, and
name each other row's declared command without assessing it. Not repeated here.

Three `work`-specific things worth calling out when present, because each is silent otherwise:

- **The bus is still at the legacy path** — `domains/PROJECT.md` rather than `.agent/PROJECT.md`.
  Name the migrate command; note the shim is temporary and will be removed.
- **A role is stale with no available command** — say which role, its stamp, and that the tool
  owning it is not installed here. That is the whole finding; do not guess a command name.
- **`domains/` exists but no doc-system is bound** — knowledge will not load. This is the known
  regression from the plugin split, and it is invisible at runtime apart from one line during a
  run, so a diagnostic that stays quiet about it is failing at its only job.

## Output format

Present a structured report. If no conflicts are found, say so in one sentence — and still report
pending versions if any, since "no conflicts" and "nothing outstanding" are different answers.

```
## Conflict scan — <project name or repo path>

### Summary
<N> conflict(s) found: <X> high, <Y> medium, <Z> low.
<One sentence on the most important finding, if any.>

---

### Conflict 1 — <class name>
**Severity:** high | medium | low
**Location:** `<file path>` (line N or section heading, if known)
**Conflicting text:** "<quoted excerpt>"
**Clashes with:** <which workflow step, PROJECT.md field, or other layer>
**Suggested resolution:** <described, not applied — e.g. "Remove or scope this
  memory to sessions outside of `work on`", "Add the test command to PROJECT.md's
  verification row", "Narrow the deny from `Bash` to the specific command you want
  blocked">

---

### Conflict 2 — …

---

### No conflicts found in: <layer list if some layers were clean>
```

**Severity guide:**
- **high** — would cause a workflow step to fail, stall, or silently produce an
  incorrect result (e.g. a deny that blocks the verification command, a memory that
  prevents the commit step, a blank PROJECT.md tracker row).
- **medium** — would degrade reliability or require a human workaround mid-run
  (e.g. an ambiguous rule that might fire during implementation, a stale reference
  in a step's Detail path).
- **low** — cosmetic or low-probability (e.g. a minor intra-project contradiction
  that rarely fires, an almost-stale reference that still resolves).

---

## How it runs

This is a read-only pass. The procedure is:

1. Derive the repo path (same method as `work on`: `git rev-parse --show-toplevel`,
   else the session's working directory).
2. Read every config layer listed above. For large repos, you may delegate the
   initial file-gathering to a read-only `Explore` subagent and keep only the text
   fragments that contain instructions (not code). Keep the main session light.
3. Classify every conflict, assign severity, draft a suggestion.
4. Present the report in the format above.
5. End with the next steps — the command for each finding worth acting on, in order, at most
   four — then: *"These are suggestions only. To act on any finding, ask me explicitly —
   `work doctor` makes no changes."* A scan that ends in a list of conflicts ends in homework;
   name what would clear each one.

No mutations at any point. No planning step. No Phase 2. The scan ends when the
report is presented.

---

## Suggestions are not automatic fixes

The suggestions in the report are descriptions of *what could be done*, written so
the user can make an informed decision. They are not tasks queued for execution.

After the report, if the user says "fix conflict 2" or "remove that memory entry",
treat it as a new explicit instruction and act on it then — not before.
