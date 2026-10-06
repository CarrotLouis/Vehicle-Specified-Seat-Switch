"""Read-only PE evidence for the locally supplied Helldivers 2 game image.

No image loading, process access, game launch, or writes to the installation.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import math
import re
import struct

SOURCE = Path('F:/SteamLibrary/steamapps/common/Helldivers 2/data/game/game.dll')
OUT = Path(__file__).parent
b = SOURCE.read_bytes()
u16 = lambda o: struct.unpack_from('<H', b, o)[0]
u32 = lambda o: struct.unpack_from('<I', b, o)[0]
pe = u32(0x3c)
assert b[:2] == b'MZ' and b[pe:pe+4] == b'PE\0\0'
opt = pe + 24
assert u16(opt) == 0x20b
sections = []
for i in range(u16(pe+6)):
    p = opt + u16(pe+20) + 40*i
    name = b[p:p+8].split(b'\0')[0].decode('ascii', 'replace')
    vs, va, size, raw = struct.unpack_from('<IIII', b, p+8)
    sample = b[raw:raw+size]
    counts = Counter(sample)
    entropy = -sum((n/len(sample))*math.log2(n/len(sample)) for n in counts.values()) if sample else None
    sections.append({'name': name, 'virtual_size': hex(vs), 'rva': hex(va),
        'raw_size': hex(size), 'raw_offset': hex(raw), 'flags': hex(u32(p+36)),
        'entropy_bits_per_byte': round(entropy, 5) if entropy is not None else None})

def rva_offset(rva):
    for s in sections:
        va, size, raw = int(s['rva'], 16), int(s['raw_size'], 16), int(s['raw_offset'], 16)
        if va <= rva < va+size:
            return raw+rva-va
    raise ValueError(f'RVA {rva:x} has no file-backed section')

def zstr(o):
    return b[o:b.index(b'\0', o)].decode('ascii', 'replace')

exports = []
exp_rva = u32(opt+112)
if exp_rva:
    exp = rva_offset(exp_rva)
    names_n, names_rva = u32(exp+24), u32(exp+32)
    names = rva_offset(names_rva)
    assert names_n < 10000
    exports = [zstr(rva_offset(u32(names+i*4))) for i in range(names_n)]

keywords = re.compile(rb'vehicle|seat|passenger|occupant|SwitchSeat', re.I)
strings = re.findall(rb'[\x20-\x7e]{6,}', b)
hits = [s.decode('ascii') for s in strings if keywords.search(s)]
report = {
    'source': str(SOURCE), 'size': len(b), 'sha256': hashlib.sha256(b).hexdigest(),
    'machine': hex(u16(pe+4)), 'image_base': hex(struct.unpack_from('<Q', b, opt+24)[0]),
    'image_size': hex(u32(opt+56)), 'entry_point': hex(u32(opt+16)),
    'sections': sections, 'export_names': exports,
    'plaintext_vehicle_keyword_strings': hits,
    'scope': 'Static file inspection only. No process access or native image execution.',
}
(OUT/'pe_evidence.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k != 'sections'}, indent=2))
