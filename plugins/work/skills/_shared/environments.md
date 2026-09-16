# Environment profiles

A starting point for `work init` Step 1 (detect the environment) and for choosing
sensible default domain topics and verification commands. **This is scaffolding,
not gospel.** Always refine against what the repo actually contains — a "React"
repo might be a Next.js app, an Nx monorepo, or a Vite SPA, and each has different
real topics. When the project doesn't match any row, reason from first principles:
what are this codebase's major subsystems, how is it built, how is it tested?

## Detection signals

Read the project root (and one level down for monorepos) and match on files. Prefer
the **most specific** signal; a repo can match several, so rank by specificity and
confirm the precise label + version with the user.

| Environment | Tell-tale files | How to pin the version |
|---|---|---|
| React / web frontend | `package.json` with `react`/`next`/`vue`/`svelte` dep | the dep's version in `package.json` / lockfile |
| Node service | `package.json` without a frontend framework; `server`/`api` dirs | `engines.node`, framework dep (express/fastify/nest) |
| Nx / Turborepo / pnpm / Yarn / Lerna monorepo | `nx.json` / `turbo.json` / `pnpm-workspace.yaml` / `lerna.json` / `package.json` `workspaces` | enumerate every workspace member from the root config (expand globs); each project becomes a deep-inspection line — never sample or eyeball directories |
| Python | `pyproject.toml`, `requirements.txt`, `setup.py`, `manage.py` | `python_requires`; framework (django/fastapi/flask) |
| Go | `go.mod` | `go` directive in `go.mod` |
| Rust | `Cargo.toml` | `edition`; workspace members |
| Other / unknown | none of the above match cleanly | ask the user to name the stack |

If several frameworks coexist (e.g. a monorepo with a React app and a Node API),
say so and let the major subsystems each become a domain topic.


## Verification — how "done" is proven (goes into PROJECT.md)

`work on` runs these before declaring a step complete; pick the ones the repo
actually supports (check `package.json` scripts, Makefile, CI config).

| Environment | Typical verification |
|---|---|
| React / Node | `npm test` / `yarn test` / `vitest`, `npm run build`, type-check (`tsc --noEmit`), lint |
| Python | `pytest`, `mypy`/`ruff`, the relevant `manage.py`/CLI command |
| Go | `go build ./...`, `go test ./...`, `go vet` |
| Rust | `cargo build`, `cargo test`, `cargo clippy` |

## Version control — detection

| Signal | VCS | Commit workflow notes |
|---|---|---|
| `.git/` | git | use `git`; defer to a `/commit` skill if the project has one |
| `.diversion/` or a `dv` workflow noted in CLAUDE.md | Diversion | use `dv`, **never** git; commits go through `/commit` |
| `.hg/` | Mercurial | `hg` |
| `.svn/` | Subversion | `svn` |
| none | none | note it; `work on` will skip the commit step and just leave the diff |

## Ticket trackers — detection

Detect from (a) MCP servers loaded in the session, (b) repo hints, then **confirm with the
user** and record `Kind`, `Access` and `Prefix` in the bus's `## Tracker`.

| Tracker | Detect via | `Access` |
|---|---|---|
| Linear | a `*linear*` MCP server is loaded | that MCP namespace, e.g. `mcp__linear-uft` |
| Jira | a Jira MCP server, or `.jira`/Atlassian config | the Jira MCP namespace, else the `jira`/`acli` CLI |
| GitHub Issues | `.github/`, a GitHub remote | `gh` |
| GitLab Issues | `.gitlab-ci.yml`, a GitLab remote | `glab` |
| Notion | a Notion MCP server | the Notion MCP namespace |
| none | nothing tracks tickets | — (omit the row) |

**How `work on` drives each one is not recorded in the bus.** It is in `tracker-ops.md`, by
`Kind`. The bus says which tracker and how it is reached; the plugin knows the rest.
