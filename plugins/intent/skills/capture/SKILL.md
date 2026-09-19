---
name: capture
description: >-
  Capture a project's design as an authoritative intent layer in an `intent/` folder — dictated
  by the maintainer, never derived from the code — and log every place the implementation
  contradicts it as an alignment gap to fix. Use whenever someone wants to "lock down the
  design", "capture the design", "capture the intent", "write design docs", "document why the app
  is the way it is", or set up docs that are the source of truth over the code. Also use it for a
  record of architectural intent, decisions or non-goals that outranks existing docs like
  CLAUDE.md, a README or a wiki — and when they want the mismatches between stated intent and
  actual code found and tracked rather than quietly resolved.
user-invokable: true
---

# Design intent capture

Most architecture docs are written by reading the code. That makes them a
second, staler copy of something already true — and it means the code can never
be *wrong*, only undocumented.

This skill produces the opposite artefact: an `intent/` folder holding what the
maintainer says the system is **for** and **meant to be**, with the code given no
vote. When the two disagree, the doc stands and the contradiction becomes work.

That inversion is the entire value. Protect it.

## The four rules

Everything below is mechanics. These are the point.

**1. The maintainer is the source of truth.** They dictate; you structure. If they
haven't said it, it isn't in the docs.

**2. Never author intent from code.** You may read code to *check* a claim, answer
a factual question, or find a contradiction. You may not read it to decide what
the design should be. The moment you infer intent from implementation you've built
the stale-copy artefact they were trying to avoid.

**3. Contradictions go in the register, never into the docs.** When code disagrees
with stated intent, you do not soften the doc, add a "currently, however…", or
quietly reword. You log it in `intent/alignment.md` as a gap with a severity. This
is the discipline that makes the docs load-bearing.

**4. Unstated is not assumed.** Leave an explicit `TODO — needs input` marker
rather than filling a gap with something plausible. A doc that's 80% stated intent
and 20% invented is worse than one that's 80% and honest, because nobody knows
which is which.

## Phase 0 — Orient, without reading code for content

Find the documentation layers that already exist: `CLAUDE.md`/`AGENTS.md`, a
`domains/` or similar operational-knowledge system, `README`, an external wiki
(Notion, Confluence). Read them to learn **what each layer is for**, not to learn
the design.

You need this because `intent/` is about to sit above these layers, and you must
be able to say how they relate — otherwise you've just added a fourth doc nobody
knows the standing of.

If the project has a domain/context system with a load command (e.g. `prep <topic>`),
use it. It's cheaper than exploring, and it tells you the project's own vocabulary.

## Phase 1 — Agree the shape of *this run*

**The layer must already exist.** If there is no `intent/` and no registered intent artifact, say
so and name `/intent:init` — it creates the root, the register and the bus rows, and it takes
seconds. Do not scaffold one on the way past: setup is once per repo, this is once per run, and
running them together is what had an upgrade sequence asking how content should be captured
months before anyone had content to capture.

Two things decide *this* run, and guessing either wastes a pass. Ask them together:

- **How will content be captured?** Interview section-by-section · maintainer
  brain-dumps and you structure · you draft from code and they correct. Say plainly
  that the third option risks anchoring the design on the current implementation —
  that's the one that quietly reintroduces rule 2. **Ask it every run**: it depends on
  how much the maintainer has in their head today, not on the project.
- **What this run is about**, in their words — one line. Not a topic list: a subject. *"How
  invoicing is supposed to work"*, *"why we refuse to do X"*.

**Do not agree a topic set yet, and do not derive one from the repo.** Topics are how the
material gets organised, and the material does not exist yet. Ask for labels first and you are
asking somebody to name boxes before they have said anything to put in them — and a list you
derived from the code anchors the whole layer on the implementation's shape, which is rule 2
arriving through the back door. The one place a maintainer's own framing shows up is exactly the
place a pre-populated multi-select crowds out.

The **spine** is different and is safe to name now: `purpose`, `architecture`, `workflow` are a
template, derived from nothing, and they exist to stop the dictation covering what the thing does
while skipping what it must refuse to become. Say you will use them and move on.

Standing and layout were settled by `/intent:init` and are in the README. Read them; do not
re-ask them.

## Phase 2 — Scaffold the spine only

Create a stub for each spine topic — `purpose`, `architecture`, `workflow` — and nothing else.
`README.md` and `alignment.md` already exist from `/intent:init`; fill what is absent, overwrite
nothing. Templates: `references/templates.md`.

**The middle topics come out of Phase 3, not into it.** A stub is a claim that somebody agreed the
topic, and so far nobody has.

