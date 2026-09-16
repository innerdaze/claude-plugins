# Choosing the topic set

The topic list decides what the docs can say, so **it is arrived at after the
dictation, not before it** (`SKILL.md` Phase 3). What follows is a prompt sheet
for a maintainer who has run dry — not an opening menu.

⚠️ **Never present the derived middle as a list to pick from.** A topic offered up
front is yours, and it will be accepted out of politeness; a topic that fell out
of what they actually said is theirs. Worse, a list derived from the repo frames
the whole layer around the implementation's shape, which is rule 2 — *never author
intent from code* — arriving where nobody is watching for it. Choosing which
subjects to *ask* about is legitimate; choosing them from the code and showing
them as options is how the code ends up deciding.

When you do use a signal below, **say where it came from**: *"you have migrations,
so there may be a data-model intent you have not stated"* is an honest prompt that
the maintainer can reject. The same list as tickboxes is not.

A CLI tool has no theming, a library has no deployment model, and scaffolding
empty docs for things a project doesn't have teaches the maintainer that the
folder is boilerplate.

## The spine (nearly always)

Three topics apply to almost any project:

| Topic | Answers |
|---|---|
| **purpose** | Why does this exist? Who is it for? What must it refuse to become? |
| **architecture** | What are the pieces, what are the boundaries, what may depend on what? |
| **workflow** | How does work arrive, get done, get proven, and land? |

`purpose` is the one people skip and the one that pays off most. Non-goals in
particular — "what should this refuse to become" — settle arguments a year later.

## Prompts for the middle, when they run dry

Look at what the project actually is, then propose topics for the parts a
newcomer could get wrong. Signals worth checking:

- **A database, schema, or migrations** → a data-model topic: what's stored, at what
  grain, what's rebuildable vs irreplaceable, retention, what may be reshaped.
- **Anything pulling from external sources** (scrapers, collectors, sync jobs, ETL)
  → a collection topic: who triggers it, on what cadence, what's allowed to fail.
- **An API, MCP server, plugin surface, or public interface** → a surface topic:
  what callers may do, and specifically what they may *never* do.
- **Theming, design tokens, or a component library** → a visual-intent topic.
- **Auth, tenancy, or permissions** → its own topic; intent here is usually
  strongly held and rarely written down.
- **A published artefact** (package, image, docs site) → a release/compatibility
  topic: what stability is promised.
- **Multiple deploy environments** → fold into architecture unless it's genuinely
  involved.

## How to raise one

Say *why* the topic occurred to you
("you have a Postgres schema and collectors, so data model and collection look
worth their own docs"), and let the maintainer cut or add. They may also have a
topic you'd never infer — the reason the project exists is often social, not
technical.

Two failure modes to avoid:

- **Too many topics.** Eight sparse docs read as unfinished. Six full ones beat ten
  thin ones; fold rather than split when unsure.
- **Topics that mirror the source tree.** One doc per package or service produces a
  code map, not intent. Topics should follow *problems and decisions*, which usually
  cut across modules.

## Always include the register

Whatever the topic list, `alignment.md` is not optional. Without it the process has
nowhere to put contradictions, and rule 3 collapses — the docs quietly get edited
to match the code instead.
