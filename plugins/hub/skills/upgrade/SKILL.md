---
name: upgrade
description: >-
  Bring a project and the plugins it needs up to date together — detect what is installed, ask
  what scope of upgrade they want (finish what is here, add everything missing, or pick), update each plugin before
  running its migrations, then run each owner's own init and migrate in order until nothing more
  applies. Stops on contradictions and offers the resolutions rather than picking. Use when the
  user runs `/hub:upgrade`, says the stack or the project is out of date, is upgrading a repo
  set up against an older release, or acts on a stale-scaffolding warning.
argument-hint: "[--dry-run]"
user-invokable: true
---

Follow `${CLAUDE_PLUGIN_ROOT}/skills/_shared/upgrade.md` exactly.

It reads `${CLAUDE_PLUGIN_ROOT}/skills/_shared/detect.md` for detection and
`${CLAUDE_PLUGIN_ROOT}/skills/_shared/roster.md` for resolving a role to the plugin that serves
it.

With `--dry-run`, do the detection and print the sequence you *would* run — every command, in
order, per role — and change nothing. That is `/hub:status` plus a plan, and it is the right
thing to offer anyone who has not decided yet.

Three rules that outrank convenience, restated here because this is the command most likely to be
run in a hurry:

- **Never apply another owner's migration.** Invoke their command; never do its work.
- **Never install what the user did not choose.** The procedure asks; the answer is theirs.
- **Never resolve a contradiction by picking.** Stop, show what differs, offer the resolutions,
  apply the one they choose.
