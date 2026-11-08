#!/usr/bin/env python3
"""Read the shared config bus and print what is in it, as JSON.

**One spec, vendored by every plugin.** This file is the authority; each plugin
ships a byte-identical copy at `checks/bus_facts.py`. It is the executable half of
`BUS-CHECKS.md` — the mechanical checks only, which is every check that needs no
knowledge of any plugin's payload.

    python3 checks/bus_facts.py [--repo PATH]
    python3 checks/bus_facts.py --digest

`--digest` prints one hash over the shared rules this copy sits beside — the vendored
`BUS-CHECKS.md`, this script and `DOD-ANCHOR.md` — so two doctors can tell whether they
hold the same rules without reading each other's files (`BUS-CHECKS-OWN.md`).

Read-only. It never writes, never fetches, and never decides anything: it reports
what the file says and which frozen-core rules it breaks. Judgements that need an
owner's canonical version, or anyone's intent, are the caller's and stay the
caller's.

Exit status is 0 whenever the file could be read and parsed, findings or not — a
finding is data, not an error. Non-zero means this script could not do its job,
and the caller should fall back to reading the bus itself.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

CANONICAL = ".agent/PROJECT.md"
LEGACY = "domains/PROJECT.md"

# The frozen core, from BUS-CHECKS.md § "The frozen core is intact".
SHARED = ["Project", "Environment", "Version control", "Tracker", "Verification"]
ADDITIVE = ["Bindings", "Artifacts", "Versions", "Commands"]
FROZEN_COLUMNS = {
    "Artifacts": ["Artifact", "Path", "Owner"],
    "Versions": ["Component", "Version", "Owner"],
}

HEADING = re.compile(r"^##\s+(?P<name>[^<\n]+?)\s*(?:<!--\s*owner:\s*(?P<owner>[^>]*?)\s*-->)?\s*$")
MARKER = re.compile(r"<!--\s*manifest schema:\s*(?P<value>\d+)\s*-->")


def rows(lines, start):
    """Parse the markdown table that follows a heading. Returns (header, rows)."""
    table = []
    for raw in lines[start:]:
        line = raw.strip()
        if line.startswith("## "):
            break
        if line.startswith("|"):
            table.append([c.strip().strip("`") for c in line.strip("|").split("|")])
    if not table:
        return [], []
    header = table[0]
    body = [r for r in table[1:] if not all(set(c) <= set("-: ") for c in r)]
    return header, body


def read_bus(repo):
    canonical = os.path.join(repo, CANONICAL)
    legacy = os.path.join(repo, LEGACY)
    have_c, have_l = os.path.isfile(canonical), os.path.isfile(legacy)
    if have_c and have_l:
        return canonical, "dual"
    if have_c:
        return canonical, "canonical"
    if have_l:
        return legacy, "legacy"
    return None, "absent"


def analyse(repo):
    out = {"ok": True, "repo": os.path.abspath(repo), "findings": []}

    def finding(band, check, detail, owner=None, remedy=None):
        # `owner` and `remedy` are not decoration. A finding about another role's
        # rows travels with the rule that they are not yours to write — BUS-CHECKS
        # §3b and §4 — because a caller handed a problem and no constraint will
        # reach for the nearest fix, and the nearest fix is a cross-owner write.
        out["findings"].append({"band": band, "check": check, "detail": detail,
                                "owner": owner, "remedy": remedy})

    path, state = read_bus(repo)
    out["bus"] = {"path": None if path is None else os.path.relpath(path, repo), "state": state}

    if state == "absent":
        finding("broken", "bus-exists", "no config bus at .agent/PROJECT.md or domains/PROJECT.md",
                owner="shared",
                remedy="any role may create it, from the skeleton in BUS-CHECKS.md")
        return out
    if state == "dual":
        finding("broken", "bus-exists",
                "two buses: .agent/PROJECT.md and domains/PROJECT.md both exist",
                owner="shared",
                remedy="do not merge them; the delivery role's migrate command stops on this "
                       "state deliberately and offers the choices")
    if state == "legacy":
        finding("drifted", "bus-exists",
                "bus is at the legacy path domains/PROJECT.md",
                owner="delivery", remedy="the delivery role's migrate command moves it")

    text = open(path, encoding="utf-8", errors="replace").read()
    lines = text.splitlines()

    m = MARKER.search(text)
    out["schema_marker"] = int(m.group("value")) if m else None
    if not m:
        finding("drifted", "schema-marker", "no <!-- manifest schema: N --> marker")

    sections, seen = [], {}
    for i, raw in enumerate(lines):
        h = HEADING.match(raw)
        if not h:
            continue
        name = h.group("name").strip()
        owner = (h.group("owner") or "").strip() or None
        sections.append({"name": name, "owner": owner, "line": i + 1})
        seen[name] = owner
        if owner is None:
            finding("drifted", "owner-marker", "section '%s' has no owner marker" % name)
    out["sections"] = sections

    for name in SHARED:
        if name not in seen:
            finding("drifted", "frozen-core", "shared section '## %s' is absent" % name)
        elif seen[name] != "shared":
            finding("drifted", "frozen-core",
                    "shared section '## %s' is marked '%s', expected 'shared'" % (name, seen[name]))
    for name in ADDITIVE:
        if name not in seen:
            finding("drifted", "frozen-core", "additive table '## %s' is absent" % name)
        elif seen[name] != "shared, additive":
            finding("drifted", "frozen-core",
                    "additive table '## %s' is marked '%s', expected 'shared, additive'"
                    % (name, seen[name]))

    tables = {}
    for s in sections:
        header, body = rows(lines, s["line"])
        tables[s["name"]] = (header, body)
        want = FROZEN_COLUMNS.get(s["name"])
        if want and header and [c.lower() for c in header] != [c.lower() for c in want]:
            finding("broken", "frozen-shape",
                    "'## %s' columns are %s, frozen shape is %s" % (s["name"], header, want))

    def table(name, keys):
        header, body = tables.get(name, ([], []))
        return [dict(zip(keys, r + [""] * (len(keys) - len(r)))) for r in body]

    out["artifacts"] = table("Artifacts", ["artifact", "path", "owner"])
    out["versions"] = table("Versions", ["component", "version", "owner"])
    out["commands"] = table("Commands", ["role", "migrate", "re_scaffold", "doctor"])
    out["bindings"] = table("Bindings", ["seam", "kind"])

    for a in out["artifacts"]:
        target = a.get("path") or ""
        a["exists"] = bool(target) and target.lower() != "none" and os.path.exists(
            os.path.join(repo, target))
        if target and target.lower() != "none" and not a["exists"]:
            finding("drifted", "artifact-resolves",
                    "artifact '%s' owned by %s points at '%s', which does not exist"
                    % (a.get("artifact"), a.get("owner"), target),
                    owner=a.get("owner"),
                    remedy="report it; the row is its owner's to fix. Do not go looking for a "
                           "replacement path and do not delete the row")

    versioned = {v.get("owner") for v in out["versions"]}
    for a in out["artifacts"]:
        owner = a.get("owner")
        if owner and owner not in versioned and a.get("exists"):
            finding("drifted", "unregistered-component",
                    "role '%s' owns '%s' but has no ## Versions row" % (owner, a.get("path")),
                    owner=owner,
                    remedy="that role's own init registers and stamps it. **Never write another "
                           "role's rows**, and do not name a command for it - with no ## Commands "
                           "row there is nothing to read and guessing one is the error the table "
                           "exists to prevent")
    out["unregistered_roles"] = sorted({
        a["owner"] for a in out["artifacts"]
        if a.get("owner") and a["owner"] not in versioned and a.get("exists")})

    return out


# The files the digest covers, in order: (name in a plugin's checks/, name in the
# authority's references/). Content only, so the authority and an in-sync copy hash
# the same.
DIGEST_FILES = (
    ("BUS-CHECKS.md", "bus-checks.md"),
    ("bus_facts.py", "bus_facts.py"),
    ("DOD-ANCHOR.md", "dod-anchor.md"),
)


def digest(here=None):
    """One hash over the shared rules beside this script. Raises when one is missing:
    a caller that cannot compare must run the shared checks in full."""
    here = here or os.path.dirname(os.path.abspath(__file__))
    h = hashlib.sha256()
    for vendored, authority in DIGEST_FILES:
        path = next((p for p in (os.path.join(here, vendored), os.path.join(here, authority))
                     if os.path.isfile(p)), None)
        if path is None:
            raise FileNotFoundError("%s not found beside %s" % (vendored, here))
        with open(path, "rb") as fh:
            body = fh.read()
        h.update(b"%d\n" % len(body))
        h.update(body)
    return h.hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", default=".", help="repository root (default: cwd)")
    ap.add_argument("--digest", action="store_true",
                    help="print a hash of the vendored shared rules and exit")
    a = ap.parse_args()
    if a.digest:
        try:
            print(digest())
        except OSError as exc:
            print("cannot digest: %s" % exc, file=sys.stderr)
            return 2
        return 0
    try:
        print(json.dumps(analyse(a.repo), indent=2))
    except Exception as exc:                                  # noqa: BLE001
        print(json.dumps({"ok": False, "error": "%s: %s" % (type(exc).__name__, exc)}, indent=2))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
