---
name: session
description: Start or end a bounded work session in a project configured with Cadence. Start loads context, picks one goal per the flow's priority policy, and hands off to the project's execution skill; end runs the flow's gates, advances the item, verifies or performs the checkpoint, prunes the session scratchpad, and sets the next goal. Environment- and process-agnostic. Use when the user runs /cadence:session, says "start a session", "begin a work session", "wrap up", "end my session", "what should I work on next", or asks to close out the ticket they were working on.
---

# /cadence:session — Cadence session interpreter

Invoked as `/cadence:session start` or `/cadence:session end`. If no argument is
given: start a session when the session-state file records no open goal, end one
when it does — and say which you inferred before acting, so a wrong guess costs a
sentence rather than a mis-run ritual.

This skill assumes **nothing** about the environment or the process. It reads the project's **config** (bindings: tracker, VCS, docs, execution skill) and its **flow** (methodology: states, roles, gates, priority, decision rights), and executes the session ritual by interpreting them. Where the flow sets a **hook**, run that instruction doc; otherwise use the default described here.

## Load order (do this first, every time)

1. **Read the config** at `.agent/cadence/config.md` — one location, always. If it isn't there, tell the user to run `/cadence:init` and stop. (A config at some other path is a pre-0.2 layout; say so and point at `/cadence:doctor`.)
2. **Load the flow spec** named in `config.flow` — a shipped preset at `${CLAUDE_PLUGIN_ROOT}/flows/<name>.flow.md`, or a project-local path resolved relative to the config file.
3. **Resolve adapters** from `config.tracker.kind`, `config.vcs.kind`, `config.doc_system.kind`. For each family, look first for a project-local adapter at `.agent/cadence/adapters/<family>/<kind>.md`, else the shipped fallback at `${CLAUDE_PLUGIN_ROOT}/adapters/<family>/<kind>.md`. Read each adapter's **Capabilities** block — it tells you which operations and fields actually exist here.
4. **Resolve the lane roles.** Every status this skill sets comes from `flow.states.roles.<role>` mapped through `config.tracker.status_map` to a real status. Never write a literal status name.
5. **Note `config.execution`** — the project's execution skill and what it `owns`.

