"""Bounded static ownership callback research against immutable captures.

This never opens a process, changes a game file, or executes game code.
"""
from pathlib import Path
import json
import re
import struct
import sys

R = Path(__file__).resolve().parent
W = R.parent
sys.path.insert(0, str(W))
from reverse import Module

O = R / "native-return"
O.mkdir(exist_ok=True)
root = W / "reverse/capture-25480438"
m = Module("game.dll", root)
h = (root / "game.dll.headers.bin").read_bytes()
pe = struct.unpack_from("<I", h, 0x3C)[0]
image_base = struct.unpack_from("<Q", h, pe + 24 + 24)[0]
targets = [0x53DE90, 0x53DF40, 0x53E020, 0x53E0B0, 0x53E0F0,
           0x53E100, 0x71B060, 0x71B410]

report = {"capture": root.name, "image_base": hex(image_base), "callbacks": {}}
for a in targets:
    f = m.function(a)
    # The two tail-call wrappers do not have their own unwind entries.
    size = min(f[1] - a, 0x1000) if f else 0x20
    (O / f"game-{a:x}.txt").write_text(m.dis(a, size) + "\n", encoding="utf-8")
    refs = []
    for base, data in m.sections[1:]:
        for hit in re.finditer(re.escape(struct.pack("<Q", image_base + a)), data):
            at = base + hit.start()
            if at % 8 == 0:
                refs.append({"at": hex(at), "neighbors": [hex(v - image_base)
                             if image_base <= v < image_base + 0x4000000 else hex(v)
                             for v in struct.unpack("<9Q", m.read(at - 32, 72))]})
    report["callbacks"][hex(a)] = {
        "function": [hex(x) for x in f] if f else None,
        "callers": m.callers([a]),
        "rip_references": [[hex(p), hex(t), [hex(x) for x in fn] if fn else None]
                           for p, t, fn in m.xrefs([a])],
        "pointer_references": refs,
    }
(O / "vehicle-callback-registration.json").write_text(
    json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
