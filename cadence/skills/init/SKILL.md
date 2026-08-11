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

Inspect the repo and connected tools, present findings as one summary the user confirms or corrects, and **for each non-fallback tool, generate a project-local adapter** at `.claude/cadence/adapters/<family>/<kind>.md` implementing that family's contract — including its **Capabilities** block — against what you actually find. Never assume a tool or its interface.

1. **Doc system.** If the project keeps structured knowledge docs with an index → propose that `kind` and generate `.claude/cadence/adapters/docs/<kind>.md`, including `taxonomy()` from its headings. Else → the shipped `none` fallback. Either way, ask where the roadmap should live (`doc_system.roadmap`, default `docs/ROADMAP.md`) — it is a project document, not Cadence state, so it belongs where a person would look for it.

2. **VCS.** Detect `.git` / `.diversion` / `.jj` / `.hg`. `git` → use the shipped fallback. Anything else → inspect its CLI and generate `.claude/cadence/adapters/vcs/<kind>.md` against the tool's real commands, capturing only **tool-generic** gotchas; machine- or workspace-specific quirks go in `config.vcs.gotchas`, not the adapter. Detect an existing commit skill to delegate to.

3. **Execution skill.** Scan `.claude/skills/`, enabled plugins, and global skills for a ticket-execution skill. **Propose a candidate, but confirm three things with the user**: that it's the right one, how it's invoked, and what it `owns`. Also check it can actually run *here* — a skill that hardcodes another project's engine, tracker, or VCS will abort on first use, and `execution.skill: none` is better than a binding that fails. `none` is a first-class answer, not a fallback.

4. **Tracker.** Detect connected tracker MCPs.
   - **Before binding any of them, confirm the workspace belongs to *this* repo.** MCPs are user-scoped and Cadence is installed once for every project, so the tracker you can see is very often somebody else's. Query the tool for its teams/projects and look for corroboration: a name matching this repo, an existing ticket prefix that matches, recent items referencing this codebase. **If you cannot confirm it, ask.** Do not bind a tracker on the strength of its being the only one connected — that is how tickets end up filed into another product's board.
   - Once confirmed, inspect the verbs it actually exposes and generate `.claude/cadence/adapters/trackers/<kind>.md` implementing the tracker contract against those exact operations. Collect `mcp_namespace` and IDs into config.
   - If none is connected, or none is confirmed → the shipped `markdown` fallback. This needs no MCP and is a perfectly good answer.

Show the generated adapters and the assembled bindings, and get explicit confirmation. Adapters are stored **in the project**; the plugin is untouched.

## Phase 2 — Choose the flow

**A) Pick a preset**, then optionally override axes:
- `solo-greenfield` — one builder, pre-release; high autonomy, continuous, bugs deferred.
- `team-sprints` — cycle cadence; the skill proposes, the team commits scope. Needs a tracker with cycles.
- `live-oncall` — an incident lane that preempts the roadmap; more gates; releases human-approved.

Summarize each, let the user pick, then offer to tweak any axis. Say plainly which parts of a preset are **not yet automated** (ceremonies, release pipelines) so nobody adopts `team-sprints` expecting Cadence to run their standup.

**B) Author a custom flow** — walk the vocabulary in `${CLAUDE_PLUGIN_ROOT}/flows/FLOW-SPEC.md`. For any step the vocabulary can't express, author a **hook doc** against the contract in `${CLAUDE_PLUGIN_ROOT}/flows/HOOKS.md`. Write to `.claude/cadence/<name>.flow.md` (+ `.claude/cadence/hooks/*.md`).

### Then map the lanes to real statuses — do not skip this

The flow's lanes are **process vocabulary**. Your tracker has whatever columns it has. `config.tracker.status_map` is the only place the two meet, and it is built from what the tool reports, never from the preset:

1. Call the tracker adapter's **`statuses()`**. If the adapter declares `statuses` unsupported, ask the user to list their columns once.

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

4. **Lanes with no counterpart are left unmapped — not invented.** Say what that disables, concretely: *"no column for `In Progress`, so sessions won't mark work in flight."* That is a normal outcome on a two-column board.

5. Confirm the **roles**. The draft above proposes them; the user disposes. Never settle a role from a lane's *name* — whether picking up work means `Todo` or `In Progress` is a process decision, and no amount of reading the board reveals it. If the user doesn't want an `active` role, write it absent.

6. **Never create a column in their tracker.** Cadence adapts to the board; the board does not adapt to Cadence.

**The `markdown` tracker is the one case that inverts.** There is no existing board to read: its `statuses()` returns the values of `status_map`, which at init time is empty. The user is *defining* columns rather than mapping to them, so offer the flow's lanes as a starting set and let them cut it down — a solo builder who wants two columns should end with two, not five. Everything after that behaves identically; the map is just authored rather than discovered.

