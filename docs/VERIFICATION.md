# Manual verification checklist

Everything in `tools/validate_cadence.py` runs without installing anything. This
checklist covers what it structurally cannot: **whether the plugin works when
actually installed.**

That distinction matters because the plugin's most load-bearing assumptions have
never been tested. Skills reference bundled files through `${CLAUDE_PLUGIN_ROOT}`;
commands are supposed to register as `/cadence:*`; the `mechanical` subagent is
supposed to be spawnable by name with a per-invocation model override. All of
that is asserted, not proven — and the characteristic failure is silent, so a
run that *looks* fine is not evidence.

Work through this in order. Record actual behaviour, not expected behaviour, and
treat anything unexpected as a finding rather than a hiccup.

---

## 0. Before you start

```
python tools/validate_cadence.py     # must exit 0
git status --short                   # must be clean
```

Have a **scratch project** ready — a throwaway git repo with a little real code,
not an empty directory, so detection has something to work with. Do not run this
against a project you care about: init writes files and makes a commit.

---

## 1. Install — from the local path

The repository has no remote yet, so install from disk. This is the *whole*
point of a local-path marketplace: you can verify a plugin before publishing it,
which is the right order.

```
/plugin marketplace add C:\Users\Lee\Projects\claude-plugins
/plugin install cadence@innerdaze
```

A local marketplace reads the working tree, so whatever branch is checked out is
what you are testing. Confirm you are on the branch you mean to verify.

- [ ] The marketplace resolves and the plugin installs.
- [ ] `/plugin` lists Cadence with its version (`0.2.0`) and description.

**If the marketplace name is rejected**, check `.claude-plugin/marketplace.json`.
Claude Code refuses a marketplace `name` containing "claude" or "anthropic" —
it reads as impersonating an official source. The name is `innerdaze` and
deliberately differs from the repository name; the install command must match the
manifest, not the repo.

> The published form — `/plugin marketplace add innerdaze/claude-plugins` — only
> works once the repo exists on GitHub. It resolves that shorthand over SSH, so
> it also needs working GitHub SSH keys (or an explicit HTTPS URL). Verifying
> that path belongs in **section 10**, after publishing; do not treat its failure
> now as a plugin defect.

### Re-testing after a change

The cache is keyed by version, so a fix only reaches you if the version changed:

```
git push                                  # with a bumped version in both manifests
/plugin marketplace update innerdaze      # refreshes the clone
/plugin                                   # should now offer an upgrade
```

If it says *"already at the latest version"* after you pushed a fix, the version
wasn't bumped — the clone updated but the installed payload didn't. Confirm by
comparing the two:

```
ls ~/.claude/plugins/marketplaces/innerdaze/cadence/skills   # the fetched clone
ls ~/.claude/plugins/cache/innerdaze/cadence/*/skills        # what is installed
```

They must match. If they don't, that is the version-bump trap, not a plugin bug.

## 2. Command and skill registration

- [ ] Typing `/cadence:` offers **exactly five** entries: `init`, `session`, `plan`, `roadmap`, `doctor` — and no `cadence:cadence-*` duplicates. Ten entries means a stale cache (see above) or a `commands/` directory has come back.
- [ ] Each shows its `description`, and `session` shows the `start | end` argument hint.
- [ ] **Nothing shadows an existing skill.** If you have your own `/session`, confirm it still resolves to yours and Cadence's is separately `/cadence:session`. This is what the `cadence-` prefix exists for.
- [ ] Ask, in plain language, *"what should I work on next?"* in the scratch project. Does `cadence-session` engage on its own? Skill descriptions are the only dispatch surface, and they have never been measured.

## 3. `${CLAUDE_PLUGIN_ROOT}` actually resolves

**The single most important check here.** If the variable doesn't expand inside a
skill body, adapter resolution, hook resolution, and template scaffolding all
quietly fall back to guessing.

- [ ] Run `/cadence:init` in the scratch project and watch the tool calls: does it **read real files** out of the installed plugin directory (`flows/`, `adapters/`, `templates/`)?
- [ ] Confirm it is not searching the *scratch project* for `flows/HOOKS.md` or similar. Searching-then-improvising is the failure; it will not announce itself.

## 4. `/cadence:init` on the zero-dependency path

Answer the interview choosing the `markdown` tracker (or let it detect no tracker).

- [ ] Config written to `.claude/cadence/config.md` — and nowhere else.
- [ ] **The config contains only keys you were asked about.** In particular there is no `vcs_ignored`, and no value belonging to another project. This is the regression that motivated most of this work.
- [ ] `status_map` contains only lanes you actually mapped.
- [ ] `.claude/cadence/SESSION.local.md` exists and is listed in `.gitignore`.
- [ ] The roadmap is scaffolded at `config.doc_system.roadmap` (default `docs/ROADMAP.md`) — **not** buried in `.claude/cadence/`.
- [ ] `feature-process.md` and `session-goals.md` were **not** copied into the project.
- [ ] Init committed its own output; `git status` is clean apart from the ignored session file.
- [ ] No file anywhere in the installed plugin directory was modified.

