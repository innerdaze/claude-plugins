---
name: doctor
description: Check a project's Cadence setup and report what is broken, drifted, or disabled — config keys, flow validity, adapter coverage, tracker reachability, whether the flow's lanes still match the tracker's real columns, and whether session state is being ignored. Read-only; it never fixes anything. Use when the user runs /cadence:doctor, says Cadence is behaving oddly, asks why a session or plan step was skipped, asks whether their setup is correct, or after upgrading the plugin.
---

# /cadence:doctor — check this project's Cadence setup

**Read-only. This skill never writes, never fixes, and never rebinds anything.**
Every finding names its remedy — almost always `/cadence:init`, which is the only
skill that writes configuration. Keeping exactly one writer is what makes this
one safe to run anywhere, including on a project you don't own.

Report findings in three bands and say plainly which is which:

- **Broken** — something will fail or already has.
- **Disabled** — a legitimate configuration that turns a feature off. Not an
  error. Users most often run this skill because a step didn't happen, and the
  honest answer is usually here.
- **Drifted** — the setup was right once and the world moved.

If everything passes, say so in one line. Don't pad a clean report.

## 0. The shared config-bus checks

Read `${CLAUDE_PLUGIN_ROOT}/checks/BUS-CHECKS.md` and run **every** check in it first. Those are
the checks all four tools in this stack run **identically** — vendored rather than shared,
because no plugin may read another's files, and this is the only legal way to make four tools
agree about one file.

Everything below is cadence's **own** additional checking: its flow, its gates, its adapters, its
session state. Check 5 of the shared spec covers reporting the whole `## Versions` table, so do
not re-derive that here.

## 1. Config

- Read **both halves** of the configuration, because 0.5.0 split it:
  - the **config bus** at `.agent/PROJECT.md` for the bindings — tracker, VCS, doc-system,
    execution. Missing bus → **broken**: run `/cadence:init`.
  - `.agent/cadence/config.md` for the methodology — flow, gates, session state, models.
    Missing → **broken**: run `/cadence:init`.
- **A binding still sitting in cadence's own config is drift**, not a working setup: it means the
  split migration has not run, so two files can disagree about the same value. Report it and name
  `/cadence:migrate`.
- **A `cadence methodology` row missing from the bus's `## Versions`** means this project predates
  the split entirely. Report **v0** and name `/cadence:migrate`.
- **Compare `cadence_version` against the declared contract** in `${CLAUDE_PLUGIN_ROOT}/flows/CONTRACT-VERSION.md` — *not* against the plugin version, which moves for releases no flow author can observe. A config written
  against a *newer* contract than the plugin is **broken**, not drifted: it may
  use shapes the installed skills cannot read — a qualified `status_map` entry
  against a plugin that only understands plain names, say — and the older skill
  has no way to recognise why. Say which side is behind. A config with no
  `cadence_version` at all predates 0.3; report it and suggest re-running init.
- If there is no config there but one exists at another path (a `PROJECT.md` in a
  docs folder, say), report the **pre-0.2 layout** and its remedy: move it to
  `.agent/cadence/config.md`, or re-run init.
- Parse the YAML block. Report unparseable content with the line.
- **Report unknown keys.** Compare against `${CLAUDE_PLUGIN_ROOT}/config.example.md`
  and name anything that isn't in the documented shape. This is the check that
  catches a key copied in from somewhere else — the failure mode init is now
  built to prevent, but old configs still carry.
- Report required keys that are missing for the declared `kind`s: `tracker.path`
  for `markdown`, `doc_system.notes` for `none`, `mcp_namespace` for a hosted
  tracker.

## 2. Flow

- Resolve `config.flow` — a shipped preset or a project-local path. Unresolvable
  → **broken**; do not guess a substitute, because the flow *is* the process.
- Validate against `${CLAUDE_PLUGIN_ROOT}/flows/FLOW-SPEC.md`: known keys,
  `states.roles` values that are real lanes, `backlog` and `done` present, both
  sides of every gated transition declared, referenced gates defined, valid
  approver levels, `hooks:` entries naming real hooks whose docs exist.