**Definition of Done:** present a multi-select, always ending in "define your own" — `tests` · `docs` · `no-warnings` · `accessibility` · `perf-budget` · `persistence` · `changelog` · `security-review` · *define your own…* The selection becomes `config.dod_gates`, which **adds to** the flow's `gates.dod.checks` rather than replacing it. Keep the shipped menu domain-neutral; a project's own bar arrives through "define your own."

**Model tiers.** Set `config.models` — default `mechanical: haiku`, `reasoning: inherit`. Rebind if the user lacks that tier.

## Phase 3 — Coherence check

Before writing, validate and **warn on any contradiction**:
- Every `states.roles` value is a member of `states.lanes`; `backlog` and `done` are present.
- Both lanes of every gated transition are declared, and every gate referenced exists.
- **Lane reachability**: a lane on the right of a gated transition that nothing reaches means that gate will never fire. Report it.
- Every `hooks:` entry names a real hook from `${CLAUDE_PLUGIN_ROOT}/flows/HOOKS.md` and points at a readable doc.
- No step whose decision right is `human` has a hook returning an autonomous decision.
- Every `config.<family>.kind` resolves to a generated adapter or a shipped fallback.
- Every priority-policy token's required field is supported by the tracker adapter — or the token is flagged as one that will be skipped.

## Phase 4 — Write

Write the config to **`.claude/cadence/config.md`** — one location, always. Include `cadence_version`, set to this plugin's contract version, so a later upgrade mismatch is detectable rather than silent. Assemble the rest from the answers; **never write secrets or credentials**. For the `markdown` tracker, note that its `path` directory is created lazily on first item rather than seeded empty.

Set `session_state.file` (default `.claude/cadence/SESSION.local.md`), create it, and call the VCS adapter's `ignore()` on it. If updating, back up the prior config first.

Then **commit Cadence's own output** via `add_untracked` + `checkpoint`: the config, generated adapters, and any flow are project state that collaborators need (see "Where adapter data lives" in `${CLAUDE_PLUGIN_ROOT}/adapters/ADAPTERS.md`). Leaving them untracked contradicts that, and risks them being swept into an unrelated commit later. The session-state file is the one thing that stays out.

## Phase 5 — Scaffold the docs

Create `config.doc_system.roadmap` from `${CLAUDE_PLUGIN_ROOT}/templates/vision-and-roadmap.md`, pre-filled with what you actually know about the project. Leave the sections you *don't* know as marked placeholders rather than inventing a vision — vision is human-led, and a confident fabrication is worse than an honest gap. Point the user at `/cadence:roadmap` to fill them.

Do not copy `feature-process.md` or `session-goals.md` into the project. They are plugin references, read from `${CLAUDE_PLUGIN_ROOT}/templates/` when needed; copying them creates a fork that silently goes stale when the plugin updates.

Do not overwrite existing docs — only fill gaps.

## Phase 6 — Dry-run

Resolve config + flow + adapters and show what `/cadence:session start` would surface now, including **which steps are disabled** by unmapped lanes or unsupported capabilities. Finish by naming the next moves: `/cadence:roadmap`, then `/cadence:plan`, then `/cadence:session start`. Mention `/cadence:doctor` as the way to re-check the setup later.

## Non-interactive mode (`--defaults`)

For automated or headless use, `--defaults` skips the interview and writes the zero-dependency stack: `markdown` + `git` + `none` + `solo-greenfield`, `execution.skill: none`, a two-entry `status_map` (`backlog`, `done`), `dod_gates: [tests, docs]`, prefix derived from the directory name.

**It must never bind an MCP-backed tracker, and never adopt a config it finds in context.** The whole risk of a non-interactive mode is that it makes a confident guess with nobody watching; restricting it to the stack that assumes nothing removes that risk. If the user wants a real tracker, they run init properly.

## Notes

- **What init does NOT do:** create work items (that's `/cadence:plan`) or implement anything.
- **Idempotent:** safe to re-run; updates and backs up rather than clobbering. Re-run to regenerate an adapter if a tool's interface changed, or after upgrading Cadence if `meta.cadence_version` no longer matches.
- **Check for skill collisions.** If the project or user scope already has a `session`, `plan`, or `roadmap` skill, say so — Cadence's are namespaced `cadence-*` and won't be shadowed, but two live session rituals is a confusion worth naming rather than discovering mid-flow.
- **Never touch the project's own memory.** Cadence owns only `.claude/cadence/` plus one line in the ignore file. It must not read, write, or depend on a project's `CLAUDE.md` or agent `MEMORY.md`.
- **Zero-dependency default:** if nothing is detected, `markdown` + `git` + `none` + `solo-greenfield` is a complete, runnable setup with no external service and no generated adapters.
