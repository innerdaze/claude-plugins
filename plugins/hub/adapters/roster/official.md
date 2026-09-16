# `official` — the roster for the plugins that ship together

The shipped fallback for the `ROSTER` contract. It names the plugins published from this
ecosystem's own repo, and nothing else.

## Capabilities

```markdown
## Capabilities
supports:    resolve(), roles()
costly:      —
unsupported: —
```

## Why a shipped list is safe here, and would not be in general

Every plugin named below is released from the same repository as this one, in the same release.
So this list cannot drift from the plugins it names: it is the same source, packaged twice. A
roster naming plugins released elsewhere would be a second source of truth, which is what the
project-local adapter is for.

## Marketplace

Every entry below is served by `innerdaze`, the marketplace this plugin itself ships from.

**So it is always already added.** A machine running `hub` installed `hub`, and installing `hub`
required that marketplace — there is no reachable state where these entries name a marketplace
the user does not have. Nothing here needs to check for one.

## Entries

| Role | Plugin | Migrate | Re-scaffold | Doctor |
|---|---|---|---|---|
| `delivery` | `work@innerdaze` | `work migrate` | `work init` | `work doctor` |
| `knowledge` | `domains@innerdaze` | `domains migrate` | `domains init` | `domains doctor` |
| `methodology` | `cadence@innerdaze` | `/cadence:migrate` | `/cadence:init` | `/cadence:doctor` |
| `intent-layer` | `intent@innerdaze` | *(none yet)* | `/intent:init` | `/intent:doctor` |

The ids are marketplace-qualified because that is what `claude plugin install` and
`claude plugin list --json` both use. A bare name reads fine in a doc and is not a thing you can
install.

`shared-memory` is **deliberately absent.** The `memento` service is deferred, and an entry for
it would claim a plugin that does not ship.

## Behaviour

- **`resolve(role)`** — the row above, with `source: shipped`. A role not in the table returns
  **none**, which means *ask the user*.
- **`roles()`** — the four role ids above.

## What this list is not

It is **not the set of plugins that exist**, and a caller that treats it that way turns "the core
plugins" into "the only plugins". It is the set that can be bootstrapped without asking. Anything
else is a question, and asking is a working outcome.

The commands are recorded as each plugin declares them, so they can be shown to a user. **They
are still not yours to invoke on a role that has registered itself** — read `## Commands` for
that, because the repo is the authority on a project that has already answered.
