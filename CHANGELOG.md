# Changelog

All notable changes to the plugins in this marketplace are recorded here. This
file covers **Cadence**; if the marketplace gains a second plugin, it gets its
own section.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
Cadence uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html) with one
project-specific rule: **the contracts are the public API.** Renaming a hook,
changing a hook's Input/Output, removing an adapter operation, or changing the
meaning of a config key is a *major* change. Adding an optional hook, operation,
field, or config key is *minor*.

## [0.4.1] — 2026-08-11

### Changed

- **Adapter generation reads the project's own documentation first, then the
  tool.** Init previously said to generate a VCS adapter by inspecting the CLI. A
  real project's notes turned out to carry what no interface can express: that its
  VCS *"has no amend or reword — a garbled commit message is permanent"*, and that
  the documented fix for one failure mode *"overwrites local edits"*. `--help`
  lists verbs; it does not tell you which of them will quietly discard a day's
  work. An adapter built only from an interface knows how to call things and not
  when calling them is a mistake — which is exactly what the etiquette rules
  (never push, never force, surface destructive actions) depend on knowing.

  Docs for judgement, the tool for verbs, and **cite where each gotcha came from**
  so it can be re-checked when the tool changes. Applies to trackers too.

- **The "never touch project memory" rule was over-broad, and it forbade this.**
  It said Cadence must not *read* a `CLAUDE.md` or agent `MEMORY.md`. The
  principle's purpose is that Cadence must not **own or depend on** those files:
  never write to one, never require one, never read one **at run time**, because a
  skill that only works when a memory file is present has a hidden dependency on a
  file it does not control.

  Reading one *once at init*, as evidence for a binding the user then confirms, is
  a different act — init already reads READMEs, manifests and skill files — and
  leaves nothing depending on the original. The rule now says dependency and
  ownership rather than reading. `/cadence:session` keeps the run-time
  prohibition unchanged.

### Not yet exercised

Both changes were verified by review and by the payload validator, **not by a run
against a real project**. The docs-first adapter path especially: it has never run
where there was actual project prose to read, which is the only case that
motivated it. Released, but unproven on that axis — and the honest failure mode
is silent, since an init that ignores an existing project config and re-interviews
from scratch produces a plausible config rather than an error.

## [0.4.0] — superseded

Found by running `/cadence:doctor` against a real project for the first time —
MachineGame54, 245 issues, a Diversion working copy, a `domains/` doc system, and
a Linear board with eight statuses.

### Added

- **An item whose status maps to no lane is never a selection candidate.** A real
  board carries states no flow named — that board has `Blocked`, another team's
  has `Needs Design` or `Waiting on Vendor`. Such an item is neither terminal nor
  ready, and Cadence does not know what the status means, so offering it as a
  session goal would be claiming knowledge it doesn't have. Previously
  `list_open` returned them and goal selection would have picked one.

  This is deliberately **one rule rather than a role per status**. Chasing
  `blocked`, then `waiting`, then `needs-design` has no end, and each new role
  would be Cadence guessing at another team's semantics.

- **Optional `blocked` role**, for the single thing the rule above cannot do:
  *park* a stuck item somewhere honest. Leaving it `active` claims someone is
  working on it; sending it back to `backlog` loses that it was started. Nothing
  moves an item there automatically — Cadence cannot tell "stuck" from
  "unfinished", and only an explicit statement parks one. Blocked items do not
  count toward `wip_limit`, since the limit caps concurrent work and blocked work
  is not progressing.

  **No shipped preset declares it.** Adding a `Blocked` lane to a preset would
  assert that boards ought to have that column, contradicting the rule that lanes
  are process vocabulary rather than columns you must create. `/cadence:init` now
  spots statuses a preset cannot name and offers the two honest options: leave
  them unmapped, or fork the preset into a project-local flow with a lane for it.

