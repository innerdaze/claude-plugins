# tools/

Repository infrastructure. **Never shipped** — the plugin payload in `cadence/`
stays pure Markdown, and nothing here is part of what an adopter installs.

```
python tools/validate_cadence.py            # what CI runs
python tools/validate_cadence.py --quiet    # only print failures
```

Requires PyYAML. Exit code 0 means no errors (warnings are allowed); 1 means at
least one error.

## Why this exists

Everything Cadence ships is Markdown that an agent executes at run time. There is
no compiler between what we write and what happens, and the characteristic
failure is **silent**: an unanchored file path or a contradictory instruction
doesn't crash, it makes the model improvise. By the time you notice, it has
already produced confident work against the wrong assumption.

So every rule below exists because the thing it checks *actually went wrong*, not
because it seemed tidy. If a rule ever fires on something correct, fix the rule —
but read this file first, because the reasoning is usually the point.

## The rules

**Manifests** — both JSON files parse; the marketplace `name` avoids "claude"
and "anthropic"; `plugin.json` carries the fields a
published plugin needs; the marketplace entry's version matches `plugin.json`;
the CHANGELOG knows about the current version. *Why:* the repo shipped for two
commits with a marketplace name that made the documented install command fail,
and with no changelog at all.

**Skills and commands** — a skill's directory name equals its frontmatter `name`;
every skill has a name and description; every command points at a skill that
exists. *Why:* skills are addressed `plugin:skill`, and a mismatch between the
directory and the declared name makes resolution depend on which one the harness
happens to use. The `cadence-` prefix also exists so installing can never shadow
a `session` or `plan` skill an adopter already has — a check that the names stay
namespaced protects that.

**`${CLAUDE_PLUGIN_ROOT}` paths** — every anchored path resolves to a real file,
and a skill may not reference a bundled file *without* anchoring it. *Why:* this
is the highest-value rule here. A skill's working directory is the consumer's
repo, so `flows/HOOKS.md` resolves to nothing there. Adapter resolution, hook
resolution, and template scaffolding all depend on those loads succeeding, and
the failure mode is the model guessing rather than erroring.

**Banned terms** — no `machinegame`, `unreal`, `linear-uft`, `mp-safe`, or
`domains/PROJECT.md` in the payload. *Why:* Cadence is installed once and serves
every project, so another project's name or namespace sitting in the payload is a
live contamination source. This is not hypothetical — a worked example in
`config.example.md` leaked an undocumented config key into two unrelated projects
during testing.

**Flow specs** — validate against `FLOW-SPEC.md`: no unknown top-level keys;
`meta.cadence_version` present; `states.roles` values are real lanes; `backlog`
and `done` roles exist; both sides of every gated transition are declared lanes;
every referenced gate exists; approvers and decision rights use the documented
levels; `hooks:` entries name real hooks whose docs exist. *Why:* the schema used
to *be* a preset, so the other presets invented keys nothing recognised.

**Lane reachability** (warning) — a transition starting in a lane nothing
declared reaches means any gate on it never fires. Entry points are the `backlog`
role and the first incident lane. *Why:* a shipped preset gated
`"In Review -> Done"` while declaring no review step, so its only gate was
attached to a transition that never happened.

**Priority-policy tokens** (warning) — tokens should be documented in
`FLOW-SPEC.md`. Unknown ones are legal (they're read as prose) but warned, since
a token nothing recognises silently does nothing. The manuscript example
deliberately trips this.

**Hook firing sites** — every hook in the catalog has a `*Fired by:*` line naming
a skill that exists, or is explicitly marked deferred. *Why:* seven catalogued
hooks were never invoked by any skill. A hook nothing fires is a promise of
extensibility that silently does nothing, which is worse than not offering it.

**Adapter coverage** — every shipped fallback mentions every operation of its
contract, either implementing it or declaring it unsupported, and has a
`## Capabilities` block. *Why:* an optional capability a tracker lacks must
degrade *visibly*. Silence is indistinguishable from a bug.

## What it cannot check

Whether the prose is *correct*. Whether a preset's stated default matches the
hook contract's stated default. Whether an adapter's described commands actually
work against the real tool. Whether the session-end ordering is right.

Those need a human, or a live run — see `docs/VERIFICATION.md`. The validator
catches drift and broken references; it does not read for meaning.

## Adding a rule

Two questions first: has this actually gone wrong, and is it mechanically
decidable from the files alone? If yes to both, add it here with a comment saying
which defect it prevents, and add a line to this file. Then verify it by
reintroducing the defect and confirming a non-zero exit — a rule that has never
been seen to fail is a rule you don't know works.