- **Lane reachability**: a lane on the right of a gated transition that nothing
  declared reaches means that gate never fires. Report it with the gate's name,
  because a gate that silently never runs looks exactly like a gate that passes.
- Compare `meta.cadence_version` against the declared contract version, and say
  which kind of mismatch it is. **A major behind is drifted**: something the flow
  relies on was renamed or changed meaning — list what changed and suggest
  re-running init. **A minor behind is informational**: the contract only gained
  optional vocabulary, so the flow is still valid and still means what it says.
  Name what was added and leave it at that. Reporting an additive gap as drift is
  the same noise the contract/plugin split was introduced to stop, arriving one
  size smaller.

## 2b. Sprint flows and cycles

Where the flow is sprint-shaped — a `committed` role, or a cycle token in the priority policy —
check the tracker adapter supports `current_cycle()` and the `cycle` field.

Supported → pass. Selection scopes to the active sprint, which is where the team's committed work
is: **the team commits the cycle in the tracker, and cadence reads it.** Nothing here needs to
populate that lane.

Unsupported → **disabled**, and say what it costs: selection cannot tell which items are in the
current sprint, so it falls back to the committed lane by status and then to ranked backlog order.
Work still gets picked; it is just not scoped to the cycle. Name the missing operation, since that
is what a generated adapter can be taught.

Also worth reporting if **no item carries a cycle at all** on a sprint flow: either no sprint has
been started yet, or the field is not being populated. Say which you found rather than treating
an empty result as normal.

## 2bb. Every column accounted for

Take `statuses()` and check each one appears somewhere: mapped in `status_map`, listed in
`tracker.hands_off`, or in the abandoned list. **A column in none of them is drifted** — name it
and ask which it is.

An unaccounted column is not cosmetic: nothing knows whether work sitting there is waiting on
cadence, on a person, or on nothing at all. That is the difference between "handed to review, not
my problem" and "stalled for three weeks", and the tool cannot tell them apart by looking.

Report a `hands_off` entry naming a status the tracker no longer has, too — a board that dropped a
column leaves a note describing something that cannot happen.

## 2bc. Can anything reach `done`?

Walk the flow's `gated_transitions` from the `active` lane and ask whether a path to
`roles.done` exists **through lanes this tracker maps**. A hands-off column in the middle of that
path breaks it: cadence takes work as far as the hand-off, ends involvement there by design, and
never marks anything done.

**Report it, and do not call it an error.** It is usually correct — a board whose last two
columns are human steps is a real process — but the consequence is worth saying out loud once:
*"cadence will move work to `In Review` and stop; `Done` is yours to set."* A team that assumed
otherwise will read an unmoved board as the tool being broken.

Where the break is a *lane* rather than a hand-off — the flow's path from review goes straight to
`done` and the board has an extra column between them — say what the fix costs: a project-local
flow that declares the extra lane. Presets are read-only, and forking one to add a lane is a
supported thing to do rather than an escape hatch.

## 2bd. Checks that can never apply

Take the effective DoD — `flow.gates.dod.checks` ∪ `config.dod_gates`, and the `checks` of every
other gate — and look at each entry that declares `applies_when`:

- **`changed_paths` matching nothing in the repo is drifted.** A check scoped to `docs/**` in a
  project with no `docs/` cannot fire, and a Definition of Done nobody can fail reads exactly like
  one nobody has broken. Name the check and the globs, and ask whether the path moved or the check
  is obsolete. Match against the tracked tree, not the working tree — an ignored build directory
  is not evidence either way.
- **Report the judged ones, once, as a list.** A prose `applies_when`, and anything set to
  `applies: infer`, are decided per change and legitimate — but nothing here can tell a narrow
  condition from an empty one, so the honest report is *"these <n> checks are judged per change:
  …"* rather than silence or a false pass.
- **Report a gate whose checks are *all* judged or conditional** — no `always` among them. It can
  in principle apply to nothing, which is worth seeing once even where every individual check is
  right. Not a defect: a fact about how much of the bar is decided at the moment it is being met.

The two together answer the question this section exists for: *which of the checks this
project declares could actually stop a session?*

## 2c. Can ownership be determined?

