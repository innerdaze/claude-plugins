# Creating `.agent/local`, and sharing it across worktrees

**One procedure, vendored by every plugin.** This file is the authority; each plugin ships a
byte-identical copy at `checks/LOCAL-DIR.md`, for the reason `checks/BUS-CHECKS.md` is vendored: no
plugin may read another's install path. The validator compares the copies and fails on any
difference.

**Read it only to set `.agent/local` up** — an init, `/cadence:session start`, a migration, or
the start of a `work on` run (in the restricted mode at the end). A doctor never reads it: it
judges the result through `checks/BUS-CHECKS.md` § *5b* and names the command that runs this.

## Why it is a procedure every plugin can run

**`.agent/local` belongs to the working copy, not to a plugin**, so — as with the bus in
BUS-CHECKS § *2b* — any plugin about to need it creates it, by this procedure, rather than assuming
another has. No plugin may hard-fail, or silently do without, because the one that usually does
this is absent. Every step is a no-op on a setup that is already right, so running it twice costs
nothing.

**It runs at init and session start, not only in a migration**, because a migration's stamp is
committed: it runs once per repository, a second worktree checks out the stamp already current,
and that worktree is exactly where an unshared `.agent/local` costs something. **Not a
`post-checkout` hook either:** the payload is Markdown with nothing to install one, husky v4 owns
`.git/hooks` and husky v5+ points `core.hooksPath` elsewhere — so a hook written there is
overwritten or never runs — and hooks are absent from a fresh clone.

## The procedure

Run from the repository root, in this order.

**1. Ignore it — before any link exists.**

```bash
X=$(git rev-parse --git-path info/exclude)   # resolves into the common dir: every worktree reads it
```

In **both** `.gitignore` and `$X` — the first reaches every clone, the second every worktree,
including one on a branch whose `.gitignore` predates the entry — look at each line, trimmed:

- `.agent/local` or `/.agent/local` → nothing to do in that file.
- `.agent/local/` or `/.agent/local/` → rewrite that line in place without the slash. A
  directory-only pattern does not match a symlink, so it stops working at step 3.
- Neither → append, creating the file and its folder if absent:

  ```
  # no trailing slash: also matches a symlink
  .agent/local
  ```

Touch no other line. Then `git check-ignore -q .agent/local` must succeed. If it does not — a
later negation such as `!.agent/local`, or the path already tracked — **stop**: report the cause
and do not link. A link that is not ignored is committed by the next `git add -A`.

**2. Find the shared target.**

```bash
C=$(git rev-parse --path-format=absolute --git-common-dir)
# git < 2.31 has no --path-format:  C=$(cd "$(git rev-parse --git-common-dir)" && pwd -P)
T="$C/agent-local"
```

**Absolute, always.** In the main checkout `--git-common-dir` prints a bare `.git`, and a link's
relative target resolves from the link's own folder — so `.git/agent-local` written into
`.agent/local` points at `.agent/.git/agent-local` and dangles. The common dir is shared by every
worktree of the repository, and nothing in it is committed.

**3. Act on what is at `.agent/local`** — looking at the path itself (`test -L` before `test -d`),
never following a link:

| Found | Do |
|---|---|
| Nothing | `mkdir -p "$T" .agent && ln -s "$T" .agent/local`, then confirm `test -L .agent/local`. If linking fails — Windows without symlink rights, or MSYS, whose `ln -s` copies — make or leave `.agent/local` a plain folder and say once that it is not shared |
| A link to an existing folder | Leave it, whatever it targets — someone chose that |
| A dangling link | Ask whether to repoint it: `mkdir -p "$T" && rm .agent/local && ln -s "$T" .agent/local`. No, or no one to answer → leave it; it is **broken** (BUS-CHECKS § *5b*) |
| An empty plain folder | `rmdir .agent/local`, link as for *nothing*, and say so in one line — nothing can be lost |
| A plain folder with files | **Ask first.** On yes: for every entry, dotfiles included, check `$T/<name>`; if any exists, **stop** and report both paths, moving nothing. Otherwise move each entry into `$T` with a plain `mv` — never a VCS move — then `rmdir .agent/local`, link, confirm `test -L`. On no, or no one to answer → leave it, and say once that it is not shared across worktrees |
| A regular file | **Broken**: report it and leave it untouched |

**Never follow a link elsewhere and reorganise what you find there.** A link pointed at some
other folder is its owner's arrangement; this procedure stops at the link.

**4. Report** each ignore line changed — per file, before and after — and the final state of
`.agent/local`: linked to `$T`, a plain folder and why, or left as found and why. A `.gitignore`
edit is a change to a committed file; report it and leave the commit to the user. A run that
changed nothing says so in one line.

## Restricted mode: when the caller must not change a committed file

A delivery run (`work on`) needs `.agent/local` before it reads a step's settings, but it must
never change scaffolding: an edit there would turn up in someone's feature branch. So it runs this
procedure in a restricted mode. Everything it does is uncommitted, and it never asks a question:

- **Step 1** — leave `.gitignore` alone. If its lines do not already ignore `.agent/local` (no
  slash), do not edit it: carry on, and say so once in step 4. Still write the entry to `$X`, which
  is uncommitted. Then `git check-ignore -q .agent/local` must succeed, or stop as step 1 says.
- **Step 3** — *nothing* and *an empty plain folder* are handled as above. A dangling link, or a
  plain folder that has files in it, is **left as found**: do not ask, and move nothing. A regular
  file is left alone too, as above.
- **Step 4** — when `.agent/local` is linked, or `.gitignore` was fine, say nothing. Otherwise
  print **one line** that says what was left as it is, that values stored in the shared folder are
  not read here (the defaults apply instead), and that the caller's re-scaffold command fixes it
  (`work init`, or the `delivery` row's `Re-scaffold` in `## Commands`). For example:
  *"`.agent/local` is a plain folder in this worktree, not the shared one — step settings use
  their defaults; run `work init` to share it."*

- **Under another VCS, or none** — change nothing at all. Its ignore file is committed, and there is
  no shared folder to link to. If `.agent/local` is missing or not ignored, print the one line.

The run carries on either way. Never stop a delivery run over this.

## Under another VCS, or none

Do step 1's ignore part with that system's mechanism, make `.agent/local` a plain folder, and say
once that it is not shared. Worktrees and a common dir are git's; guessing an equivalent is worse
than saying there is none.
