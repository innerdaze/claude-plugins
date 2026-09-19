# The shared config-bus checks

**One spec, vendored by every plugin.** This file is the authority; each plugin ships a
byte-identical copy at `checks/BUS-CHECKS.md` and its doctor runs it.

## Why vendored rather than shared at runtime

Because the alternative is illegal. A plugin may not read another plugin's install path
(the cardinal rule), and this repo is not present in an adopter's project — so there is no
runtime location every doctor could read. The frozen core has the same shape and the same
reason: **vendored, identical, and never changed unilaterally.**

The cost is real and worth naming: four copies can drift. That is why keeping them identical is
a mechanical check rather than a convention — the validator compares them and fails on any
difference. A spec that four tools *nearly* implement is worse than four tools with none,
because a project then gets four almost-answers and no way to tell which is right.

## Gathering the facts — one call, not forty

**Every check below needs the same handful of facts**, and reading them costs more than checking
them: a bus parsed line by line across a dozen tool calls is a dozen turns, and every later turn
re-reads all of it. Measured on a real upgrade run, inspection was a third of the cost and the
context it accumulated was re-read on each of 136 turns.

So gather first, in as few calls as possible:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/checks/bus_facts.py"      # from the repo root
```

It prints JSON: the bus path and whether it is canonical, legacy, dual or absent; the schema
marker; every section with its owner marker; `## Artifacts`, `## Versions`, `## Commands` and
`## Bindings` parsed into rows; which artifact paths resolve; which roles own an artifact and have
no version row; and a `findings` list for every mechanical rule in section 2 and 3 below. It is
read-only and decides nothing.

**What it does not do is the part you keep.** It cannot know any owner's canonical version, so it
never says a component is behind; it cannot read intent, so it never says a finding matters. Those
judgements are yours and they are why a model is running this at all.

⚠️ **A finding is not a licence to fix it.** Every finding carries an `owner` and a `remedy`, and
where the owner is not you the remedy is *report it and name whose it is* — the rules in sections
3, 3b and 4 below apply exactly as they do when you read the file yourself. A machine-readable
problem with no machine-readable constraint is the trap here: handed *"role `knowledge` owns
`domains/` and has no version row"*, the nearest fix is to write the row, and writing another
role's row is the one thing this whole registry exists to prevent.

**If `python3` is not available:** say so once, **offer to install it**, and *carry on without
it* — read the bus yourself and run the checks by hand. It is a faster path to the same answer,
never a requirement, and a doctor that refused to run because a script was missing would be the
hard-fail this ecosystem forbids anywhere else. Where the script errors rather than being absent,
report that too: it is a defect in a vendored file and its copies are hash-checked, so a failure
is worth someone's attention.

**Batch whatever it does not cover.** Where you still need shell — `git status`, the plugin
inventory — put the independent commands in one call rather than one each. Forty round-trips to
learn forty facts is the expensive shape, whatever the facts are.

## What every doctor checks

Each check below has a **band**: **broken** (something cannot work), **disabled** (works, but a
capability is off or absent), **drifted** (works, wrong shape). These are bands, not a severity
scale — a disabled feature is not "less bad" than a broken one, it is a different kind of fact.

### 1. The bus exists, in one place

- `.agent/PROJECT.md` present → pass.
- Absent, but `domains/PROJECT.md` present → **drifted**: the legacy path. Name the migrate
  command from `## Commands`, and say the shim is temporary.
- Neither → **broken**: nothing is configured. Name the re-scaffold command for your own role
  only.
- **Both present → broken.** Two buses is not a working setup and not a state to resolve by
  guessing which is real. Report both paths and **do not merge them** — but name the migrate
  command from the `delivery` row as the next action: the migration that moves the bus stops on
  this state deliberately and offers the choices, which is more than a doctor may do. A finding
  that leaves a broken bus with no next action is the complaint this band exists to avoid.

### 2. The frozen core is intact

- The **schema marker** `<!-- manifest schema: N -->` is present and parses. Absent →
  **drifted**. A value higher than you understand → **disabled**: say you cannot read this bus
  fully, and do not guess at its contents.
- Every section heading carries an **owner marker** `<!-- owner: <role-id> -->`. A section
  without one → **drifted**: it is unowned and nothing will maintain it.
- **Five settings sections belong to no role** and are marked exactly `shared`: `## Project`,
  `## Environment`, `## Version control`, `## Tracker` and `## Verification`. Any tool may create
  the bus, so every tool needs their exact headings. A bus whose settings sit in a loose
  `| Key | Value |` table with no heading above it is **pre-v10** → **drifted**, and the fix is
  the `delivery` row's migrate command from `## Commands`.