Where the flow is team-shaped — a `review` role, `wip_limit: per-person`, `commit_scope: human`,
or simply items carrying more than one assignee — check that the tracker adapter supports **both**
`me()` and the `assignee` field.

Missing either → **disabled**, and say what it costs: goal selection cannot tell whose work is
whose, so it can propose an item somebody else is mid-way through. Name the adapter operation that
is missing rather than the symptom, because that is what a generated adapter can be taught.

Both supported → pass, and worth a line: ownership filtering is active.

**Not a finding on a single-author project.** The `markdown` tracker declares both unsupported by
design, and a repo-backed backlog with one author has nothing to disambiguate.

## 3. Adapters

For each of `tracker`, `vcs`, `doc_system` — and `intent`, whenever the bus's `Intent` binding is present and not `none`:

- Resolve `kind` → project-local `.agent/cadence/adapters/<family>/<kind>.md`,
  else the shipped fallback. Neither → **broken**.
- Check the adapter covers every operation in
  `${CLAUDE_PLUGIN_ROOT}/adapters/ADAPTERS.md` for its family, or declares it
  unsupported in a `## Capabilities` block. A missing block is **drifted** —
  likely generated against an older contract, and the remedy is to re-run init
  to regenerate it.
- List each unsupported capability and **what it disables**, concretely: "no
  `cycle`, so the `committed-sprint` priority token is skipped." Silent
  degradation is the thing this skill exists to make visible.

## 4. The tracker, live

This is where the checks that static analysis cannot do earn their place.

- **Reachable?** Is the MCP connected, does the namespace resolve, does a
  `list_open` return? Unreachable → **broken**. Say so; never fall back to the
  `markdown` tracker, because a second empty backlog looks like a working system
  while forking the project's state.
- **Does this workspace belong to this repo?** Compare the tracker's
  team/project names, the configured `ticket_prefix`, and recent items against
  this repository. MCPs are user-scoped while Cadence is installed once for every
  project, so a tracker bound from another product is a real and quiet failure —
  work gets filed into someone else's board. If you cannot corroborate it, say
  so and ask. **Report only. Never rebind.**
- **Do the mapped statuses still exist, and resolve uniquely?** Call `statuses()`
  and check every value in `config.tracker.status_map`. Two failures to look for:
  a value matching **nothing** (a column renamed or deleted in the tool — the
  single most likely way a working setup silently rots), and a bare name matching
  **more than one** status, which `set_status` must refuse. Report the second as
  **broken** and name the qualified form that would fix it. Neither is visible to
  any static check.
- **Which lanes are unmapped?** For each flow lane with no `status_map` entry,
  report it as **disabled**, naming the consequence: "no column mapped for the
  `active` lane, so `/cadence:session start` won't mark work in flight." On a
  two-column board this is correct and expected — say that too, so nobody
  "fixes" it by adding columns they don't want.
- **Does a gated transition pass through an unmapped lane?** Report it as
  **drifted**, and say plainly that the gate *still runs*: skills collect gates
  along the whole declared path, so an unrepresentable lane costs you the status
  write, not the check. Name it precisely — *"`gate.dod` is on
  `In Progress -> Done`, but `In Progress` is unmapped, so items reach `Done`
  from `Backlog`; the gate still runs."*

  Do not call this broken. Nothing fails, and a diagnostic that cries wolf on a
  correctly-configured two-column board teaches people to ignore it.

  Give both remedies and let the user choose: **map the lane** if their tracker
  has a column for it, or **redraw the flow's `gated_transitions`** to describe
  the board they actually have. The second is usually right for a small board —
  the flow should describe your process, not aspire to someone else's.

  The genuinely broken case is narrower: a gate on a transition that is **not on
  any path** the item can travel — an orphaned branch of the state machine. That
  gate can never fire under any mapping. Report *that* as broken.

## 5. Live data

Cheap reads that catch real corruption:

- **Items in statuses the flow maps to no lane** — `Blocked`, `Needs Design`,
  whatever this board has that the flow never named. Report the count and the
  statuses, as **disabled**: those items are excluded from goal selection, which
  is correct (Cadence does not know what the status means) but means they are
  invisible to the process. A handful is normal; a third of the board is a sign
  the flow does not describe how this team actually works. If the flow declares a
  `blocked` role and the board has a matching status, say so — that one at least
  can be parked deliberately.
