# Adapters — what `work` consumes

*`work` exposes one contract ([execution](../contracts/EXECUTION.md)) and consumes three. Each
consumed seam resolves the same way, and each ships a `none` fallback so a project that has
bound nothing still works.*

| Seam | Contract owned by | Shipped fallback | With the fallback, `work` |
|---|---|---|---|
| **doc-system** | the knowledge tool | [`doc-system/none.md`](doc-system/none.md) | plans from the ticket and the code, and declares `docs: unsupported` |
| **intent-read** | the intent tool | [`intent/none.md`](intent/none.md) | never checks a plan against stated design |
| **shared-knowledge** | the shared-memory service | [`shared-knowledge/none.md`](shared-knowledge/none.md) | records project memory without checking what is already known elsewhere |

**Resolution order:** project-local adapter → the shipped `none` fallback → never an error. A
missing binding is a normal project, not a broken one.

## A `none` fallback is a real implementer

It answers. "Not configured" is an answer, and a caller that receives it behaves correctly. That
is why a contract may ship before anything interesting implements it — the interesting
implementation arrives later as a project-local adapter, **with no version bump here**.

It is also why these are not *dead* seams. Dead means nothing answers; these answer.

## The rule that keeps this a seam

**`work` never learns which tool is behind a binding.** It calls the operations the contract
declares. A `kind` naming a specific product is *configuration*, resolved late from the bus, and
nothing in `work`'s procedures may branch on which one answered — a branch on the name is
awareness by another route, and awareness is what the cardinal rule forbids.
