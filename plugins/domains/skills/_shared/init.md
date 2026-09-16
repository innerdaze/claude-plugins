# `domains init` — scaffold the knowledge system

Creates a repo's **project memory**: per-topic knowledge files plus the manifest that says which
of them a task should load. Run once per repo; re-run to reconcile (it fills gaps and leaves
everything else alone).

## What this owns, and what it does not

| | |
|---|---|
| **Owns** | `domains/**` — the manifest, the maintenance guide, the scan guide, and every topic file. The `knowledge` rows in the config bus's `## Artifacts`, `## Versions` and `## Commands`. The `Domain Knowledge System` section of `CLAUDE.md` and one `## Rules` bullet |
| **Does not own** | the config bus itself, the environment/VCS/tracker bindings in it, the ticket-flow overlay, or anything under `.agent/work/` |

**The bus may already exist, and that is the normal case.** Whichever tool inits first creates
it; you add your rows to it. Never rewrite a section you do not own, never reorder the file, and
preserve anything you do not recognise verbatim.

## Step 1 — Read the bus; do not re-derive it

Read the config bus at **`.agent/PROJECT.md`** (if it is absent, fall back to the legacy
`domains/PROJECT.md` and say once that it should be migrated).

Take the **`## Environment`** section's `Stack` row as given. Do not re-detect the environment:
whoever wrote that row already asked the user, and a second detection that disagrees is worse
than no detection — `environments.md` here holds *topic seeding hints only*, not detection
signals.

**If the row is absent, you may write it** — `## Environment` and `## Version control` are
`shared` sections, not another role's, precisely so a repo with only this plugin installed is not
stuck. Ask the user, write the row, and **never overwrite a value someone else already put
there.**

The six `shared` sections and their exact headings are frozen-core, listed in
`${CLAUDE_PLUGIN_ROOT}/checks/BUS-CHECKS.md` — which is why they can be named here without
reading another plugin's files.

If no bus exists at all, **create it** from the skeleton in
`${CLAUDE_PLUGIN_ROOT}/checks/BUS-CHECKS.md` § *Creating the bus, when nothing has* — it carries
the frozen core verbatim, including the `<!-- manifest schema: N -->` value, so you never have to
invent one. Add the sections you own, fill only the rows you actually know, and say so. Any tool
may create the bus; none may wait for another to do it, and none has to guess its shape.

**Step 2 — Write `domains/INDEX.md`.** Seed the always-load and topic-triggered rows from
the environment's typical topics (`environments.md`), then **refine them
against the real repo**: the topics should mirror this codebase's actual subsystems,
and the trigger keywords should be real directory names, symbols, and file prefixes
you can see in the tree. A manifest full of generic guesses is worthless; one keyed
to real paths is what makes `work on`'s domain selection accurate. (You'll often
finalize topics after the scan in 3f reveals the true structure — it's fine to write
a first cut here and tighten it after.)

**Step 3 — Write `domains/prep-refresh-guide.md`.** This is the re-runnable scan
procedure, tailored to the detected environment — see "Writing the scan guide" below.
It exists so `prep refresh` works later even without the `work` skill present.

**Step 4 — Write `domains/meta.md`.** This is the domain-system guide *for this project*
— how loading works, **how to add a new domain**, **how to maintain existing ones**,
and the environment-specific hard rules. Fill the template from
`templates.md`. It's scaffolding (not scan output), and it's what lets a
future agent or human extend the system without ever reading this skill — so don't
skip it. If a plugin or framework already ships a general `meta`, your project
`meta.md` covers the project-specific layer and points at the plugin's rather than
duplicating it.


**Step 5 — Run the first scan (`prep refresh`).** Follow the guide you just wrote in Step 3
to scan the project and write the per-topic domain files into `domains/`. This is the content
generation — the step that turns an empty manifest into real operational knowledge.
For environments with dedicated scan tooling (an editor MCP, a framework CLI),
use it. For everything else, gather knowledge from **reading files + safe, read-only commands**
(package/dependency listing, type-check in no-emit mode, test discovery) — never run
mutating commands. Respect the per-file token budgets and the scaling rules in the
guide. For a large scan, consider delegating Phase 1 discovery to an `Explore`
subagent and keeping only the findings.

**Step 6 — Reconcile and summarize.** With real domain files written, revisit INDEX.md
(3b) and tighten topics/triggers to match what the scan actually found.