- Item statuses that aren't in `statuses()` at all — a status the tracker itself
  no longer has.
- Items parked in a lane with no declared exit transition — stranded work.
- For a `markdown` tracker: front-matter that doesn't parse, and **unquoted
  titles containing a colon**, which is the specific way an item file silently
  becomes unreadable.
- `epic` or `milestone` references pointing at items that don't exist.
- **Items in a terminal lane whose body still carries an unchecked box** (`- [ ]`) and whose
  comments record no waiver for it — report as **drifted**, naming the item and the box. Either
  the item was closed outside the session path, or before the gate walked checklists. The
  remedy is a person's: tick it with evidence, waive it with a reason, or reopen. Where
  `list_closed` is unsupported, say the check could not run.

## 6. Session state

- Does `config.session_state.file` exist, and does it match the schema in
  `${CLAUDE_PLUGIN_ROOT}/adapters/ADAPTERS.md`?
- Is it **actually ignored**? Check the VCS ignore file, not just the config. If
  it isn't, that's **broken**: one `git add -A` commits a local scratchpad onto a
  shared branch. The remedy is the VCS adapter's `ignore()`, via `/cadence:init`.
- Is it over budget (~40 lines)? Over-length means `session_state.prune` is
  under-pruning and the file is becoming a stale second copy of the backlog.

## 7. Housekeeping

- Files under `.agent/cadence/` that `ADAPTERS.md` says should be committed but
  are untracked — the config, adapters, a custom flow, the backlog. Being
  untracked risks them being swept into an unrelated commit.
- **Was every done item closed through the session path?** Where `list_closed` is supported,
  read the items in the `done` lane — recent ones, or all if cheap — and look for the
  `Session end — gate.<name> …` comment session end writes. **An item in `done` with no such
  comment → drifted**, named: it reached done without the gate, either by an inline status change
  or before this marker shipped; the fix is a person's, since the work may well be fine. Where
  `list_closed` is unsupported, say the check could not run.
- **Does the bus's `## Execution` `Owns` row name `status`?** → **disabled**, and say what it
  costs: the execution skill closes items itself, so the DoD gate runs after the item is already
  done. A legitimate project statement, reported so nobody is surprised by a held gate on a closed
  item.
- **Does `execution.owns` match what the repo shows?** If it claims `commit` but
  recent items have no checkpoint referencing them, report it as **drifted**: the
  execution skill is failing, or `owns` overstates what it actually does. Either
  way sessions are silently doing — or skipping — work the config says belongs
  elsewhere. Name which items lack a referencing commit.
- A `session`, `plan`, or `roadmap` skill at user or project scope. Cadence's are
  namespaced `cadence-*` so they can't be shadowed, but two live session rituals
  is worth naming rather than discovering mid-flow.
- Does `config.doc_system.roadmap` point at a file that exists?
- **An `## Artifacts` row owned by `intent-layer` with the `Intent` binding `none` or absent** →
  **disabled**, and say what it costs: a design layer exists and neither `/cadence:plan` nor
  `/cadence:roadmap` will check a milestone against it. The remedy is the intent role's own
  re-scaffold command from `## Commands`; cadence writes no binding row it does not own. Report
  the reverse too — `Intent` bound to a kind whose artifact row or folder is missing → **drifted**,
  the check will silently skip.

## Reporting

Group by band, most consequential first, and for each finding give: what,
where (file and key), why it matters in one clause, and the remedy. Prefer
concrete consequences over severity labels — "sessions won't mark work in
flight" tells the user more than "warning."

One line per finding. If it does not change what the reader does next, leave it
out — a doctor that reports its reasoning makes the reader audit it.

End with the one-line summary (how many broken, disabled, drifted) **and then the
commands to run, in order** — at most four, copy-pasteable — or one line saying
nothing needs doing. If a finding needs the user to decide something (an
unconfirmable tracker workspace, an unmapped lane they may have wanted), say so
explicitly, and say what the decision is between rather than implying a default.