- `/cadence:doctor` reports how many items sit in unmapped statuses. A handful is
  normal; a third of the board means the flow does not describe how that team
  actually works.

## [0.3.6] — 2026-08-11

Closes the hosted-tracker work. A full kanban loop ran against a live Linear
board with no new broken behaviour — the two findings below are a missing rule
and a diagnosis, not failures.

### Fixed

- **Goal selection could return a container.** `FLOW-SPEC.md` has always said the
  last entry in `hierarchy.levels` is the unit a session works on; the session
  skill never implemented it. Every earlier run hid this because candidates were
  chosen by judgment, which naturally skips epics. A mechanical token has no
  judgment: `oldest-open` returned the epic, and the framing step would have
  written "by end of session this epic is Done" — a promise no session can keep.
  Candidates are now filtered to the working level before ranking.

  Worth recording as a pattern: **automating a step removes the human judgment
  that was silently compensating for a missing rule.**

- **Switching flows can strand an item** in a status the new flow maps to no lane.
  Observed moving a board from `team-sprints` to a kanban flow. Harmless when
  moving forward, and `/cadence:doctor` already flags it, but the session now says
  so rather than proceeding as if the item's position were known.

### Added

- **`oldest-open` priority token** — the only one that can always be evaluated,
  since every tracker knows creation order. Every other token needs a field the
  board may lack (`order`, `milestone`, `cycle`) or an item already in flight to
  anchor against, so a policy built only from those can select nothing at all on a
  fresh board. Two shipped presets did exactly that on a real team with five open
  items in it.

  It is **opt-in and absent from every shipped preset**, by design: appending it
  everywhere would be the "arbitrary pick dressed as a decision" that 0.3.2
  forbids, and would have masked the signal that found two defects in this
  session. For a sprint team "nothing is committed" is the right answer.

### Verified against a live Linear board

A full kanban loop: `ai-proposes` presented three candidates and waited; the
working-level filter excluded the epic; both gates on a path through an *unmapped*
`In Review` ran; `gate.code_review` (`human`) held and was not auto-cleared;
`gate.dod` (`ai-proposes`) reported a recommendation rather than a clearance; the
held gate did not cost the work — committed, tree clean, commit naming the gate.

### Known gaps, recorded not glossed

- **A cycle actually running.** Scope commitment is verified; a session drawing
  from a live cycle is not. Linear will not backdate a cycle's start date.
- **A gate that fails outright**, as opposed to being held by a human approver.
- The ceremony layer remains documented and deliberately not invokable.

## [0.3.5] — superseded

### Fixed

- **"The priority policy found nothing" conflated a gap with an answer.** 0.3.2
  treated an exhausted policy as a failure and offered the backlog for picking.
  But a token that *could not be evaluated* (field unsupported or unpopulated) is
  a gap, while a token that *was* evaluated and returned nothing is an answer.
  `committed-sprint` on a board with work committed to a cycle starting next week
  has not failed — it has said the sprint hasn't begun. Presenting a free choice
  there quietly invites starting cycle work early, which is the one thing a sprint
  flow exists to prevent. The two cases are now handled separately.

### Verified against a live board

- **Cycle commitment is two writes, and both landed**: `cycle: 1` plus a move to
  `roles.committed`. Deferred items stayed in `Backlog`, so the board now
  distinguishes "in the backlog" from "committed to the cycle" — which is what the
  `committed` role was added for.
- Both lanes resolve to a status *displayed* as `Queued` (categories `backlog` and
  `unstarted`). They look identical on the board and are different states; the
  qualified `status_map` form is what keeps them apart.

## [0.3.4] — superseded

### Added

