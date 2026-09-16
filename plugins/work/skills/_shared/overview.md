# The domain-system mental model (shared context for the work:* skills)

Read this before running `work:init` or `work:on` — it is the shared model the whole
skill family is built on.

This skill family is built around one idea: **a project should carry its own operational
knowledge and its own config, in plain files, so that any agent picking up work
already knows how this specific codebase wants to be worked.** That apparatus is
the *domain system*:

```
<project root>/
├── domains/
│   ├── PROJECT.md          ← config: environment, VCS, ticket tracker, how "done" is proven
│   ├── INDEX.md            ← manifest: topic → domain file, with trigger keywords
│   ├── meta.md             ← the domain-system guide: how loading works, how to ADD & MAINTAIN domains, hard rules
│   ├── prep-refresh-guide.md ← the re-runnable scan procedure that (re)generates the topic files below
│   ├── workflow.md         ← OPTIONAL overlay: custom steps/skills folded into the 3 phases (written by update-workflow)
│   ├── code.md             ← per-topic operational knowledge (names vary by environment)
│   ├── <topic>.md          ← more topic files, discovered dynamically
│   └── ...
└── CLAUDE.md               ← gains a "Domain Knowledge System" section documenting the `prep` commands
```

Two commands operate it (documented into the project's `CLAUDE.md` by `work:init`):

- **`prep <domain>`** — load the matching domain file(s) before starting a task
  (e.g. `prep code`, `prep ui + persistence`).
- **`prep refresh`** — (re)scan the project and (re)write the per-topic domain
  files. Run during `work:init` for the first pass, then re-run after major changes.
  (`prep one time init` is accepted as a legacy alias.)

`meta.md` is the system's self-documentation: it tells a future agent or human how
the domain system works *in this project* and — crucially — **how to add a new
domain and how to keep existing ones current**. Adding a domain is always: write
`domains/<name>.md` in the house structure, register it in `INDEX.md` with real
trigger keywords, stay within the token budget. `work:init` writes `meta.md`;
`work:on`'s wrap-up phase keeps the topic files current by promoting recurring gotchas
into them per `meta.md`'s conventions.

**`.agent/PROJECT.md` — the config bus — is the single source of truth.** `work:on` reads it every
run and adapts its behavior — VCS commands, ticket-tracker calls, verification
steps — to whatever it finds there. That is why there is one adaptive `work:on`
rather than a per-project copy: `work:init` writes the config, `work:on` reads it.

### The spine is invariant — every phase, every domain step, every ticket

**The three phases are invariant; PROJECT.md adapts *how* they run, never *whether*
they run.** `work:on` always executes Phase 1 (Context & Planning), Phase 2 (Execute),
Phase 3 (Wrap up), and always keeps domain integration inside them — **regardless of
ticket size or how familiar it looks.** There is no small/known/trivial fast-path that
skips picking domains from `INDEX.md` and running the Domain Loader; a one-line fix takes
the same spine (just fewer domains). The Loader is spawned as an `Explore` subagent but is
**not** interchangeable with open-ended exploration: Explore reads the code fresh, the
Loader front-loads *this project's* distilled conventions and gotchas so you don't
rediscover known traps the hard way. Projects customize
the flow — folding in their own workflow skills or extra steps — through the optional
`.agent/work/workflow.md` overlay, written by `work:update-workflow`. The overlay is a **step
library** plus **scenarios** (a bug, a hotfix, and a feature can each select/order steps
differently); it *slots steps around* the core spine (with model + effort chosen by the same
rule `work:on` uses) and never removes a phase or a domain-integration step. When a folded
skill isn't committed to the repo, its load-bearing detail is **extracted** into
`.agent/work/rules/*.md` so the overlay never depends on a skill teammates lack. See
`update-workflow.md`.

### The cardinal rule: never assume the environment

These skills run in any kind of project. **Detect what the project actually is;
never carry vocabulary, file types, or commands from one ecosystem into another.**
The domain file names, the trigger keywords, the verification commands, and the
language you use must all come from *this* project's reality, established by reading
the repo — not from a template you assumed. When in doubt, look, then confirm with
the user.

Environment detection signals, per-ecosystem domain topics, and verification
commands are tabulated in **`environments.md`** — consult it, but treat
it as a starting point you refine against the actual repo, not a fixed menu.
