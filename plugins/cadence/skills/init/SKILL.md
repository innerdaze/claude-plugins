---
name: init
description: Set up Cadence in a project. Detects the project's conventions (doc system, VCS, execution skill, issue tracker), confirms them, and GENERATES a project-local adapter for each non-fallback tool it finds; then helps you pick or author a flow, maps your tracker's real statuses to the flow's lanes, writes the config, and scaffolds your roadmap. Use when the user runs /cadence:init, says "set up Cadence", "initialize Cadence", or asks to put a project-management process, a roadmap-and-tickets workflow, or goal-driven work sessions in place for a project.
---

# /cadence:init — set up Cadence in a project

Invoked as `/cadence:init`, or `/cadence:init --defaults` for the non-interactive
zero-dependency setup described at the end of this file.

Produce: a **config** (bindings), a **flow** selection (methodology), any **project-local adapters** the environment needs, and the starter docs. The governing rule is **detect, then confirm — never assume.** Nothing is written until the user approves.

Cadence ships no integration for a specific external tool (see `${CLAUDE_PLUGIN_ROOT}/adapters/ADAPTERS.md`). Where a project uses a real tracker/VCS/doc-system, init **generates a project-local adapter** tailored to it. The plugin's `${CLAUDE_PLUGIN_ROOT}/flows/`, `${CLAUDE_PLUGIN_ROOT}/templates/`, and the adapter **contracts** are the sources to read; the plugin itself is never modified.

If a Cadence config already exists, this is an **update**: read it first, propose changes, back it up before overwriting.

## The rule that matters most

**Assemble the config from the user's answers. Never copy a config from anywhere — not from `config.example.md`, not from another project, not from something in your context.**

`config.example.md` documents the *shape* of each key. It is a reference to read, not a file to duplicate. Write only keys the user actually answered; leave the rest out. A key you didn't ask about should not appear in their file.

This is not fussiness. These skills are installed once and serve every project, so another project's ticket prefix, MCP namespace, or DoD is often already in context and will look entirely plausible here. Nothing gets stored wrongly — the substitution happens in the *reasoning*, which is what makes it silent and confident. **No project's configuration is ever a default for another's.**

## Phase 1 — Detect the environment, and generate its adapters (propose → confirm)

**Ask only what the repo cannot answer.** Every question is a claim that the answer could not be
found, and most can. Sort each unknown before you open your mouth:

| The repo… | Then | Examples here |
|---|---|---|
| **answers it** | infer it and *show it as inferred, with the evidence* — do not ask | ticket prefix from the project name; roadmap under an existing `docs/`; `status_map` lanes as the chosen flow declares them; DoD extras defaulting to none |
| **does not**, or the only evidence might belong to another project | **ask** | which flow; whether a connected MCP tracker is this repo's; whether to scaffold at all |
| **contradicts what they asked for**, or cannot satisfy it | **ask** | *"you asked for `linter passes`; there is no lint script and no linter config"* |

Weigh it by what being wrong costs: a wrong prefix is a rename, a wrong flow is the wrong process
for the project. Cheap to reverse *and* evidenced → infer. Expensive or unevidenced → ask.

**Anything inferred still reaches the user** — in the confirmation at the end, marked, with its
evidence. That is what that surface is for. Asking a question *and* listing its answer as an
inference to check charges them twice for one fact.

⚠️ **This does not soften *detect, then confirm — never assume*.** That rule guards
**cross-project substitution**: another project's prefix, board or DoD is often in context and
will look entirely plausible here. Evidence means evidence *in this repo* — `package.json`, the
directory layout, the bus. A plausible value with no local evidence is exactly the failure, and
it is still a question.

`[budget]` More than three or four questions and you are asking things the repo could have told
you. If the list is long, go back and read.

Inspect the repo and connected tools, present findings as one summary the user confirms or corrects, and **for each non-fallback tool, generate a project-local adapter** at `.agent/cadence/adapters/<family>/<kind>.md` implementing that family's contract — including its **Capabilities** block — against what you actually find. Never assume a tool or its interface.