- **`/cadence:init` drafts a `status_map` from the tracker's own categories.**
  Most trackers already classify their statuses — Linear's
  `backlog`/`unstarted`/`started`/`completed`/`canceled`, and equivalents
  elsewhere. Init now reads that classification, drafts a starting map, and puts
  it up for correction, rather than making the user hand-write one.

  This is **detection, not inference**: it reads a classification the tool already
  made and asks. Nothing is written unconfirmed, the draft is explicitly a hint
  with no authority — a category says how the tool files a status, not what the
  team means by it — and duplicate names are always asked about, never drafted.
  Where a tool has no categories there is nothing to read, so init asks rather
  than manufacturing a proposal from lane names that look similar.

  Checked against the board this was built on: the draft reproduces the map that
  was hand-written for it, and additionally catches `abandoned` (`Dropped`,
  `Duplicate`) — which the hand-written version missed.

- The `markdown` tracker is documented as the case that inverts: there is no
  board to read, so the user is *defining* columns rather than mapping to them,
  and init offers the flow's lanes as a starting set to cut down.

## [0.3.3] — superseded

### Fixed

- **Three shipped flows declared lanes nothing could ever reach.** `team-sprints`
  and `live-oncall` each had a `Sprint Backlog` that no role named and no
  transition mentioned; `solo-greenfield` had `Todo` and `In Review` in the same
  state — the second of which *this cleanup created*, when the gate moved to
  `In Progress -> Done` and left `In Review` stranded. A flow naming a part of a
  process it cannot perform is a promise it cannot keep.
- **The vocabulary had no way to say "committed to the cycle, not yet started".**
  That is why `Sprint Backlog` was orphaned rather than simply deleted — the state
  is real in every sprint process. Added an optional **`committed`** role, wired
  it into both sprint presets with transitions in and out, and made
  `/cadence:plan` move items there when scope is committed. Committing scope is
  two things, not one: writing the cycle *and* moving the item.
- `solo-greenfield` now declares three lanes rather than five. It never used the
  other two.

### Added

- **Validator rule: orphan lanes.** A lane in `states.lanes` that no role names
  and no transition mentions is an error. The existing reachability rule only
  inspected lanes that *appeared in* transitions, so it structurally could not see
  this. The new rule found all three cases on its first run.

## [0.3.2] — superseded

### Fixed

- **The priority policy could exhaust while open work sat there, and nothing said
  what to do.** A live board had five open items and matched no token: nothing in
  flight, so `blocker-for-current-ticket` and `current-epic` had no anchor, and no
  item carried a milestone, so `next-roadmap-ticket` found nothing. The skill
  covered "no open items" but not "items exist, no token matched". It now lists
  them, names which tokens missed **and why**, and asks — explicitly refusing to
  fall back to "the oldest" or "the first listed". Under `select_goal: ai` the
  policy *is* the mandate to choose; with it exhausted there is no mandate, and an
  arbitrary pick dressed as a decision is worse than a question.
- **`/cadence:plan` set `epic` but not `milestone`,** which is what left goal
  selection blind. Its instruction to set "milestone/epic links always" was too
  glib: some fields are **conditionally** settable — a Linear milestone needs a
  project to exist first, so `milestone` can be adapter-supported and still
  unsettable. Plan now checks each policy field is actually settable here, and
  where it isn't, says which token that disables rather than silently omitting it.

### Verified against a live board

- `set_status` twice on a hosted tracker: `Queued(backlog)` → `Building` →
  `Shipped`, resolved through lane roles and the qualified `status_map`. Linear
  set `startedAt` and `completedAt` itself.
- **The terminal-union fix, demonstrated rather than reasoned about.** Cancelling
  an item and re-listing shows the old rule returning it as open — a cancelled
  ticket would have been a candidate goal in every future session — and the new
  rule correctly excluding it.
- Tracker writes left the repo untouched, so the checkpoint ordering held for the
  opposite reason to the markdown case: not because tracker writes are repo
  writes, but because they aren't.

## [0.3.1] — superseded

### Added

