# Resolving `## Verification → Definition of Done`

**One rule, vendored by every plugin.** This file is the authority; each plugin ships a
byte-identical copy at `checks/DOD-ANCHOR.md`, for the reason `checks/BUS-CHECKS.md` is vendored: no
plugin may read another's install path. The validator compares the copies and fails on any
difference.

**Read it whenever you resolve the row** — the delivery skill before planning, the methodology gate
before judging, a doctor checking the row, a writer before it writes one. It is kept out of
`checks/BUS-CHECKS.md` so a consumer reads this rule and not the whole spec.

## The rule

The row's value is a path, or `path#heading`.

1. Strip one pair of surrounding backticks from the value, and split at the first `#`.
2. No `#` → the bar is the **whole file**.
3. Otherwise look in the file for a Markdown heading **outside fenced code** whose text equals the
   part after `#` **exactly**, or whose GitHub-style slug does (lower-case, spaces to `-`,
   punctuation other than `-` and `_` dropped — `Definition of Done` ⇄ `definition-of-done`).
   Exact text is tried first; the slug form is accepted because it is what editors and renderers
   generate, and a slug that silently failed to resolve is how this rule was found.
4. The section runs to the next heading of the same level.

**Writers write the exact text** and resolve it before writing; the slug form is for rows written
by hand.

## When it does not resolve

**File missing, no heading matches, or more than one heading matches** → the row is **broken**.
Say which: a document that has moved, a heading renamed or only ever inside a template's code
fence, or an ambiguous anchor (name every match), and for a near miss the heading that was meant.

**Every consumer stops on it**: the delivery skill before planning, the methodology gate before
judging. A row naming a bar nobody can find is not a project without a bar — it is one whose bar is
lost — so **no consumer falls back**: not to the whole file (a bar quietly widened to an entire
process document) and not to check names alone (a bar quietly lowered to the words). Both are the
silent degradation this form exists to prevent.

Remedy: a hand edit of the row, or the `delivery` or `methodology` role's re-scaffold command, which
re-asks for it.
