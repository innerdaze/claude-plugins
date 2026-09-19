# `hub upgrade` — the guided sequence

Brings a project and the plugins it needs up to date together, in the order that works, asking
before it changes the shape of anyone's stack.

It exists because of one gap: on a repo whose knowledge system predates the plugin split, the
tool that notices a role is unregistered is forbidden from naming the plugin that would fix it.
Every existing adopter is in that state.

## What it never does

- **Apply another owner's migration.** It invokes `domains migrate`; it never does what that
  migration does. A version stamp is a claim about what wrote the files, and only the thing that
  wrote them may make it.
- **Install anything the user did not choose.** Step 2 asks. A `hub` that installed the stack on
  the way to answering something else would be making a stack decision on someone's behalf.
- **Resolve a contradiction by picking.** Two buses, two real paths for one artifact: stop, show
  what differs, offer the resolutions, apply the chosen one. A central plugin is the worst
  possible place for a silent choice.
- **Run a role's *usage* command.** An upgrade runs **setup** commands only — the migrate,
  re-scaffold and doctor a role declares. `/intent:capture`, `/cadence:plan`,
  `/cadence:session start` and `work on` are the work itself, and the work is not something to
  perform on somebody's behalf while they are waiting for a migration to finish. Name them as
  next steps; never invoke them.

  The tell is whether the command needs to know **what the user wants to do today**. A migration
  does not. An interview does — which is how a first attempt at this sequence ended up asking
  *"how should the content be captured — interview, brain-dump, or draft from the code?"* in the
  middle of registering a role.

## Procedure

**Before anything, confirm this is the coordinated run.** A migration edits shared committed
files. One developer, clean tree, its own branch, merged on its own. If the tree is dirty or the
branch is `main`, say so and let them decide before you touch anything.

### 1. Detect

Follow [`detect.md`](./detect.md) in full: what is installed **and enabled**, whether each
payload is current, what the bus says, and any knowledge-shaped folder nobody registered.

### 2. Ask what scope of upgrade they want

First sort the missing plugins into two piles, because they are not the same question:

| The plugin is missing and… | It belongs to | Because |
|---|---|---|
| **this repo has its artifact** — a knowledge folder on disk, unregistered | **the upgrade itself** | the content is already committed; the plugin is the tool needed to migrate it. Leaving it out does not leave the repo alone, it leaves it half-migrated |
| **this repo has no artifact for that role** | **a stack decision** | nothing here needs it, and adding it changes what this project runs |

Then offer three answers:

1. **Upgrade** — every registered role brought up to date, **plus install what is needed to
   finish the artifacts already here**. Name each such plugin in the option itself: *"installs
   `domains@…` so `domains/` can be registered and migrated"*. Never silent, never a surprise.
2. **Upgrade, and install anything missing** — as (1), plus every role in the roster this repo
   has no artifact for.
3. **Upgrade, and install these** — as (1), plus a list they choose from. Show the roles, what
   each owns, and that this repo has no artifact for them.

**Collapse the options when they resolve to the same action.** If nothing is missing beyond what
the artifacts here entail — one plugin, or none — then (1), (2) and (3) are the same sequence
written three ways, and offering all three implies a choice that does not exist. Ask the single
question that is actually open: *"`domains/` is committed here and unregistered;
`domains@…` is the plugin that registers and migrates it. Install it as part of this upgrade?"*
Say in one line what the other options would have added and why they are empty here, so the
person can see the scope rather than trust it.

**Do not offer "migrate only what is here" as a headline option.** On the repo this command
exists for it means *leave the knowledge folder committed, unregistered and unmigrated*, which
nobody chooses on purpose. An option whose own description is the problem is not a choice.

**Declining an entailed install stays available** — just not as the default framing. If they say
they would rather not install it, skip that role, carry on with the rest, and say plainly in the
report which artifact was left unmigrated and what it is waiting for.