- **`cadence_version` in the config.** Flows have always declared the contract
  version they target; configs did not — so a config using a newer contract
  feature than the installed plugin was undetectable. That is not theoretical: it
  happened here, when a config written with the qualified `status_map` form met a
  plugin that predated it. The older skill reads a mapping where it expects a
  string and cannot know why. Init now stamps it and `/cadence:doctor` reports a
  mismatch as **broken**, naming which side is behind.

## [0.3.0] — superseded

First run against a **hosted tracker**. Three defects that the `markdown`
fallback structurally could not expose, because its statuses are the values of
`status_map` and therefore unique, complete and non-terminal by construction.

### BREAKING

- **`statuses()` returns records, not names.** `{name, id?, category?, terminal?}`
  per status. A name is not a unique key on a real board.

### Fixed

- **A status name can be ambiguous.** A live Linear board had two states both
  called `Queued`, one `backlog` and one `unstarted` — a configuration Linear,
  Jira and GitHub Projects all permit. `status_map` mapped lanes to statuses by
  name and `set_status` only had to reject a name matching *nothing*; neither
  handled a name matching *two*. `status_map` now accepts a qualified
  `{name, category}` form, `set_status` must refuse an ambiguous target rather
  than pick one, init asks which is meant, and doctor reports the ambiguity.
- **A tracker's own terminal states were ignored.** The terminal set came only
  from the flow's `done` + `abandoned` roles, so a board's `canceled` and
  `duplicate` states — which `solo-greenfield` does not model — counted as
  **open**, and cancelled work would resurface as a candidate goal forever. The
  terminal set is now the union of what the flow declares and what the tracker
  knows.
- **Capability declaration was binary; real adapters are not.** Linear accepts
  `blockedBy` on a write but returns no relations from its list query, so
  `depends_on` is writable and readable only one item at a time. Added a
  **`costly`** tier so a skill narrows the set or delegates the sweep, rather
  than fanning out over a backlog or silently skipping the field.

### Verified against a real board

- Init **discriminated** between two visible Linear teams, binding the one whose
  name matches the repo and rejecting the other. Previously it had only ever been
  observed refusing.
- The generated adapter is the first written against a real interface: it records
  that `save_issue` without `id` creates (a duplicate-issue hazard on a live
  board), that `labels` is a full replacement, and that `blockedBy` needs
  `includeRelations: true` on a per-item read.
- `plan` created an epic and four children with real parent links and
  dependencies, invented no labels (`taxonomy()` unsupported), skipped
  `backlog-by-rank` (this MCP exposes no sort order), and **committed nothing** —
  the first exercise of the hosted-tracker branch, where the backlog is not in
  the repo.

## [0.2.6] — 2026-08-11

### Fixed

- **Two end-of-session rules contradicted each other when both fired.** The
  gate-held rule said "still checkpoint (step 5)"; step 5's verify branch said
  "do not quietly commit on execution's behalf — offer". With a held gate *and*
  an execution skill that owed a commit and didn't make one, an agent reading
  the first would commit and one reading the second would offer. The gate rule
  now defers to step 5 to decide *how* the work is saved, and says explicitly
  that a held gate is not a licence to paper over a broken execution binding.

### Verified

All three fixture shapes run clean against this build:

- `reduced-lane` — `In Progress` unmapped: transition skipped and noted, no
  status written outside `status_map`, `gate.dod` still ran, item reached `Done`,
  tree clean, HEAD agreeing with the working copy.
- `intermediate-gate` — project-local flow and both authored hooks resolved;
  **`gate.citations` ran** from the intermediate hop into an unmapped `Reviewed`;
  `gate.editorial` (`human`) was not auto-cleared; the item was not dragged
  backwards to an `active` lane it had already passed; the held gate did not
  abandon the work — committed, tree clean, commit naming the holding gate.
- `execution-owns-commit` — the verify branch ran for the first time, correctly
  reported that nothing referenced `UC-1` and the tree was dirty, and named the
  two possible faults.

## [0.2.5] — superseded

### Fixed