- **`## Bindings` belongs to no role either, and is `shared, additive`** — a row per seam, and
  seams accumulate as plugins arrive, so a second writer appends rather than overwrites. It has
  no `Owner` column, which is what separates it from the three registries below: nobody owns a
  binding, they are facts about the project.

  *Corrected 2026-09-10: this file previously listed `Bindings` among six sections "marked
  `shared`", while the skeleton below writes `shared, additive` for it — so a doctor following
  the prose would have reported a conformant bus as drifted, and one following the skeleton
  would have written a bus the prose called wrong. Six sections are unowned; they are not all
  the same permission.*
- **Three tables belong to every role at once** and are marked `shared, additive`:
  `## Artifacts`, `## Versions` and `## Commands`. Their marker is exactly
  `<!-- owner: shared, additive -->`. They are not in the six above because they are not settings
  — each *row* carries its own `Owner`, so the table is shared while every row has a single
  owner. Marking one of them with a role id is **drifted**: it claims a table other roles must
  write into.
- **`shared` and `shared, additive` differ in what a second writer may do.** In a `shared`
  section you write a *value* that is absent and never overwrite one another tool wrote. In a
  `shared, additive` table you append *rows*, and you edit only rows whose `Owner` is your own
  role. A disagreement between two values, or two rows claiming one owner, is a **finding**, not
  something to resolve by picking one.
- **A `shared` row that is present with an empty value** → **drifted**. Absent is a state every
  reader handles; blank looks answered and is not. The remedy is a person's — the shared rows
  are the project's to edit — **or** the `delivery` or `methodology` role's re-scaffold command
  from `## Commands`, both of which ask for a blank they find and write nothing else. Never name
  a migrate for it: no migration fills in a value a person has to supply.
- **`## Configuration` is a parking section, not a home.** A delivery migration creates it for
  legacy keys it did not recognise, so nothing is lost and a reviewer can move each one. A row
  there whose **value** also appears in one of the five `shared` settings sections or in
  `## Bindings` → **drifted**: the bus states one fact twice. Remedy: the `delivery` role's
  migrate command **while that role's stamp is behind its canonical**; once it is current, the
  fix is a hand edit — say so, and name no command. A row whose value appears nowhere else is
  reported as *parked*, with the section it most plausibly belongs to, and is a hand edit
  regardless: no migration can know which section owns a key the template never had.
- An owner marker naming something that is **not a known role id** → **drifted**, and report the
  value verbatim. Do not normalise it, and do not assume it means a plugin: role ids exist
  precisely so a rename cannot break resolution.
- `## Artifacts` and `## Versions` match their frozen shapes — `Artifact | Path | Owner` and
  `Component | Version | Owner`. A different column set → **broken** for those tables: they are
  frozen, so a mismatch means something wrote a shape that can never be correct.

### 2b. Creating the bus, when nothing has

Any plugin may be the first to run in a repo, so **any plugin may create the bus** — which means
every plugin needs its exact starting shape, not only the checks that judge it. This is that
shape. Write it verbatim, then add your own sections:

```markdown
# Project Configuration — <project name>

<!-- manifest schema: 1 -->

## Project              <!-- owner: shared -->

| Key | Value |
|---|---|
| Name | <project name> |

## Environment          <!-- owner: shared -->

| Key | Value |
|---|---|
| Stack | <what you detected, or leave the row out> |

## Version control      <!-- owner: shared -->

| Key | Value |
|---|---|
| Kind | <git, or what you found> |

## Tracker              <!-- owner: shared -->

| Key | Value |
|---|---|
| Kind | <none, or what you found> |

## Verification         <!-- owner: shared -->

| Key | Value |
|---|---|
| Proven by | <the command that proves done> |

## Bindings             <!-- owner: shared, additive -->

| Seam | Kind |
|---|---|

## Artifacts            <!-- owner: shared, additive -->

| Artifact | Path | Owner |
|---|---|---|

## Versions             <!-- owner: shared, additive -->

| Component | Version | Owner |
|---|---|---|
| manifest schema | 1 | shared |

## Commands             <!-- owner: shared, additive -->

| Role | Migrate | Re-scaffold | Doctor |
|---|---|---|---|
```

**The schema number is `1`, and it is declared here** rather than left for each plugin to know.
Without that, a plugin that is first to run has to either invent a frozen-core number or write a
bus that fails check 2 immediately — and inventing it is worse, because the value means "this is
the shape I wrote" and a guess makes that a lie.

