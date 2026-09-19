---
name: init
description: >-
  Scaffold an empty intent layer and register it — create the `intent/` root with its index,
  rules and alignment register, add the `intent-layer` rows to the config bus, and point
  CLAUDE.md at it. Sets up the layer; captures no design content. Use when the user says
  "set up the intent layer", "initialise intent", "intent init", when an orchestrator is
  registering the intent-layer role, or before a first `/intent:capture` in a repo that has no
  `intent/` yet.
user-invokable: true
---

# /intent:init — set up the layer, capture nothing

**This skill creates a home for design intent. It does not gather any.** That is
`/intent:capture`, and the split is deliberate: setup happens once per repo, capture happens
whenever there is something to say. Running them as one command meant an upgrade sequence asking
*"how should the content be captured — interview, brain-dump, or draft from code?"*, which is a
decision about the run in front of you and cannot be answered months in advance.

## What it decides, and what it must not

**Ask two things, at most.** Both are durable properties of the layer:

- **Standing.** How does `intent/` relate to the docs that already exist? Usually *intent = why,
  existing docs = how it is built*; sometimes the maintainer wants it to supersede them outright.
  This goes in the README, because it is the sentence that settles arguments later.
- **Layout**, only if the default is wrong. One file per topic is the default and is right for
  almost everything; a single `DESIGN.md` suits a small project. Propose the default rather than
  asking cold.

**Ask nothing else.** In particular, do **not** ask how content will be captured, and do not ask
for a topic set — both belong to a capture run, both change between runs, and an answer given now
is an answer given without the work in view.

## Procedure

1. **Look before you scaffold.** If `intent/` (or the root the bus already registers) exists,
   this is a re-scaffold: fill what is absent, change nothing that is there, and say which.
   Never overwrite a captured document.

2. **Create the root**, empty and honest — `README.md` carrying the index, the four rules and the
   attribution legend, and `alignment.md` as the register with no rows. Templates are in
   `${CLAUDE_PLUGIN_ROOT}/skills/capture/references/templates.md`.

   **Write no design content and no topic stubs.** A stub implies somebody agreed the topic, and
   nobody has.

3. **Register the layer in the config bus** — only the `intent-layer` rows in `.agent/PROJECT.md`.
   If no tool has made one, create it from the skeleton in
   `${CLAUDE_PLUGIN_ROOT}/checks/BUS-CHECKS.md` § *Creating the bus, when nothing has*, then add:

   - `## Artifacts` → `| Intent | intent/ | intent-layer |`
   - `## Versions` → `| intent scaffolding | <version> | intent-layer |` — **canonical for a layer
     this command creates, the floor for a folder that already existed and is only now being
     registered.** Both integers are declared once, in
     `${CLAUDE_PLUGIN_ROOT}/skills/migrate/SKILL.md`; read them there rather than remembering them.
   - `## Commands` → `| intent-layer | /intent:migrate | /intent:init | /intent:doctor |`
   - the `Intent` binding row → `markdown`, the kind the shipped fallback implements

   **The version row is not optional, and "no migrations yet" is not a reason to omit it.** A
   role that owns an artifact and has no `## Versions` row is *drifted* by the shared checks
   (`${CLAUDE_PLUGIN_ROOT}/checks/BUS-CHECKS.md` §3b) — permanently, on every doctor run in the
   project, because the check cannot distinguish "this layer was scaffolded by a plugin that has
   never needed a migration" from "somebody's folder is on disk and nothing owns it". Those are
   the two states the registry exists to tell apart.

   A stamp is a claim about what wrote the files. **A folder that predates this command is
   stamped at the floor, never at canonical**, so its pending migrations are genuinely pending
   rather than silently skipped — `/intent:migrate` then raises it, the way every other role's
   does.

   **Write the `## Commands` cell from what this payload actually ships.** Projects registered
   before the `migrate` skill existed carry `n/a — no migrations yet` in that cell, and an
   orchestrator reads the bus — so until the cell is repointed nothing will ever invoke the
   migration. Re-running `/intent:init` on a registered project is a supported, idempotent
   re-scaffold, and repointing that cell is one of the things it is for. `/intent:doctor` reports
   the disagreement so nobody has to notice it themselves.

   **This is what makes the layer visible to tooling at all.** Until these rows exist the folder
   is readable by humans and invisible to every tool, because no other tool may register an
   artifact it does not own.

   Write no other role's rows. If the `Intent` binding already names a different kind, leave it —
   a project-local adapter someone generated outranks the fallback.

4. **Point CLAUDE.md at it**, insert-if-absent: what the layer is, that it outranks the code and
   the other docs within its scope, and that `[inference]` means *not ratified*. Touch only the
   section this plugin owns.

## Report

Headline, the files created, and **end with the next step**, which is always the same and is the
point of the whole exercise: `/intent:capture` to put something in it. An empty registered layer
is a correct outcome of this command and a useless one to stop at — say so in a line.
