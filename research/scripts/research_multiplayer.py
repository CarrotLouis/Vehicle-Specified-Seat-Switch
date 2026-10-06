"""Offline protocol inventory from the EXISTING build-25327279 capture only."""
from pathlib import Path
import json, struct, sys
sys.path.insert(0, str(Path(__file__).parent))
from reverse import Module

out = Path(__file__).parent / 'multiplayer-research'
out.mkdir(exist_ok=True)
mod = Module()
report = {}
for name, value in [('seated_snapshot', 0xd4f97316), ('seat_transition', 0xdcc32107)]:
    hits = []
    pat = struct.pack('<I', value)
    for base, data in mod.sections:
        start = 0
        while (pos := data.find(pat, start)) >= 0:
            rva = base + pos
            fn = mod.function(rva)
            hits.append({'rva': hex(rva), 'function': hex(fn[0]) if fn else None})
            if fn:
                (out / f'{name}_{fn[0]:x}.txt').write_text(mod.dis(fn[0]), encoding='utf-8')
            start = pos + 4
    report[name] = hits
report['callers'] = mod.callers([0x63eb10, 0x63ecc0, 0x637360, 0xbeb980, 0xbe22b0, 0xbf12e0])
(out / 'protocol-inventory.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
for label, rva in [('transition_receive', 0x63ecc0), ('seated_receive', 0x63eb10), ('request_packet', 0xbeb980), ('accepted_packet', 0xbe22b0), ('transition_packet', 0xbf12e0)]:
    (out / (label + '.txt')).write_text(mod.dis(rva), encoding='utf-8')
print(json.dumps(report, indent=2))