1. **Doc system.** **The kind is the bus's `Doc system` binding row, never a name you invent.** Read that row first. Present → that is the kind; if neither a project-local `.agent/cadence/adapters/docs/<kind>.md` nor a shipped `${CLAUDE_PLUGIN_ROOT}/adapters/docs/<kind>.md` exists for it, generate the project-local one **under exactly that name**, including `taxonomy()` from the knowledge folder's manifest. Absent → if the bus's `## Artifacts` registers a `knowledge` folder, or the project keeps structured knowledge docs with an index, propose `markdown` — the kind the shipped fallback implements and the one the knowledge tool's own init writes — and write the row; else the shipped `none`. An older init proposed its own name for a knowledge system it recognised (`domains`), and a project could then carry a row saying one thing and an adapter file saying another, resolving to nothing on both sides; `/cadence:migrate` v4 repairs that, and this step no longer causes it. Either way, place the roadmap (`doc_system.roadmap`) where a person would look for it, and **infer that rather than asking**: an existing docs directory takes it, else the repo root. It is a project document, not Cadence state. Show it as inferred; a wrong path is a `git mv`.

2. **VCS.** Detect `.git` / `.diversion` / `.jj` / `.hg`. `git` → use the shipped fallback. Anything else → generate `.agent/cadence/adapters/vcs/<kind>.md`.

   **Read what the project already documents before inspecting the CLI.** A repo that uses an unusual VCS has almost always written down how to drive it — in a README, a contributing guide, a doc-system page, a convention file. That prose is a *better* source than `--help`, because it contains the operational knowledge a CLI cannot express: which operations are irreversible, which recovery steps destroy local work, which failures look like something else. A real project's notes recorded that its VCS *"has no amend or reword — a garbled commit message is permanent"* and that the documented fix for one failure mode *"overwrites local edits"*. No amount of CLI inspection produces either, and an adapter missing them is an adapter that will eventually lose someone's work.

   So: read the project's own docs first, inspect the CLI to confirm the verbs and fill gaps, and **cite where each gotcha came from** so it can be re-checked when the tool changes. Capture only **tool-generic** behaviour in the adapter; machine- or workspace-specific quirks go in `config.vcs.gotchas`. Detect an existing commit skill to delegate to.

3. **Execution skill.** Scan `.claude/skills/`, enabled plugins, and global skills for a ticket-execution skill. **If `## Execution` already names one that no longer resolves** — the usual cause is a skill that was packaged into a plugin and now addresses as `/<plugin>:<name>` — say so, propose the same-named skill you found inside an installed plugin, and confirm before writing; a stale command is the one binding that stops a session from handing off at all. **Propose a candidate, but confirm three things with the user**: that it's the right one, how it's invoked, and what it `owns`. **Do not put `status` in `owns` unless the user asks for it in as many words** — the done transition is the session's, gated by the DoD, and an execution skill that closes items itself moves the gate to after the fact; say that cost if they ask. Also check it can actually run *here* — a skill that hardcodes another project's engine, tracker, or VCS will abort on first use, and `execution.skill: none` is better than a binding that fails. `none` is a first-class answer, not a fallback.

4. **Tracker.** Detect connected tracker MCPs.
   - **Before binding any of them, confirm the workspace belongs to *this* repo.** MCPs are user-scoped and Cadence is installed once for every project, so the tracker you can see is very often somebody else's. Query the tool for its teams/projects and look for corroboration: a name matching this repo, an existing ticket prefix that matches, recent items referencing this codebase. **If you cannot confirm it, ask.** Do not bind a tracker on the strength of its being the only one connected — that is how tickets end up filed into another product's board.
   - Once confirmed, inspect the verbs it actually exposes and generate `.agent/cadence/adapters/trackers/<kind>.md` implementing the tracker contract against those exact operations. Collect `mcp_namespace` and IDs into config.
   - **Read the project's own notes on the tracker too**, for the same reason as the VCS: a team records which fields are load-bearing, which statuses mean something non-obvious, and which operations they have learned not to trust. Cite what you carry across.
   - If none is connected, or none is confirmed → the shipped `markdown` fallback. This needs no MCP and is a perfectly good answer.

Show the generated adapters and the assembled bindings, and get explicit confirmation. Adapters are stored **in the project**; the plugin is untouched.

## Phase 2 — Choose the flow

**A) Pick a preset**, then optionally override axes:
- `solo-greenfield` — one builder, pre-release; high autonomy, continuous, bugs deferred.
- `team-sprints` — cycle cadence; the skill proposes, the team commits scope. Needs a tracker with cycles.
- `live-oncall` — an incident lane that preempts the roadmap; more gates; releases human-approved.

Summarize each, let the user pick, then offer to tweak any axis. Say plainly which parts of a preset are **not yet automated** (ceremonies, release pipelines) so nobody adopts `team-sprints` expecting Cadence to run their standup.

