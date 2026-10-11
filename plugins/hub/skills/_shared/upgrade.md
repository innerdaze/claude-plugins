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
- **Write a file itself — any file.** Not a missing document a finding pointed at, not a config
  key, not a "quick fix" between two owners' commands. Found on a real upgrade: cadence's
  `dod_gates` were set and no Definition of Done document existed, so the run wrote one — with
  gates the config did not declare — left the config alone, and then explained the mismatch as
  the two having *"no link"*. They are linked, by the bus's `## Verification → Definition of
  Done` row, which the owner's own init writes. Every gap a run finds is closed by the command of
  the role that owns it (step 4, row 4) or reported as outstanding; there is no third route
  where `hub` improvises the content. **And never explain a gap by asserting two artifacts are
  unrelated** — if you cannot see the link, the owner's doctor or contract can; say you do not
  know and run it.
- **Install anything the user did not choose.** Step 2 asks. A `hub` that installed the stack on
  the way to answering something else would be making a stack decision on someone's behalf.
- **Resolve a contradiction by picking.** Two buses, two real paths for one artifact: stop, show
  what differs, offer the resolutions, apply the chosen one. A central plugin is the worst
  possible place for a silent choice.
- **Run a role's *usage* command.** An upgrade runs **setup** commands — the migrate and
  re-scaffold a role declares — and its **diagnostic** doctor, which writes nothing. `/intent:capture`, `/cadence:plan`,
  `/cadence:session start` and `work on` are the work itself, and the work is not something to
  perform on somebody's behalf while they are waiting for a migration to finish. Name them as
  next steps; never invoke them.

  The line is **the command's role, not whether it asks questions.** A role's migrate and init
  are setup; its doctor is **diagnostic** and writes nothing; its capture, plan, session and
  `work on` are usage. A first attempt at this
  sequence ran `/intent:capture` while registering a role — that is the mistake this rule exists
  for.

  **Asking questions does not make an init a usage command.** An init that asks which flow the
  project follows, confirms a detected tracker, or needs tracker auth to read the board's
  statuses is asking about the project's *configuration*. That is setup, and step 4 runs it.
  Never decline an init on the grounds that it is "its own command" — every command `hub` runs is
  somebody else's.

## Procedure

**Before anything, confirm this is the coordinated run.** A migration edits shared committed
files. One developer, clean tree, its own branch, merged on its own. If the tree is dirty or the
branch is `main`, say so and let them decide before you touch anything.

### 1. Detect

Follow [`detect.md`](./detect.md) in full: what is installed **and enabled**, whether each
payload is current, what the bus says, and any knowledge-shaped folder nobody registered.

### 2. Ask what scope of upgrade they want

First sort **every role from the roster's `roles()`** by one question: **is this project using
it?** Whether its plugin is absent, disabled or installed does not decide the pile — it only
decides whether the action needs an install (or `claude plugin enable`) step in front.

| The role… | It belongs to | Because |
|---|---|---|
| **is registered here** | **the upgrade itself** — migrate | it is in use |
| **is unregistered, but this repo has its artifact** — a knowledge folder on disk | **the upgrade itself** — install the plugin if needed, init, migrate | the content is already committed; the plugin is the tool needed to migrate it. Leaving it out does not leave the repo alone, it leaves it half-migrated |
| **is not used here** — no row, no artifact | **a stack decision** — install the plugin if needed, then init | nothing here needs it, and adding it changes what this project runs. A plugin installed for other repos is not consent to scaffold this one, and not a reason to leave it out of the question either |

Then offer three answers:

1. **Upgrade** — every role in use brought up to date, **plus install what is needed to finish
   the artifacts already here**. Name each such plugin in the option itself: *"installs
   `domains@…` so `domains/` can be registered and migrated"*. Never silent, never a surprise.
2. **Upgrade, and set up everything else** — as (1), plus every role not used here: install its
   plugin if needed, then scaffold it. Name each, and which have an install step.
3. **Upgrade, and set up these** — as (1), plus a list they choose from. Show the roles, what
   each owns, and whether choosing it means an install.

**Never skip this question** — not when every plugin is installed, not when every role is
registered, not when the answer looks obvious. The question is where the person sees what is
about to change and agrees to it; a run that skips it has made the scope decision for them.
Found on a real upgrade: every plugin installed, the question skipped, and the person learned
the scope from the report.

**The shape may collapse; the question may not.** When no role is in the stack-decision pile,
(1), (2) and (3) are the same sequence written three ways, so do not offer three. Ask instead:

1. **Upgrade all of these** — one line per role: its stamp now, the command that will move it,
   and any install or enable it needs, named (`delivery 14 — work migrate`). **Never print a
   target version.** The canonical lives in the owner's payload, which `hub` does not read
   ([detect.md](./detect.md) § 1b); a number here would be a guess presented as a plan. The
   owner's migrate says where it landed, and the report carries that.
2. **Upgrade only these** — the same list, to pick from.
3. **Dry run** — print the sequence and change nothing.

Say in one line why there is no "set up everything else" option — every role is already in
use — so the person can see the scope rather than trust it. **Nothing to do is still asked**:
*"everything is current — run the doctors anyway?"* is the question then, and the answer is
theirs.

**A role with no artifact never disappears from the question.** Found on a real upgrade: a repo
with `work` and `domains` set up, `cadence` installed but unregistered and `intent` not
installed. The run reported "nothing left to apply", mentioned `intent` nowhere, and treated
`cadence` as something it could not do. Every role in `roles()` is either registered, set up by
this run, declined by the user, or named in the report as available — there is no fifth state.

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
| 2 | the role owns an artifact but has no `## Versions` row, **or** the user chose the role in step 2 | that role's **init** — it registers itself and stamps itself, at its floor when the files predate it |
| 3 | always | that role's **migrate** |
| 4 | the role's migrate or doctor names its own **init** or **re-scaffold** as the remedy for something | that command, now — see below |

