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

## 1. Config

- Read `.claude/cadence/config.md`. Missing → **broken**: run `/cadence:init`.
- If there is no config there but one exists at another path (a `PROJECT.md` in a
  docs folder, say), report the **pre-0.2 layout** and its remedy: move it to
  `.claude/cadence/config.md`, or re-run init.
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
- Compare `meta.cadence_version` against the installed plugin's version. A
  mismatch is **drifted**: list what changed and suggest re-running init.

## 3. Adapters

For each of `tracker`, `vcs`, `doc_system`:

- Resolve `kind` → project-local `.claude/cadence/adapters/<family>/<kind>.md`,
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

- Item statuses that aren't in the flow's lanes (or aren't in `statuses()`).
- Items parked in a lane with no declared exit transition — stranded work.
- For a `markdown` tracker: front-matter that doesn't parse, and **unquoted
  titles containing a colon**, which is the specific way an item file silently
  becomes unreadable.
- `epic` or `milestone` references pointing at items that don't exist.

## 6. Session state

- Does `config.session_state.file` exist, and does it match the schema in
  `${CLAUDE_PLUGIN_ROOT}/adapters/ADAPTERS.md`?
- Is it **actually ignored**? Check the VCS ignore file, not just the config. If
  it isn't, that's **broken**: one `git add -A` commits a local scratchpad onto a
  shared branch. The remedy is the VCS adapter's `ignore()`, via `/cadence:init`.
- Is it over budget (~40 lines)? Over-length means `session_state.prune` is
  under-pruning and the file is becoming a stale second copy of the backlog.

## 7. Housekeeping

- Files under `.claude/cadence/` that `ADAPTERS.md` says should be committed but
  are untracked — the config, adapters, a custom flow, the backlog. Being
  untracked risks them being swept into an unrelated commit.
- **Does `execution.owns` match what the repo shows?** If it claims `commit` but
  recent items have no checkpoint referencing them, report it as **drifted**: the
  execution skill is failing, or `owns` overstates what it actually does. Either
  way sessions are silently doing — or skipping — work the config says belongs
  elsewhere. Name which items lack a referencing commit.
- A `session`, `plan`, or `roadmap` skill at user or project scope. Cadence's are
  namespaced `cadence-*` so they can't be shadowed, but two live session rituals
  is worth naming rather than discovering mid-flow.
- Does `config.doc_system.roadmap` point at a file that exists?

## Reporting

Group by band, most consequential first, and for each finding give: what,
where (file and key), why it matters in one clause, and the remedy. Prefer
concrete consequences over severity labels — "sessions won't mark work in
flight" tells the user more than "warning."

End with the one-line summary: how many broken, disabled, drifted. If a finding
needs the user to decide something (an unconfirmable tracker workspace, an
unmapped lane they may have wanted), say so explicitly rather than implying a
default.
