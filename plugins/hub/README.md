# `hub`

The stack's front door. Three commands:

| Command | Does |
|---|---|
| `/hub:status` | what is installed, what is pending, what is unregistered — read-only |
| `/hub:upgrade` | the guided sequence: detect, ask, update plugins, then run each owner's init and migrate in order |
| `/hub:doctor` | every installed plugin's doctor, collated into one report |

## What it is for

On a repo set up against an older release, the tool that notices a role is unregistered is
forbidden from naming the plugin that would fix it — plugins in this stack interop through repo
artifacts and never by reading each other's install paths. That rule is right, and it leaves the
last mile of an upgrade with no owner. `hub` is that owner.

## What it is not

- **Not required.** It declares no dependencies and nothing depends on it. Every plugin in this
  stack works alone and together without it; `hub` makes the sequence pleasant, not possible.
- **Not a migration engine.** It invokes each owner's own commands. The component that stamps a
  version is the component that wrote the files.
- **Not a closed set.** The shipped roster names the plugins released alongside it, and a project
  can generate its own roster adapter that outranks it — so an in-house plugin serving a role is
  bootstrapped exactly like an official one. A role the roster does not know is **asked about**,
  never reported as unsupported.

## Published contract

[`contracts/ROSTER.md`](contracts/ROSTER.md) — resolving a role id to the plugin that serves it,
with `adapters/roster/official.md` as the shipped fallback and `none.md` for a stack of unknown
plugins.
