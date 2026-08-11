# claude-plugins

A small marketplace of Claude Code / Cowork plugins.

## Plugins

### [Cadence](./cadence) — a configurable project-management methodology

Gives an AI-assisted project a spine: vision → roadmap → epics → tickets → gates, worked in bounded **sessions** that each have one concrete goal. It carries the *method* and binds to *your* tools (adapters), *your* models (tiers), and *your* team's process (a flow spec) — assuming an environment for none of them. Ships with three preset flows (`solo-greenfield`, `team-sprints`, `live-oncall`), a zero-dependency fallback stack, and a hook API for authoring your own. See [`cadence/README.md`](./cadence/README.md).

## Using this marketplace

Add it in Claude Code, then install a plugin from it:

```
/plugin marketplace add innerdaze/claude-plugins
/plugin install cadence@innerdaze
```

Or, to try it from a local clone without going through GitHub:

```
/plugin marketplace add /path/to/claude-plugins
/plugin install cadence@innerdaze
```

`innerdaze` is the marketplace name declared in `.claude-plugin/marketplace.json` — note that it differs from the repository name, because Claude Code rejects marketplace names containing "claude" or "anthropic" as impersonating an official source. `cadence` is the plugin. Once installed, Cadence's commands are namespaced under the plugin: `/cadence:init`, `/cadence:session start|end`, `/cadence:plan`, `/cadence:roadmap`, `/cadence:doctor`.

(Exact commands depend on your Claude Code version — see the plugins docs.)