**B) Author a custom flow** — walk the vocabulary in `${CLAUDE_PLUGIN_ROOT}/flows/FLOW-SPEC.md`. For any step the vocabulary can't express, author a **hook doc** against the contract in `${CLAUDE_PLUGIN_ROOT}/flows/HOOKS.md`. Write to `.agent/cadence/<name>.flow.md` (+ `.agent/cadence/hooks/*.md`).

### Then map the lanes to real statuses — do not skip this

The flow's lanes are **process vocabulary**. Your tracker has whatever columns it has. `config.tracker.status_map` is the only place the two meet, and it is built from what the tool reports, never from the preset:

1. Call the tracker adapter's **`statuses()`**. If the adapter declares `statuses` unsupported, ask the user to list their columns once.

   **The `markdown` fallback is the exception, and it must not become an interview.** There is no board to read, so `status_map` *defines* the columns rather than mapping to them — which means the flow already answers it. Take the flow's declared lanes verbatim, and the ticket prefix from the project name in the bus. Both are inferences with local evidence and both are cheap to change, so they belong in the confirmation, not in a question.

2. **Draft a proposal from the tool's own categories, then put it up for correction.** Most trackers classify their statuses — Linear's `backlog` / `unstarted` / `started` / `completed` / `canceled`, Jira's `To Do` / `In Progress` / `Done`, GitHub Projects' column kinds. Where a category exists, use it to draft a starting map:

   | Tracker category | Draft it as |
   |---|---|
   | backlog | the `backlog` role's lane |
   | unstarted | the `committed` role's lane, if the flow has one |
   | started | the `active` role's lane |
   | completed | the `done` role's lane |
   | canceled, duplicate, and similar | the `abandoned` list |

   This is **detection, not inference**: you are reading a classification the tool already made, showing it, and asking. Present it as *"here is what your board's own categories suggest — correct anything wrong"*, never as a decision already taken. Nothing is written until the user says so.

   Where the tool has no categories, there is nothing to draft from. Skip straight to asking; do not manufacture a proposal from lane names that happen to look similar.

3. **The proposal is a hint with no authority.** A category tells you how the tool files a status, not what the team means by it. A board can use `unstarted` for "triaged but not planned", or keep two `started` states where only one means "someone is working on this". Where the draft looks thin or odd — several statuses in one category, a category with none — say so rather than presenting a tidy map that quietly guesses.

   **Duplicate names always get asked, never drafted.** Two states called `Queued`, one `backlog` and one `unstarted`, is a configuration Linear permits and a live board was observed using. Show both, ask which the lane means, and write the qualified form (`{name, category}`). The two halves of an ambiguity are different columns; choosing wrong puts work somewhere the user didn't ask for.

4. **Account for every column — an unmapped column is a question, not a silence.** Work through
   the whole list from `statuses()` and give each one a disposition. There are three, and the
   second is the one that was missing:

   | Disposition | Means | Recorded as |
   |---|---|---|
   | **a lane** | cadence moves work into and out of it | `status_map` |
   | **hands-off** | the column is real and cadence does **nothing** there — someone else's step | `tracker.hands_off` |
   | **abandoned** | terminal, not done — cancelled, duplicate, won't do | the abandoned list |

   **Ask about anything you cannot draft confidently. Do not leave it out.** A column left out is
   indistinguishable from a column nobody thought about, and the difference shows up later as the
   tool doing something odd with work that was never its business.

   **Hands-off is the answer people forget they need.** A board often has states where the team's
   process continues and cadence's does not: `In Dev Review` once the MR is with a peer, `QA`,
   `Awaiting Release`, `Blocked on Vendor`. Offer it explicitly rather than waiting to be told —
   *"once something reaches `In Dev Review`, should I do anything with it, or is it out of my
   hands?"* — because a user answering "what does this column mean" will describe the column, not
   your involvement in it, and those are different questions.

   Record a short note with each one, in the user's words: *"MR is with a peer; I take no action
   and the item is not stalled."* That sentence is what stops the next session treating a
   fortnight in review as something to chase.

5. **Ask for anything the board cannot tell you.** Before you write the config, ask plainly:
   *"Is there anything about how your team uses this board that I would get wrong from looking at
   it?"* Record the answer as prose in `tracker.notes`.

   The point is to make **asking cheaper than assuming**, because the failure mode is silent: a
   convention you did not know about produces confident wrong behaviour, and the user only finds
   out when they have to correct it mid-session. One open question at init costs a sentence.

