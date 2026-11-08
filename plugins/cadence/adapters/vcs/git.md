# VCS adapter: `git`

*The default VCS adapter. Implements the vcs contract from the plugin's `adapters/ADAPTERS.md` via the `git` CLI.*

## Capabilities

```
supports:    status, diff, log, add_untracked, checkpoint, ignore, shared_local_dir
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
  Prefer explicit paths over `git add -A`. A blanket add sweeps in whatever else happens to be sitting in the tree — build output, a stray scratch file, another task's half-finished edit — and attributes it to this item's commit. If you do use `-A`, run `status()` first and say what you are about to include. **The session's `## Tree at start` snapshot says which dirty paths were never this session's**; a path that appeared without this session editing it is another writer's and is not staged, however plausible its name. A correct file list is not evidence of correct content.
- **`shared_local_dir()`** — `$(git rev-parse --path-format=absolute --git-common-dir)/agent-local/`.
  **Absolute, always:** in a main checkout `--git-common-dir` prints a relative `.git`, and a link
  built from a relative target dangles the moment it is read from anywhere else. This only
  **names** the folder — it does not create it; `${CLAUDE_PLUGIN_ROOT}/checks/LOCAL-DIR.md`
  creates it and links
  `.agent/local` to it. **Shared by every worktree of this repo and never committed**, which is
  the pair of properties nothing else has: the working tree is per-worktree, and anything
  committed is everyone's forever. The name is role-neutral because the folder holds every tool's
  local files, not only cadence's. See *Sessions across worktrees* in `ADAPTERS.md`. Never put
  anything here that matters after today: it is not backed up and not cloned. (`git worktree
  prune` does not touch it — that only clears stale entries under `.git/worktrees/`.)
- **`ignore(paths)`** — make git ignore each path, idempotently, in **both** `.gitignore`
  (created if missing) and the shared exclude file at `git rev-parse --git-path info/exclude`.
  Write each path **without a trailing slash**: `.agent/local/` matches only a directory, so it
  stops matching the moment `.agent/local` becomes a symlink, and the first symptom is the link
  showing up as untracked. Where a line reading `<path>/` is already there, **rewrite that line in
  place** rather than adding a second one beside it. Leave every other line alone. Confirm with
  `git check-ignore -q <path>`. Used at init to keep `.agent/local` — Cadence's session state and
  every other tool's local files — out of the repo.

## Etiquette

- **Reference the item.** The commit subject leads with `item_ref` (e.g. `ABC-12: add throughput evaluator`) so tracker and repo stay linked.
- **Branch awareness.** If committing directly to the default branch (`main`/`master`) would violate the project's norms, surface that to the user rather than assuming — Cadence doesn't enforce a branching model (a flow can, via a `transition`/`checkpoint` hook).
- **No history rewrites.** No amend/rebase/force unless explicitly requested.
- **Message quality.** If no message is supplied, draft one from `diff()` focused on the *why*, and show it before committing.

## Delegating to a project commit skill

If the project has its own commit skill, set `vcs.checkpoint: skill:/commit`. Then `checkpoint` invokes that skill (passing the message + item_ref) instead of running git directly — the same seam that lets Cadence integrate with an existing workflow rather than replace it.
