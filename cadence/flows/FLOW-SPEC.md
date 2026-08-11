# Cadence Flow Spec — the schema

*A **flow** declares how you work: the levels work is broken into, the states it
moves through, what is gated, how new work enters, and how much the skill may
decide. This file is the **schema**; the files in this directory beside it are
**instances**. It is a versioned interface — adding an optional key is a minor
change, renaming one or changing its meaning is breaking.*

A flow spec is a Markdown file containing one fenced `yaml` block. Prose around
the block is for humans and is ignored.

---

## The one rule that prevents the most damage

**A lane is process vocabulary. It is never a column in your tracker.**

A flow says "this process has a state where work is in flight." It does *not*
say your tracker has a column called `In Progress`. Those are different layers:

| Layer | Declares | Lives in |
|---|---|---|
| **Flow** — process | `lanes`, `roles`, `gated_transitions` | this file's schema |
| **Config** — binding | `tracker.status_map`: lane → *your tool's real status* | `config.md` |
| **Tracker** — tool | the statuses that actually exist, via `statuses()` | the adapter |

This matters because presets are copied. If a preset's five lanes were treated
as required columns, adopting `solo-greenfield` on a two-column board would make
the skills target columns that do not exist — which is exactly the failure this
layering was introduced to stop. A lane with no `status_map` entry is **normal**:
the step that would use it is skipped, once, with a note. Nothing is invented and
no column is ever created in your tracker.

---

## `meta` — identity

| Key | Type | Required | Read by |
|---|---|---|---|
| `name` | string | **yes** | all skills (diagnostics) |
| `summary` | string | **yes** | `/cadence:init` when offering presets |
| `cadence_version` | semver string | **yes** | `/cadence:doctor`, validator — the Cadence contract version this flow targets |
| `autonomy` | `high` \| `mixed` \| `low` | no | *none — documentation.* The human-readable through-line for a flow author; deliberately not machine-read |

## `hierarchy` — the levels work is broken into

| Key | Type | Required | Read by |
|---|---|---|---|
| `levels` | list of strings, broadest first | **yes** | `/cadence:plan` (what to create), `/cadence:roadmap` |
| `first_class` | map of `<name> → above-all` | no | `/cadence:session` — a category that outranks the hierarchy, e.g. `incident: above-all` |

Levels are names, not fixed concepts: `[milestone, epic, ticket]`,
`[milestone, epic, story, task]`, and `[work, section, claim]` are all valid.
The last level is the unit a session works on.

## `states` — the lanes work moves through

| Key | Type | Required | Read by |
|---|---|---|---|
| `lanes` | list of strings | **yes** | `/cadence:plan`, `/cadence:session`, validator |
| `roles` | map, see below | **yes** (`backlog`, `done`) | `/cadence:session`, `/cadence:plan` |
| `gated_transitions` | map of `"<lane> -> <lane>"` → list of gate names | no | `/cadence:session` at the transition |
| `incident_lanes` | list of strings | no | `/cadence:session` when `hierarchy.first_class.incident` is set |
| `release_pipeline` | list of gate names | no | *deferred — no skill fires this yet* |
| `wip_limit` | `none` \| integer \| `per-person` | no | `/cadence:session start` — warns when the active lane is over the limit |

### `states.roles` — which lane plays which structural part

Skills never name a lane directly; they ask for a role. Every value is
**declared by a human** and must be a member of `lanes`. Nothing here is inferred
from a lane's name — whether picking up work means `Todo` or `In Progress` is a
process decision only you can make.

| Role | Required | Meaning | If absent |
|---|---|---|---|
| `backlog` | **yes** | where `/cadence:plan` creates new items | — |
| `done` | **yes** | the success terminal | — |
| `committed` | no | accepted into the current cycle, not yet started | committing scope changes no status |
| `active` | no | work is in flight | `/cadence:session start` does **not** change status |
| `review` | no | awaiting review | no review step is implied |
| `abandoned` | no | list of terminal-but-not-success lanes | nothing is treated as abandoned |

The **terminal set** is computed as `done` + `abandoned`. It is never declared
separately, so it cannot drift. `list_open` is "not in the terminal set."

**Roles never imply a path between lanes.** `gated_transitions` is the only
declaration of how items move. Declaring a `review` role does not mean work
passes through review — a flow that reviews says so with a transition.

**Every lane must be reachable.** A lane that no role names and no transition
mentions is an **orphan**: nothing in Cadence can ever put an item there, so it is
a promise the flow cannot keep. This is easy to introduce — `team-sprints` shipped
a `Sprint Backlog` lane in exactly that state, naming a real part of the process
that no skill could act on. Either give the lane a role, put it in a transition,
or remove it. The validator reports orphans.

## `gates` — named checkpoints

`gates.<name>` with:

| Key | Type | Required | Read by |
|---|---|---|---|
| `approver` | `ai` \| `ai-proposes` \| `human` | **yes** | `/cadence:session`, `/cadence:plan` |
| `checks` | list of strings | no | the `gate.<name>.check` hook |

`ai` may decide autonomously · `ai-proposes` produces a recommendation a human
accepts · `human` stops and requires explicit sign-off. A skill must honour the
level; a `human` gate is never auto-cleared.

