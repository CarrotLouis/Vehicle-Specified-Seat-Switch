"""Find RIP-relative table references, including SIMD/immediate stores."""
import os, sys, struct, json
from pathlib import Path
W = Path(__file__).resolve().parent.parent
os.environ['VSS_CAPTURE'] = str(W / 'reverse/capture-25480438')
sys.path.insert(0, str(W))
from reverse import Module
m = Module()
hits = []
for align in range(4):
    data = m.code[align:len(m.code) - (len(m.code) - align) % 4]
    for i, (d,) in enumerate(struct.iter_unpack('<i', data)):
        p = m.base + align + 4 * i
        if not (0x31b0370 - 8 <= p + 4 + d < 0x31b03c0):
            continue
        for start in range(p - 6, p):
            ins = next(m.md.disasm(m.read(start, 15), start), None)
            if not ins or '[rip ' not in ins.op_str or not start <= p < start + ins.size:
                continue
            target = ins.address + ins.size + d
            if 0x31b0370 <= target < 0x31b03c0:
                hits.append(dict(address=hex(start), target=hex(target), instruction=ins.mnemonic+' '+ins.op_str,
                                 function=m.function(start)))
out = Path(__file__).resolve().parent / 'reservation-20260925/table-initializer-references.json'
out.write_text(json.dumps(hits, indent=2))
print(json.dumps(hits, indent=2))
