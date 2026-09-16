# `none` — no intent layer registered

## Capabilities

```markdown
## Capabilities
supports:    —
costly:      —
unsupported: locate(), check()
```

## Behaviour

Both operations return **empty**. No intent layer is registered in the config bus's
`## Artifacts` under owner role `intent-layer`, so there is nothing to read.

## What the caller must do with that

**Nothing, and say nothing.** Unlike a missing knowledge system, this needs no message: most
projects have no intent layer, and announcing its absence every run would be noise.

The Planner's `## Intent conflicts` section reads *"none — this project has no intent layer"*,
which is where the fact belongs: in the artifact a human is already reading.

**Do not go looking.** A folder that looks like design documentation is not a registered intent
layer, and treating it as one would mean guessing at another tool's artifact path — the coupling
the registry exists to remove. An unregistered layer is invisible **by design**, and it becomes
visible when its owner runs and registers it.

**An empty result is not an endorsement.** With this binding, nothing has been checked. Never
report "no conflicts with stated intent" — there was nothing to conflict with, and the two read
identically to anyone downstream.
