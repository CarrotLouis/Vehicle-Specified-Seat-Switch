"""Execute actual native entry/reserve/authority/release instructions offline.

Entity and network lookup, static writable tables, asset events, deferred
property publication, peer lookup and ownership backend are explicit doubles. Seat selection, vacancy,
mask mutation, role choice and wire-adapter branches are captured x64 code.
No running game, live memory, real packets, physics or remote rendering.
"""
from pathlib import Path
from collections import deque
import os, sys, struct, json
R = Path(__file__).resolve().parent
W = R.parent
BUILD = os.environ.get('VSS_TEST_BUILD', '25480438')
os.environ['VSS_CAPTURE'] = str(W / 'reverse' / ('capture-' + BUILD))
sys.path.insert(0, str(W))
from emulate_seats import StaticVM
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *

v = StaticVM(); u = v.vm
# The unpacked writable preference arrays are absent from both code-only
# captures AND from the packed on-disk image. These are EXPLICIT synthetic
# table fixtures. Live code must derive/check exact rows and entrance mappings
# on demand; these tests do not establish the actual game's entrance layout.
for transition, mapping in ((26, [0, 2, 4, 3, 1]), (27, [0, 2, 3, 1]),
                            (28, [0, 2, 1]), (43, [0, 1, 2, 3]), (44, [0, 1, 2, 3])):
    count = len(mapping)
    for node in range(count * 2):
        pointer = v.run(0x11966f0, transition, node)
        if node < count:
            values = {26: [[1,-1],[0,-1],[3,-1],[2,-1],[-1,-1]],
                      27: [[1,-1],[0,-1],[3,-1],[2,-1]]}.get(transition)
            row = values[node] if values else [-1,-1]
        else: row = [mapping[node - count], -1]
        w_placeholder = struct.pack('<2i', *row)
        u.mem_write(pointer, w_placeholder)
CM, MAP, STATE, FREE, LIST, CAR, AVATAR, ASSET = [0x10010000 + i * 0x1000 for i in range(8)]
HUB, PARAMS, VALS, SERVICES, PEER_TABLE, PEER_ENGINE = [0x10020000 + i * 0x2000 for i in range(6)]
CAR_ID, AVATAR_ID, CAR_NET, AVATAR_NET = 9, 7, 4123, 4107
DRIVER_PEER, INSTALLER_PEER = 0xD9008359D0A55B54, 0x7E026AFCD11CFA02
calls, results = [], []
recent = deque(maxlen=16)
resource_mode = False
busy = False
owned = True

def w(a, fmt, *values): u.mem_write(a, struct.pack(fmt, *values))
def read(a, fmt): return struct.unpack(fmt, u.mem_read(a, struct.calcsize(fmt)))
def reg(r): return u.reg_read(r)
def ret(value=0):
    sp = reg(UC_X86_REG_RSP)
    u.reg_write(UC_X86_REG_RAX, value)
    u.reg_write(UC_X86_REG_RIP, read(sp, '<Q')[0])
    u.reg_write(UC_X86_REG_RSP, sp + 8)
def map_(manager, offset, rows, key):
    w(manager + offset, '<QIII', rows, 2, 0xffffffff, 1)
    w(rows, '<4I', 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff)
    w(rows + key % 2 * 8, '<II', key, 0)
def global_(insn, disp, length, value):
    at = insn + length + struct.unpack('<i', v.mod.read(insn + disp, 4))[0]
    w(at, '<Q', value)
    return at

map_(CM, 0x20, MAP, CAR_ID)
w(CM + 0x38, '<Q', LIST); w(LIST, '<Q', CAR)
w(CM + 0x48, '<Q', STATE); w(CM + 0x50, '<Q', FREE)
w(CAR + 8, '<IIII', CAR_ID, 8391940, CAR_NET, 1)
w(AVATAR + 8, '<IIII', AVATAR_ID, 8392704, AVATAR_NET, 0)
w(ASSET + 0x128, '<II', 0, 0)
w(ASSET + 0x10e, '<B', 1)
w(0x3483c20, '<I', 0xffffffff)
global_(0xba9d3e, 3, 7, HUB)
global_(0xb86bde, 3, 7, HUB)
w(HUB + 0x57a8, '<I', 1); w(HUB + 0x57b0, '<QI', CM, 0x76)
w(HUB + 0x57f0, '<I', 1); w(HUB + 0x57f8, '<QI', CM, 0x76)
global_(0x63577e, 3, 7, SERVICES)
global_(0x635a79, 3, 7, SERVICES + 0x600)
w(SERVICES + 0x38, '<Q', PEER_TABLE); w(SERVICES + 0x40, '<Q', PEER_TABLE + 0x200)
w(PEER_TABLE + 8, '<Q', 0x20000100); w(PEER_TABLE + 0x200 + 0x160, '<Q', 0x20000110)
global_(0xba9dba, 3, 7, SERVICES + 0x400)
w(SERVICES + 0x408, '<Q', 0x10060000)
session_at = global_(0x6357a9, 3, 7, SERVICES + 0x800)
w(SERVICES + 0x800 + 0xb398, '<Q', 0x10061000)