6. **Lanes with no counterpart are left unmapped — not invented.** Say what that disables, concretely: *"no column for `In Progress`, so sessions won't mark work in flight."* That is a normal outcome on a two-column board.

   **And the reverse: statuses the flow cannot name.** A board often has states no preset models — `Blocked`, `Needs Design`, `Waiting on Vendor`. Name them and say what it means: items there are excluded from goal selection, because Cadence does not know what the status signifies. Then offer the two honest options rather than picking one:

   - **Leave them unmapped.** Correct when the status marks work that genuinely shouldn't be picked up. Nothing breaks; those items are simply outside the process.
   - **Fork the preset into a project-local flow** with a lane for it. Worth it when the state is part of how the team actually works — a `Blocked` status the team uses daily deserves a `blocked` role, so a session can park a stuck item there instead of leaving it looking active.

   Do not add lanes to a shipped preset to make a board fit; presets are read-only and a flow should describe the process, not the other way round.

7. Confirm the **roles**. The draft above proposes them; the user disposes. Never settle a role from a lane's *name* — whether picking up work means `Todo` or `In Progress` is a process decision, and no amount of reading the board reveals it. If the user doesn't want an `active` role, write it absent.

8. **Never create a column in their tracker.** Cadence adapts to the board; the board does not adapt to Cadence.

**The `markdown` tracker is the one case that inverts.** There is no existing board to read: its `statuses()` returns the values of `status_map`, which at init time is empty. The user is *defining* columns rather than mapping to them, so offer the flow's lanes as a starting set and let them cut it down — a solo builder who wants two columns should end with two, not five. Everything after that behaves identically; the map is just authored rather than discovered.

**Definition of Done:** **state the flow's existing bar, say what the repo suggests adding — usually nothing — and ask once, open.** *"The flow already requires `tests`, and `docs` when a documented surface changes. Nothing here suggests more. Anything you want to require beyond that?"*

This is the one thing a repo scan cannot answer, and it is worth being precise about why: a DoD is a **commitment about future work**, not a description of current practice. No `CHANGELOG.md` does not mean they do not want one required. So it stays a question — but an *open* one with a stated default, never a menu.

**A menu of plausible checks is not neutral.** Offering `accessibility` · `perf-budget` · `security-review` invites someone to pick the ones that sound responsible, and every pick is a gate their sessions must satisfy forever. One of them being unsatisfiable here is then discovered by cadence rather than by them — which is exactly what happened on a real init, where a selected `linter passes` met a repo with no lint script and no linter config. Ask open, and let the answer be theirs.

**Look for the bar already written down.** A file or heading called *Definition of Done*, a
feature-process or contributing document that lists what every change must satisfy — propose it,
confirm, and write it as `## Verification → Definition of Done` in the bus (a `shared` row: write
it only when absent). It is what session end quotes when it judges each declared check, and what
the delivery skill plans against. Checks the document lists that the user does not add here are
reported by the doctor as written-but-not-gated, so name them now: *"your document also lists
`accessibility-reviewed`; gate it, or leave it as guidance?"*

Whatever they name becomes `config.dod_gates`, which **adds to** the flow's `gates.dod.checks` rather than replacing it. Keep the shipped menu domain-neutral; a project's own bar arrives through "define your own."

**Check each named gate is satisfiable here before writing it**, and say so when it is not: a `linter passes` check in a repo with no lint script is a gate that fails every session or is quietly ignored, and both are worse than not declaring it. Offer to fold it into a check that exists, keep it and record that it is unsatisfiable for now, or add the missing tooling — their call, not yours.

**Write every check they add as `applies: infer`, and do not ask about applicability.** One question per check is an interview, and the default settles it without one: the session judges whether the check has anything to say about the change in front of it, and **names every skip with its evidence** (`${CLAUDE_PLUGIN_ROOT}/flows/FLOW-SPEC.md`). That is what makes inference safe rather than a quiet override — the trace, not the judgement.

Unconditional was the previous default and was worse: a check that fires at changes it has nothing to say about is how a Definition of Done turns into a toll people want an override for.

