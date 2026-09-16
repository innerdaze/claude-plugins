# The intent-read contract

*What a tool may ask an intent layer. Read-only, at every tier, forever — see the last section
for why that is a design rule and not an oversight.*

**Contract version: 1.** A new optional field is minor. Changing what an operation means, or
adding a write, is breaking — and the write would be refused rather than versioned.

## Two operations

### `locate(topics, paths?) → ranked statements`

**Which stated intent applies here.** Deliberately the same shape as the doc-system contract:
a caller doing one job — *what applies to what I am about to touch* — should not learn two
signatures, and a caller typically holds both bindings at once.

What differs is **standing, not shape**: intent outranks learned knowledge and outranks the code,
so a caller holding both answers knows which gives way. That ordering is the layer's whole
purpose; the contract just makes it reachable.

Each statement carries `topic`, `title`, `digest`, the `document` it came from, and `body` when
expanded. An empty result means nothing stated applies here.

### `check(plan) → contradictions`

**Does this specific plan contradict anything stated.** Each contradiction names the
**statement**, the **part of the plan** that collides with it, and **why**.

**It never returns a verdict, a score, or a fix.** Not "reject", not "risk: high", not "change X
to Y". The reason is structural rather than stylistic: adjudicating intent belongs to the human
at the approval gate, and a contract that returned judgements would relocate that decision into
whichever tool called it — which is the same mistake as letting the caller adjudicate, wearing a
different hat.

⚠️ **An empty result is not an endorsement.** It means nothing was detected. A caller that
reports it as "no conflicts with stated intent" has invented a guarantee that nothing offered —
and the two are indistinguishable to whoever reads that line.

`check` is a **convenience, not a gate.** A caller may do the same comparison from `locate`
alone; this exists because the layer knows its own statements better than a caller does.

## Capability declaration

```markdown
## Capabilities
supports:    locate(topics), locate(paths)
costly:      —
unsupported: check()
```

### The floor

| Operation | May be |
|---|---|
| `locate` | **required** — a layer that cannot say what applies is not answering its only question |
| `check` | `unsupported` — holding statements without comparing them is legitimate; the caller falls back to `locate` |

## There is no write operation, at any tier

Not `record`, not `annotate`, not "log that a contradiction was hit".

The intent layer's first rule is that **the code gets no vote**. A contract that let a tool write
here would let the implementation edit the thing it is measured against — quietly, at the moment
it was found to disagree, which is exactly when the record matters most.

So a contradiction is reported *outward* and resolved by a person. The alignment register is
written by the capture workflow with a human present, and never by whatever hit the gap.

`[note]` This is the one contract in the ecosystem where an absent operation is a **guarantee**
rather than a limitation. Adding a write later would not be a minor version; it would be a
different contract.
