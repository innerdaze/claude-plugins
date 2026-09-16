# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repository.

## What this repo is

A **public plugin marketplace** and nothing else. It holds five plugins — `hub`,
`cadence`, `domains`, `work`, `intent` — under `plugins/`, and serves them
directly: `.claude-plugin/marketplace.json` points at each directory, so
**merging to `main` is publishing**. There is no registry and no release step.

**The plugins are not developed here.** They are developed in a private monorepo
(`agent`, cloned at `~/Projects/agent`) and mirrored in by
`tools/sync_from_agent.py`. Everything under `plugins/` is generated output.

### The rule that matters most

**Never edit anything under `plugins/`.** A fix made here survives exactly until
the next sync, which deletes and rewrites each plugin directory wholesale. It
also diverges the public copy from the one the author is actually maintaining,
which is worse than the bug being fixed — the two look identical and behave
differently.

When something in a plugin is wrong: fix it in `~/Projects/agent/plugins/<name>/`,
commit it there, then re-run the sync. If the user asks for a plugin change while
in this repo, say where it has to be made rather than making it here.

The same applies to `CHANGELOG.md` and `tools/validate_cadence.py`, which are
also mirrored (from `intent/cadence/CHANGELOG.md` and `scripts/validate_cadence.py`
upstream). `tools/sync_from_agent.py`, `README.md`, `CLAUDE.md` and
`.github/workflows/` are this repository's own and are edited here.

## The sync

```
python tools/sync_from_agent.py              # sync, push, open the PR
python tools/sync_from_agent.py --dry-run    # report what would change, write nothing
python tools/sync_from_agent.py --no-pr      # commit locally, stop there
```

It reads the **committed** upstream tree (`git archive origin/main`), never the
working copy, so it neither disturbs nor is disturbed by whatever is checked out
over there. In order it: resolves the ref, copies each plugin's published file
set, scrubs the private repo's identity, regenerates the marketplace manifest,
records provenance in `.upstream.json`, audits, validates, commits, pushes, and
opens the PR with `gh`.

Three of its design choices are load-bearing, and all three exist because the
alternative failed:

- **What to copy comes from upstream's `package.json` `files` array**, not a list
  in this script. That array already governs what npm publishes, so it is
  maintained; a list here would be a second answer to the same question, and the
  second answer is the one that goes stale. It also excludes exactly the right
  things — `evals/`, `.npmrc`, `package.json` itself.
- **Each plugin directory is deleted before it is rewritten.** A mirror that only
  adds files keeps serving a skill that upstream deleted, and a skill is usually
  deleted because following it now does the wrong thing.
- **Text is normalised to LF on ingest** (`to_lf`). `git archive` honours
  `core.autocrlf`, so on Windows upstream bytes arrive CRLF while the rules that
  rewrite them are anchored on `\n`. Against CRLF those rules do not error, they
  match nothing — which is how a README once shipped a page of private-registry
  install instructions through a scrub that reported "clean".

## The scrub, and why it fails closed

This repository is public; its source is not. The sync rewrites the private
repo's identity out of every file — npm scope, GitLab URLs, project id, author —
and then **audits the result and refuses to commit if anything survives**. A
warning would be useless: the next statement in the script is `git push`.

The audit checks two different things, because the first is not enough:

1. **Identifier tokens** — `acresoftware`, `skunkworks`, the project id, the
   registry endpoint.
2. **The shape of private-install prose** — `The repo is private`, `read_registry`,
   `.npmrc`. Rewriting `@acresoftware` to `@innerdaze` inside a paragraph about
   wiring a scope to a token-gated registry produces text that passes every
   identifier check and still sends a reader somewhere they cannot go. This is
   not hypothetical; it is what the first run produced.

If the audit fires, the fix is a rule in `REWRITES` or `INSTALL_BLOCK` in the
sync tool — never a hand-edit of the mirrored file, which the next sync reverts.

CI runs the same audit against the committed tree
(`python tools/sync_from_agent.py --audit-only`), which is what covers a file
edited by hand.

## Adding a sixth plugin

Add its name to `PLUGINS` in `tools/sync_from_agent.py` and re-run. Everything
else — the marketplace entry, the README install block, the manifest rewrite —
is derived. It must exist upstream with a `files` array in its `package.json`.

## Before committing

```
python tools/validate_cadence.py            # payload invariants (vendored)
python tools/sync_from_agent.py --audit-only # leak check
```

Both run in CI, along with a check that nothing but Markdown, manifests and the
vendored `checks/*.py` readers reach a plugin payload, and that the marketplace
manifest's versions match the plugin manifests'.

## Conventions

- **One skill, one surface. There is no `commands/` directory.** A plugin skill
  is both typeable as `/<plugin>:<name>` and selectable by Claude from its
  description, so a command wrapper only registers every capability twice.
- **Skill names are bare** (`init`, `session`, `doctor`), with the directory name
  matching the frontmatter `name`. The plugin namespace already prefixes them.
- **Bundled-file references need `${CLAUDE_PLUGIN_ROOT}`.** A skill's working
  directory is the *consumer's* repo, so a bare relative path resolves to
  nothing there and the model improvises rather than erroring.
- Prose style in the plugins is deliberate — a rationale for every rule, because
  these docs are read by models as well as people, and the rationale is what
  makes a rule survive contact with a case nobody wrote down.
