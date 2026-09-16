# claude-plugins

A Claude Code plugin marketplace: five plugins that interoperate as one stack,
or work on their own.

```
/plugin marketplace add innerdaze/claude-plugins
/plugin install cadence@innerdaze
```

Nothing else is needed — no registry, no token. The marketplace serves each
plugin straight out of this repository.

## Plugins

| plugin | what it does |
| --- | --- |
| [**hub**](./plugins/hub) | The stack's front door: what is installed, what is out of date, one guided upgrade across every owner, and one report from every doctor. |
| [**cadence**](./plugins/cadence) | A configurable project-management methodology — vision → roadmap → epics → tickets → gates, worked in bounded sessions, bound to *your* tracker, VCS and process rather than assuming any. |
| [**domains**](./plugins/domains) | Project memory: per-topic knowledge files a repo authors about itself, plus the manifest that says which ones a given task should load. |
| [**work**](./plugins/work) | Ticket delivery: `work on <TICKET>` takes a tracked ticket end to end via subagent orchestration, in whatever environment it finds. |
| [**intent**](./plugins/intent) | The design layer that outranks the code: what the maintainer says the system is *for*, dictated rather than inferred, with every contradiction logged as a tracked gap. |

Each has its own README. Once installed, a plugin's commands are namespaced
under it — `/cadence:init`, `/work:on`, `/hub:status`, and so on.

To try it from a local clone instead:

```
/plugin marketplace add /path/to/claude-plugins
```

## Licence

Apache-2.0. See [LICENSE](./LICENSE).