**A remedy an owner names for its own role is part of the upgrade.** When a migrate declines with
*"run `/cadence:init`"*, or a doctor reports *"row absent — `/cadence:init` confirms it and writes
the row"*, that is the owner saying which of its setup commands finishes the job. Run it, in this
run, and let it ask what it asks. Never end the run telling the person to go and run an init the
sequence could have run itself — found on a real upgrade, which closed by suggesting
`/cadence:init` to fix cadence findings it had just watched appear. An init re-run on a
registered role fills gaps and overwrites nothing; that is what makes it safe to run here.

**Scaffolding a role that owns nothing here still means its init.** When the user has asked for a
role to be set up — a knowledge system, an intent layer — run that role's init and let it create
its artifact, empty. An empty registered layer is a real outcome: the folder exists, the bus names
it, and every tool can see it. **The absence of content is not a reason to skip the setup**, and
filling it is the user's next command rather than this sequence's business.

**An init that stops is outstanding, not out of scope.** An init may stall on something only the
person can supply — tracker auth, a choice between flows — and they may interrupt it. Report it
as an outstanding item: the role, the init command, and what it was waiting for (*"`/cadence:init`
— needs Jira auth to read the board's statuses"*). On a re-run, offer it again with that
precondition named so they can clear it first. Never re-describe a stalled init as a command
`hub` cannot run; it is the same command it was before it stalled.

**Delivery first when it is in scope.** Its migrations do the structural moves — the bus, the
overlay, the extracted rules — and other roles' migrations repoint what those moves broke. This
is the one ordering `hub` may hold, because it follows from what the migrations *say* about their
own preconditions rather than from `hub` knowing anyone's internals.

### 5. Loop while anything applied

A migration may **decline** because a precondition is unmet, and become ready once something else
has run. So run another pass over everything still pending. **Stop when a whole pass applies
nothing** — on lack of progress, not on a count — and report each remaining item with what it
said it was waiting for.

**Then run each touched role's doctor** — diagnostic, writes nothing — and act on what it says
about its own role: a finding whose remedy is that role's migrate, init or re-scaffold is step 4,
row 4, and goes back into the loop. Only a finding whose remedy is a *usage* command, a person's
hand edit, or another plugin is outstanding. The report is written after this, so it never names
a setup command the run could have run.

### 6. Report — four parts, and nothing else

**The test for every line: if it does not change what the reader does next, leave it out.** The
reasoning, the preconditions you checked, the ordering argument — all of it is already in the
transcript above for anyone who wants it. Repeating it here buries the answer in evidence.

| Part | Content |
|---|---|
| **Headline** | one line: what state the project is in now |
| **What changed** | one line per role, with the versions it moved between. *Not* one line per migration — ten applied migrations is one line saying `delivery 2 → 12` |
| **Outstanding** | one line per item, each naming the command that clears it and whose it is. Includes every role from `roles()` that is still not set up here — declined, stalled, or not offered because the user picked a narrower scope — with whether its plugin is installed. One line each; never omit one because the scope left it out |
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
  or its equivalent) and cannot be judged by a migration.

Then suggest `hub doctor`, which is how they check the result rather than take your word for it.