Hook resolution, for any step named below: if `flow.hooks[<step>]` is set, load and follow that doc (passing it the step's Input, expecting its Output — the contracts are at `${CLAUDE_PLUGIN_ROOT}/flows/HOOKS.md`); else use the default here.

## Resolving a role to a status — read this once

Three things must line up before this skill changes an item's status:

1. the flow declares the **role** (`roles.active`, `roles.done`, …),
2. that role names a **lane**, and
3. `config.tracker.status_map` maps that lane to a **status the tracker really has**.

If any link is missing, **do not perform that transition.** Say so once, in one
sentence, and carry on with the rest of the session. A flow with no `active` role
is a legitimate process — it means "don't mark work in flight." A lane with no
`status_map` entry means the tracker cannot represent that step, which is normal
on a two-column board.

What you must never do is substitute a plausible-looking status. Moving an item
to a column that doesn't exist, or to a nearby one that does, is worse than not
moving it: the first fails loudly at best, and the second silently puts the
user's board into a state they never chose.

`roles.done` is the exception worth stating: if it is missing or unmapped, an
item cannot be completed, so **stop and ask** rather than ending the session
with the work in limbo.

## `/cadence:session start`

0. **Claim the session before anything else.** Read the session-state file's `claimed-by` and
   `claimed-at` header. Yours, absent, or older than a day → take it (write your token and
   timestamp; say one line if you took over a stale one). **Recent and not yours → stop**: another
   session is live in this working copy. Offer to continue its goal, to start a separate session
   file beside it (`cadence-session-2.md`), or to stop — and until they answer, pick no goal, move
   no item and write nothing. See *Sessions across worktrees* in `${CLAUDE_PLUGIN_ROOT}/adapters/ADAPTERS.md`.

   The session file is **keyed by worktree** — `.agent/local/cadence-session-<worktree>.md` —
   because `.agent/local/` is meant to be shared across worktrees and therefore does not separate
   them itself.

   Then work out whether cross-worktree coordination is even possible: ask the VCS adapter for
   **`shared_local_dir()`** and compare it with where `.agent/local/` resolves. Shared → read the
   claims file there. Not shared, or unsupported → say **once** that sessions in other worktrees
   are invisible, name the fix (link `.agent/local/` to the shared target), and carry on.

1. **`session.start`** (default): read the session-state file (`config.session_state.file`) — Cadence's own local scratchpad, *not* the project's memory. Determine the current milestone from the roadmap (`config.doc_system.roadmap`) and the tracker.

1b. **Snapshot the tree.** Call `status()` and write what is dirty *now* — path per line, or `clean` — into the session-state file's `## Tree at start` block, replacing whatever the last session left there. This is the one fact end cannot recover later: which changes were already sitting in the working copy before this session wrote anything. A shared working tree — a second session, a colleague on the same checkout, a capture pass running beside you — is the hazard, and `checkpoint` cannot tell its edits from yours by looking at a file list. The snapshot is what turns *"note the file count at session start"* from advice nobody follows into a fact end reads.
2. **`session.select_goal`** (default): walk `flow.intake.priority_policy` in order, gathering candidates via the tracker adapter.

   **On a sprint flow, scope the search to the active cycle first.** If the flow's priority policy
   names a cycle token, or its states declare a `committed` role, ask the tracker for
   `current_cycle()` and look for candidates **inside that cycle** — that is where a team's
   committed work lives, because the team commits it in the tracker rather than here. Unassigned
   items *within the current sprint* are the takeable pool; unassigned items outside it are next
   cycle's problem and proposing one is how a sprint stops meaning anything.

   `current_cycle()` unsupported → say so once and fall back to the `committed` lane by status,
   then to the flow's other tokens. A tracker that cannot name its cycles can still tell you which
   items are in the committed column.

   **Drop anything in a `tracker.hands_off` status before you rank.** Those columns are somebody
   else's step — an MR with a peer, a QA queue — so an item there is not a candidate, not stalled,
   and not to be chased. Read the note recorded beside each one; it says in the user's own words
   why nothing is owed there.

   **Filter candidates by ownership before ranking them.** On a project where work is owned, the
   goal has to be something this person may actually act on — proposing a colleague's in-progress
   ticket is worse than proposing nothing, because it invites two people onto one item.

   Resolve the current user with the tracker's `me()`, then read each candidate's `assignee`
   *together with its lane*: the assignee says whose it is, the lane says in what capacity. An
   item assigned to the user in a review lane is their review work even though they did not write
   it. An item assigned to somebody else is not a candidate — surface it as context or as a
   blocker if it is one, never as the goal. Unassigned work is available, and **taking it means
   assigning it**, so nobody else starts the same thing.

   Read the situation rather than matching cases: the question is always *can this person
   legitimately act on this item now*. `ADAPTERS.md` § *Ownership* has the concept and its
   degradation — with `me()` or `assignee` unsupported you cannot tell, so say so once and treat
   assignment as advisory rather than guessing identity from a git email.

   **Skip a candidate another worktree is holding**, per the cross-worktree claims file, and say
   which worktree holds it — a candidate that vanishes without explanation reads as a priority
   bug. When you take an item, record it there; when the session ends or releases it, remove the
   entry. With `shared_local_dir()` unsupported, there is no claims file and no skipping: that is
   the degraded mode you announced at start.

   **Exclude items whose status maps to no lane.** A real board carries statuses the flow never named — `Blocked`, `Needs Design`, `Waiting on Vendor`. Those items are neither terminal nor ready, and you do not know what the status means, so they are not candidates. Say how many you set aside and in which statuses; a board where most work is invisible to the process is worth surfacing rather than silently narrowing.

   **Candidates are items at the flow's working level — the *last* entry in `hierarchy.levels`.** Everything above it is a container: an epic or a milestone is not a session's goal, and "by end of session this epic is Done" is a promise no session can keep. Filter before ranking, or a mechanical token will hand you a container and the framing step will dutifully write a goal nobody can finish. Where the tracker has no explicit level field, infer it structurally — an item with children, or with no parent in a flow whose levels nest, is not the working level. **Skip any token whose required field the adapter declares unsupported** (see the token table in `${CLAUDE_PLUGIN_ROOT}/flows/FLOW-SPEC.md`) and say which you skipped — a policy that silently does nothing is worse than a shorter one that works. If the flow has `hierarchy.first_class.incident`, check `states.incident_lanes` first. Where more than one candidate survives, run **`intake.prioritize`**. Respect `flow.decision_rights.select_goal`:
   - `ai` → pick it and state the choice.
   - `ai-proposes` → present the top 1–3 and let the user choose.
   - `human` → present the board; the user decides; don't pre-empt.
3. **Frame the goal** in one sentence ("By end of session, `<id> <title>` is `<done role>`") and name the **session type**. If it can't be said in one sentence, it's too big — offer to split it first.
4. **Move the item to `roles.active`**, per the resolution rules above, and fire **`transition.<from>_to_<to>`**
5. **Record the goal** via the tracker adapter (`comment`) as the anti-drift anchor.
6. **State the bug rule** for this session (`flow.intake.bug_triage`), and mean it: if a bug surfaces later, fire **`bug.triage`** rather than deciding on impulse. New work arriving mid-session goes through **`intake.classify`** first.
7. **Hand off** to `config.execution.skill`. Do not implement here.

### When `config.execution.skill` is `none`

This is a normal, fully supported setup — the zero-dependency default, not a degraded one. It means **there is no execution skill to hand off to: the work happens in this session, with the user, in the open conversation.** `execution.owns` is empty, so nothing is owned elsewhere, and `/cadence:session end` performs the checkpoint itself rather than verifying someone else's.

## `/cadence:session end`

The order of these steps matters and is explained below — do not reorder them.
The governing rule: **every tracker write happens before the checkpoint, and the
checkpoint is the last thing that touches the repo.**

1. **Gate(s).** Work out the flow's **declared path** from the item's current lane to the lane you are moving it to, following `gated_transitions`. Run **every gate attached to any transition on that path** — including transitions whose lanes this tracker cannot represent.

   **An unmapped lane skips the status write. It must never skip a gate.** Otherwise a board with fewer columns silently lowers the quality bar, and the fewer columns a team has, the fewer checks they get — exactly backwards. A flow that gates `Supported -> Reviewed -> Final` still owes you both gates on a board that only has `Outline` and `Final`.

   Matching only the *final* transition is not enough: gates on intermediate hops (a citations check on the way to review, a postmortem before an incident closes) are precisely the ones an unmapped lane would drop.

   The **effective DoD** is `flow.gates.dod.checks` ∪ `config.dod_gates` — a union; a project may raise the flow's bar, never lower it. Honour each gate's approver: a `human` gate is **never** auto-cleared — `needs-human` is not a pass.

   **Walk the item's own checklist too, and first.** `get(id)` the item and read its body for the bar its author set: checkbox lines (`- [ ]`, `- [x]`), or a section headed *Acceptance criteria*, *Definition of Done*, *Done when* or the like. That list is the most specific standard the item will ever be held to, and the project gates are usually the wrong questions for it — a persistence check passes a documentation ticket that fixed one of its three named locations. So every unchecked box is either **met** (name the evidence in the change, and tick it in the body where the adapter can write the description) or **explicitly waived by the user** with the reason recorded on the item — never inferred waived, and never ticked because the session ran out. **An item whose own checklist is unmet does not reach `done`, whatever the project gates said.** The checklist is always applicable: it is not a check somebody might have declared too broadly, it is what this item is. No checklist → nothing to walk, and nothing to say.

   **Decide applicability the way each check says to, then report every skip.** Everything is judged against **the change the gate is being run on** — the work since the item entered the active lane, not merely the files still uncommitted. Four modes (`FLOW-SPEC.md` § *Declaring what makes a check applicable*):

   - a **bare string** or `applies: always` — it runs. Nothing to decide.
   - `applies: infer` — judge whether it has anything to say about *this* change, and **quote the evidence** for a skip: the file, the symbol, the absence you are relying on.
   - `applies_when: {changed_paths: […]}` — match the globs against the change's paths. Nothing to judge.
   - `applies_when: "<sentence>"` — judge that stated rule, not your own, and quote the evidence.

   **`infer` is a judgement you must be able to show, not a discretion.** *"Not applicable"* with no evidence is the override this whole mechanism exists to prevent, and it is the reason a skipped check is never silent. If you cannot name what makes it inapplicable, it applies.

   Where the flow and the project both name a check, the **stricter** mode wins — `always` > `applies_when` > `infer` — because the union may only raise the bar, and a stated condition is reviewable where a judgement is not.

   **Name every skipped check in the report, each with its reason** — `docs — skipped: no documented surface changed (nothing matched docs/**, **/*.md)`. A gate whose checks all skipped is reported as *applied to nothing*, never as passed: those two look identical in a one-line summary and mean opposite things.

   **You may not overrule what a check declares.** `always` is not yours to skip, and a stated `applies_when` is the author's rule rather than a starting point for your own — the moment to have narrowed either was when it was declared, by someone who did not yet know which check would be inconvenient. Judging is permitted exactly where the check asked for it by saying `infer`.

   A check that never fits this project is a change to the flow or to `config.dod_gates`; say so, and offer it. **Offer the same when you keep inferring the same answer** — a check you have skipped on every change of a kind wants a stated `applies_when`, which is cheaper to trust than a judgement repeated.

   **If a gate does not clear, the item does not advance — but the work is not abandoned.** Skip step 2 and carry on through the rest of end: record why the gate held (step 4), then **go to step 5 and let it decide how the work is saved** — by checkpointing, or, in the verify branch, by offering to. Gates govern whether the *item* moves, not whether the *work* survives.

   The distinction matters when both things are wrong at once: a gate held *and* the execution skill that owed you a commit didn't make one. Step 5 still declines to commit silently on execution's behalf — a held gate is not a licence to paper over a broken binding.

   Stopping dead here would leave real work uncommitted and, under a file-based tracker, the tree dirty — which poisons the `status()`-clean check the next session depends on, and leaves the work one careless `git add -A` from landing in someone else's commit. A held gate is a normal outcome of a session, not a crash.

   Say plainly in the commit message and the session state that the item is *not* done and which gate is holding it.
2. **Advance the item** to `roles.done` (via `roles.review` first if the flow declares that transition *and* the lane is mapped), firing `transition.<from>_to_<to>`. Skip this step entirely if a gate held.

   **If the user says the work is blocked**, park it in `roles.blocked` instead of advancing — when the flow declares that role and its lane is mapped. Leaving a stuck item in `active` claims someone is working on it; sending it back to `backlog` loses that it was started. Record what it is blocked *on*, since a blocked item with no stated blocker is indistinguishable from an abandoned one a month later.

   **Only an explicit statement parks an item.** Never infer blockage — not from a gate failing, not from a short session, not from work looking incomplete. Cadence cannot tell "stuck" from "unfinished", and guessing wrong writes a status the user never chose.

   Only move **forward** along the declared path. If the item already sits past the lane you were going to move it to — an `active` role naming a lane the item left three transitions ago — do not move it backwards; say so once and leave it. A status that walks backwards misrepresents the board more than a status that stands still.
3. **Prune the session state** — run `session_state.prune`. The default rule lives in `${CLAUDE_PLUGIN_ROOT}/flows/HOOKS.md`; in short, reconcile the scratchpad **against the tracker** (not against what the file claims) and drop anything the tracker already tells you, keeping only non-obvious traps.
4. **Decide the next goal and record it** via the tracker adapter (`comment`), and record any durable gotcha through the doc adapter's `record()`. **The comment opens with `Session end — gate.<name> passed|held`** for every gate on the path, so an item's history says which ritual closed it: this line is what `/cadence:doctor` looks for on a done item, and an item in the done lane without one was closed outside the session path. **Any DoD check that did not apply goes in that comment too**, with its reason — the terminal output is gone by morning, and *which checks this item was actually held to* is the thing a reviewer needs later. Both of these write files that may be under version control, which is why they come *before* the checkpoint.
5. **Checkpoint — the last repo write.** First call `status()` and look at what is actually there: running the gates may have produced artefacts the gates themselves created (`__pycache__`, coverage output, a build directory). Ignore or remove those before committing rather than attributing them to this item — the tree being clean afterwards is only meaningful if you didn't commit rubbish to achieve it.

   **Then compare against `## Tree at start`.** Three kinds of dirty path, and only one is yours:
   - **dirty at start, untouched by this session** — somebody else's, or a previous session's leftovers. Never staged; named once.
   - **appeared since start, and this session did not edit it** — another writer in the same tree. Never staged, and **surfaced by name**: *"`docs/roadmap-notes.md` changed under this session without it; left uncommitted."* A correct file count is not evidence of correct content, and this is the case the snapshot exists for.
   - **this session's work** — what it edited for the item, and what the item's change shows on `diff()`. Staged, by explicit path.
   Where you cannot tell — a path you touched that was also dirty at start — `diff()` it and say which hunks are the item's; if they cannot be separated, stage it and say that too, rather than silently taking the other writer's edit under this item's message. Under `execution.owns: commit`, the same comparison is how you verify the execution skill's checkpoint took only its own work.
   Then take one of two branches.

   **If `config.execution.owns` includes `commit` — verify, don't repeat.** Use `log()` to confirm a checkpoint referencing this item exists, and `status()` to confirm the tree is clean.

   **When that verification fails**, say exactly what you found — *"`execution.owns` says `/do-ticket` commits, but no checkpoint references `UC-1` and two paths are dirty."* Then:
   - **Do not quietly commit on execution's behalf.** The seam exists so each side's failure is visible; absorbing it silently means the execution binding can stay broken forever while sessions appear to succeed.
   - **Do not abandon the work either.** Offer to checkpoint it, saying plainly that you are doing execution's job because execution didn't.
   - Say that one of two things is wrong, because the user can only fix it if they know which: **either the execution skill failed**, or **`execution.owns` claims a responsibility it doesn't actually take**. A binding that overstates what it owns produces exactly this and looks like a Cadence bug.

   **Otherwise — including whenever `execution.skill` is `none`** — run the checkpoint yourself via the `checkpoint` hook / VCS adapter, and **confirm it landed** with `log()` afterwards. A checkpoint you performed is not more trustworthy than one you verified; it just failed more recently if it failed.

   **In either branch, if no checkpoint exists at the end of this step, the item must not stay advanced.** Step 2 has already moved it, so offer to revert the status — a tracker claiming work is finished when nothing was committed is worse than either failure alone.
6. **`session.end`** (default): write the pruned session state to `config.session_state.file`, per the schema in `${CLAUDE_PLUGIN_ROOT}/adapters/ADAPTERS.md`. This file is git-ignored, so it is the one write that may safely follow the checkpoint. Clear `## Tree at start` — it describes a session that is over, and the next start writes its own.

7. **If the item landed in a hands-off status, you are finished with it.** Say so in one line —
   *"handed to review; nothing further from me"* — and do not carry it into the next session's
   goal, poll it, or report it later as stalled. Ending involvement cleanly is the behaviour;
   silence about it is what makes a user wonder whether the tool is still waiting on something.

8. **Release what you claimed.** Remove this item's entry from the cross-worktree claims file
   (`shared_local_dir()`), and clear `claimed-by` / `claimed-at` from the session-state header.
   A released claim is what lets the next session — here or in another worktree — pick this item
   up without asking anybody.

   **Release even when the session ended badly.** A gate failed, the item did not advance, you
   are stopping early: release anyway. A claim held by a session that is over is exactly the
   stale claim the next person has to reason about, and the whole point of a claim over a lock is
   that nobody should have to.

9. **Report, and keep it to what they act on.** One line of headline (the item and where it
   ended up), then only: any gate that held and what it is waiting for, any DoD check that did
   not apply and why, anything the tracker refused, and the next goal. **End with the next
   steps** — the commands to run, in order, at most four — or one line saying the session is
   closed and nothing is pending. The session's workings are above this in the transcript.

### Why the checkpoint goes last

Under a tracker whose items live in the repo (the `markdown` fallback commits its
backlog deliberately), **every tracker write is a repo write.** Anything that
touches the tracker after the commit leaves the tree dirty — which contradicts
the commit, and poisons the `status()`-clean check that the *next* session uses
to verify a checkpoint happened.

That applies to all three tracker writes at end, not just the status change: the
status, the next-goal comment, and any recorded gotcha. Fixing only the status
ordering and then commenting afterwards reintroduces the same failure two steps
later — which is exactly what happened the first time this was fixed.

The order is also correct for hosted trackers, where tracker and repo are
independent. So it is universally right, and the reverse is quietly wrong in
precisely the configuration Cadence ships as its default.

**If the checkpoint fails**, say so plainly and offer to revert the status. Do
not leave the item marked done with the work uncommitted — a tracker claiming
work is finished when nothing was committed is worse than either failure alone.

The same applies when you were only *verifying* someone else's checkpoint and it
isn't there. "Execution owns the commit" is a statement about whose job it is,
not evidence the job was done.

## When something doesn't resolve

Cadence is a chain of lookups — config → flow → adapters → roles → tracker — and a stranger's project will break that chain in ways yours never does. The rule at every link is the same: **surface the gap, don't fill it by inference.** A wrong guess here produces confident work against the wrong tool, the wrong process, or another project's conventions.

- **No config** → route to `/cadence:init` and stop.
- **`config.flow` names a file that isn't there** → stop. Name the missing path; offer to re-point `flow:` at a shipped preset or re-run init. Never silently substitute a preset — the flow *is* the process.
- **An adapter `kind` resolves to nothing** → stop and route to `/cadence:init`, which generates it.
- **A tracker is configured but unreachable** → say so and stop. Do not fall back to the `markdown` tracker: a second, empty backlog looks like a working system while forking the project's state.
- **A hook doc named in `flow.hooks` is missing** → report which, use the built-in default for that step, and continue. A flow author mid-authoring is better served by a working session and a warning.
- **A role or `status_map` entry is missing** → see the resolution rules above: skip the transition and note it, except for `roles.done`, where you stop and ask.
- **The tracker returns no open items** → not an error. Say the backlog is empty for this milestone and offer `/cadence:plan`.
- **Open items exist but every priority token missed them** → not an error, and not a licence to pick one anyway. But **why** each token missed changes what you should do, and there are two quite different reasons:

  **A token that could not be evaluated is a gap.** The tracker doesn't support the field, or nothing has populated it — a board whose items carry no milestone makes `next-roadmap-ticket` match nothing however much work is sitting there. List the open items, say which tokens missed and why, and let the user choose. Then say what would fix it next time, usually a field `/cadence:plan` should have set.

  **A token that *was* evaluated and returned nothing is an answer.** `committed-sprint` on a board where two items are committed to a cycle that starts next week has not failed — it has told you the sprint hasn't begun. Report that as the finding it is, and **do not** present the backlog for picking as though the policy were broken. Offering a free choice there quietly invites the user to start cycle work early, which is the one thing a sprint flow exists to prevent. If they want to start anyway that is their call, but it should be a decision they make against a stated process, not a menu you handed them.

  **On a sprint flow, tell those two apart before falling through.** An empty committed lane has
  two very different causes: a cycle that was committed and is now finished — an answer — or a
  cycle **nobody ever committed**, which is the "nothing has populated it" gap above. Check
  whether *any* item carries a cycle: none anywhere means no sprint has ever been committed here,
  and quietly falling through to `backlog-by-rank` produces a session that looks normal while the
  sprint is fictional. Say which of the two you found.

  Do not fall back to "the oldest" or "the first one listed". Under `select_goal: ai` the policy *is* the skill's mandate to choose; with the policy exhausted there is no mandate, and an arbitrary pick dressed up as a decision is worse than an honest question.

## `wip_limit` — warn, never block

`states.wip_limit` is `none`, an integer, or `per-person`. At **`session start`**, count the items
in the `active` lane and warn when the limit is exceeded — after picking the goal, not instead of
picking it:

- **integer** — more items active than the number.
- **`per-person`** — any one assignee holding more than one active item. Unassigned active items
  are counted and reported as unassigned rather than attributed to anybody.
- **`none`** — no check.

**Blocked items do not count** ([`FLOW-SPEC.md`](${CLAUDE_PLUGIN_ROOT}/flows/FLOW-SPEC.md)): the
limit caps concurrent *work*, and blocked work is not progressing.

It is a **warning, not a gate**. Cadence cannot know whether a second active item is thrash or a
legitimate hand-off, and a limit that blocked would be a gate nobody declared. Say it once, name
the items, carry on.

## Notes

- **Honour decision rights.** Never auto-decide a step the flow marks `human`.
- **Never repeat execution-owned work.** `config.execution.owns` is the seam that keeps this skill and the execution skill from duplicating commit/doc steps — and it cuts both ways: what execution doesn't own, this skill must do.
- **Stay fast.** ~5 minutes each end. The value is the goal in and the verified close out, not ceremony.
- **Delegate the grunt work.** Batchy adapter reads/writes can go to the `mechanical` subagent, spawned per the calling convention in `${CLAUDE_PLUGIN_ROOT}/adapters/ADAPTERS.md`. The goal *decision* and gate *judgment* stay on the session model.
- **Session state is Cadence's own local file.** Read and write only `config.session_state.file`. Never read, write, or depend on the project's own memory (`CLAUDE.md`, agent `MEMORY.md`), and never reach outside `.agent/cadence/`.
