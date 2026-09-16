# `none` — no roster

Every `resolve` returns **none**. Nothing is known about which plugin serves which role, and the
caller asks the user for every unregistered role it finds.

## Capabilities

```markdown
## Capabilities
supports:    roles()
costly:      —
unsupported: resolve()
```

## Behaviour

- **`resolve(role)`** → **none**, immediately. Not an error: an unregistered role becomes a
  question for the user, which is the same path a known-but-uninstalled role takes anyway.
- **`roles()`** → empty.

## What the caller must do with that

**Say it once, then carry on.** *"No roster bound; I will ask about any role I find unregistered."*
The guided upgrade still works — it asks for every role instead of some of them.

**Do not fall back to guessing from a name.** That a folder is called `domains/` does not make
`domains` its owner: a project may have renamed it, or served that role with something in-house.
Inferring the mapping from a path is the guess a roster exists to remove, and doing it under a
`none` binding would be worse than having no roster at all.

⚠️ **This binding is the correct state for a stack of unknown plugins — and also what a project
gets if its generated roster adapter was deleted.** Those look identical from here, which is why
a caller reports the binding it resolved rather than assuming one.
