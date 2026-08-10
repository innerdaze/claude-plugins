# Cadence config — <Project Name>

*Copy this into your project. **Location:** if you use a `domains/` doc system, put it at `domains/PROJECT.md`; otherwise `.claude/cadence/config.md`. Cadence's `/cadence init` writes this for you — this file documents the shape. Replace every `<...>` placeholder; **never commit real credentials or private workspace IDs to a public repo.***

```yaml
project:
  name: <Project Name>
  ticket_prefix: <PREFIX>          # e.g. ABC -> ABC-42

# --- Bindings: WHERE and WITH WHAT you work (resolved via adapters) ---

tracker:
  kind: <linear | github | jira | notion | markdown>
  mcp_namespace: <e.g. linear-uft>       # the exact MCP tool namespace for THIS project
  team_id: <id-or-omit>
  project_id: <id-or-omit>
  epic_convention: <label:"Epic" | native | parent>
  statuses: { todo: "<Todo>", doing: "<In Progress>", review: "<In Review>", done: "<Done>" }

vcs:
  kind: <git | diversion | jj | hg>
  checkpoint: <skill:/commit | commands>  # delegate to a commit skill, or run adapter commands
  gotchas: "<optional: project-specific VCS quirks>"

execution:
  skill: <e.g. /work-on | none>           # the project's own ticket-execution skill
  owns: [implement, test, docs, commit]   # what /session END must VERIFY, not repeat

doc_system:
  kind: <domains | docs | none>
  index: <e.g. domains/INDEX.md | omit>
  ticket_to_docs: "<rule, e.g. labels == domain names | omit>"

memory:
  location: <project-memory | path>
  format: markdown

# --- Models: WHICH tier does WHICH work (a third binding) ---

models:
  mechanical: haiku      # cheap tier: adapter file/CLI ops, scaffolding, collating packs
  reasoning:  inherit    # the session model handles judgment (breakdown, gate checks, goal selection)

# --- Methodology: HOW you work ---

flow: <solo-greenfield | team-sprints | live-oncall | ./cadence/my-flow.flow.md>

dod_gates: [tests, docs]                   # extend per project; feeds gate.dod in the flow
```

## Notes

- **Bindings vs flow.** Everything above `flow:` is *bindings* (toolchain + model tiers, resolved by adapters / subagents). `flow:` + `dod_gates:` select the *methodology*. Change bindings → different tools/models; change flow → different process.
- **Models are a binding, not an assumption.** Available models differ per user (not everyone has every tier; IDs differ on Bedrock/Vertex), so tiers are *config*, never hardcoded. `mechanical` names the cheap model Cadence delegates batchy mechanical work to (via the `mechanical` subagent); `reasoning: inherit` keeps judgment on the session model. Aliases (`haiku`/`sonnet`/`opus`) resolve to current versions automatically; rebind if you lack a tier or want a different cheap model. Delegation only pays off on *batchy* work — trivial one-off ops stay inline.
- **Private vs shared.** This example ships with placeholders. Your filled-in copy — with real IDs and namespaces — lives in *your* project repo, not in Cadence.

---

### Example: MachineGame54's filled-in config (lives in Lee's private repo, not shipped)

```yaml
project:   { name: MachineGame54, ticket_prefix: MACH }
tracker:   { kind: linear, mcp_namespace: linear-uft, epic_convention: label:"Epic" }
vcs:       { kind: diversion, checkpoint: skill:/commit, gotchas: "dv add new/untracked files first" }
execution: { skill: /work-on, owns: [domains, implement, test, docs, commit] }
doc_system:{ kind: domains, index: domains/INDEX.md, ticket_to_docs: "labels == domain names" }
memory:    { location: project-memory, format: markdown }
models:    { mechanical: haiku, reasoning: inherit }
flow:      solo-greenfield
dod_gates: [tests, docs, mp-safe, persistence]
```

*(Real Linear team/project GUIDs omitted here on purpose — they belong only in the private repo.)*
