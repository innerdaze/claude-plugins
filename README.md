# claude-plugins

A small marketplace of Claude Code / Cowork plugins.

## Plugins

### [Cadence](./cadence) — a configurable project-management methodology

Gives an AI-assisted project a spine: vision → roadmap → epics → tickets → gates, worked in bounded **sessions** that each have one concrete goal. It carries the *method* and binds to *your* tools (adapters), *your* models (tiers), and *your* team's process (a flow spec) — assuming an environment for none of them. Ships with three preset flows (`solo-greenfield`, `team-sprints`, `live-oncall`), a zero-dependency fallback stack, and a hook API for authoring your own. See [`cadence/README.md`](./cadence/README.md).

## Using this marketplace

Add it in Claude Code, then install a plugin from it:

```
/plugin marketplace add <this-repo-url-or-path>
/plugin install cadence@claude-plugins
```

(Exact commands depend on your Claude Code version — see the plugins docs.)