Every stub gets a `Needed from you` block listing the specific questions that
topic can't be written without. This is doing real work — it turns "tell me about
your architecture" into a set of answerable prompts, and it shows the maintainer
the shape they're filling.

Write **no design content**. Not even the obvious parts.

## Phase 3 — Capture, then let the topics fall out

The maintainer dumps; you organise it into the stubs.

**When the material stops fitting the spine, that is a topic.** Name it from what they said, in
their vocabulary, and show the grouping: *"this is really three things — the invoice lifecycle,
the API surface, and who is allowed to change a posting. Split them out?"* Topics arrived at this
way are theirs; topics offered up front are yours, and they will accept yours out of politeness.

`references/topic-selection.md` still holds the signal table — a schema suggests a data-model
topic, an external interface suggests a surface topic. **Use it as a prompt when they run dry,
never as an opening menu**, and when you do, say where the idea came from: *"you have migrations,
so there may be a data-model intent you have not stated"* is an honest prompt. Presenting the same
list as a set of options to tick is code deciding the shape of the layer.

While organising:

**Turn statements into rules where they are rules.** "The API is read-only" is
more useful written as a constraint the project must hold than as a description.

**Surface implications they didn't state, and label them.** If they say themes are
added locally and ship via PR, the consequence — playing is local, sharing needs a
review — is worth writing down, marked as your inference so they can strike it.
This is where a lot of the value lands: the maintainer knows their intent, but
hasn't always followed it to its end.

**Watch for conflicts between their own answers.** Over several rounds people say
things that don't compose. When answer B contradicts answer A, say so and offer
options — do not pick one silently, and do not average them. Record it as a
conflict in the register until they choose.

**Keep the TODO markers where nothing was said.** Resist tidiness.

## Phase 4 — Check the code, log what disagrees

Now read code — to test claims, not to write them.

For each substantive statement, ask what would have to be true. Then check the
cheap ones directly: a grep that settles "no module imports another module's code"
takes seconds and is worth more than a paragraph of hedging. **Verify what's cheap,
log what's expensive.**

**Establish provenance before severity.** Before logging a mismatch, ask whether the
implementation is something the maintainer *chose* or something that *arrived* — with a
framework template, a vendor plugin, a starter kit, sample content, a generated scaffold. Inherited
code is evidence of nothing about the design: a sample project's default behaviour contradicting
a stated rule is not the maintainer disagreeing with themselves. It is still worth a row, because
it will shape the design by inertia if nobody decides about it — but it goes in the register's
**Inherited, not chosen** section as scaffolding to keep or remove, never in the gap table as
drift. Ask when unsure; a wrong severity here costs a round of withdrawals, and the pattern is
general — `create-react-app` defaults, a cloud provider's starter IaC, a vendored SDK's example
handlers, an engine's sample game.

Every mismatch that *was* chosen becomes a row in `alignment.md` with a severity:

- **blocker** — the intent is unachievable as built
- **drift** — works, but the wrong shape
- **cosmetic** — naming or docs only

Key each row by a content slug — `<area>/<claim>`, never a number. A register is a list
more than one pass appends to, and a sequential key is only correct for the writer who holds
the current state; two passes in one tree will mint the same number from a stale read, silently.
Same rule for any list the index grows (`references/templates.md`).

**A register you find already keyed by number was written by an earlier version of this skill.**
Offer to re-key it — this is the one workflow allowed to write the register, and the maintainer
is present, which is the condition. Each row gets a slug from its subject; a permanent *Legacy
numbering* table (`Was | Now`) goes at the foot so the numbers quoted in older commits and
tickets still resolve; every cross-citation in the layer's other docs is rewritten. Content is
untouched — you are changing keys, not claims — and say so when you show what you wrote. Decline
to do it silently as a side effect of something else: it is a change to a doc set somebody cites.