- `tools/make_fixture.py` generated configs whose YAML did not parse — the
  status_map block was spliced into an indented template that was then dedented,
  leaving the first mapped lane at a different depth from the rest. All three
  fixtures were affected, so a verification run against them would have "found" a
  config-parse failure in the plugin that was really in the harness. The config
  is now built flat, and **the generator self-checks**: it parses the config, every
  item's front-matter, and any project-local flow's hook references, and refuses
  to report success if the fixture is not the shape it claims.

## [0.2.4] — superseded

### Fixed

- **The verify branch had no failure path.** When `execution.owns` includes
  `commit`, `/cadence:session end` verifies someone else's checkpoint instead of
  making one — and said nothing about what to do when that verification fails.
  Every test run until now used `execution.skill: none`, so the branch had never
  executed at all. It now reports the discrepancy precisely, declines to commit
  silently on execution's behalf (which would hide a broken execution binding
  forever), declines to abandon the work, and says the fault is either the
  execution skill or an `execution.owns` that overstates what it does. If no
  checkpoint exists by the end of the step, the item does not stay advanced.
- `/cadence:doctor` now reports an `execution.owns` that claims `commit` while
  recent items have no referencing checkpoint.

### Added

- `tools/make_fixture.py` — scripted scratch projects in the configuration
  *shapes* the default cannot expose: `reduced-lane`, `intermediate-gate`,
  `execution-owns-commit`.
- A **coverage table** in `docs/VERIFICATION.md` naming the configuration axes
  and which shape covers each, so the gaps are visible rather than discovered.
  Two axes are still uncovered and now say so: a hosted tracker, and sprint
  cadence with cycles.

## [0.2.3] — superseded

### Fixed

- **A held gate abandoned the session's work.** `/cadence:session end` stopped
  dead when a gate didn't clear, so the prune, next-goal and checkpoint steps
  never ran — leaving real work uncommitted and, under a file-based tracker, the
  tree dirty. That poisons the `status()`-clean check the next session depends
  on, which is the exact failure the checkpoint-ordering fix existed to prevent,
  reached through a different door. Gates decide whether the **item** advances,
  not whether the **work** is saved: end now skips only the status change and
  still records why the gate held, still checkpoints, and says in the commit
  message which gate is holding the item.
- **A session could move an item backwards.** `session start` moved the goal to
  `roles.active` unconditionally. In a flow whose lanes are a pipeline rather
  than a single in-flight state, an item already downstream of the active lane
  got dragged back up it. Transitions now only ever move forward along the
  declared path.

## [0.2.2] — superseded

> **Tagged `v0.2.6`.** `docs/VERIFICATION.md` sections 1–7b pass against a real
> install. Sections 8–9 remain unrun and their gaps are recorded in the coverage
> table rather than glossed: a hosted tracker, sprint cadence with cycles, and a
> gate that fails outright rather than being held.

### Fixed

- **Gates on intermediate transitions could still be skipped.** 0.2.1 matched
  gates on the *destination* lane, which rescued the gate immediately before
  `done` and nothing else. Two shipped flows have gates that this missed:
  `manuscript`'s `gate.citations` on `Supported -> Reviewed` — the entire point
  of that flow — and `live-oncall`'s `gate.postmortem` on
  `Resolved -> Postmortem`. On a board without those columns, both silently
  never fired. Gates are now collected along the **whole declared path**: an
  unmapped lane skips the status write, never a gate. Otherwise the fewer
  columns a team has, the fewer checks they get, which is backwards.
- `/cadence:doctor` reported an unmapped lane under a gated transition as
  **broken** when nothing actually fails. It is now **drifted**, states that the
  gate still runs, and offers both remedies — map the lane, or redraw the flow's
  transitions to describe the board you have. A diagnostic that cries wolf on a
  correctly-configured board teaches people to ignore it. The genuinely broken
  case is narrower and still reported: a gate on a transition no item can reach.

## [0.2.1] — superseded

