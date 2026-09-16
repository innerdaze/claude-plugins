# Hook: `gate.citations.check` — "every claim cited"

*Authored gate for the `manuscript` flow. Implements the `gate.<name>.check` contract from the plugin's `flows/HOOKS.md`. Approver: `ai-proposes` — recommend, let the author accept.*

**Input** (provided by `/cadence:session` at the `Supported -> Reviewed` transition): `{item, context, checks}`.
`item` is a claim, or a section (a set of claims). `checks` is `[every-claim-cited]`.

**Do:** for each claim under `item`, verify that
1. at least one source is recorded, and
2. the source actually *supports* the claim (not merely adjacent to the topic), and
3. if sources conflict, the claim acknowledges the contest.

Flag: uncited claims; claims resting on a single weak source; claims that overstate what their source shows.

**Output:** `{result, notes}` —
- `result`: `pass` (all claims adequately supported), `fail` (list the offending claims in `notes`), or `needs-human` (a sourcing judgment the author should make),
- `notes`: the specific claims and what's missing.

Because this gate is `ai-proposes`, a `fail`/`needs-human` result **keeps the item in `Supported`** and surfaces the list to the author — it never advances or blocks silently.