Also answer any factual questions they asked along the way ("are these kept up to
date on CI?"). Getting a real answer often uncovers the most interesting gaps.

Keep a **"decided, not yet checked"** section for intent you recorded but nobody has
verified. It's an honest third state between "confirmed" and "known broken", and it
becomes the audit list later.

One more thing, easy to get wrong: if a note you wrote earlier prescribes a fix,
and inspecting reality shows that fix would be *wrong*, correct the plan and say
why. Don't execute a bad plan just because it's written down — including one you
wrote.

## Phase 5 — Close the open questions

Work through the `TODO — needs input` markers in batches of about four, each with
a recommendation and the trade-off spelled out. Recommendations are welcome; the
maintainer's answer is what gets recorded.

Two things to do with every answer:

- **Follow it through the other docs.** An answer often overturns an earlier one.
  If they add a non-technical audience, a "no accessibility floor" decision made
  when the audience was developers may no longer hold. Apply the consequence and
  tell them you did.
- **Read partial answers precisely.** If they pick one item from a list of four,
  the other three were *declined* — record that, since "we deliberately did not
  rule this out" is real information. Same for "any of the above", which usually
  means *any one suffices*, not *all are required*.

Stop when the markers are gone.

## Phase 6 — Follow through

Docs nobody points at get ignored, and gaps nobody tracks get forgotten.

0. **Register the layer in the config bus, if `/intent:init` has not already.** Normally it has,
   and this step is a no-op you confirm rather than repeat. Add or update **only** the
   `intent-layer` rows in
   `.agent/PROJECT.md` (if no tool has made one, create it from the skeleton in `${CLAUDE_PLUGIN_ROOT}/checks/BUS-CHECKS.md` § *Creating the bus, when nothing has*, which carries the frozen core and the schema marker's value, then add just these rows — any tool
   may create it, none may wait for another):

   - `## Artifacts` → `| Intent | intent/ | intent-layer |`
   - `## Versions` → `| intent scaffolding | <floor> | intent-layer |` — a role owning an artifact
     with no version row is drifted by the shared checks. A layer you are registering here
     already existed, so it gets the **floor**, and `/intent:migrate` brings it up; both integers
     are declared in `${CLAUDE_PLUGIN_ROOT}/skills/migrate/SKILL.md`
   - `## Commands` → `| intent-layer | /intent:migrate | /intent:init | /intent:doctor |`
   - the `Intent` binding row → `markdown`, the kind the shipped fallback implements

   **This is what makes the layer visible to tooling at all.** Until it exists, the folder is
   perfectly readable by humans and invisible to every tool — because no other tool may register
   an artifact it does not own, and guessing at a folder that looks like design documentation is
   the path-detection the registry exists to remove.

   Write **no other role's rows**, and if the `Intent` binding already names a different kind,
   leave it: a project-local adapter someone generated outranks the fallback.

1. **Make `intent/` discoverable.** Add a pointer from `CLAUDE.md`/`AGENTS.md` and
   the operational docs: what `intent/` is, that it outranks them, and that
   contradictions go to the register. Name the two or three rules most likely to
   bite someone mid-task.
2. **External surfaces.** If there's a wiki page, *inspect it before touching it*.
   It usually holds operational content `intent/` deliberately excludes — in which
   case the right move is an additive pointer, not a regeneration. Confirm before
   writing to anything shared.
3. **Commit.** Docs only, so nothing to run. Write the message so the *decisions*
   are visible in the log, not just "add design docs".
4. **File tickets for the gaps** — see `references/tickets.md`. Group gaps that are
   one coherent change, note dependencies between them, and skip anything that's a
   doc chore you can just do. Then link the ticket keys back into the register so
   the two stay connected.

## What good output looks like

- Every statement traceable to something the maintainer said.
- Zero invented intent; explicit markers where nothing was stated.
- A register where each row names the intent, what the code does instead, a
  severity, and a status — not a vague list of concerns.
- Existing docs pointing up at `intent/`, so the layering is discoverable.
- The maintainer surprised at least once by a gap they didn't know they had. That's
  the signal the process did something reading the code wouldn't have.

## Show what you wrote, and have it confirmed

This plugin writes **documents, not configuration**, so the ecosystem's confirm-your-config
convention lands differently here — but it lands harder, because everything produced is a claim
about what the maintainer meant.

End by listing what you wrote and, for each doc, **what is dictated versus what carries an
`[inference]` marker**. The markers are the confirmation surface: they are the claims that have
not been ratified, and asking someone to read a whole doc set is asking for a yes. Asking them to
strike or confirm six marked lines is a task.

Also name what stayed `TODO — needs input`, since an unanswered question is easy to lose and is
the thing most likely to matter later.

## Reporting

Keep it to what changes what the reader does next: the documents written, the count of
`[inference]` markers and unanswered `TODO — needs input` lines, and anything you deliberately
left alone.

**End with the next steps** — in order, at most four. For this skill the next step is usually a
person's rather than a command's: the marked lines are the confirmation surface, so say how many
there are and that striking or confirming them is what turns a draft into an intent layer.

## References

- `references/topic-selection.md` — deriving the topic set for the repo at hand
- `references/templates.md` — stubs for the index, topic docs, and the register
- `references/tickets.md` — filing gap tickets in an unfamiliar tracker
