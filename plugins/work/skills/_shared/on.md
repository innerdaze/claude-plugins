# `work on <TICKET>` — deliver a tracked ticket end-to-end

This is an **orchestration procedure**. The main session stays lean and delegates
each phase to a subagent with a model sized to the task. Do not do the work yourself
in the main session — spawn subagents and synthesize their results.

Your **first action** — before entering plan mode, spawning anything, or normalizing
the ticket id — is to read the **config bus** from the repo root. It supplies every
project-specific value this procedure needs. `work on` is environment-, VCS-, and
tracker-agnostic *because* it reads that file; if it's missing or has blank/`TODO`
fields, the project hasn't been set up — tell the user to run `work init` first (or fill
the gaps), and don't proceed on guesses.

**Where the bus is: `.agent/PROJECT.md`.** One place, always. Do not look anywhere else,
do not accept a configured alternative path, and do not fall back to a private copy — with
the single, expiring exception below.

> **Legacy-path shim.** If `.agent/PROJECT.md` is absent **and** `domains/PROJECT.md`
> exists, read the old path and print one line: *"config bus is still at
> `domains/PROJECT.md`; run `work migrate` to move it."* Then carry on normally —
> non-blocking.
>
> This is the **only** permitted second location, and it is bounded on purpose:
> - **exactly one legacy path** — `domains/PROJECT.md`, not a list, not a pattern, and
>   never "wherever a `PROJECT.md` turns up";
> - **read-only** — the shim never writes either path; `work migrate` does the moving;
> - **it always says so** — every read prints the line, because a silent fallback is
>   indistinguishable from searching;
> - **it expires.** The shim ships with the bus migration and is **removed in the
>   following minor**. Removal is gated on a doctor check reporting repos still on the
>   legacy path — not on anyone remembering;
> - **it sets no precedent.** A future legacy path gets its own decision; this exemption
>   does not extend to it.
>
> A shim with no expiry is the searching this rule exists to stop.

**Everywhere below, "`PROJECT.md`" means whichever path you resolved here.** Resolve once, at
the top, and carry the answer — re-deciding mid-run is how two halves of one invocation end up
reading different files.

`PROJECT.md` deliberately does **not** store a repo path — it's machine-specific and
the file is checked into the repo. Determine the repo path at runtime instead: run
`git rev-parse --show-toplevel` (or fall back to the session's working directory if
not a git repo). Subagents start with no cwd, so you paste this absolute path into
every subagent prompt as `<repo path>`.

**Version check (do this as you read the bus).** This is a **pure integer compare — read no
migration files.** Prefer the **`## Versions`** section and take the rows owned by `delivery`;
if that section is absent, fall back to the legacy `Domain system version` row (missing ⇒ treat
as 1). Read the two integers from `templates.md` (same
directory as this file): the canonical **Domain system version** and the **Minimum
supported version** (floor). Then, in one line, non-blocking:
- stamp **≥** canonical → say nothing.
- floor **≤** stamp **<** canonical → "⚠️ domain system is v{stamp} (skill is v{canonical});
  run `work migrate` to apply pending migrations. Best done by **one** dev on a **separate**
  branch/PR and merged on its own — it edits shared repo files (`CLAUDE.md`, `PROJECT.md`),
  so several people migrating in parallel just collide."
- stamp **<** floor → "⚠️ delivery scaffolding is v{stamp}, below the minimum supported
  v{floor}; re-scaffold rather than migrate." Name the re-scaffold command from the bus's
  `## Commands` row for `delivery` if one is declared, else `work init`. (Too far behind to
  chain migrations.)

**Only report on components you own.** Other rows in `## Versions` belong to other owners; a
stale one is reported by whoever runs a migration or a doctor, naming the command that row's
owner declared — never by guessing on their behalf here.

Don't block or auto-apply — the warning is a prompt; `work migrate` (or `work init`) is
where the change happens. Do **not** open `migrations/` here; naming individual migrations
is `work migrate`'s job. (This is coarse, scaffolding-level drift; the overlay check below
is the fine-grained, workflow-only one — the two are independent.)

**Then check for a workflow overlay.** If `.agent/work/workflow.md` exists, read it. It holds a
**step library** (each injected step defined once) and **scenarios** (each a match
condition + an ordered step sequence).

