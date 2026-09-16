# `work update-workflow` — customize the workflow without breaking the spine

Use this when the user wants to (a) **integrate an existing workflow skill** into
`work on`, (b) **modify how a phase runs**, (c) **add a scenario** (a distinct kind of
ticket that runs a different set/order of steps), or record "**use skill X when working
tickets**". The output is a lean `.agent/work/workflow.md` *overlay* (created or edited).

The three phases are **invariant**. This procedure *augments* them — it never removes
Phase 1/2/3, and it never drops the domain-integration steps. Everything you add slots
*around* the core spine, not in place of it.

---

## What stays fixed (you may not edit these away)

- **The spine:** Phase 1 — Context & Planning, Phase 2 — Execute, Phase 3 — Wrap up.
- **Domain integration**, the whole point of the system: Step 1.0 domain pick, the Domain
  Loader (1.1), the Memory Curator (3.1a), the Domain Doc Updater (3.1b). Overlays slot
  around these; they never replace them.
- **The plan-mode gate** (`ExitPlanMode` before any mutation) and *orchestrate, don't do*.

If a request would gut any of the above, say so and propose a slot-around alternative.

---

## Refresh mode (`update-workflow refresh`)

Take this branch when the rest of `$ARGUMENTS` is `refresh`/`--refresh`, or the user says
"refresh the overlay", "upgrade the workflow to the new schema", or is acting on `work on`'s
stale-overlay warning. **Refresh is a migration, not a re-interview.** It re-expresses the
project's *existing* step library and scenarios in the current overlay schema — filling in
fields the older format lacked — and bumps the version stamp. It does **not** add, remove,
or reorder the user's steps; their workflow decisions are preserved exactly.

1. **Read** `.agent/work/workflow.md` (the existing overlay) and the canonical `Overlay schema
   version` from `templates.md`. If there's no overlay, there's nothing to
   refresh — tell the user and stop (they want `update-workflow` proper, or nothing).
2. **Diff the schema.** Compare the existing overlay against the current skeleton in
   `templates.md`. Identify what the current schema has that the overlay lacks —
   e.g. a per-step **effort** level, scenario **parallel-group** marks, any newly-added
   fields. Read this file's step 5/6 conventions for how those fields are meant to be set.
3. **Fill the gaps by the standing rules — don't reinvent the workflow.** For each existing
   step, derive the missing field from its already-recorded intent: assign **effort** by the
   same model+effort rule (`work on`'s "Model & effort selection"); within each scenario,
   mark adjacent steps that are mutually independent (disjoint files/outputs, no data
   dependency) as a **parallel group**. Keep every step id, model, slot, gate, detail-ref,
   and scenario sequence as they are — you're annotating, not redesigning.
4. **Show the upgraded overlay as a diff for approval.** Make clear this only adds the new
   annotations + the bumped stamp. `AskUserQuestion` to approve, or to adjust any
   auto-assigned effort/parallel call you got wrong. **Write nothing before approval.**
5. **Write** the regenerated `.agent/work/workflow.md` (step 8's stamp instruction applies — write
   the current canonical version). Report what fields were back-filled.

If, while reading, you find the overlay references a detail file that no longer exists or a
step whose intent is now unclear, surface that to the user rather than guessing — that's a
content problem refresh can't silently fix.

---

## Procedure (interview mode)

### 1 — Read the current shape
Read `on.md` (the canonical 3-phase orchestration — the spine you merge into)
and, if it exists, `.agent/work/workflow.md` (the current overlay: its step library + scenarios).

### 2 — Understand the request
- *"integrate <skill>"*, *"use <skill> when working tickets"* → fold a skill in (step 3).
- *"modify phase N"*, *"add a <step> step"* → a direct phase edit (skip to step 5 with the
  user's described step).
- *"for <kind> tickets, do …"*, *"hotfixes should skip X and add Y"* → a **scenario** (step 6).

### 3 — Investigate the source skill (and locate it)
Read the skill's `SKILL.md` + any step/reference files it points to. Extract its discrete
**steps and their intent** — what each produces and *why* it matters.

**Then check where the skill lives**, because portability depends on it:
- **In-project** — under `<repo>/.claude/skills/` or a committed plugin. Teammates have it
  on clone. The overlay can reference it by repo-relative path.
- **External** — a personal/global skill (`~/.claude/skills/…`) or an uninstalled one.
  Teammates won't have it, so the overlay must not depend on reading it. Go to step 4.

### 4 — External skill: make it portable (present options, don't assume)
An external skill carries load-bearing detail the overlay would otherwise lose — decision
rules, exact templates, per-case playbooks (the nuance that doesn't survive a one-line
summary). Don't leave the overlay pointing at a path teammates lack. Present, via
`AskUserQuestion`:

1. **Move the skill into the project** — copy it to `<repo>/.claude/skills/<name>/` and
   commit it. Teammates get it on clone; the overlay references the in-repo path. Choose
   this when the whole skill is worth sharing as-is.
2. **Extract the load-bearing context into in-project references *(preferred)*** — pull the
   nuances that compression would lose into `.agent/work/rules/<topic>.md` (committed,
   convention-layer). The step library references those files; the external skill is then
   optional enrichment, not a dependency. Choose this to keep the repo lean and avoid
   importing a whole skill for a few load-bearing rules.

For **extract**: for each injected step, ask "what would a dev produce *without* the skill,
and what nuance would they miss?" Write that missing nuance — and only that — into a
focused `.agent/work/rules/<topic>.md`. Keep it to the decision rules / templates /
playbooks; don't transcribe the skill. **Don't record provenance** — the extracted file is
now the in-repo source of truth; it shouldn't note which skill it came from. The step
library row then cites that file.

### 5 — Map steps to the spine
For each step the skill or request introduces, decide:
- **Which phase** — read-only analysis/planning → 1; making + verifying changes → 2;
  commit / comment / learnings / follow-ups → 3.
- **Where it slots** relative to core steps (before/after which one), without displacing
  domain integration.
- **Which model tier *and* effort level**, by the *same* two-dial rule `work on` uses
  everywhere (see its "Model & effort selection"): model — pure transform → **haiku**;
  synthesis/pattern-matching → **sonnet**; architectural judgment → **opus**. Effort —
  mechanical/single-path → **low**; real synthesis with a clear path → **medium**; genuine
  search over alternatives/tradeoffs → **high**. Default one notch lower than instinct on
  both dials; upgrade only where the lower setting would struggle. Effort isn't a spawn
  parameter — `work on` actuates it with a thinking keyword in the step's prompt (low →
  none, medium → `Think hard.`, high → `Ultrathink.`), so just record the level.
- **Detail ref** — where the step's full detail lives: an in-repo skill §, or the
  `.agent/work/rules/<topic>.md` you extracted. The overlay *references* it; it never
  copies the body, so there's a single source of truth.
- **Can it run in parallel?** — note whether the step is independent of its neighbours
  (disjoint files/outputs, no data dependency) so it can run concurrently with them, or
  whether an ordering constraint forces it serial. Surfacing this here is what lets a
  scenario mark steps as a parallel group rather than a strict sequence.

**Fold in, don't bolt on.** If an incoming step overlaps a core step (e.g. the skill's own
"analyze the ticket" duplicates the Ticket Analyst), *merge* and note the merge — don't run
both.