> **Supersedes 0.2.0**, which was published for about twenty minutes and is
> superseded rather than listed separately. It registered every capability twice
> (`/cadence:init` *and* `/cadence:cadence-init`) because it shipped both a
> `commands/` directory and `cadence-`-prefixed skills. Both are removed here.
>
> The version bump is also what makes the fix *reach* anyone: the plugin cache is
> keyed by version, so republishing the same number leaves installed copies on the
> old payload. **Any change to the payload needs a version bump.**

The plugin was well-designed on paper and could not actually be installed as
documented. Three rounds of audit — static review, then six live evaluation runs
in throwaway repos — found ~45 verified defects. This release fixes them.

### BREAKING

- **Config location is now `.claude/cadence/config.md`, always.** The alternative
  `domains/PROJECT.md` branch is gone: it was tool-specific inside tool-agnostic
  skills, *and* outside the root the design declares inviolable. Move an existing
  config, or re-run `/cadence:init`. `/cadence:doctor` detects the old layout.
- **`config.tracker.statuses` is replaced by `config.tracker.status_map`.** The
  old key was a fixed four-slot map that could not express a flow's lanes.
  `status_map` maps a flow lane to the status your tracker really has, and is
  built from the tracker rather than from a preset.
- **`epic_convention` moved out of config** into the tracker adapter's concept
  mapping. How a tool models an epic is a fact about the tool.
- **`/cadence:session end` reorders**: gates → set status → checkpoint. Any hook
  or authored flow that assumed the commit came first must be updated.
- **Skills renamed**, with directories matching. They are addressed
  `/cadence:init`, `/cadence:session`, and so on — the plugin namespace supplies
  the `cadence:` prefix, so the skill names themselves stay bare. A project
  referring to them by any other name must update.
- **Flow specs now require `meta.cadence_version` and `states.roles`.** An
  existing custom flow will not validate until both are added.
- **`session_state.vcs_ignored` is removed.** Ignoring is an action init takes,
  not a fact config records.

### Added

- `flows/FLOW-SPEC.md` — the flow-spec schema as its own document, with every
  key's type, whether it's required, and which skill reads it. Previously the
  schema *was* a preset, so the other presets invented keys nothing recognised.
- **Lane roles** (`states.roles`). Skills ask for a role, never a literal status.
  Roles are declared by a human and never inferred; an absent `active` role means
  sessions don't touch status, which is a valid process rather than a gap.
- **Five working commands** — `/cadence:init`, `:session`, `:plan`, `:roadmap`,
  `:doctor`. Plugin skills are addressed `plugin:skill`, so the previously
  documented `/cadence init` was never a form Claude Code could parse. The skills
  provide these directly; a `commands/` wrapper directory was tried first and
  removed once a real install showed it registered every capability twice.
- **`/cadence:doctor`** — read-only diagnosis of a project's setup: unknown config
  keys, flow validity, adapter coverage, tracker reachability *and whether its
  workspace belongs to this repo*, whether mapped statuses still exist, live data
  corruption, and whether session state is really ignored.
- **Tracker `statuses()`** — the primitive the status layering rests on. Also
  `list_closed()`, `update()`, optional `list_cycles()`/`current_cycle()`, and
  VCS `log()`, which `/cadence:session end` already required and could not do.
- **Per-adapter capability declarations**, so an unsupported field degrades
  visibly instead of silently.
- **Item fields** `assignee`, `cycle`, `order`, `depends_on`, `severity`,
  `updated_at`, so the priority policy has data to work with.
- `taxonomy()` on the doc-system contract; empty is a valid answer.
- `roadmap.milestone_progress` hook and `/cadence:roadmap` Mode C, reconciling
  the roadmap against what shipped — measured against exit criteria, not ticket
  counts.
- `tools/validate_cadence.py` and CI, enforcing eleven invariants that have each
  actually broken here. `tools/README.md` records why each rule exists.