**Staleness check (do this as you read the overlay).** The overlay carries an `Overlay
schema version: N` stamp near its top (older overlays, written before versioning, have
none). Read the skill's *current* schema version — the `Overlay schema version` declared in
`templates.md` (same directory as this file). If the overlay's stamp is missing
or lower than the current version, the overlay predates the latest skill conventions (e.g.
it may lack per-step effort levels or parallel-group marks). **Warn the user in one line and
keep going** — e.g. "⚠️ `.agent/work/workflow.md` is schema vN (skill is vM); run `work
update-workflow refresh` to upgrade it." Don't block or auto-edit it: the core spine here is live
and already applies the current model+effort+parallelisation rules, so a stale overlay only
means its *injected* steps miss the newest annotations — degraded, not broken. Pick the scenario whose match condition fits this
ticket (issue type / branch / keywords); if none match, run the plain spine. Weave that
scenario's injected steps into the phases at the slots it specifies, using the model +
effort levels the library lists. For a step's full detail, read its **Detail** ref — an in-repo skill §
or a `.agent/work/rules/*.md` file (the overlay references detail, never inlines it).
The overlay only *adds* steps — the phases, their order, and every domain-integration step
here remain exactly as written. If the user asks mid-flight to "use skill X" for this
ticket, do the same mapping inline (investigate the skill, slot its steps into the right
phase with the right model + effort) and offer to persist it via `update-workflow`. The
three-phase spine is never up for negotiation; see `update-workflow.md`.

The ticket id is the rest of `$ARGUMENTS`. Normalize a bare number (`42`) to
`<PREFIX>-42` using `Prefix` from the bus's `## Tracker` (no `Prefix` row ⇒ use the id as
given). If `$ARGUMENTS` has no id and the project has a tracker, ask which ticket. If
`## Tracker → Kind` is `none`, ask the user to describe the task instead and skip every
fetch/comment/status step below.

## Config you read from PROJECT.md (substitute before pasting into subagents)

| Placeholder | Source in PROJECT.md |
|---|---|
| `<repo path>` | **Not in PROJECT.md** — derived at runtime (`git rev-parse --show-toplevel`, else cwd). Pasted into every subagent prompt (subagents start with no cwd). |
| `<PROJECT NAME>` | `## Project → Name`. |
| `<ENV>` | `## Environment → Stack` — e.g. "React 18 (Vite + TS)", "Python 3.12 (Django 5)". Sets the vocabulary. |
| `<PREFIX>` | `## Tracker → Prefix` (row absent ⇒ no prefix). |
| `<VCS>` / `<commit workflow>` | `## Version control → Kind` and `Commit workflow`. |
| `<TRACKER>` | `## Tracker → Kind` and `Access` — which tracker, and the MCP namespace or CLI that reaches it. |
| `<verification>` | `## Verification → Proven by` — the commands that prove "done" before a step completes. |

**Tracker calls are not in the bus.** The bus says *which* tracker and *how it is reached*;
the operations — fetch, read comments, comment, status, create — are in `tracker-ops.md` (this
directory), by `Kind`, with `<NS>` replaced by `Access`. Read it only when `Kind` is not `none`.
Wherever a step below says "fetch the ticket", "post a comment" or "set status", that file is the
adapter.

## Model & effort selection — why each tier

Each subagent spawn carries **two** dials: which model, and how much it should think before
answering. Set both — they're independent. Model picks the raw capability; effort picks how
hard that model deliberates. A cheap model thinking hard still can't do what it structurally
can't; an expensive model that barely thinks wastes money deliberating over a lookup. Match
each to the task.

The model is a spawn parameter (`model: …`). **Effort is not a spawn parameter** — there is
no per-subagent effort knob — so you actuate it the one way that works through the spawn: a
**thinking-budget keyword in the subagent's prompt.** Open the prompt with the keyword the
effort level maps to:

| Effort | Keyword to put in the prompt | When |
|---|---|---|
| **low** | *(none — omit the keyword)* | mechanical, single-path work |
| **medium** | `Think hard.` | real synthesis with a mostly-clear path |
| **high** | `Ultrathink.` | genuine search over alternatives / cross-system tradeoffs |

**Model — raw capability:**
- **Haiku** — cheap, fast, good at pure transformation (read file → summarize,
  classify a note). Use where correctness comes from following a template, not judgment.
- **Sonnet** — balanced. Synthesis needing pattern recognition over moderate context:
  ticket analysis, routine implementation, code search.
- **Opus** — best reasoning. Use only where architectural judgment or multi-system
  tradeoffs move the needle: planning a non-trivial ticket, implementing changes that
  span subsystems or touch persistence/integration boundaries.

**Effort — how much it deliberates** (the meaning behind each keyword above):
- **low** — mechanical, single-path work: the answer follows from a template or a fixed
  file list, so extra deliberation buys nothing and just costs latency/tokens.
- **medium** — real synthesis with a mostly-clear path: routine implementation, ticket
  analysis, scoping a follow-up. The default for most work.
- **high** — genuine search over alternatives, tradeoffs, or cross-system consequences:
  planning a non-trivial ticket, implementation that spans subsystems. Reserve it — high
  effort on easy work is the same waste as opus on a lookup.

Default **one notch lower than instinct on both dials**; raise a dial only when the lower
setting visibly struggles. Each subagent header below states its recommended `model` +
`effort`: set `model` on the spawn, and open that subagent's prompt with the effort's
mapped keyword (low → nothing, medium → `Think hard.`, high → `Ultrathink.`).

---

## Phase 1 — Context & Planning (read-only)

Enter plan mode via `EnterPlanMode` immediately. No edits, builds, or mutating
tracker calls until the user approves the plan.

**The domain steps below (1.0 pick + 1.1a Domain Loader) run on every ticket,
regardless of size or how familiar it looks. There is no small/known/trivial
fast-path.** Phase 1 *closes* by emitting the **Domain integration** block in the plan
(Step 1.4) — if you can't fill that block, you haven't done Phase 1, so don't call
`ExitPlanMode`. Watch for the three ways this step talks you out of itself — each is the
bug, not a shortcut:

- *"It's a small / one-file / already-understood ticket."* Size never licenses skipping.
  The spine is size-invariant; a one-line fix still reads INDEX.md and loads its domains
  (often the fastest case — "no topic match → always-load only").
- *"My Explore / Analyst pass already covers this ground."* It doesn't. **An `Explore`
  subagent is not the Domain Loader** — even though the Loader is spawned *as* one. Explore
  reads the code fresh; the Loader front-loads *this project's distilled conventions and
  named gotchas* so you explore with intent and don't rediscover known traps by failing
  first. Running Explore/Analyst is not a substitute for running the Loader.
- *"The domain knowledge is already in my context (from recalled memories)."* Recalled
  memories are not this project's domain files, and betting that they overlap is luck, not
  method — it is exactly the failure this step prevents. Load the domains anyway.

### Step 1.0 — Pick domains from the manifest (skip if there is no knowledge system)

**First, resolve the binding.** Read the **`Doc system`** row in the config bus, then load the
adapter it names:

1. a project-local adapter at the path the row gives, else
2. the shipped fallback for that `kind` — `${CLAUDE_PLUGIN_ROOT}/adapters/doc-system/<kind>.md`,
   which for an unbound project is `none.md`.

**Read its `## Capabilities` block before calling anything.** An operation listed `unsupported`
is not attempted; one listed `costly` is narrowed first rather than swept. That block is what
makes degradation visible instead of silent, and skipping it is how a caller ends up reporting
an empty answer as a real one.

Then, with the binding loaded: look for a `## Artifacts` row owned by `knowledge` and read its
path. No row, or a path that does not exist → **this project has no knowledge system.** Say so
once —
*"no project memory bound; working from the ticket and the code"* — and skip to Step 1.0b. Do not
scan for a likely folder, and do not treat its absence as a setup error: ticket delivery works
without it, and a plugin that hard-failed because another is missing would be the rule this
ecosystem exists to keep.

**If there is one**, read its manifest and decide which files are relevant:

1. Always include the always-load rows. (If INDEX.md describes a two-layer setup —
   general files shipped by a plugin/framework plus project files — include both
   layers, general first.)
2. Fetch the ticket *title* (the tracker's fetch op) so you have something to match.
3. Walk the topic-triggered rows; include a row if any trigger keyword/symbol appears
   (case-insensitive) in the title or id. Err toward inclusion when ambiguous, but
   stay under ~5 topic domains. If you'd load 8+, the ticket is too broad — say so.
4. If the title is too thin to classify, fetch the description and re-match.

Output one explicit list of file paths — passed verbatim to the Domain Loader. Don't
make the subagent re-decide.

**This selection is provisional.** It's based only on the ticket title/description, and
scope routinely widens as the work is understood. Whenever it does, re-run the matching —
see the *Domain re-check* below.

### Step 1.0b — Resolve the intent layer, if this project has one

Load the intent binding the same way — project-local adapter, else
`${CLAUDE_PLUGIN_ROOT}/adapters/intent/<kind>.md` (`none.md` when unbound) — and read its
`## Capabilities`: with `locate()` unsupported there is nothing to do here and **nothing to say**,
which is the normal case.

Otherwise read the **`## Artifacts`** table in the bus. If a row's **Owner** is `intent-layer`,
note its path; the Planner reads it in Step 1.3. Match on the owner role id, not on the artifact's
name or path — the role id is stable across renames and handovers, and the name is not.

If the row's path does not exist, treat the intent layer as **absent and say so once**. Do not
go looking for it: scanning for a likely folder is the coupling this table removes.

**Never hardcode a path here.** The intent layer's folder name belongs to whatever tool owns it,
and guessing it would couple `work` to another tool's artifact. The row is the only source. No
`## Artifacts` table, or no intent row → **this project has no intent layer** → continue, and say
nothing further about it.

Why it matters: the intent layer states what the project is *meant* to be, and it **outranks the
knowledge layer and the code**. A ticket can contradict it, and that contradiction is worth more
than any single ticket.

`work` **never writes to it.** Not to soften a statement, not to add a note, not even to record
that a ticket disagreed. Reading only.

### Step 1.1 — Domain Loader, then Ticket Analyst (serial)

These two are **not** independent: the domain files are a map of *how this codebase
is laid out* (where things live, naming conventions, named gotchas). That map is
exactly the prior that lets the Analyst explore with intent instead of grepping the
repo blind. So run the Domain Loader **first** and feed its summary into the Analyst.
The Loader is haiku over a fixed file list — fast and cheap — so the extra hop costs
little, and the summary it produces is reused again by the Planner and Implementer.
The Loader is spawned *as* an `Explore` subagent but is **not interchangeable with your
open-ended exploration**: it reads only the selected domain files and returns their
distilled rules/gotchas. Skipping it because "the Analyst will read the code anyway"
is the mistake — the Analyst reads code; the Loader hands over what the project already
knows about that code.

**Step 1.1a — Domain Loader** — `subagent_type: Explore`, `model: haiku`, `effort: low`
(a fixed file list summarized to a template — no deliberation to do)

```
Read these domain files and return a single consolidated summary (≤300 words)
covering proven patterns, gotchas, and conventions relevant to <ENV> work in this
repo. Skip any file that doesn't exist — don't retry. Read nothing outside this list.

Files (orchestrator-selected from the knowledge manifest):
<paste explicit file paths from Step 1.0>

The ticket is <TICKET-ID> — <one-line title>.

Output: one ## section per domain you loaded (use the domain name as the heading),
bullets underneath.
```

**Step 1.1b — Ticket Analyst** — `subagent_type: general-purpose`, `model: sonnet`,
`effort: medium` (synthesis over the repo, but the path is exploration not architecture).
Spawn after the Loader returns, with its summary pasted in.

```
Analyze ticket <TICKET-ID> for <PROJECT NAME> (<ENV>, repo at <repo path>). You have
Read, Grep, Glob, and this project's tracker access.

== Domain context (the codebase map — use it to target your exploration) ==
<paste Domain Loader summary verbatim>

1. Fetch the ticket: <tracker fetch op from PROJECT.md, e.g. gh issue view <ID> --comments>
2. Read every comment — comments are between-session memory; read them all carefully.
3. For every file, symbol, module, or system named in the ticket/comments, locate it
   in the repo and read enough to understand what's really being asked. Use the domain
   context above to go straight to the right area — where a domain names the owning
   module/convention, start there rather than grepping blind; only widen the search
   when the map doesn't cover it.
4. If the ticket links other tickets/docs, fetch the relevant ones.

Return a structured report (≤500 words):

## Goal
One sentence — what does "done" actually mean?
## What the ticket says
Key points + any acceptance criteria.
## Comment history (between-session memory)
Prior attempts, decisions, dead ends, scope changes. Quote dates/authors where useful.
## Relevant code
file:line refs for the systems the ticket touches. What's already there.
## Ambiguities
Anything genuinely unclear that would change the approach. Phrase as questions.
## Hidden complexity
What the ticket understates — integration points, data/persistence touchpoints,
cross-module dependencies, etc.
```

### Domain re-check (reusable — run on any rescope; a no-op with no knowledge system)

The Step 1.0 selection is a first guess from the ticket text. Scope almost always widens as
the work is understood — and the loaded domain set must widen with it, or every downstream
subagent works half-blind on the newly-in-scope system. **Whenever the effective scope
changes, re-run domain matching before spawning the next subagent.** Cheap to do, expensive
to skip.

**Triggers** (non-exhaustive — treat any scope-widening event as one):
- The Analyst's *Relevant code* / *Hidden complexity* (Step 1.1b) names a system, module, or
  symbol that maps to a domain you didn't load.
- An `AskUserQuestion` answer or a mid-session instruction **rescopes** the ticket — e.g.
  "fix the root cause too", "also handle the persistence case", "do both" — into territory a
  new domain covers.
- The Planner's approach (Step 1.3) touches files outside the loaded domains.
- The Implementer STOPs and reports the work fans out into another module/system (Step 2.3).

**Procedure:**
1. Re-walk the knowledge manifest's topic triggers against the **new** scope signal (the
   newly-named systems/modules/symbols/keywords), exactly as in Step 1.0.
2. Diff against the domains already loaded this session. If nothing new matches, continue —
   zero cost.
3. For each newly-relevant domain, spawn a **Domain Loader** (Step 1.1a form, `Explore` /
   haiku / effort low) over just the *new* files. Fold its summary into the running domain
   context (append — don't reload what's already summarized).
4. Pass the augmented domain context into the next subagent you spawn. A full Analyst re-run
   is usually unnecessary — the Planner/Implementer just receive the fuller context — but if
   the rescope is large enough to invalidate the analysis, re-run the Analyst too.

### Step 1.2 — Decide whether to ask the user a question

Read both reports. If the Analyst surfaced an ambiguity where a wrong guess costs
real work, ask one focused question. Otherwise make a reasonable assumption and call
it out in the plan.

**Run the *Domain re-check* now** — potentially twice: once against the Analyst's *Relevant
code* / *Hidden complexity* (it often names systems the title never hinted at), and again
after any `AskUserQuestion` answer that widens scope, before you brief the Planner. Load any
newly-relevant domains so the Planner plans with full context.

### Step 1.3 — Spawn the Planner

**Planner** — `subagent_type: Plan`, `model: opus`, `effort: high` (the one step that is
pure architectural search over alternatives and tradeoffs — spend the deliberation here)

```
Design an implementation plan for ticket <TICKET-ID> in <PROJECT NAME> (<ENV>, repo
at <repo path>). You can read files but must not edit. The user reviews your plan
before any work begins.

== Ticket analysis ==
<paste Ticket Analyst report verbatim>
== Domain context ==
<paste Domain Loader summary verbatim>
== Assumptions to use ==
<list any assumptions you decided on the user's behalf>
== Intent layer ==
<if Step 1.0b found an intent row: name the path and the docs relevant to this ticket.
 Otherwise write "none — this project has no intent layer" and skip the section below.>

As you order the steps, actively look for **parallelisation opportunities** — steps
that touch disjoint files and share no data dependency can run concurrently instead of
serially, and that is how Phase 2 will execute them. Don't force it: serialise anything
with a real ordering constraint (B reads what A writes, B edits A's files). Identifying
the independent groups up front is what lets the orchestrator fan out implementers in one
message rather than one-at-a-time.

Produce a plan with these sections:
## Goal
## Approach   (the strategy; name alternatives considered and why this one)
## Steps      (ordered, concrete, scoped to this ticket; each step names files it touches
              and, where it depends on an earlier step, says which one)
## Parallelisation   (group the steps into independent work-streams that can run
              concurrently — disjoint files, no data dependency — vs. what must stay
              serial and why. If everything is serial, say so in one line.)
## Intent conflicts   (only if the project has an intent layer: does this ticket contradict
              anything stated there? Name the doc and the statement, and what the ticket would
              have to do instead. "None" is the normal answer and takes one line. Do NOT resolve
              it, soften it, or edit the intent layer — you are flagging it for the human at the
              approval stop, which is where it gets decided.)
## Files to touch
## Risks / open questions
## Out of scope   (what you're deliberately not doing — prevents drift)
## Verification  (how we'll know it works, using this project's checks: <verification>)

If the ticket is too large to plan confidently, propose a smaller first slice and say so.
```

When the Planner returns, if its approach touches files outside the loaded domains, run the
*Domain re-check* before Phase 2 so the Implementer inherits the fuller context.

### Step 1.4 — Present plan via `ExitPlanMode`

Pass the Planner's output to `ExitPlanMode` for approval. Don't modify it unless the
user asks — **except** that the plan must carry a **Domain integration** block so the
domain steps are visible and self-verified (same "emit the artifact" shape as the
Implementer's STOP block later). Prepend it if the Planner didn't include it:

```
## Domain integration
- Picked from INDEX.md: <explicit domain file paths>   (or: no topic match → always-load only)
- Domain Loader summary: obtained ✓
- Intent layer: <path from the Artifacts table, or "none registered">
```

**An intent conflict is surfaced here, not resolved here.** If the plan's *Intent conflicts*
section names one, say so plainly when you present the plan — this is the moment a human is
already reading, which is the whole reason it lands here rather than interrupting earlier.
Approving the plan is the decision. `work` does not adjudicate intent and does not edit the
intent layer either way.

**Gate:** if you cannot fill both lines truthfully — a real `INDEX.md`-derived selection
and an actual Loader summary in hand — Phase 1 is **not** complete. Go back and run
Step 1.0 / 1.1a; **do not call `ExitPlanMode`.** "always-load only" is a valid, fast
answer for a ticket with no topic match — but it still means you read `INDEX.md` and ran
the Loader over the always-load rows, not that you skipped the step.

---

## Phase 2 — Execute (after plan approval)

Leave plan mode. The orchestrator drives but still delegates the heavy lifting.

### Step 2.1 — Track tasks

Create one `TaskCreate` per step in the approved plan. Mark each complete as it's
done — don't batch.

### Step 2.2 — Spawn the Implementer(s)

Read the plan's **## Parallelisation** section. If it names independent work-streams
(disjoint files, no data dependency), spawn one Implementer per stream **in a single
message** so they run concurrently — pass each only the steps for its stream, and tell
each which files are off-limits (the other streams' files) so they stay in their lane.
If the streams are close enough that a stray edit could collide, give each
`isolation: "worktree"` so they edit isolated copies, then reconcile the diffs yourself
before verifying. When the plan says everything is serial, spawn a single Implementer.

**Implementer** — `subagent_type: general-purpose`, model + effort by scope:
- **sonnet, effort: medium** — single-module change, follows existing patterns, small delta.
  The plan already did the hard thinking; the Implementer mostly executes it.
- **opus, effort: high** — cross-module, touches persistence/integration boundaries, or
  needs real architectural judgment mid-implementation.

When in doubt start with sonnet/medium; if it returns merely confused but the plan still
holds, re-spawn with opus/high and pass the prior result. **If the Implementer STOPs, don't
just re-spawn — run the STOP loop in Step 2.3**, which decides whether to reload
domains and retry, or to loop all the way back through re-plan + re-approval.

```
Implement ticket <TICKET-ID> in <PROJECT NAME> (<ENV>, repo at <repo path>). Follow
the approved plan exactly. If you discover the plan is wrong or scope must expand
materially, STOP and return what you found rather than improvising. When you STOP,
classify it so the orchestrator can route correctly:
- **(A) additive** — a new adjacent system is now in scope, but the planned approach
  still holds; you just need context you didn't have.
- **(B) invalidating** — the planned approach itself is wrong, or scope expands
  materially enough that the plan must change.
State which, and why.

Version control here is <VCS>. <If not git: e.g. "Do not run git commands.">
Do not commit — the orchestrator handles that (<commit workflow>).

== Approved plan ==
<paste plan verbatim>
== Domain context ==
<paste Domain Loader summary verbatim>
== Ticket analysis ==
<paste Ticket Analyst report verbatim>

Work through the steps. For each, edit the relevant files, then run the verification
the plan specifies (<verification>) before moving on.

If you STOP early, return instead:
## STOP class   (A additive / B invalidating)
## What you found   (the system/constraint that triggered the STOP, with file:line)
## Impact on the plan   (which steps or which part of the approach is affected)
## Partial progress   (what you did / deliberately did NOT change)

When done, return:
## What changed   (file-by-file)
## Verification run   (what you ran and what it showed)
## Surprises   (anything that diverged from the plan, even small — be specific)
## Suggested commit message   (one-line conventional commit referencing <TICKET-ID>)
## Follow-ups   (anything that came up but is out of scope)
```

### Step 2.3 — Handle an Implementer STOP (rescope loop)

A STOP is the Implementer doing its job — it hit something the plan didn't cover and
refused to improvise. Don't just re-run it: route by the **STOP class** it returned, because
the two classes cost very differently and re-implementing against a stale plan burns a whole
Implementer pass and can leave a bad diff on disk.

**Class A — additive fan-out** (new adjacent system in scope, planned approach still holds):
1. Run the *Domain re-check* for the newly-named system; fold its summary into the context.
2. Re-spawn the Implementer with the augmented context and the prior STOP report pasted in,
   escalating model/effort (Step 2.2 tiers) if the fan-out added real complexity.

No re-plan, no re-approval — the strategy didn't change, only the context grew.

**Class B — plan invalidated** (the approach itself is wrong, or scope expanded materially):
the plan is now stale, and plan mode is a hard gate, so re-implementing against it would just
hit the same wall. Loop back through planning:
1. Run the *Domain re-check* for any newly-named system.
2. `EnterPlanMode` and re-spawn the **Planner** (Step 1.3 form, `opus` / `effort: high`),
   passing the original plan, the Implementer's STOP report **verbatim**, the augmented
   domain context, and the Analyst report. Ask for a revised plan (with a fresh
   **## Parallelisation** section).
3. Re-present via `ExitPlanMode` for approval — a materially changed approach means new
   mutations, which the user must re-authorize.
4. Revise the `TaskCreate` list (Step 2.1) to match the new plan.
5. Leave plan mode and re-spawn the Implementer against the approved revised plan.

**The loop.** This is a cycle:
`implement → STOP → rescope + re-domain → (Class B: re-plan → re-approve) → re-implement`,
repeating until the Implementer returns a clean *## What changed* / *## Verification run*.
**Let it run while it's making progress** — a lap that completes new steps, narrows the
problem, or STOPs for a *different* reason is the loop working as intended, and how many laps
that takes is mostly a function of how well-specified the ticket was, not a failure. Don't cap
it on a fixed count.

What you *do* watch for is **thrashing**: the loop hitting the *same* wall with no forward
progress — an identical STOP, or a Class B re-plan that STOPs the same way again. That's the
signal the plan is fundamentally off or the ticket is underspecified. When you see it, **pause
and surface it to the user** with the options — keep going, rewrite or split the ticket, or
stop — rather than silently looping or unilaterally abandoning the workflow. It's a checkpoint
for the user's judgment, not an enforced halt: repeated same-wall STOPs often *do* mean the
ticket needs a rewrite, but that's a suggestion, and the user may well say continue.

**When the class is ambiguous** (the Implementer didn't label it, or you disagree), treat it
as **Class B**. Re-planning a change that only needed a reload costs one Planner pass;
re-implementing against an invalidated plan costs a wasted Implementer pass *plus* the risk
of a bad diff — so bias toward the safer, costlier branch.

---

## Phase 3 — Wrap up (after the Implementer reports back)

The diff is on disk but nothing is preserved as learning, committed, communicated, or
tracked. This phase converts "code on disk" into "shipped + remembered + followed up
on." Skipping steps costs us: uncommitted code drifts, undocumented gotchas get
re-hit, out-of-scope discoveries get lost.

The phase ends with a report to the user, and it is short: what shipped, what is
outstanding, and **the next steps — commands in order, at most four, or one line saying
the ticket is done and nothing is pending.** The phase's own workings are above it in the
transcript; repeating them buries the part they have to act on.

Order: capture learnings (3.1) → commit (3.2) → tracker comment (3.3) → follow-ups +
status (3.4). Curator runs before the Updater (it feeds it); the Updater runs before
commit (so doc edits land in the commit); commit before the comment (so it can cite the
commit id); status change last, with user permission.

### Step 3.1a — Memory Curator — `subagent_type: general-purpose`, `model: haiku`, `effort: low`

Pass the Implementer's "Surprises" and any noteworthy Analyst findings not in the codebase.

```
Classify each note as TICKET_COMMENT (matters for this ticket only) or AUTO_MEMORY
(matters across many future sessions in this repo).

AUTO_MEMORY — helps a *different* future task: user preferences, repo-wide decisions,
broadly-applicable gotchas, external-system references, tooling quirks.
TICKET_COMMENT — tied to <TICKET-ID>: why approach A over B here, dead ends, partial
progress, this ticket's investigation findings.

Notes:
<paste notes, one per line>

Return JSON:
{ "ticket_comment": ["…"],
  "auto_memory": [ {"slug":"kebab-name","type":"feedback|project|user|reference","body":"…with Why:/How to apply: if feedback/project"} ] }
```

Save each `auto_memory` entry to your memory store and index it. Hold `ticket_comment`
items for Step 3.3.

### Step 3.1a-i — Check shared knowledge before authoring any (skip if unbound)

Read the **Shared knowledge** row in `PROJECT.md`. If it is `none` or absent — **skip this
step entirely and continue**. Most projects have no shared-knowledge service, and their wrap-up
is unchanged.

If it is bound, load its adapter the same way — project-local first, else
`${CLAUDE_PLUGIN_ROOT}/adapters/shared-knowledge/<kind>.md` — read its `## Capabilities`, and
then for each topic the Curator wants to record, ask what already exists on that topic — approved entries **and** anything pending — and put the answer in
front of the Domain Doc Updater below.

This is the one moment `work` is about to *author* knowledge, which is why the check belongs
here and not earlier: a duplicate is cheaper to not write than to find later.

**Three rules, because this is a seam and not a feature:**

- **`work` does not know which service this is.** It calls the binding by the operations the row
  declares. A row naming a specific product is configuration, not a dependency, and nothing in
  this skill may branch on *which* service answered.
- **It informs; it never blocks.** An overlap does not stop the write. It is reported, and the
  Updater decides whether to record a local variant, narrow the entry to what is genuinely
  project-specific, or skip it as already covered.
- **Unreachable is not an error.** Service down, misconfigured, or slow → note it once and carry
  on. A wrap-up that fails because a knowledge service is unavailable would make that service a
  dependency for delivering a ticket, which it must never be.

### Step 3.1b — Domain Doc Updater + Follow-up Filer in parallel

Spawn both in a **single message** — they're independent.

**Skip the Domain Doc Updater entirely when there is no knowledge system** — no `knowledge`
artifact row means nowhere to promote anything, and `work` must not create the folder to have
somewhere to put it. The Curator's findings still land in memory; say once that they were not
persisted to project memory.

**Domain Doc Updater** — `subagent_type: general-purpose`, `model: sonnet`, `effort: medium`. Promotes
the highest-leverage Curator findings from ephemeral memory into `domains/*.md`.
Sonnet, not haiku, because choosing the right doc, the right insertion point, and
matching house style takes judgment. Skip entirely if the Curator returned no
`auto_memory`.

```
You are editing structured project documentation in <repo path>. Operational
knowledge lives in per-topic files under the knowledge folder; its manifest
says which domain owns which topic.

<if Step 3.1a-i ran, paste what shared knowledge already covers these topics, then:>
Where a finding is already covered by a shared entry, do not restate it. Record only
what is genuinely specific to this project, and say in one line what you left out
because it is already held elsewhere.

Your job: of these AUTO_MEMORY entries, identify the ones that are a structured
pattern others should know BEFORE hitting the problem (canonical code shape, naming
convention, lifecycle rule, named gotcha + workaround). Promote those into the right
`domains/*.md` file as a new subsection or an addition to one. The rest stay memory-only.

**Domains are timeless reference, not a changelog.** Write each promoted finding as a
present-tense rule/gotcha and **strip every ticket ID (`<PREFIX>-NN`), date, and commit
ref** — provenance lives in the tracker/VCS, not the doc. Convert "fixed in <TICKET> on
<date>" into the underlying rule ("X causes Y — do Z"); turn root-cause narration into a
gotcha; never put a ticket id in a heading (it poisons the markdown auto-anchor).

Memory entries:
<paste auto_memory JSON>
Implementer's Surprises:
<paste verbatim>

Workflow: read INDEX.md (and `domains/meta.md` for the house structure + add/maintain
conventions) → for each candidate pick the target file → read it before editing, match
its hierarchy/style, don't duplicate → make scoped edits. If a finding deserves a brand
new topic, create `domains/<name>.md` and register it in INDEX.md per meta.md. If an
entry fits no domain cleanly, leave it as memory and say why.

Return:
## Domain doc edits   (file, section, what was added)
## Promoted from memory   (slugs)
## Skipped (memory-only)   (slug + one-line reason)
```

**Follow-up Filer** — `subagent_type: general-purpose`, `model: sonnet`, `effort: medium`. Drafts
tracker tickets for out-of-scope items. Sonnet because scoping a ticket takes
judgment. Do NOT file yet — produce drafts for Step 3.4. Skip if Follow-ups was empty.

```
Draft tracker tickets for these follow-ups from work on <TICKET-ID> (<PROJECT NAME>,
<ENV>). The orchestrator confirms each with the user before filing.

Implementer Follow-ups:
<paste verbatim>
User-flagged out-of-scope items:
<paste, or "none">

For each, decide if it warrants a ticket (a real bug/latent issue, small enough to
triage but big enough not to live as a TODO forever, would be lost if uncaptured).
For each worthy one draft: title (<80 chars, specific); description (what/where with
file:line if known/how to fix/how to verify, real newlines); labels (reuse existing
project labels if obvious); priority; and parent/related link if it belongs under an
epic or relates to <TICKET-ID>.

Return JSON:
{ "drafts":[ {"title":"…","description":"…","labels":["…"],"priority":3,"relatedTo":["<TICKET-ID>"]} ],
  "skipped":[ {"item":"…","reason":"…"} ] }
```

### Step 3.2 — Commit

After the Updater's edits land (so doc changes go in this commit), commit using this
project's `<commit workflow>` — a `/commit` skill if it has one, else the `<VCS>`
commit command directly. Reference `<TICKET-ID>` in the message. Inspect the
changeset first (the VCS status command) and confirm the file list matches the work —
strip editor/workspace noise; pass an explicit file list rather than "commit all" if
the tree is noisy. Record the commit id for Step 3.3. Orchestrator-inline — no subagent.

### Step 3.3 — Tracker summary comment

Post one completion comment on `<TICKET-ID>` via the tracker's comment op. Structure
it so a teammate scanning history immediately gets what shipped and why:
- **Root cause(s)** — the actual diagnoses, not "fixed the bug". If the symptom was
  three issues, name all three.
- **What shipped** — commit id + headline file groups.
- **Follow-ups** — pointers to the ticket ids you're about to file (or "pending user
  confirmation").
- **Verification** — one line on how it was tested.
Include the Curator's `ticket_comment` items if they add context not already covered.
Plain markdown, real newlines. Orchestrator-inline.

### Step 3.4 — File follow-ups and close the ticket

Present the Filer's drafts via a single `AskUserQuestion` (or per-ticket if many),
covering for each draft: file as-is / modify / skip — and the status change for
`<TICKET-ID>` (which state). Then act:
- For each approved draft, create the ticket via the tracker's create op with the
  draft's fields (and the project's default team/project if the tracker has them).
- Update `<TICKET-ID>`'s status via the tracker's status op.
Never change status without user permission — teams reserve different state names for "done".

---

## Rules

- **Config first.** Read the config bus (`.agent/PROJECT.md`, or the legacy path via the
  shim) before anything; fill every placeholder
  from it. Missing/blank → tell the user to run `work init` first; never invent a
  prefix, tracker, or VCS.
- **Adapt, don't hard-code.** Tracker and VCS calls come from PROJECT.md. Use *this*
  project's vocabulary (`<ENV>`); never leak another ecosystem's terms.
- **Orchestrate, don't do.** The main session reads subagent outputs and decides;
  avoid duplicating their work.
- **Domains come from the manifest — every ticket, no size fast-path.** Step 1.0 reads
  INDEX.md and picks the file list before any subagent spawns, and Step 1.1a runs the
  Domain Loader over it. This is size-invariant: a "small" or already-familiar ticket does
  not license skipping it, an `Explore`/Analyst pass does not substitute for the Loader,
  and prior knowledge from recalled memories is not a stand-in for the project's domain
  files. Phase 1 proves it ran via the **Domain integration** block in the plan (Step 1.4);
  no block → don't `ExitPlanMode`.
- **Domain selection is provisional — re-check on every rescope.** The Step 1.0 list is a
  first guess from the ticket text. Whenever scope widens (Analyst hidden-complexity, a
  scope-widening `AskUserQuestion` answer, the Planner's approach, or an Implementer fan-out
  STOP), re-run the *Domain re-check*: re-match `INDEX.md`, load only the new domains, fold
  them into the context for the next subagent. Skipping this leaves downstream agents blind
  to systems the ticket pulled in after Step 1.0.
- **Domains are timeless.** Anything promoted into a `domains/*.md` file is a present-tense
  rule/gotcha with **no ticket IDs, dates, or commit refs** — those belong in the tracker
  comment and the commit, not the doc. Same for any `INDEX.md` row. Keeps the docs from
  silently accreting changelog cruft someone later has to strip by hand.
- **Parallelize where independent.** Hunt for this at plan time: the Planner emits a
  **## Parallelisation** section grouping independent work-streams, and Phase 2 fans out
  one Implementer per stream in a single message (Step 2.2). Step 3.1b likewise runs both
  `Agent` calls in one message. Step 1.1 is deliberately serial — the Domain Loader's map
  guides the Analyst's exploration, so the Loader runs first and its summary feeds the
  Analyst. Independence means disjoint files and no data dependency; when in doubt,
  serialise.
- **Plan mode is a hard gate.** No mutations until `ExitPlanMode` is approved.
- **A STOP loops, it doesn't just retry.** An Implementer STOP routes through Step 2.3:
  a Class-A additive fan-out reloads domains and retries; a Class-B invalidated plan loops
  back through re-plan + `ExitPlanMode` re-approval before re-implementing. Let the loop run
  while it makes progress — don't cap it on a count. If it *thrashes* (same wall, no forward
  progress), pause and offer the user options (continue / rewrite / split / stop) as a
  suggestion, never a unilateral halt. Ambiguous class → treat as B.
- **Phase 3 is not optional.** Code on disk is not a shipped ticket. Run every step before
  declaring complete — skipping any of them means uncommitted code drifts, gotchas go
  undocumented, or out-of-scope discoveries get lost.
- **Overlay augments, never replaces.** If `.agent/work/workflow.md` exists, select the
  matching scenario and merge its injected steps into the phases at the stated slots and
  model + effort levels (read each step's Detail ref for specifics). The three phases and every
  domain-integration step (1.0 domain pick, Domain Loader, Curator, Domain Doc Updater)
  are invariant — an overlay can add around them, never remove them.
- **One ticket per invocation.** Multiple → ask which to start with.
- **Pass context explicitly.** Subagents start with no memory; paste reports verbatim.
- **Match model *and* effort to task.** Two dials per spawn. Don't reach for opus when
  sonnet will do, don't cheap out with haiku where judgment matters — and likewise don't
  burn high effort on mechanical work or starve real planning with low. Set `model` as the
  spawn parameter; actuate effort by opening the subagent's prompt with its mapped thinking
  keyword (low → none, medium → `Think hard.`, high → `Ultrathink.`) — there is no effort
  spawn parameter, the keyword is the lever. Default one notch lower than instinct on both,
  raise only when the lower setting struggles.
