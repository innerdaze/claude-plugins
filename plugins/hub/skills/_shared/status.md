# `hub status` — what state is this project in

Read-only. One page, and the question it answers is *"what would I have to run, and why"*.

## Procedure

1. **Detect** — [`detect.md`](./detect.md) in full.
2. **Report, in this order**, because it is the order someone acts in:

### Reviewability

Working tree clean; current branch; whether a migration would land as its own change. A dirty
tree is not an error here — it is the reason to say "not yet" before anything else.

### Plugins

Every plugin this stack knows about, and its state: installed and enabled, installed but
**disabled** (remedy: `claude plugin enable`, not an install), absent, or **behind** (remedy:
`claude plugin update`).

**Report a behind payload before you report any component as up to date.** An outdated plugin
declares an outdated canonical, so it will call a stale repo current — and every number inside
the repo agrees with it.

### Components

The whole `## Versions` table, not only the rows whose owner is installed — this is the one place
an adopter sees the full picture without running four tools.

| Row state | Report |
|---|---|
| owner installed, current | pass |
| owner installed, behind | pending, with that owner's migrate command |
| owner installed, below its floor | its **re-scaffold** command, not its migrate |
| owner not installed | its stamp and the command the bus declares — no judgement, because you cannot know its canonical |
| **role owns an artifact but has no row** | **present but unversioned** — that role's own init registers it. Say so; this is the row that is otherwise invisible |

### Bindings and artifacts

Each `## Artifacts` row and whether its path exists. Each binding row and whether it resolves to
an adapter something can load. `none` is reported only when something would have used it.

### Unregistered knowledge

Any knowledge-shaped folder no `## Artifacts` row names. Nothing will load it until its owner
registers it.

### End with what to do

One line of answer, then the commands to run, in order, copy-pasteable — `hub upgrade`, a
specific plugin to install or enable — or *"nothing pending; anything above is either another
owner's to register or a human's to judge"*.

**Keep the report to what changes what the reader does next.** A finding they cannot act on, and
whose owner you have already named, is one line. A reader who has to reconstruct the next step
from a table of findings has been handed homework, not an answer.

## Never

- **Never write.** Not a fix, not a stamp, not a missing row "while you are here". Every finding
  names the command that would change it.
- **Never judge a component whose owner is not installed.** Only that owner knows its canonical
  version. Report the stamp and the declared command; that is a complete answer.