**The Definition of Done is the union of two lists**: `flow.gates.dod.checks` ∪
`config.dod_gates`. Union, not override — a project may raise the bar above what
the flow requires, and can never silently lower it.

**Gates survive an unrepresentable lane.** A gate belongs to a *transition*, and
skills collect every gate along the declared path between two lanes. If a lane on
that path has no `status_map` entry, the status write for it is skipped — the
gate is not. Without this, a team whose board has fewer columns would silently
get fewer checks, which is the opposite of what a Definition of Done is for.

## `cadence` — rhythm

| Key | Type | Required | Read by |
|---|---|---|---|
| `model` | `continuous` \| `sprint` \| `kanban` | **yes** | `/cadence:plan` |
| `cycle_length` | string, e.g. `"2 weeks"` | no | `/cadence:plan` when `model: sprint` |
| `ceremonies` | list of ceremony names | no | *deferred — see `CEREMONIES.md`; no skill fires `ceremony.*` yet* |

## `intake` — how work enters and what gets picked

| Key | Type | Required | Read by |
|---|---|---|---|
| `new_work` | string | **yes** | `/cadence:session start` |
| `bug_triage` | `defer` \| `file` \| `preempt` | **yes** | the `bug.triage` hook, mid-session |
| `priority_policy` | ordered list of tokens | **yes** | `session.select_goal` |

### Priority-policy tokens

Evaluated in order; the first that yields a candidate wins. Each token needs a
particular item field to exist — **if the tracker cannot supply it, the token is
skipped with a note rather than guessed at**:

| Token | Needs | Meaning |
|---|---|---|
| `blocker-for-current-ticket` | `depends_on` | anything blocking the item in flight |
| `current-epic` | `epic` | the next open item in the same epic |
| `next-roadmap-ticket` | `milestone` | the next open item in the current milestone |
| `committed-sprint` | `cycle` | the top item of the committed cycle |
| `backlog-by-rank` | `order` | highest-ranked open item |
| `active-incident` | `incident_lanes` | an item in an incident lane |
| `customer-bug-by-severity` | `severity` | most severe open customer bug |
| `oldest-open` | — | the least recently created open item |

**`oldest-open` is the only token that can always be evaluated**, because every
tracker knows creation order. Every other token needs either a field the board may
not have (`order`, `milestone`, `cycle`) or an item already in flight to anchor
against (`blocker-for-current-ticket`, `current-epic`). A policy built only from
those can select nothing at all on a fresh board — which is not a hypothetical:
two shipped presets did exactly that on a real Linear team with five open items
sitting in it.

Ending a policy with `oldest-open` guarantees it never exhausts. That is a
**trade-off the flow author makes, not a fallback the skill applies**: it means
"when nothing better applies, just take the oldest thing" — reasonable for solo
and kanban work, wrong for a sprint team, where "nothing is committed" is the
correct answer and picking anyway breaks the process. The shipped presets
deliberately omit it; add it if your process wants it.

An unlisted token is legal — it is interpreted as prose — but the validator
warns, because a token nothing understands silently does nothing.

## `decision_rights` — the autonomy dial

`decision_rights.<step>` → `ai` | `ai-proposes` | `human`, for the steps
`select_goal`, `plan_breakdown`, `commit_scope`, `release`. Meanings are the
same as a gate's `approver`.

## `session` — what one session is

| Key | Type | Required | Read by |
|---|---|---|---|
| `goal` | string | **yes** | `/cadence:session start`, framing the goal |

There is deliberately no `start:`/`end:` key. The sequence of a session belongs
to the skill and the hooks — a narrative line here would be a fourth place to
state it, would collide with the `session.start` / `session.end` **hook** names,
and cannot be honoured mechanically.

## `hooks` — level-3 overrides

`hooks.<hook.name>` → path to an instruction doc, relative to the flow file.
Every key must name a hook in `HOOKS.md` (literal, or matching a documented
wildcard such as `gate.<name>.check`). Unset hooks use the built-in default.

---

## Minimum viable flow

Everything else is refinement:

```yaml
meta:
  name: minimal
  summary: The smallest flow that runs.
  cadence_version: "0.1"
hierarchy:
  levels: [milestone, ticket]
states:
  lanes: [Backlog, Done]
  roles:
    backlog: Backlog
    done: Done
gates: {}
cadence:
  model: continuous
intake:
  new_work: next-roadmap-ticket
  bug_triage: file
  priority_policy: [next-roadmap-ticket]
decision_rights:
  select_goal: ai
  plan_breakdown: ai
  commit_scope: ai
  release: human
session:
  goal: one ticket from the current milestone
hooks: {}
```

Note what this two-lane flow does *not* declare: no `active` role, so sessions
never move an item mid-flight; no gated transitions, so nothing blocks reaching
`Done`. Both are legitimate, and the skills adapt rather than complain.

## Authoring

1. Copy the nearest preset, or start from the minimum above.
2. Change values (level 1) or restructure states and gates (level 2).
3. For behaviour the vocabulary can't express, point a `hooks:` entry at your own
   instruction doc (level 3) — see `HOOKS.md` for each hook's contract.
4. Save to `.claude/cadence/<name>.flow.md` and set `flow:` in your config.
5. `/cadence:doctor` validates it against this schema and reports what it finds.