## 5. The reduced-lane case

This reproduces the failure that drove the lane-role redesign: a tracker with
fewer columns than the preset's lane list.

- [ ] Edit `status_map` down to just `backlog` and `done` (delete the `In Progress` mapping).
- [ ] Run `/cadence:plan`, then `/cadence:session start`.
- [ ] The session **says once** that it isn't marking work in flight, and continues.
- [ ] **No `set_status` call targets a column that doesn't exist.** No error, no invented status, no silent no-op.
- [ ] `/cadence:session end` still completes the item.

## 6. The full loop

Restore the `active` mapping first.

- [ ] `/cadence:roadmap` — drafts or updates the roadmap; leaves placeholders rather than inventing a vision.
- [ ] `/cadence:plan` — creates items under `.claude/cadence/backlog/`, IDs use your prefix, front-matter has `order`/`depends_on`, titles containing `:` are quoted.
- [ ] `/cadence:session start` — picks one goal per the priority policy, moves the item to the active lane, records a comment.
- [ ] Do a small piece of real work.
- [ ] `/cadence:session end` — and check this sequence precisely:
  - [ ] gates run first;
  - [ ] the item's status changes to done **before** the commit;
  - [ ] a commit exists whose subject references the item id;
  - [ ] **the working tree is clean afterwards** — this is the assertion that failed before the reorder;
  - [ ] `git show HEAD:.claude/cadence/backlog/<id>.md` shows the item as **done**, agreeing with the working copy.
- [ ] Run `/cadence:session end` a second time: it should decline gracefully, not wedge.

## 7. `/cadence:doctor`

- [ ] On the healthy project: reports clean in roughly one line.
- [ ] Break something deliberately — add a bogus key to the config, point `flow:` at a missing file, or delete a `status_map` entry.
- [ ] Doctor reports each with a remedy, in the right band (broken / disabled / drifted).
- [ ] **Doctor wrote nothing.** `git status` unchanged.

## 8. Against a real tracker

Only if you have a tracker MCP connected — and this is the contamination test, so
run it deliberately.

- [ ] `/cadence:init` in a *second* scratch project while a tracker MCP for an unrelated workspace is connected.
- [ ] **Init asks whether the workspace belongs to this repo**, rather than binding it silently.
- [ ] Decline, and confirm it falls back to `markdown` rather than binding anyway.
- [ ] Accept in a project where it *is* correct, and confirm `status_map` is built from the tool's **real** statuses — check them against the board.

## 9. Model tiers

- [ ] Trigger a batchy operation (`/cadence:plan` with a large breakdown).
- [ ] Does it spawn the `mechanical` subagent at all? Plugin-provided agents being spawnable by name is unverified.
- [ ] Set `config.models.mechanical` to a tier you don't have. Does Cadence **say so and run inline**, rather than failing opaquely or silently substituting?

If the per-invocation model override turns out not to exist, `config.models` is
inert and the cheap-tier story in `ADAPTERS.md` needs rewriting — record that
rather than working around it.

---

## 10. After publishing — the remote install path

Only once the repository exists on GitHub. Everything above is verifiable from a
local path; this section verifies distribution, which is a separate thing.

```
/plugin marketplace remove claude-plugins      # drop the local one first
/plugin marketplace add innerdaze/claude-plugins
/plugin install cadence@innerdaze
```

- [ ] The shorthand resolves. It clones over **SSH** — if you get
      `Permission denied (publickey)`, that is your GitHub SSH config, not the
      plugin. Either add a key or use the explicit HTTPS URL
      `https://github.com/innerdaze/claude-plugins.git`.
- [ ] `source: "./cadence"` resolves correctly from a cloned marketplace, not
      just from a local directory.
- [ ] The manifests validate as fetched (no field the local path tolerated but
      the remote rejects).
- [ ] The `homepage` and `repository` URLs in `plugin.json` actually load.

## Recording results

For each failure note: the step, what you expected from the docs, what actually
happened. That gap is the defect — the docs are the specification here, so a
mismatch means one of the two is wrong and it is not always the code.

File findings at <https://github.com/innerdaze/claude-plugins/issues>.

**Do not tag a release until sections 1–7 pass.** Sections 8 and 9 depend on
optional infrastructure (a tracker MCP, a second model tier); if you skip them,
say so in the release notes rather than implying they passed. Section 10 can
only run after publishing, so it gates the *announcement*, not the tag.
