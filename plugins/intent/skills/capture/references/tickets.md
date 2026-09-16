# Filing gap tickets

The register is only as good as the work it produces. This is the last phase, and
it's where an unfamiliar tracker eats time if you go in blind.

## Decide what earns a ticket

- **Group gaps that are one coherent change.** Two blockers that must land together
  are one ticket; splitting them leaves a half-migrated system between merges.
- **Note dependencies explicitly** — "depends on X, do that first" — including gaps
  that resolve *for free* once another lands. Those don't need their own ticket;
  say so in the one that fixes them.
- **Don't ticket doc chores you can just do.** Adding a pointer to `CLAUDE.md` is a
  two-minute edit, not backlog.
- **Don't ticket candidate refactors nobody agreed to.** If the register notes a
  possible improvement rather than a contradiction, leave it in the register and
  say why it has no ticket.

## Discover the tracker's conventions before creating anything

Guessing required fields wastes several failed round-trips, and guessing the
*project* can file work into the wrong team's backlog.

1. **Find prior art.** Search the tracker for the project's own name. Existing
   tickets tell you which project key is used, the issue type, and how fields were
   filled — precedent beats inference.
2. **Watch for a project split.** Many orgs route app work and infra work to
   different boards (and different teams). If the repo's history references two
   prefixes, that's usually deliberate, not a misconfiguration. Ask before deciding
   it's wrong — and file infra requests where the team that does the work looks.
3. **Fetch required-field metadata** if the tracker exposes it, and copy values from
   a comparable existing ticket rather than picking from the allowed list on vibes.
   Custom required fields (team, area, component) are common and rarely guessable.
4. **Expect iteration.** Trackers often surface one missing required field at a
   time. Fix and retry rather than assuming the whole call was wrong.

## Write the ticket so it survives without you

The register row is a pointer; the ticket has to stand alone six months later:

- **What the intent is**, with the `intent/` doc named so the *why* is one click away.
- **What the code actually does**, specifically — file, symbol, the contradicting
  comment. Quote it.
- **Scope** as a checklist of the actual changes.
- **Acceptance** in terms someone else could verify.
- **Follow-on / depends-on**, naming the other ticket keys.

Include the counter-intuitive consequences you uncovered. A ticket saying "this
also removes the volume mount and the node-pinning, which only exist because of
this bug" saves the next person the investigation you already did.

## Close the loop

Put the ticket keys back into `alignment.md` — a small table mapping gaps to
tickets, and each row's status updated to reference its ticket. Without that, the
register and the backlog drift apart within a week and the register becomes a
historical curiosity.

Note explicitly which gaps have *no* ticket and why. A register where some rows are
tracked and others silently aren't is worse than one where the distinction is
stated.
