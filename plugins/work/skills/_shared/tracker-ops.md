# Tracker operations — how `work on` drives each tracker

**This file is the adapter.** The bus's `## Tracker` says *which* tracker (`Kind`) and *how it
is reached* (`Access` — an MCP namespace or a CLI); this file says how to drive it. `work on`
reads it only when `Kind` is not `none`. Nothing here is ever written into the bus: the bus
holds facts a tool reads, and how a tool behaves is that tool's own step.

`<NS>` is the `Access` namespace. `<ID>` is the normalised ticket id.

| Op | Linear (MCP) | GitHub (`gh`) | GitLab (`glab`) |
|---|---|---|---|
| Fetch a ticket | `<NS>__get_issue id:"<ID>"` | `gh issue view <ID>` | `glab issue view <ID>` |
| Read comments | `<NS>__list_comments` | `gh issue view <ID> --comments` | `glab issue view <ID> --comments` |
| Post a comment | `<NS>__save_comment` | `gh issue comment <ID> --body …` | `glab issue note <ID> -m …` |
| Change status / close | `<NS>__save_issue id state` | `gh issue close <ID>` · `gh issue edit <ID> --add-label …` | `glab issue close <ID>` · `glab issue update <ID> --label …` |
| File a follow-up | `<NS>__save_issue` | `gh issue create` | `glab issue create` |

| Op | Jira | Notion |
|---|---|---|
| Fetch a ticket | the loaded Jira tools' *get issue* under `<NS>`, else `jira issue view <ID>` / `acli` | fetch the page by id from the configured database |
| Read comments | the same call with comments, else `jira issue view <ID> --comments` | the page's comments |
| Post a comment | the Jira tools' *add comment*, else `jira issue comment add <ID> …` | add a comment to the page |
| Change status / close | the Jira tools' *transition*, else `jira issue move <ID> <state>` | set the status property |
| File a follow-up | the Jira tools' *create issue*, else `jira issue create` | create a page in the database |

Jira and Notion MCP servers name their tools differently; match on what the loaded server
under `<NS>` offers rather than on a name written here.

**`Kind: none`** — describe-the-task-inline: the user states the task, and every fetch, comment
and status step is skipped.

**A `Kind` this file does not list** — ask the user once how to fetch, comment and set status, and
use the answer for this run. If the project wants it kept, it is knowledge about the tracker: a
`domains/` topic, loaded when relevant. It does not go in the bus.