### 6 — Express as a step library + scenarios
Projects often have several kinds of ticket that share steps but select/order them
differently (a bug runs a root-cause gate + TDD; a hotfix may skip QA; a feature adds a
design-review step). Model this DRY-ly:

- **Step library** — define each injected step *once*: an id, its intent, model + effort,
  gate (does it pause for the user?), and its detail ref. Defined once, reused by any scenario.
- **Scenarios** — each is a *match condition* (issue type / branch / keywords) plus an
  *ordered list of step-ids with slots*. Same step reused across scenarios without
  restating it; a different order is just a different sequence. Where consecutive step-ids
  are mutually independent (per the parallel flag in step 5), mark them as a **parallel
  group** rather than a sequence, so `work on` fans them out in one message. A ticket that
  matches no scenario runs the plain spine.

Keep core spine steps implicit (they always run) — scenarios list only the injections and
where they slot, so the overlay stays small.

### 7 — Present the combined flow for confirmation
For **each affected scenario**, print the full merged flow — every core step *and* every
injected step, in execution order, each tagged with model + effort and (for injected ones)
its source/detail-ref. Make crystal clear which steps are core (unchanged) vs injected. Then
call `AskUserQuestion` to approve, reorder, retier, or drop injections per scenario. **Edit
nothing before approval.**

### 8 — Write the overlay (and any extracted refs)
On approval:
- Write/update `.agent/work/workflow.md` from the skeleton in `templates.md`: the
  integrated-skills reference table, the **step library**, and the **scenarios**. Lean —
  ids, slots, refs; never copied step bodies.
- **Classify every step as `slot` or `hook`.** A step that adds behaviour is a `slot`; one that
  replaces a core step's behaviour is a `hook`. If a proposed step would hook a **gate** or a
  **domain-integration step**, say so and stop — that overlay is invalid and the validator will
  reject it. Offer the slot form instead (run beside it, not instead of it).
- **Write the `## Step schema — normative` section verbatim** from `templates.md`. It is not
  commentary: it is the published contract that lets another plugin — or a person with no
  access to this skill — author a valid overlay by reading only the repo. Dropping it to save
  space breaks that promise silently, since the file still parses.
- **Stamp the schema version.** Read the canonical `Overlay schema version` from
  `templates.md` and write that exact number into the overlay's
  `Overlay schema version:` header line (replacing `{N}`). This is what lets `work on`
  detect when a project's overlay has fallen behind a later skill version — without it the
  overlay reads as pre-versioning and will always warn as stale.
- If you chose extract in step 4, write the `.agent/work/rules/<topic>.md` files (the
  load-bearing nuance only).
- If you chose move, ensure the skill is under `<repo>/.claude/skills/` and reference that
  path.
- Ensure the bus's `## Artifacts` `Ticket flow` row names `.agent/work/workflow.md` (add the row
  if missing), and — when the overlay has extracted rules — a `Ticket flow rules` row naming
  `.agent/work/rules/`. **Register the directory even though it looks like an internal detail:**
  the knowledge system's own files reference these rules by path, and the only way its owner can
  repoint them after a move without learning `work`'s layout is to read where they went from
  the registry. An unregistered path is one another plugin has to guess at, and guessing is
  what the registry exists to remove. That registry row is where the overlay's path lives — there is no separate
  `Workflow overlay` config row to keep in step, and there deliberately isn't, because two
  places recording one path are two places that can disagree.

Report what changed, and confirm the spine + domain integration are preserved.