- `CONTRIBUTING.md`, `docs/VERIFICATION.md`, a root `LICENSE`, and this file.
- A `--defaults` non-interactive mode for init, deliberately restricted to the
  zero-dependency stack and forbidden from binding any MCP.

### Fixed

- **`/cadence:session end` committed before writing to the tracker.** Under the
  `markdown` tracker — whose items are committed files — every tracker write is a
  repo write, so committing first captured the item still open and re-dirtied the
  tree, and the "tree clean" check later sessions depend on could never pass
  again. The checkpoint is now the last repo write, after *all three* tracker
  writes (status, next-goal comment, recorded gotcha). Fixing only the status
  ordering left the same failure two steps later — a regression run caught it.
- **A gate could be silently skipped on a board with fewer columns.** Gates were
  matched on the exact `"<from> -> <to>"` transition, so if an intermediate lane
  was unmapped the item took a different route and the gate never fired — meaning
  a missing column silently lowered the Definition of Done on the zero-dependency
  default. Gates now match on the **destination** lane. *(Partial — corrected in
  0.2.2, which collects gates along the whole declared path.)*
- **`In Progress` and `In Review` were unreachable.** `set_status` was called once
  and went straight to done, so items jumped `Backlog → Done` and
  `solo-greenfield`'s only gate was attached to a transition that never occurred.
- **`config.example.md` shipped a real project's filled-in config** while init was
  told to write configs "per" that file. An undocumented key from that example
  leaked into two unrelated projects during testing. Init now assembles the config
  from the user's answers and copies nothing.
- **Init bound any connected tracker MCP without checking whose it was.** MCPs are
  user-scoped and Cadence is installed once for every project, so the tracker in
  view is often another product's. Init now corroborates the workspace against the
  repo and asks when it can't.
- **Seven catalogued hooks were never fired by any skill.** `intake.classify`,
  `intake.prioritize`, `bug.triage`, `transition.*` and `checkpoint` now have real
  firing sites; `ceremony.*` and `release` are explicitly marked deferred.
  `bug.triage` mattered most — the bug rule was stated at session start and never
  applied.
- Skills referenced bundled files by bare path, which resolves into the
  *consumer's* repo. All such references are now anchored with
  `${CLAUDE_PLUGIN_ROOT}`.
- The marketplace name didn't match the documented install command. It is now
  `innerdaze`, and install is `cadence@innerdaze`. Note it deliberately does not
  match the repository name: Claude Code rejects a marketplace whose `name`
  contains "claude" or "anthropic" as impersonating an official source, and that
  rejection only surfaces at install time.
- `execution.skill: none` — the advertised default — was undefined in the flow
  spec and actively forbidden by a shipped template.
- Definition-of-Done precedence between `flow.gates.dod.checks` and
  `config.dod_gates` was never stated. It is a union: a project may raise the
  flow's bar, never lower it.
- Item titles containing a colon were unquoted and silently unparseable.
- `comment()` didn't refresh `updated:`, so commented items fell out of
  `updated_since` filters.
- The `git` adapter's `checkpoint` staged with a blanket `git add -A`, attributing
  build output and unrelated stray edits to the item's commit.
- `markdown` tracker data moved from `.cadence/` into `.claude/cadence/`, the root
  the design says Cadence never writes outside of.
- Game-specific gates removed from the shipped DoD menu and templates.

### Known limitations

- **The ceremony layer is documented but not invokable.** No skill fires
  `ceremony.*`; no command runs a standup, review, retro, or incident review.
  `team-sprints` and `live-oncall` are usable for their lanes, gates and decision
  rights, but Cadence will not run your meetings. `/cadence:plan` writes a
  planning pack when `commit_scope` is `human`, which is the one real path.
- **`states.release_pipeline` is declarable but not walked.**
- **The `markdown` fallback has no cycles or assignees**, so `committed-sprint`
  is skipped on it.

## [0.1.0]

Initial internal version. Never published.
