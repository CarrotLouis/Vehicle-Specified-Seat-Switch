"""Offline native reservation exploration; never attaches to the game."""
from pathlib import Path
import sys, struct, json, os
R = Path(__file__).resolve().parent
sys.path.insert(0, str(R.parent))
from reverse import Module
from emulate_seats import StaticVM
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *

m = Module('game.dll', R.parent / 'reverse' / 'capture-25480438')
out = R / 'native-nonowner'
out.mkdir(exist_ok=True)
targets = {'reserve_target': (0x636a30, 0x636d67),
           'reserve': (0x6344d0, 0x63487c),
           'release': (0x6349b0, 0x634ca0),
           'release_owner': (0xb86bd0, None),
           'authority': (0x635710, 0x635adc),
           'entrance_node': (0x1197750, 0x11981ce),
           'entrance_mode': (0x119fa40, None),
           'seat_preference': (0x11966f0, None)}
for name, (start, end) in targets.items():
    (out / (name + '.txt')).write_text(m.dis(start, end - start if end else None))

os.environ['VSS_CAPTURE'] = str(R.parent / 'reverse' / 'capture-25480438')
v = StaticVM()
rows = []
visited = []
def hook(u, at, size, _):
    visited.append(at)
    if at == 0x119fa40:
        sp = u.reg_read(UC_X86_REG_RSP)
        u.reg_write(UC_X86_REG_RAX, 0)
        u.reg_write(UC_X86_REG_RIP, struct.unpack('<Q', u.mem_read(sp, 8))[0])
        u.reg_write(UC_X86_REG_RSP, sp + 8)
v.vm.hook_add(UC_HOOK_CODE, hook)
for transition in (26, 27, 28, 33, 43, 44):
    for entrance in range(12):
        visited.clear()
        node = v.run(0x1197750, transition, 9, entrance) & 0xffffffff
        if node != 0xffffffff:
            rows.append({'transition': transition, 'entrance': entrance,
                         'node': node, 'resource_mode': False,
                         'branch': [hex(x) for x in visited if 0x1197750 <= x < 0x11981ce]})
(out / 'entrance-legacy.json').write_text(json.dumps(rows, indent=2))
print(json.dumps([{k: x[k] for k in ('transition', 'entrance', 'node')} for x in rows]))
print('Native disassembly saved; lookup backend mode is explicitly legacy here.')
