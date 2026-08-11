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

## [0.2.4] — pending verification

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

> **Not yet tagged.** Installation is now verified — the plugin loads,
> `${CLAUDE_PLUGIN_ROOT}` resolves inside skill bodies, the `mechanical` subagent
> registers, and `/cadence:doctor` runs correctly. The rest of
> `docs/VERIFICATION.md` gates the tag; sections 1–7 must pass first.

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
