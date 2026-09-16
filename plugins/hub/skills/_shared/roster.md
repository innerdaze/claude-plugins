# Resolving a role to the plugin that serves it

Used only for a role that has **never registered itself**. A role with a `## Commands` row is
resolved from the bus, always — the repo is the authority on a project that has already answered.

## Resolve the binding first

The `ROSTER` contract is at `${CLAUDE_PLUGIN_ROOT}/contracts/ROSTER.md`. Load the adapter in this
order:

1. the project's own adapter at **`.agent/hub/adapters/roster/project.md`**, if it exists;
2. the shipped fallback `${CLAUDE_PLUGIN_ROOT}/adapters/roster/official.md`;
3. `${CLAUDE_PLUGIN_ROOT}/adapters/roster/none.md`.

**Read the `## Capabilities` block before calling anything.** Under `none`, `resolve()` is
`unsupported` — every unregistered role becomes a question for the user, and that is a working
outcome rather than a failure.

A project adapter **outranks** the shipped one for every role it names, and only for those —
roles it is silent about fall through to the shipped list. That is the mechanism by which an
in-house plugin is bootstrapped exactly like an official one, and it is why the shipped list is a
fallback rather than a gate.

**Read it; never write it.** If the user tells you which plugin serves a role, use the answer for
this run and, where they want it to stick, tell them where the file goes and what it contains
(`${CLAUDE_PLUGIN_ROOT}/contracts/ROSTER.md` § *Resolution order*) — offer to write it only if
they ask for that in so many words. An answer you obtained by asking, committed without being
asked, is a guess with a filename.

## What `none` means, and what it does not

`resolve(role) → none` means **ask the user**: name the role, name the artifact it owns, and ask
which plugin serves it — or ask them to install it and re-run.

It does **not** mean unsupported, and it must never be reported that way. The shipped roster is
the set of roles that can be bootstrapped without asking; it is not the set of roles that work.
A `hub` that told someone their in-house knowledge plugin was unsupported would have turned "the
core plugins" into "the only plugins", which is the one failure this plugin's own design refuses.

## Installing what a role needs

`hub` **declares no manifest dependencies**, deliberately: the harness's plugin dependencies
cannot be marked optional, so declaring them would install the whole stack at `hub`'s own install
time — for someone who may have wanted one plugin and a report. Installing is therefore a step
inside the sequence, taken only when the user has asked for it.

```bash
claude plugin install <id>          # id from the roster entry, marketplace-qualified
```

For the shipped roster that is the whole story: those plugins come from the same marketplace as
`hub`, so a machine running this command has it already.

**A project adapter can name a plugin from somewhere else**, and then the marketplace may
genuinely be missing — `claude plugin marketplace list` says. That is not a missing plugin but a
machine that was never told where this one comes from, and it is a decision about where code is
fetched from, so **ask before adding one** exactly as you ask before installing. An entry with
neither a marketplace nor an installable id: name it, say where it would have to come from, and
let the user install it. A working outcome, not a failure.

**If that is unavailable, or the user prefers to do it themselves:** name every plugin to install,
ask them to install them and run `/reload-plugins`, and continue from there. That path is not a
degraded mode — it is the same sequence with the install performed by a person.

After an install, the newly available skills may need `/reload-plugins` before they can be
invoked. Treat that as a seam in the sequence rather than a problem: it is also the natural point
at which someone can stop.

## Never

- **Never read the named plugin's files** to learn what it does or how its formats work. A roster
  entry is an id and some command names. This is the cardinal rule and a roster is not an
  exemption from it.
- **Never invoke a roster command on a role that has a `## Commands` row.** Use the row. The two
  should agree; when they do not, the repo is right and the difference is worth reporting.
- **Never write a resolved mapping into the repo.**