**Write only the rows you actually know.** A `| Key | Value |` table with no rows is a correct
empty section; a row filled with a plausible guess is the thing every plugin's init is forbidden
to do. Leave the rest for whoever asks the user.

### 3. Registered artifacts resolve

For every `## Artifacts` row:

- Path exists → pass.
- Path missing → **drifted**: report it as **absent**, once, naming the row and its owner. **Do
  not go looking** for a replacement and do not delete the row — scanning is what the registry
  exists to remove, and the row is its owner's to fix.

### 3b. A registered artifact whose role has no component

For every `## Artifacts` row whose owner is **not** yours: if that role has no `## Versions` row,
report it as **drifted** — "role `X` owns `<path>` but is not registered as a component". The
artifact is on disk and its owner's version is unknown, so nothing can tell whether it is current,
and no migration will ever act on it. Name the role and say its owner's init registers it; **do
not name a command** — with no `## Commands` row there is nothing to read, and guessing one is the
error this table exists to prevent.

### 4. Ownership is respected

- A section whose owner marker is **yours** but whose content you did not write, or cannot
  parse → **drifted**.
- A section owned by **another role** is **never** reported as wrong. You may report that it is
  *absent* when something you do depends on it, but its contents are not your finding. The
  artifact's owner is authoritative; anyone else's reading is advisory and names the owner's
  command.

### 5. Every component's version, and who can act

Report the **whole `## Versions` table**, not only your own rows — this is the one place an
adopter sees the full picture without running four tools:

| For each row | Report |
|---|---|
| Owned by you, current | pass |
| Owned by you, behind | **drifted** + your own migrate command |
| Owned by you, below your floor | **drifted** + your re-scaffold command |
| Owned by another role | its stamp and the command from `## Commands` — no judgement |
| Owned by another role, **no `## Commands` row** | **disabled**: "stale and its migrate command is not available here". That is the complete finding |

**Never guess another owner's canonical version.** You cannot know it — only that tool can — so a
row you do not own is reported, never assessed.

### 5b. Uncommitted things are actually uncommitted

If **`.agent/local/`** exists, the project's ignore file must ignore it. Present and **not**
ignored → **broken** for that path, and name your own role's re-scaffold command, which adds the
entry.

This is one check rather than a nicety because of how it fails: an ignore entry that has stopped
matching looks exactly like one that works, and the first symptom is somebody's local state
arriving in a diff — a session scratchpad, a personal preference, a half-finished goal — where it
then becomes everyone's. `cadence`'s first migration exists partly to repair such an entry.

Report any **local file outside that directory** — a `*.local.*` under a plugin's own folder —
as **drifted**, naming the owning role and its migrate command. Its owner moves it; you do not,
even when the destination is a shared directory.

### 5c. Nothing local is shadowing a committed decision

Read what is in `.agent/local/` — names and keys, not contents. A file or key there that sets a
value a **committed** config owns is **broken**: report the local key, the committed one it
shadows, and say the committed one wins.

The point is not tidiness. A local override of a committed setting is invisible to everyone else
on the project — it does not show up in a diff, a review, or another developer's checkout — so the
two people debugging the same behaviour see different systems. Worst of all for a **gate**: a gate
a developer can switch off for themselves is not a gate, because the opt-out gets taken at exactly
the moment it is inconvenient.

Settings a project's own extensions declare are **not** this finding: those are declared in a
committed artifact with their values local, which is the arrangement working as intended. The
finding is a local value for a key the committed config already answers.

### 6. Bindings resolve to something

For each binding row (`Doc system`, `Intent`, `Shared knowledge`, and any other):

- Names a kind with a project-local adapter or a shipped fallback → pass.
- Names a kind with **neither** → **broken** for that seam: name the command that generates an
  adapter.
- `none` → **disabled**, and only mention it when something you do would have used it. `none` is
  the correct state for most projects and most seams; announcing every unbound seam on every run
  is how a real finding gets lost.

### 7. The report says what to run

Every finding names **exactly one command** — the single writing command for that artifact — or
says plainly that none is available. A finding with no next action is a complaint.

**And the command must act.** A `migrate` named for a role whose stamp already equals its
canonical will do nothing; a `re-scaffold` named for a blank row re-asks what init already asked.
Before naming a command, ask what it would change here. Where the honest answer is *nothing — a
person edits this row*, say that: the shared rows are the project's, and a hand edit is a
legitimate remedy. A finding that sends someone to run a no-op teaches them to ignore findings.

**A doctor never writes.** Not a fix, not a re-stamp, not a "helpful" missing section. It reads
and reports; the named command changes things.