**Write `applies: always` instead where inference is unreliable** — and say why in one line when you do. A human gate (`peer-approved`: a person's absence is not evidence they had nothing to say), a check whose absence of evidence is not evidence of absence (`security-review`), or one cheap enough to just run (`tests`).

**Capture a condition they state themselves.** *"comment quality, but only for code"* is the user declaring applicability, not you inferring it: write it as a mapping with `applies_when` (`${CLAUDE_PLUGIN_ROOT}/flows/FLOW-SPEC.md`), preferring `changed_paths` globs when the surface is a path.

**Then say once, in the confirmation, how each check is decided** — inferred, always, or by a stated rule — and the one line that pins or narrows one. That keeps the property the field was added for: a condition is written by someone who does not yet know which check is about to be inconvenient, and it stays cheaper to write now than at the gate. A sentence they can act on beats four questions they have to answer.

**Model tiers.** Set `config.models` — default `mechanical: haiku`, `reasoning: inherit`. Rebind if the user lacks that tier.

## Phase 3 — Coherence check

Before writing, validate and **warn on any contradiction**:
- Every `states.roles` value is a member of `states.lanes`; `backlog` and `done` are present.
- Both lanes of every gated transition are declared, and every gate referenced exists.
- **Lane reachability**: a lane on the right of a gated transition that nothing reaches means that gate will never fire. Report it.
- Every `hooks:` entry names a real hook from `${CLAUDE_PLUGIN_ROOT}/flows/HOOKS.md` and points at a readable doc.
- No step whose decision right is `human` has a hook returning an autonomous decision.
- Every `config.<family>.kind` resolves to a generated adapter or a shipped fallback.
- The bus's `Intent` binding, if present, resolves the same way (`adapters/intent/<kind>.md`). It is another role's row — read it, never write it (Phase 4).
- Every priority-policy token's required field is supported by the tracker adapter — or the token is flagged as one that will be skipped.

## Phase 4 — Write

**Two writes, and the split is not negotiable** (see `config.example.md`): bindings go to the
**shared config bus**, methodology goes to cadence's own root.

**1. The bus — `.agent/PROJECT.md`.** One place, always: no alternative path, no configurable
override, no private copy. If it does not exist, **create it** from the skeleton in
`${CLAUDE_PLUGIN_ROOT}/checks/BUS-CHECKS.md` § *Creating the bus, when nothing has*, which carries
the frozen core verbatim including the schema marker's value — any tool may create the bus, none
may wait for another, and none may invent that number. Then add only the sections you own:

- **`## Tracker`** — a **`shared`** section. Present → **read it and leave it alone**, values
  and marker both. Absent → ask the user and write it. There is no takeover: which tracker a
  project uses is an environment fact, not a methodology decision, and rewriting another tool's
  marker to claim it would be claiming the fact rather than the decision.
- **`## Execution`** — the execution skill name and its `owns` set: what cadence must *verify*
  rather than repeat.
- **`## Version control` and `## Verification`** — also `shared`. Same rule: read what is
  there, write what is absent **or blank** (a present row with no value is a question nobody
  answered — ask it, fill that one row, touch nothing else), overwrite nothing. `## Verification` carries two rows, `Proven by` (what is automated) and `Definition of Done` (the path to the bar in the project's words); write either only when absent. You need verification for the DoD gate, which
  is exactly why it cannot belong to one tool.
- **The `Doc system` binding row** — read it. Write it only if absent.
- **The `Intent` binding row** — read it, and **never write it**, not even when absent. It belongs
  to the `intent-layer` role, whose own init writes it. A project with no intent layer has no row,
  and that is the correct state rather than a gap for cadence to fill.
- **`## Versions`** → `| cadence methodology | <this plugin's canonical> | methodology |`
- **`## Commands`** → `| methodology | /cadence:migrate | /cadence:init |`

**Preserve everything you do not recognise, verbatim.** Never reorder the file, never touch a
section whose owner marker is not yours.

**2. Cadence's own root — `.agent/cadence/config.md`.** Include `cadence_version`, set to this plugin's contract version, so a later upgrade mismatch is detectable rather than silent. Assemble the rest from the answers; **never write secrets or credentials**. For the `markdown` tracker, note that its `path` directory is created lazily on first item rather than seeded empty.

Set `session_state.file` (default `.agent/local/cadence-session.md`), create it, and call the VCS adapter's `ignore()` on it. If updating, back up the prior config first.

Then **commit Cadence's own output** via `add_untracked` + `checkpoint`: the config, generated adapters, and any flow are project state that collaborators need (see "Where adapter data lives" in `${CLAUDE_PLUGIN_ROOT}/adapters/ADAPTERS.md`). Leaving them untracked contradicts that, and risks them being swept into an unrelated commit later. The session-state file is the one thing that stays out.

## Phase 5 — Scaffold the docs

Create `config.doc_system.roadmap` from `${CLAUDE_PLUGIN_ROOT}/templates/vision-and-roadmap.md`, pre-filled with what you actually know about the project. Leave the sections you *don't* know as marked placeholders rather than inventing a vision — vision is human-led, and a confident fabrication is worse than an honest gap. Point the user at `/cadence:roadmap` to fill them.

Do not copy `feature-process.md` or `session-goals.md` into the project. They are plugin references, read from `${CLAUDE_PLUGIN_ROOT}/templates/` when needed; copying them creates a fork that silently goes stale when the plugin updates.

Do not overwrite existing docs — only fill gaps.

## Phase 6 — Dry-run

Resolve config + flow + adapters and show what `/cadence:session start` would surface now, including **which steps are disabled** by unmapped lanes or unsupported capabilities. Say whether `/cadence:plan` will check milestones against stated intent — it will when the bus binds `Intent` to anything but `none` — because the consequence of `none` is worth one line here rather than a discovery at planning time. Finish by naming the next moves: `/cadence:roadmap`, then `/cadence:plan`, then `/cadence:session start`. Mention `/cadence:doctor` as the way to re-check the setup later.

**Then say what to run next, and where the team's own step sits in it.** A flow with
`decision_rights.commit_scope: human` gets a planning *pack* rather than committed scope, because
the team commits its cycle in the tracker — that is the normal way sprints run, and cadence reads
the result rather than producing it.

So the next steps read: `/cadence:roadmap`, then `/cadence:plan` for the pack, then **your
planning meeting**, then commit the sprint on your board, then `/cadence:session start` — which
scopes to that cycle. Saying it as a sequence stops the pack looking like the end of the process.

## Non-interactive mode (`--defaults`)

For automated or headless use, `--defaults` skips the interview and writes the zero-dependency stack: `markdown` + `git` + `none` + `solo-greenfield`, `execution.skill: none`, a two-entry `status_map` (`backlog`, `done`), `dod_gates: [tests, docs]`, prefix derived from the directory name.

**It must never bind an MCP-backed tracker, and never adopt a config it finds in context.** The whole risk of a non-interactive mode is that it makes a confident guess with nobody watching; restricting it to the stack that assumes nothing removes that risk. If the user wants a real tracker, they run init properly.

## Notes

- **What init does NOT do:** create work items (that's `/cadence:plan`) or implement anything.
- **Idempotent:** safe to re-run; updates and backs up rather than clobbering. Re-run to regenerate an adapter if a tool's interface changed, or after upgrading Cadence if `meta.cadence_version` no longer matches.
- **Check for skill collisions.** If the project or user scope already has a `session`, `plan`, or `roadmap` skill, say so — Cadence's are namespaced `cadence-*` and won't be shadowed, but two live session rituals is a confusion worth naming rather than discovering mid-flow.
- **Never *own* the project's own memory.** Cadence writes only inside `.agent/cadence/`, plus one line in the ignore file. It must not write to a project's `CLAUDE.md` or agent `MEMORY.md`, must not require one to exist, and must not read one at run time — a skill that only works when a memory file is present has a hidden dependency on a file it does not control.

  **Reading one at init, as evidence, is different and is allowed.** Init already reads READMEs, manifests and skill files to work out what a project does; a convention file is the same kind of source, and often the best one. What matters is that whatever you learn gets *confirmed with the user and written into Cadence's own config or adapter* — after which nothing depends on the original. Quote the source for anything you carry across, so a stale claim can be traced back.
- **Zero-dependency default:** if nothing is detected, `markdown` + `git` + `none` + `solo-greenfield` is a complete, runnable setup with no external service and no generated adapters.

## Show what you wrote, and have it confirmed

**Every init ends by presenting the configuration it produced.** Not a summary — the content, or a
faithful rendering of it. A summary is where a wrong assumption survives: *"configured your
tracker"* reads as correct whatever actually got written.

**Mark what you inferred, separately from what you were told.** The lines the user supplied need no
scrutiny. The inferred ones are the whole reason to ask, and separating them turns "does this look
right?" — whose honest answer is usually "I suppose so" — into a short list of specific claims
somebody can check.

Say two more things while you have their attention: **what this configuration switched off** (a
binding left `none`, anything the tool cannot do here) and **how to change each part** — the file
to edit, or the command to re-run. A confirmation nobody can act on is a notification.

Running non-interactively: print the same thing and say plainly that it was **not confirmed**.
