# Methodology scaffolding version

**Methodology scaffolding version: 4**
**Minimum supported version: 1**

The canonical version of cadence's own project-local scaffolding — where its config lives, what
is in it, where its root sits, and how its generated adapters are named. `/cadence:init` stamps this into the bus's `## Versions` as
the **`cadence methodology`** row; `/cadence:migrate` reads it back and applies what is pending.

**Cadence's number, and nobody else's.** No other tool may raise it and it raises no other tool's
— that independence is why the stamp is per component rather than one shared integer.

(History: v1 = the config split and the root move at 0.5.0. v2 = session state to
`.agent/local/`, keyed by worktree. v3 = the `project:` block dropped, since its two values are
the bus's. v4 = the doc-system adapter file named by the bus's `Doc system` kind, never a name
cadence invented. Everything before v1 is pre-versioning: a project with no `cadence methodology` row is
treated as **v0** and gets v1 applied.)