def hook(uc, at, size, _):
    recent.append(at)
    cx, dx, r8, r9 = [reg(r) for r in (UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8, UC_X86_REG_R9)]
    if at == 0xfd9ba0:
        entity = {CAR_NET: CAR_ID, AVATAR_NET: AVATAR_ID}.get(dx)
        assert entity is not None, ('unknown net ref', dx)
        w(cx, '<I', entity); ret(cx)
    elif at == 0xfd9d40:
        assert cx in (0, CAR_ID, AVATAR_ID), ('entity lookup', cx)
        ret(CAR if cx == CAR_ID else AVATAR if cx == AVATAR_ID else 0)
    elif at == 0x510e60:
        assert cx == CAR
        ret(ASSET)
    elif at == 0x1309d00:
        raise AssertionError('unexpected asset event')
    elif at == 0x926ef0:
        assert dx == CAR_ID
        ret(0)
    elif at == 0xfd97e0:
        assert cx == CAR_NET and dx == 0x6d2d83f8
        assert r8 == FREE, 'property must refer to lifetime-stable mask storage'
        calls.append({'event': 'deferred_free_mask', 'value': read(r8, '<I')[0], 'pointer': r8})
        ret()
    elif at == 0x119fa40:
        ret(int(resource_mode))
    elif at == 0x50acb0:
        assert cx == CAR
        ret(ASSET)
    elif at == 0x5a8870:
        # Linked-weapon backend resolves no synthetic child entities. The
        # native role/chassis authority branch itself is never stubbed.
        w(dx, '<I', 0); ret(dx)
    elif at == 0xfde390:
        calls.append({'event': 'busy_checked', 'busy': busy}); ret(int(busy))
    elif at == 0xfd9af0:
        assert cx in (CAR_ID, AVATAR_ID)
        ret(1 if cx == CAR_ID else 2)
    elif at == 0x20000100:
        ret(PEER_ENGINE)
    elif at == 0x20000110:
        assert cx == PEER_ENGINE
        ret(DRIVER_PEER if dx == 1 else INSTALLER_PEER)
    elif at == 0xbf3ad0:
        calls.append({'event': 'authority_transfer', 'unit': dx, 'peer': hex(r8)})
        ret()
    elif at == 0xbf1b70:
        calls.append({'event': 'authority_request', 'unit': dx, 'peer': hex(r8)})
        ret()
    elif at == 0xbe22b0:
        assert cx == 0xffffffffffffffff and dx == CAR_ID and r8 == AVATAR_ID
        calls.append({'event': 'accepted', 'chosen': r9 & 0xffffffff}); ret()
    elif at == 0xbf2ee0:
        assert dx == CAR_ID and r8 == AVATAR_ID
        calls.append({'event': 'denied'}); ret()
    elif at == 0xbe36a0:
        calls.append({'event': 'entry_redirect', 'peer': hex(cx), 'entrance': r9}); ret()
    elif at == 0xbee380:
        calls.append({'event': 'release_redirect', 'peer': hex(cx), 'slot': r8}); ret()
    elif at == 0xbde430:
        assert cx == 0x4506cd6
        calls.append({'event': 'release_retry'}); ret()
    elif at == 0x634370:
        calls.append({'event': 'dependent_reserve', 'slot': r8}); ret()
    elif at == 0x634420:
        calls.append({'event': 'dependent_release', 'slot': r8}); ret()
u.hook_add(UC_HOOK_CODE, hook)

def setup(transition, mask, entity_owned=True):
    global owned
    owned = entity_owned
    w(STATE, '<I', transition)
    # Preserve native dependent-slot logic (byte9==0); backend mask helpers
    # are separately recorded, not silently treated as actual publication.
    w(STATE + 9, '<B', 1)
    w(FREE, '<III', mask, 0x11223344, 0x55667788)
    w(CAR + 0x14, '<I', int(entity_owned))
    calls.clear()
def descriptors(values):
    for i, value in enumerate(values):
        w(VALS + i * 4, '<I', value)
        w(PARAMS + i * 16, '<IIQ', 1, 4, VALS + i * 4)
