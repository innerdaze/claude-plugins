# `ROSTER` — resolving a role to the plugin that serves it

**Contract version: 1.1.** Additive changes — a new optional field, a new optional operation — are
minor. Removing an operation or changing what one means is breaking.

*1.1 (2026-09-09): `marketplace` added to an entry, and `plugin` tightened to an installable id.*

## The question this answers

A repo's `## Artifacts` table says role `knowledge` owns `domains/`. Nothing in the repo, and
nothing in any plugin manifest, says **which plugin serves role `knowledge`**. A manifest carries
`name`, `description`, `version` and `keywords`; there is no declared role. So a tool can learn
that a plugin called `domains` is installed and not that it is the knowledge system.

That gap is not cosmetic. It is why an orchestrating `migrate` on a repo whose knowledge system
predates the plugin split can name the role, name the artifact, and then stop: the thing that
noticed cannot name the thing that would fix it, and the rule every plugin in this stack follows
— interop through repo artifacts, never by reading another plugin's install path — forbids it
guessing.

**This contract is that mapping, and nothing more.** It does not describe what any plugin does,
and a roster entry is not permission to read that plugin's files.

## Operations

### `resolve(role) → entry | none`

| Input | Required | Meaning |
|---|---|---|
| `role` | **yes** | a role id from the config bus's owner markers — `delivery`, `knowledge`, `methodology`, `intent-layer`, `shared-memory` |

Returns, when known:

| Field | Meaning |
|---|---|
| `plugin` | the id to install, **exactly as `claude plugin install` takes it** — `name@marketplace` wherever the plugin comes from a marketplace, which is every case that is not a local directory |
| `marketplace` | optional: `{name, add_url}` for the marketplace that serves this entry. Only meaningful for a **project adapter** naming a plugin from somewhere else — the shipped roster's own marketplace is, necessarily, already added |
| `commands` | that role's `migrate`, `re-scaffold` and `doctor` commands, as the plugin itself would declare them in `## Commands`. **Setup commands only, by design** — a roster carries what an orchestrator may run unattended, and a role's actual work (`/intent:capture`, `/cadence:plan`) never qualifies, because it needs to know what the user wants to do today |
| `source` | where this entry came from: `project` (a generated adapter) or `shipped` |

**A bare name is not an installable id.** It reads fine in prose and fails at the command line,
and the failure arrives at the worst moment — mid-sequence, on a machine the user is watching.
Where an adapter genuinely has no marketplace (a local directory, a plugin installed by hand),
say so in the entry rather than emitting a name that looks installable and is not.

**The shipped roster never needs `marketplace`**, and this is worth stating so nobody adds a
check for it: `hub` is served by the same marketplace as the plugins it rosters, so a machine
running `hub` has that marketplace by construction. The field exists for the tier where the
assumption fails — a project adapter naming an in-house plugin published somewhere this machine
may never have been told about.

Returns **none** for a role the roster does not know. `none` is an ordinary answer: it means *ask
the user*, never *unsupported*.

### `roles() → known role ids`

The roles this roster can resolve. Used to report coverage honestly — "these I can bootstrap
unattended; anything else I will ask about."

## The floor

`resolve` is **required**. A roster that cannot answer the one question it exists for is not a
roster — declare `none` and let the caller ask the user, which is the honest degradation and the
one every caller already handles.

`roles()` may return an empty set. An empty roster is a working roster with nothing in it.

## What a caller must never do with an entry

- **Never read the named plugin's files.** The entry is an id and a set of command names. Learning
  a sibling's *format* from its payload is the cardinal rule, and a roster does not exempt anyone
  from it.
- **Never treat `## Commands` as second to this.** A role already registered in the bus is
  resolved from the bus, always. The roster exists for the role that has *never registered
  itself* — that is its only job.
- **Never write a resolved entry into the repo.** It would be a committed claim about what is
  installed, and wrong for the next person.

## Resolution order

1. **`.agent/hub/adapters/roster/project.md`** — the project's own adapter, if it exists;
2. the shipped fallback;
3. `none`.

A project adapter **outranks** the shipped one for every role it names — which is how an in-house
plugin becomes first-class rather than tolerated. Roles it does not name fall through to the
shipped list, so an adapter is a supplement rather than a replacement: naming `knowledge` does not
lose you `delivery`.

One fixed path, not any file in that directory. Two local adapters naming the same role would
need merge rules and a precedence story, for a depth of customisation nobody has asked for.

### What one looks like

The same shape as the shipped adapter — a `## Capabilities` block and an `## Entries` table of
`Role | Plugin | Migrate | Re-scaffold | Doctor`. Copy `adapters/roster/official.md` and replace
the rows. A missing command is written as *(none)* rather than omitted, because "this plugin has
no migrate" and "nobody filled this in" are different facts.

### Who writes it

The in-house plugin's own init, as part of declaring itself — or a person, once. **Never a
consumer of this contract**, `hub` included: a caller that wrote its own resolution back into the
repo would be committing a claim it had just guessed.

That is not in tension with *never record which plugins are installed*. The two look identical in
a diff and are not:

| A committed claim about | Allowed | Why |
|---|---|---|
| which plugin **serves a role** here | yes | the project's own choice, as durable as the artifact it names |
| which plugins are **installed** | no | per-user, per-session — true when written, a lie by the next morning |

So an entry may say *role `knowledge` is served by `acme-notes`, whose doctor is
`/acme-notes:doctor`*. It may not say `acme-notes` is installed, and every caller still asks the
harness that question itself.
