# `intent` — the design layer that outranks the code

Most architecture docs are written by reading the implementation. That makes them a second,
staler copy of something already true — and it means the code can never be *wrong*, only
undocumented.

This plugin produces the opposite artifact: an `intent/` folder holding what the maintainer says
the system is **for**, with the code given no vote. When the two disagree, **the doc stands** and
the contradiction becomes tracked work.

## Skills

| Command | Does |
|---|---|
| `/intent:capture` | Interview or structure dictated intent into `intent/`, and open an alignment register for the gaps |

## What it owns

`intent/**` — the documents, the index, and the alignment register — plus the `intent-layer` rows
in the config bus (`.agent/PROJECT.md`).

`CLAUDE.md` belongs to the project; this plugin only adds a pointer to it, insert-if-absent.

## The contract, and the operation it deliberately lacks

- [`contracts/INTENT-READ.md`](contracts/INTENT-READ.md) — `locate` (which stated intent applies
  here) and `check` (what a plan contradicts). `check` reports contradictions and **never returns
  a verdict**: adjudicating intent belongs to the human at an approval gate, and a contract
  returning judgements would relocate that decision into whichever tool called it.
- [`adapters/markdown.md`](adapters/markdown.md) — the shipped fallback: the folder as files.

**There is no write operation, at any tier.** The layer's first rule is that the code gets no
vote; a contract that let a tool write here would let the implementation edit the thing it is
measured against, at exactly the moment it was found to disagree. That absence is a guarantee,
not a gap.

## If it is absent

A repo's `intent/` folder is Markdown that a human reads regardless. A tool wanting the contract
gets no binding and **says nothing** — most projects have no intent layer, and announcing that
every run is noise. Nothing hard-fails because this is missing.