def execute_entry(entrance):
    descriptors([CAR_NET, AVATAR_NET, entrance])
    try:
        v.run(0xba9d10, INSTALLER_PEER, PARAMS)
    except Exception:
        print('Execution failed', 'entrance', entrance, 'state', read(STATE, '<I'),
              'last', [hex(a) for a in recent], 'calls', calls,
              'registers', {str(r): hex(reg(r)) for r in (UC_X86_REG_RAX, UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8, UC_X86_REG_R9, UC_X86_REG_RIP)})
        raise
    return calls.copy()

for transition, seats, source in ((26, 5, 1), (27, 4, 1), (28, 3, 1), (43, 4, 2), (44, 4, 2)):
    all_mask = (1 << seats) - 1
    # Native entrance-to-seat preferences, including existing-reservation
    # context: installer source is taken and friend stays in driving slot0.
    mask = all_mask & ~(1 << 0) & ~(1 << source)
    choices = []
    for entrance in range(seats):
        setup(transition, mask)
        event = execute_entry(entrance)
        accepted = [x for x in event if x['event'] == 'accepted']
        chosen = accepted[0]['chosen'] if accepted else None
        if chosen is not None:
            assert mask & (1 << chosen), 'owner never chooses occupied source/driver'
            assert read(FREE, '<I')[0] == mask & ~(1 << chosen)
            assert not read(FREE, '<I')[0] & (1 << source), 'source reservation remains until explicitly released'
            role = v.run(0x11957c0, transition, chosen)
            if role == 3:
                assert not any(x['event'].startswith('authority_') for x in event), 'passenger entry must retain chassis authority'
        choices.append({'entrance': entrance, 'chosen': chosen, 'events': event})
    results.append({'transition': transition, 'mode': 'legacy_asset_fallback', 'source_reserved': source,
                    'driver_reserved': 0, 'mask': mask, 'synthetic_preference_tables': True,
                    'dependent_mask_helpers_excluded': True, 'choices': choices})

# Empty/occupied: native owner denies with all reservations taken, and does
# not publish or touch chassis authority. A busy owner denies before reserve.
for mask, blocked in ((0, False), (0b11100, True)):
    busy = blocked; setup(26, mask)
    events = execute_entry(2)
    assert [x['event'] for x in events].count('denied') == 1
    assert read(FREE, '<I')[0] == mask
    assert not any(x['event'] in ('accepted', 'authority_transfer', 'authority_request', 'deferred_free_mask') for x in events)
    results.append({'case': 'busy' if blocked else 'all_slots_taken', 'events': events})
busy = False

# Production path on modern entrance resources: for each transition execute
# true resource lookup with native compared entrance identifiers, no hand-
# written target result. Values come from the actual disassembly constants.
for transition, entrance_hashes in ((26, [0x11547c58, 0x3de87f95]),):
    resource_mode = True
    for entrance_hash in entrance_hashes:
        setup(transition, 0b11100)
        w(ASSET + 0x14, '<I', entrance_hash)
        events = execute_entry(0)
        results.append({'case': 'resource_entrance', 'transition': transition,
                        'identifier': hex(entrance_hash), 'events': events})
resource_mode = False

# A genuine driver entry is the counterexample: it DOES invoke chassis
# transfer. We must therefore exclude driving seats from this prototype.
setup(26, 0b11111)
driver_entries = []
for entrance in range(5):
    setup(26, 0b11111)
    events = execute_entry(entrance)
    if any(x['event'] == 'authority_transfer' for x in events):
        driver_entries.append(events)
assert driver_entries, 'driver control counterexample must execute actual authority branch'
results.append({'case': 'driver_changes_chassis_owner', 'events': driver_entries})

# Real release wire adapter -> owner branch -> native release. Releasing
# installer source1 preserves friend0 and the new target2 reservations.
setup(26, 0b11000)
descriptors([CAR_NET, 1])
v.run(0xbbafe0, INSTALLER_PEER, PARAMS)
assert read(FREE, '<I')[0] == 0b11010
assert not any(x['event'].startswith('authority_') for x in calls)
results.append({'case': 'release_original_installer_slot', 'mask': read(FREE, '<I')[0], 'events': calls.copy()})
calls.clear(); v.run(0xbbafe0, INSTALLER_PEER, PARAMS)
assert read(FREE, '<I')[0] == 0b11010 and not any(x['event'] != 'busy_checked' for x in calls), 'duplicate release is owner-side no-op'
results.append({'case': 'duplicate_release_noop'})

out = R / ('reservation-native-' + BUILD + '.json')
out.write_text(json.dumps({'boundary': __doc__, 'build': BUILD, 'cases': results}, indent=2))
print('PASS', BUILD, len(results), 'actual reservation/release adapters; passenger retains chassis, source reservation needs explicit release; backend doubles')