For anything being installed: resolve each role through [`roster.md`](./roster.md), name every
plugin, and install them — or ask them to and run `/reload-plugins`.

⚠️ **Installing new plugins means everything already present must be migrated too.** A stack
where one plugin is new and another is two versions behind is the out-of-sync state this whole
sequence exists to prevent, and it is worse than either extreme because nothing reports it.

### 3. Update before you migrate

For every role that is going to be migrated: **its plugin must be current first.**

This is a precondition, not politeness. An outdated plugin declares an outdated canonical, so a
repo at that old number reports "nothing pending" and the chain stops silently — see
[`detect.md`](./detect.md) step 2. Migrating against a stale payload produces a repo that looks
finished and is not.

`claude plugin update <id>`, then `/reload-plugins` if the update needs it.

**If `hub` itself was among the plugins updated, stop here.** The rest of this procedure would
run from the copy that was loaded before the update — an older roster and an older sequence —
which is exactly what [`detect.md`](./detect.md) step 0 refuses at the start. Say `/reload-plugins`,
then re-run `/hub:upgrade`; it resumes from the state it finds, and nothing done so far is lost.

### 4. Run each owner's own commands, in this order per role

| Order | When | Command |
|---|---|---|
| 1 | the role's plugin is behind | its update (step 3) |
| 2 | the role owns an artifact but has no `## Versions` row, **or** the user asked for the role to be scaffolded | that role's **init** — it registers itself and stamps itself, at its floor when the files predate it |
| 3 | always | that role's **migrate** |

**Scaffolding a role that owns nothing here still means its init.** When the user has asked for a
role to be set up — a knowledge system, an intent layer — run that role's init and let it create
its artifact, empty. An empty registered layer is a real outcome: the folder exists, the bus names
it, and every tool can see it. **The absence of content is not a reason to skip the setup**, and
filling it is the user's next command rather than this sequence's business.

**Delivery first when it is in scope.** Its migrations do the structural moves — the bus, the
overlay, the extracted rules — and other roles' migrations repoint what those moves broke. This
is the one ordering `hub` may hold, because it follows from what the migrations *say* about their
own preconditions rather than from `hub` knowing anyone's internals.

### 5. Loop while anything applied

A migration may **decline** because a precondition is unmet, and become ready once something else
has run. So run another pass over everything still pending. **Stop when a whole pass applies
nothing** — on lack of progress, not on a count — and report each remaining item with what it
said it was waiting for.

### 6. Report — four parts, and nothing else

**The test for every line: if it does not change what the reader does next, leave it out.** The
reasoning, the preconditions you checked, the ordering argument — all of it is already in the
transcript above for anyone who wants it. Repeating it here buries the answer in evidence.

| Part | Content |
|---|---|
| **Headline** | one line: what state the project is in now |
| **What changed** | one line per role, with the versions it moved between. *Not* one line per migration — ten applied migrations is one line saying `delivery 2 → 12` |
| **Outstanding** | one line per item, each naming the command that clears it and whose it is |
| **Next** | the commands to run, in order, copy-pasteable. At most four. Or one line: nothing pending |

A behaviour change — a migration that changed what happens, not where a file lives — is one line
in *What changed*, marked as a change rather than a move. Never omit it; never spend a paragraph
on it.

Then, and only where they exist:

- **Every remaining item with its next action**, or a plain statement that none exists. A role
  whose plugin the roster does not know; a reference nothing could repoint; a contradiction you
  stopped on.
- **What is outside this repo and therefore nobody's migration.** Auto-memories, personal notes
  and saved commands that named the old paths are now stale, and no migration can reach them.
  Name the file and the replacement where you can see it; a doctor will keep reporting them
  either way.
- **What is deliberately not done here.** Topic-content accuracy needs a re-scan (`prep refresh`
  or its equivalent) and cannot be judged by a migration; the workflow overlay has its own
  upgrade path.

Then suggest `hub doctor`, which is how they check the result rather than take your word for it.
