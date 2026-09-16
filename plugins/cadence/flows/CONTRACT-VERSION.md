# Contract version

**Hook & flow contract version: 0.6**

The version of cadence's **public interface for flow authors**: the hook names and their
Input → Output contracts (`HOOKS.md`), the flow-spec vocabulary (`FLOW-SPEC.md`), and the adapter
operation lists (`adapters/ADAPTERS.md`). Every flow declares the contract it targets in
`meta.cadence_version`, and that is what a flow is compared against.

**This is deliberately not the plugin version.** They answer different questions:

| Number | Answers | Moves when |
|---|---|---|
| **Contract version** (here) | which interface was this flow authored against? | a hook is renamed, an Input/Output changes, or the flow vocabulary gains or loses a term |
| **Plugin version** (`plugin.json`) | which release is installed? | anything ships — including changes no flow author can observe |
| **Methodology scaffolding version** (`migrations/`) | has this project's cadence scaffolding been migrated? | where cadence's own files live or what is in them changes |

**Why they were separated, at 0.5.0.** They used to be the same number: a flow was compared
against the plugin's minor. Then 0.5.0 moved cadence's config into the shared bus and its root to
`.agent/cadence/` — a change no flow author can observe, because not one hook name, contract or
vocabulary term moved. Under the old rule every shipped flow would have had to claim it targeted
a "0.5 contract" identical to 0.4, and every adopter's custom flow would read as **stale after a
release that did not touch its interface**. That is precisely the drift-noise the comparison
exists to prevent, arriving from the other direction.

So the rule is now: **a flow is stale when the contract moved, not when the plugin did.**

## 0.6 — 2026-09-09

Additive: a `checks` entry may declare `applies: always | infer` alongside the existing
`applies_when`. **A bare string still means `always`**, so no flow written against 0.5 changes
meaning — the new value is `infer`, which asks the skill to judge whether the check has anything
to say about the change and to name every skip with its evidence.

`/cadence:init` writes `infer` for a check a user adds. That is a change of *authoring* default,
not of vocabulary: unconditional fires a check at changes it has nothing to say about, which is
how a Definition of Done becomes a toll people want an override for. Where both a flow and a
project name one check, the stricter mode wins — `always` > `applies_when` > `infer`.

## 0.5 — 2026-09-08

Additive, so a flow targeting `0.4` is still valid and still means what it said. Two things arrived together: a `checks` entry may now be a mapping declaring `applies_when` as well as a bare string (`FLOW-SPEC.md`), and `gate.<name>.check` gained an input `change` and an output `skipped` (`HOOKS.md`). A flow author only needs to act if they want a check to stop firing on work it has nothing to say about.

## Raising it

Additive changes — a new optional hook, a new optional Output field — are a **minor** bump here.
Renames and Input/Output changes are **breaking** and bump the major. Raising this number means
telling every flow author their flow may need attention, so raise it only when that is true.

**Where the scope above and that last sentence disagree, the sentence wins.** `ADAPTERS.md` is in
the contract because the operations a flow's hooks can *rely on* are part of the interface — not
because every line of that file is. An operation added for a skill's own use, which no hook can
call and no flow can declare, changes nothing a flow author could act on, so it does not move
this number. Bumping anyway would mark every shipped and custom flow as needing attention over
something invisible to all of them: the exact drift-noise the separation at 0.5.0 was introduced
to stop.
