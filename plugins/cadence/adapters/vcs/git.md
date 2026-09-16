# VCS adapter: `git`

*The default VCS adapter. Implements the vcs contract from the plugin's `adapters/ADAPTERS.md` via the `git` CLI.*

## Capabilities

```
supports:    status, diff, log, add_untracked, checkpoint, ignore
costly:      —
unsupported: —
```

## Config

```yaml
vcs:
  kind: git
  checkpoint: commands          # this adapter runs git directly
  # checkpoint: skill:/commit    # or delegate to a project commit skill, if it has one
```

## Operations

- **`status()`** — `git status --porcelain`. Empty output = clean tree. Parse lines for changed/untracked paths.
- **`diff(paths?)`** — `git diff` (unstaged) and `git diff --staged` (staged); scope to `paths` when given. Use to review changes and draft a message.
- **`log(n?, paths?)`** — `git log -n <n|10> --format='%h %s'`, scoped to `paths` when given. Return `{ref, message, item_refs}` per entry, where `item_refs` are the `<PREFIX>-<n>` tokens found in the subject. This is how `/cadence:session end` confirms a checkpoint referencing the item exists.
- **`add_untracked(paths)`** — `git add -- <paths>` (git needs new files staged before they commit).
- **`checkpoint(message, item_ref)`** — stage **the paths belonging to this piece of work**, then `git commit -m "<item_ref>: <message>"`. Confirm with `git log -1 --oneline`. **Do not `git push`** unless the user asks.
  Prefer explicit paths over `git add -A`. A blanket add sweeps in whatever else happens to be sitting in the tree — build output, a stray scratch file, another task's half-finished edit — and attributes it to this item's commit. If you do use `-A`, run `status()` first and say what you are about to include.
- **`shared_local_dir()`** — `git rev-parse --git-common-dir`, then `<that>/cadence/` (create if
  absent). **Shared by every worktree of this repo and never committed**, which is the pair of
  properties nothing else has: the working tree is per-worktree, and anything committed is
  everyone's forever. Used only for cross-worktree coordination — see *Sessions across worktrees*
  in `ADAPTERS.md`. Never put anything here that matters after today: it is not backed up, not
  cloned, and a `git worktree prune` may take it.
- **`ignore(paths)`** — append each path to `.gitignore` if not already present (idempotent; create the file if missing). Used at init to keep Cadence's session-state file (`.agent/cadence/SESSION.local.md`) out of the repo.

## Etiquette

- **Reference the item.** The commit subject leads with `item_ref` (e.g. `ABC-12: add throughput evaluator`) so tracker and repo stay linked.
- **Branch awareness.** If committing directly to the default branch (`main`/`master`) would violate the project's norms, surface that to the user rather than assuming — Cadence doesn't enforce a branching model (a flow can, via a `transition`/`checkpoint` hook).
- **No history rewrites.** No amend/rebase/force unless explicitly requested.
- **Message quality.** If no message is supplied, draft one from `diff()` focused on the *why*, and show it before committing.

## Delegating to a project commit skill

If the project has its own commit skill, set `vcs.checkpoint: skill:/commit`. Then `checkpoint` invokes that skill (passing the message + item_ref) instead of running git directly — the same seam that lets Cadence integrate with an existing workflow rather than replace it.
