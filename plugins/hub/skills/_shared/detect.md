# Detecting the stack — the step everything else starts with

Read once, at the start of `status` and `upgrade`. Nothing here writes.

## 0. Is the copy of `hub` that is running the one that is installed?

Read your own version from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`, then find `hub`'s
entry in `claude plugin list --json`. **Installed newer than loaded → this session is running a
stale `hub`**: an older roster, older detection rules, an older sequence. Say so first — *"running
hub 1.0.0; 2.0.0 is installed — run `/reload-plugins`, then re-run this command"* — and for
`upgrade` **stop there**: a migration sequence driven by a stale orchestrator is the failure this
step exists to prevent. `status` and `doctor` may continue after saying it, because reporting
from an old copy is still reporting; put the line at the top of the report so nothing below it
is read as current.

Found on a real upgrade: `/hub:upgrade` and `/hub:doctor` loaded from the `hub/1.0.0` cache while
2.0.0 was installed. The content happened to be identical that day; the trap is the one § *Loaded
is not the same as installed* below already describes for every other plugin, and `hub` is not
exempt from its own rule.

## 1. Installed *and enabled*, not merely present

```bash
claude plugin list --json
```

Each entry carries `id` (`name@marketplace`), `version`, `scope`, `enabled` and `lastUpdated`.

**A plugin can be installed and disabled.** The harness's own dependency resolution checks
`enabled`, and real installs report `"enabled": false`. So:

| State | What it is | The remedy to name |
|---|---|---|
| absent | not installed | install it (see [roster.md](./roster.md)) |
| installed, `enabled: false` | present and inert | `claude plugin enable <id>` — **not** an install |
| installed and enabled | usable | — |

Treating a disabled plugin as absent sends someone to install what they already have, and the
install will look like a no-op while nothing starts working. Report the state you actually found.

## 1b. Read the bus in one call

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/checks/bus_facts.py"
```

JSON: bus path and state, schema marker, sections with owner markers, the four tables parsed,
which artifact paths resolve, which roles own an artifact with no `## Versions` row, and the
mechanical findings. Use it instead of reading the bus line by line — the facts are identical and
it is one turn rather than a dozen, each of which the rest of the run would re-read.

No `python3`? Say so once, offer to install it, and read the bus yourself. It is a shortcut, never
a requirement (`${CLAUDE_PLUGIN_ROOT}/checks/BUS-CHECKS.md` § *Gathering the facts*).

**It does not answer the next question.** Canonical versions live in each owner's payload, which
this plugin may not read, so nothing it prints says whether a component is behind.

## 2. Is each installed plugin's payload current?

```bash
claude plugin list --json --available
```

Compare each installed `version` against what the marketplace offers, and name
`claude plugin update <id>` for anything behind.

**This is the check no repo-only tool can perform, and it is not a tidiness matter.** A plugin's
migrations live in its payload, and so does the canonical version they climb towards. An
outdated plugin therefore declares an outdated canonical — so a repo stamped at that old number
reports *"nothing pending"*, and the rest of the chain is skipped in silence. Every number inside
the repo is consistent; they are consistent with the wrong canonical.

So: **a stale payload makes a stale repo look current.** Report it before reporting any version
as up to date, and never present a component as current while its owner's payload is behind.

**"Current" means current within the range the marketplace offers, and that range can be wrong.**
A marketplace entry pins a version range, and a published release outside it is invisible to
every command here — `--available` will not list it and `claude plugin update` will report
nothing to do. Under `^0.x` semantics this bites hardest: `^0.1.0` excludes `0.2.0` entirely, so
a plugin that shipped a minor release reads as up to date forever.

This is the same trap one level out — the numbers agree, and they agree about the wrong thing —
so it earns the same treatment: **say what you compared against.** *"work 0.1.1, and the
marketplace offers nothing newer within `^0.1.0`"* is a sentence someone can act on. *"work is up
to date"* is not, and it is what sent one rehearsal into concluding a release did not exist when
it was published and merely unreachable.

**Never conclude that a capability does not exist because no reachable release has it.** When a
role's chain is blocked and the remedy would be a release, distinguish the two — *no release
provides this* versus *no release reachable from here provides this*, the second naming the pin
and the marketplace. A tool that reports the first when the second is true sends someone to write
code that already exists.

### Loaded is not the same as installed

`claude plugin list --json` reports what is **installed**. A plugin can also be loaded from a
directory — a development worktree, or `~/.claude/skills/` — and those do not appear there.
Worse, when both exist, **invoking a skill may resolve to the installed copy while you are
reading the directory one**, so a payload you have just confirmed as current is not necessarily
the payload that runs.

This was found on this plugin's own first rehearsal: five payloads were reported current from a
dev worktree, and one command resolved to an older installed cache instead.

So: **say which copy you checked.** For each plugin, report whether it is installed (with its
version) or loaded from a path, and when both are true, report both and say the installed one is
what a command will most likely resolve to. Never merge the two into one version number — that
number would be true of neither.

## 3. What the repo says

Read the config bus — `.agent/PROJECT.md`, else the legacy `domains/PROJECT.md` (say once that
it should be migrated). From it:

- **`## Artifacts`** — which roles own something on disk here. This is the set of roles the
  project *has*, whatever is installed.
- **`## Versions`** — which of those roles are registered as components, and at what stamp. A
  role in `## Artifacts` with no row here is **present but unversioned**: registered on disk,
  unregistered as a component, and invisible to anything that reads `## Versions` alone.
- **`## Commands`** — what each registered role declares. For a role that has registered itself,
  **this is the authority** and the roster is not consulted.

No bus at all: the project is not set up. Say so, and name the re-scaffold command for each role
the roster knows — that is a setup question, not a migration.

## 4. Knowledge-shaped folders nobody registered

A plugin resolves artifacts from `## Artifacts` and **never scans**, so a knowledge folder at a
path no row names is invisible to every plugin — permanently, and correctly. `hub` may look,
because it is the operator's tool rather than a resolver, and it **reports without registering**.

Look for a folder holding an index plus topic files that no `## Artifacts` row names. If you find
one, say that nothing will load it until its owner registers it, and that registering is that
role's own init.

## What this step must not do

- **Never write.** Detection is read-only, including the bus.
- **Never infer a role from a folder name.** That a directory is called `domains/` does not make
  `domains` its owner; a project may have renamed it or served the role with something in-house.
  Resolution comes from the bus or the roster, never from a path.
- **Never record what is installed into the repo.** Plugin availability is a per-session fact,
  and a committed note of it is wrong for the next person.
