"""Offline code-only search for exact static M102 preference-table references."""
from pathlib import Path
import sys, struct, re, json
R = Path(__file__).resolve().parent
sys.path.insert(0, str(R.parent))
from reverse import Module
m = Module('game.dll', R.parent / 'reverse/capture-25480438')
rows, seen = [], set()
for match in re.finditer(rb'[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]', m.code):
    p = match.start()
    if p + 5 > len(m.code): continue
    displacement = struct.unpack_from('<i', m.code, p + 1)[0]
    for extra in (0, 1, 4):
        target = m.base + p + 5 + extra + displacement
        if not 0x31b0370 <= target < 0x31b03c0: continue
        for back in range(1, 5):
            start = m.base + p - back
            if start in seen: continue
            instructions = list(m.md.disasm(m.read(start, 16), start, count=1))
            if not instructions: continue
            i = instructions[0]
            if '[rip' in i.op_str and i.address + i.size == m.base + p + 5 + extra:
                seen.add(start)
                f = m.function(start)
                rows.append({'at': hex(start), 'target': hex(target), 'instruction': i.mnemonic + ' ' + i.op_str,
                             'function': [hex(x) for x in f] if f else None})
(R / 'native-nonowner/static-table-xrefs.json').write_text(json.dumps(rows, indent=2))
print(json.dumps(rows))