Then report, and keep it to what changes what the reader does next: the config you wrote
(shown, not summarised — it is what they are being asked to check), the files created as a
list, and anything you deliberately left alone. **End with the next steps** — `prep <domain>`
and `work on <TICKET>` once the system is live, or the command that clears whatever is still
outstanding. One line each; the reasoning is already above.


## Writing the scan guide (Step 3, expanded)

The guide's three-phase shape is constant; its content must be the detected
environment's reality. Use the skeleton in `templates.md` and fill it so
that a fresh agent, reading only the guide, could regenerate the domain files:

- **Phase 1 (Discovery, breadth):** name the exact files to read and the exact
  read-only commands to run for *this* stack, and what to extract from each. E.g. for
  a Node/TS repo: `package.json` (scripts, deps, workspaces), `tsconfig.json`, the
  app entry + routing/module wiring, the test config; plus `yarn list --depth=0` or
  `npm ls`. Be specific — vague guides produce vague domain files.
- **Phase 2 (Deep inspection, depth):** give the heuristic for finding the core
  subsystems (entry points, the biggest feature areas, the most-imported modules)
  and what to capture about each: structure, dominant patterns, naming conventions,
  the seams other code extends. Cap the number of deep dives; summarize the rest.
- **Phase 3 (Write):** one file per always-load + major topic, with the token budget
  and the per-file contents (what it is, where it lives, proven patterns, gotchas).
- **Scaling rules:** how to group when counts explode so output stays token-efficient.

Keep all of it in the environment's vocabulary. If a plugin or framework already
ships its own scan procedure (e.g. a `prep-init-guide.md` under a plugin's
resources), point at that and have your guide capture only the *project-specific*
layer rather than duplicating it.


## Step 7 — Register in the bus

Add or update **only** the `knowledge` rows:

- **`## Artifacts`** — `| Knowledge | domains/ | knowledge |`
- **`## Versions`** — the stamp depends on **who wrote the folder you are registering**, and
  getting this wrong silently skips migrations:

  - **You just scaffolded it** (there was no `domains/`, or you rewrote it): stamp
    `<canonical from templates.md>`. The content is this release's, so nothing is pending.
  - **It already existed** — you are registering knowledge written by an older release, or by
    `work` before this plugin existed: stamp the **`Minimum supported version`** instead, and say
    that `domains migrate` will raise it. That content predates every migration in the chain, and
    a stamp at canonical means "up to date", so the pending work would be skipped without anyone
    seeing a message. A stamp is a claim about what wrote the files, not a wish about their state.

  Either way the row reads `| knowledge scaffolding | <N> | knowledge |`.
- **`## Commands`** — `| knowledge | domains migrate | domains init | domains doctor |`,
  **including the `Doctor` cell.** This plugin ships a doctor, so the cell has an answer, and
  nobody else can supply it: `work` is forbidden from guessing another role's command name, so an
  undeclared doctor means every tool reports "`knowledge` is stale and its doctor is not
  available here" — a false statement about a command that exists. If the table has no `Doctor`
  column yet (a bus below `delivery` v7), write the three-cell row and say the column is missing.
  Fill your own cell, never another role's.
- **The `Doc system` binding row** — set it to `markdown`, the kind this plugin's shipped
  fallback implements. That row is what tells any other tool it can ask *what applies here*
  rather than reading files it should not know about.

  ⚠️ This is the one row you write that is **not** a `knowledge` row, and it needs saying why:
  the binding is a statement about *this project's* configuration, and you are the tool that
  just made it true. If it already names a different kind, leave it — a project-local adapter
  someone generated outranks the fallback, and overwriting it would break a working setup.

That last row is what lets any other tool's `migrate` bring this system up to date without
knowing this plugin exists. **Declare no other role's rows**, and if a row you own already exists
with a different value, update the value and leave the rest of the table exactly as it is.

## Show what you wrote, and have it confirmed

**Every init ends by presenting the configuration it produced.** Not a summary — the content, or a
faithful rendering of it. A summary is where a wrong assumption survives: *"configured your
tracker"* reads as correct whatever actually got written.

**Mark what you inferred, separately from what you were told.** The lines the user supplied need no
scrutiny. The inferred ones are the whole reason to ask, and separating them turns "does this look
right?" — whose honest answer is usually "I suppose so" — into a short list of specific claims
somebody can check.

Say two more things while you have their attention: **what this configuration switched off** (a
binding left `none`, anything the tool cannot do here) and **how to change each part** — the file
to edit, or the command to re-run. A confirmation nobody can act on is a notification.

Running non-interactively: print the same thing and say plainly that it was **not confirmed**.
