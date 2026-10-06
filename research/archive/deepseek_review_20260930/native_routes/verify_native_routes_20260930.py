#!/usr/bin/env python3
"""Read-only verifier for the six-vehicle native seat-adjacency arrays.

Parses only the given log file and an expected-seat-count table. It does NOT scan memory,
send messages, or touch the game / Arsenal / any configuration.

Facts taken from the main project (cited, not re-derived):
  * work/seat_switch/src/profile.lua   -> tables: row (bytes per seat row) and roles (seat count)
  * work/seat_switch/src/snapshot.lua  -> L122 reads row * seat_count bytes;
                                          L125 iterates row/4 four-byte entries;
                                          L127 the FIRST -1 terminates the row (break);
                                          L128 every target must satisfy 0 <= t < seat_count;
                                          L131 every row must be terminated, i.e. contain a -1
  * work/seat_switch/src/entry.lua     -> L43 logs "seat_adjacency <name> <comma values>"
"""
import json
import os
import sys

LOG = r"E:\Document\codex\2026-09-21\https-github-com-cowboybingus-bingussharedloader-https\work\seat_weapon_clear_diagnostic\capture-20260930-0101\VehicleSeatSwitch.log"

# profile.lua tables: name -> (row bytes, seat count = len(roles))
#   m102 row=8 roles=5 | m103 row=8 roles=4 | m104 row=8 roles=3
#   bastion row=12 roles=4 | maelstrom row=12 roles=4 | tanker row=8 roles=2
EXPECTED = {
    "m102":      {"row": 8,  "seats": 5},
    "m103":      {"row": 8,  "seats": 4},
    "m104":      {"row": 8,  "seats": 3},
    "bastion":   {"row": 12, "seats": 4},
    "maelstrom": {"row": 12, "seats": 4},
    "tanker":    {"row": 8,  "seats": 2},
}


def parse(path):
    out = {}
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if "seat_adjacency" not in line:
                continue
            tail = line.split("seat_adjacency", 1)[1].strip()
            name, _, values = tail.partition(" ")
            out[name] = [int(v) for v in values.split(",") if v != ""]
    return out


def build(name, raw):
    meta = EXPECTED[name]
    per_row = meta["row"] // 4
    want = per_row * meta["seats"]
    problems = []
    if len(raw) != want:
        problems.append(f"length {len(raw)} != seats*per_row {want}")
    rows, edges = [], []
    for node in range(meta["seats"]):
        chunk = raw[node * per_row:(node + 1) * per_row]
        neighbours, terminated = [], False
        for value in chunk:
            if value == -1:            # snapshot.lua L127: first -1 ends the row
                terminated = True
                break
            if not (0 <= value < meta["seats"]):
                problems.append(f"seat {node}: target {value} out of bounds")
                continue
            neighbours.append(value)
        if not terminated:
            problems.append(f"seat {node}: row not terminated by -1 (snapshot.lua L131)")
        rows.append(neighbours)
        edges.extend((node, t) for t in neighbours)
    return rows, edges, problems


def components(seats, edges):
    adj = {n: set() for n in range(seats)}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)          # undirected view for connectivity only
    seen, comps = set(), []
    for n in range(seats):
        if n in seen:
            continue
        stack, comp = [n], []
        seen.add(n)
        while stack:
            cur = stack.pop()
            comp.append(cur)
            for nxt in adj[cur]:
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        comps.append(sorted(comp))
    return comps


def main():
    if not os.path.isfile(LOG):
        print("log not found:", LOG)
        return 1
    found = parse(LOG)
    missing = [n for n in EXPECTED if n not in found]
    result = {"log": LOG, "vehicles": {}, "missing_from_log": missing, "ok": True}
    for name in sorted(EXPECTED):
        if name not in found:
            continue
        rows, edges, problems = build(name, found[name])
        comps = components(EXPECTED[name]["seats"], edges)
        indirect = []
        for comp in comps:
            direct = {(a, b) for a, b in edges if a in comp and b in comp}
            for a in comp:
                for b in comp:
                    if a != b and (a, b) not in direct:
                        indirect.append([a, b])
        result["vehicles"][name] = {
            "raw": found[name],
            "edges_direct": [[a, b] for a, b in edges],
            "components": comps,
            "reachable_only_via_intermediate": indirect,
            "problems": problems,
        }
        if problems:
            result["ok"] = False
        print(f"{name}: seats={EXPECTED[name]['seats']} rows={rows}")
        print(f"   direct edges (0-based, directed): {edges}")
        print(f"   components: {comps}   indirect-only: {indirect}")
        if problems:
            print(f"   PROBLEMS: {problems}")
    print("\nOK" if result["ok"] and not missing else "\nCHECK FAILED")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_native_routes_20260930.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)
    print("wrote", out)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
