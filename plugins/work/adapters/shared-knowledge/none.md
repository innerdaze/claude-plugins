# `none` — no shared-memory service bound

## Capabilities

```markdown
## Capabilities
supports:    —
costly:      —
unsupported: gate()
```

## Behaviour

`gate(topic)` returns **empty**: nothing is known elsewhere about this topic, as far as this
project can tell.

This is the fallback most projects will run forever, and the seam ships with nothing else behind
it. That is deliberate rather than provisional — see [the adapters README](../README.md) on why a
`none` fallback is a real implementer.

## What the caller must do with that

**Proceed and record normally.** Wrap-up writes project memory without cross-checking, which is
exactly what it did before this seam existed.

**Say nothing.** A project that has never had shared memory does not need telling it has none.

**Never treat unreachable as unsupported.** A *bound* service that times out is a different
situation: note it once and carry on, because a wrap-up that failed on an unreachable knowledge
service would make that service a dependency for delivering a ticket. This fallback means "not
configured"; it must not become the place slow or broken bindings quietly land.
