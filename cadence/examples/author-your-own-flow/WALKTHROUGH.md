# Walkthrough: authoring your own flow

*How the `manuscript` example is built, so you can author a flow for your own domain. It runs the same Cadence skills (`/session`, `/plan`, `/roadmap`) — only the flow spec and its hooks are custom.*

## 1. Why a custom flow (not a preset)

The three shipped presets (`solo-greenfield`, `team-sprints`, `live-oncall`) all assume a *software* shape — code, tests, commits, releases. Writing a researched document has a different spine: the unit of work is a **claim**, "done" means **supported by sources**, and the natural priority is **shore up the weakest argument next.** None of that fits a preset, so we author a flow.

## 2. Bend the vocabulary to the domain

Every section of `manuscript.flow.md` is a slot from the flow-spec vocabulary, filled for writing:

| Vocabulary slot | Software preset | Manuscript |
|---|---|---|
| `hierarchy.levels` | milestone/epic/ticket | work/section/**claim** |
| `states.lanes` | Backlog…Done | Outline…**Needs-Support**…**Supported**…Final |
| `intake.bug_triage` | a code bug | a **broken argument** |
| `intake.priority_policy` | next roadmap ticket | **weakest claim first** |
| `gates` | dod (tests, docs) | **citations**, editorial |

This is levels 1–2 of customization: pick the vocabulary values that describe your process.

## 3. Reach for a hook only when the vocabulary can't say it (level 3)

Two behaviours here can't be expressed as declarative values, so they're **authored hooks** in `./hooks/`, wired via the flow's `hooks:` map:

- **`session.select_goal` → `select_weakest.md`.** "Weakest claim first" needs *logic* (score claims by support strength), not a value. The hook receives the standard `session.select_goal` Input and returns the standard Output — see `flows/HOOKS.md` for the contract.
- **`gate.citations.check` → `citations.md`.** Checking that every claim is genuinely sourced is a judgment, so the gate's check is authored. It returns `pass | fail | needs-human` per the gate contract, and — being `ai-proposes` — surfaces findings for the author instead of auto-advancing.

**Rule of thumb:** if you can say it as a value, put it in the flow spec; if it needs reasoning at run time, author a hook. Never fork the plugin.

## 4. Use it

In a project's config: `flow: ./cadence/manuscript.flow.md` (copy this file + its `hooks/` there). Then `/session start` will pull your weakest claim, and `/session end` will run the citations gate. `/plan` breaks a `work` into `section`s and `claim`s using the same templates.

## 5. Checklist for your own flow

1. Name the **unit of work** and the **hierarchy** around it.
2. Define the **states** and which transitions are **gated**.
3. Write the **gates** (condition + approver) — what does "done/ready" mean here?
4. Set **cadence**, **intake/priority**, and **decision rights** (how much may the skill decide?).
5. Only then, author **hooks** for anything that needs run-time logic — each against its `HOOKS.md` contract.
6. Run `/cadence init` (or hand-write the config) pointing `flow:` at your spec, and let the coherence check catch contradictions.
