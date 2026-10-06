"""Offline native entry selection over every player-seat occupancy mask.

Runs captured code under Unicorn. Entity/component access, reservation side
effects and authority transfer are explicit stubs; no game process is touched.
Both interaction-component and legacy-index lookup branches are exercised.
"""
from pathlib import Path
import hashlib, json, os, struct, sys

R = Path(__file__).resolve().parent
W = R.parent
os.environ['VSS_CAPTURE'] = str(W / 'reverse/capture-25480438')
sys.path.insert(0, str(W))
from emulate_seats import StaticVM
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *

OUT = R / 'reservation-20260925'
OUT.mkdir(exist_ok=True)
disk = Path(r'F:\SteamLibrary\steamapps\common\Helldivers 2\data\game\game.dll').read_bytes()
disk_hash = hashlib.sha256(disk).hexdigest()
assert disk_hash == '2e2c3b7c2500646dadd5f2b4c6e0504dbb7e7896139f64cddc0d1813c718f51e'
pe = struct.unpack_from('<I', disk, 0x3c)[0]
opt = struct.unpack_from('<H', disk, pe + 20)[0]
sections = []
for i in range(struct.unpack_from('<H', disk, pe + 6)[0]):
    h = pe + 24 + opt + 40 * i
    vs, va, rs, raw = struct.unpack_from('<IIII', disk, h + 8)
    sections.append((va, rs, raw))
def read_disk(rva, n):
    for va, rs, raw in sections:
        if va <= rva and rva + n <= va + rs:
            return disk[raw + rva - va:raw + rva - va + n]
    raise AssertionError(hex(rva))

s = StaticVM()
u = s.vm
def w32(p, x): u.mem_write(p, struct.pack('<I', x & 0xffffffff))
def w64(p, x): u.mem_write(p, struct.pack('<Q', x))
def r32(p): return struct.unpack('<I', u.mem_read(p, 4))[0]
def ret(value=0):
    sp = u.reg_read(UC_X86_REG_RSP)
    addr = struct.unpack('<Q', u.mem_read(sp, 8))[0]
    u.reg_write(UC_X86_REG_RAX, value & 0xffffffffffffffff)
    u.reg_write(UC_X86_REG_RSP, sp + 8)
    u.reg_write(UC_X86_REG_RIP, addr)

MANAGER, MAP, INFO, MASK, COMPONENT = [0x10000000 + v for v in (0, 0x1000, 0x2000, 0x3000, 0x4000)]
w64(MANAGER + 0x20, MAP)
w32(MANAGER + 0x28, 1)
w32(MANAGER + 0x2c, 0xffffffff)
w32(MANAGER + 0x30, 1)
w32(MAP, 123)
w32(MAP + 4, 0)
w64(MANAGER + 0x48, INFO)
w64(MANAGER + 0x50, MASK)
w32(0x3483c20, 0xffffffff)
state = dict(component=True, effects=[])
def hook(uc, addr, size, _):
    if addr == 0x119fa40:
        ret(int(state['component']))
    elif addr == 0xfd9d40:
        ret(0x10006000)
    elif addr == 0x50acb0:
        ret(COMPONENT)
    elif addr in (0x6344d0, 0x6349b0, 0x635710):
        node = uc.reg_read(UC_X86_REG_R8) & 0xffffffff
        state['effects'].append(dict(kind={0x6344d0: 'reserve', 0x6349b0: 'release', 0x635710: 'authority'}[addr], seat=node))
        if addr == 0x6344d0:
            assert r32(MASK) & (1 << node), 'native tried reserving an occupied player seat'
            w32(MASK, r32(MASK) & ~(1 << node))
        ret()
u.hook_add(UC_HOOK_CODE, hook)

profiles = [('m102', 26, 5), ('m103', 27, 4), ('m104', 28, 3),
            ('bastion', 43, 4), ('maelstrom', 44, 4), ('tanker', 33, 2)]
# Candidates come from native comparisons, not guessed input numbers.
ins = list(s.mod.md.disasm(s.mod.read(0x1197750, 0x11981ce - 0x1197750), 0x1197750))
hashes = sorted({int(i.op_str.rsplit(', ', 1)[1], 16) for i in ins
                 if i.mnemonic == 'cmp' and ', 0x' in i.op_str and
                 int(i.op_str.rsplit(', ', 1)[1], 16) > 0xffff})
# Packed disk data does not contain these decrypted runtime tables. Compute the
# exact ranges from the captured lookup code before requesting a narrow sample.
table_capture = OUT / 'entry-tables.json'
if not table_capture.exists():
    needed = []
    for name, kind, n in profiles:
        state['component'] = True
        mapping = []
        for h in hashes:
            w32(COMPONENT + 0x14, h)
            node = s.run(0x1197750, kind, 123, 0) & 0xffffffff
            if node != 0xffffffff:
                mapping.append(dict(interaction_hash=hex(h), node=node))
        base = s.run(0x11966f0, kind, 0)
        stride = s.run(0x11966f0, kind, 1) - base
        count = max(n, 1 + max(x['node'] for x in mapping))
        needed.append(dict(vehicle=name, transition=kind, rva=base, row=stride,
                           seat_count=n, rows=count, size=count*stride, interaction_nodes=mapping))
    report = dict(status='needs_runtime_entry_tables', capture='25480438', game_sha256=disk_hash,
                  ranges=needed, total_bytes=sum(x['size'] for x in needed),
                  evidence='Native 0x1197750 executed with synthetic component hashes; 0x11966f0 computed table ranges. Selection/fallback not emulated yet: runtime table data absent from original static capture and packed disk file.')
    (OUT / 'entry-table-requirements.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    sys.exit(0)
runtime = json.loads(table_capture.read_text())
assert runtime['game_sha256'] == disk_hash
def read_table(rva, n):
    for t in runtime['tables']:
        data = bytes.fromhex(t['hex'])
        if t['rva'] <= rva and rva + n <= t['rva'] + len(data):
            return data[rva-t['rva']:rva-t['rva']+n]
    raise AssertionError(('missing_runtime_range', hex(rva), n))
results = []
for name, kind, n in profiles:
    w32(INFO, kind)
    pointers = set()
    sampled = next(t for t in runtime['tables'] if t['vehicle'] == name)
    for node in range(sampled['rows']):
        ptr = s.run(0x11966f0, kind, node)
        if ptr and ptr not in pointers:
            # Load only one short static row; terminators are inside these rows.
            data = read_table(ptr, sampled['row'])
            u.mem_write(ptr, data)
            pointers.add(ptr)
    entries = []
    state['component'] = True
    for h in hashes:
        w32(COMPONENT + 0x14, h)
        normalized = s.run(0x1197750, kind, 123, 0) & 0xffffffff
        if normalized == 0xffffffff:
            continue
        state['effects'] = []
        w32(MASK, (1 << n) - 1)
        preferred = s.run(0x636a30, MANAGER, 123, 456, 0) & 0xffffffff
        assert preferred < n, (name, hex(h), normalized, preferred)
        rows = []
        for mask in range(1 << n):
            w32(MASK, mask)
            state['effects'] = []
            result = s.run(0x636a30, MANAGER, 123, 456, 0) & 0xffffffff
            effects = list(state['effects'])
            assert not any(e['kind'] == 'release' for e in effects)
            if result != 0xffffffff:
                assert result < n and mask & (1 << result), (name, mask, result)
                assert effects == [dict(kind='reserve', seat=result), dict(kind='authority', seat=result)]
                assert r32(MASK) == mask & ~(1 << result)
            else:
                assert not effects and r32(MASK) == mask
            if mask & (1 << preferred):
                assert result == preferred, (name, mask, preferred, result)
            # Real masks also retain free bits above the number of player seats.
            # Ensure these do not change denial/fallback behavior when low bits
            # are all occupied (the native fallback checks mask != 0).
            padding_checks=[]
            for high in (0x3fffff, 0xffffffff):
                padded=mask | (high & ~((1 << n)-1))
                w32(MASK,padded);state['effects']=[]
                alternate=s.run(0x636a30,MANAGER,123,456,0) & 0xffffffff
                assert alternate==result and state['effects']==effects, (name,mask,padded,alternate,result)
                assert r32(MASK)==(padded if result==0xffffffff else padded & ~(1<<result))
                padding_checks.append(padded)
            rows.append(dict(free_mask=mask, selected=-1 if result == 0xffffffff else result,
                             redirected=result not in (preferred, 0xffffffff), effects=effects,
                             padding_masks_checked=padding_checks))
        entries.append(dict(interaction_hash=hex(h), normalized_node=normalized,
                            preferred=preferred, masks=rows))
    assert {e['preferred'] for e in entries} == set(range(n)), (name, entries)
    # Legacy physical indices are also computed; don't assume today's components
    # retain this ordering (the runtime M102 recordings show a different order).
    state['component'] = False
    legacy = []
    for i in range(n):
        w32(MASK, (1 << n) - 1)
        state['effects'] = []
        node = s.run(0x1197750, kind, 123, i) & 0xffffffff
        dst = s.run(0x636a30, MANAGER, 123, 456, i) & 0xffffffff
        legacy.append(dict(index=i, normalized=node, selected=dst))
    results.append(dict(vehicle=name, transition=kind, entries=entries, legacy_indices=legacy))

report = dict(game_sha256=disk_hash, capture='25480438', table_source_sha256=runtime['source_sha256'],vehicles=results,
              cases=sum(len(e['masks'])*3 for v in results for e in v['entries']),
              base_cases=sum(len(e['masks']) for v in results for e in v['entries']),
              base_redirects=sum(x['redirected'] for v in results for e in v['entries'] for x in e['masks']),
              limits='Synthetic entity/component hashes. Native selector and fallback execute unchanged; reserve/authority effects are stubs, not engine/network validation. No messages sent.')
(OUT / 'entry-selection.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
for r in results:
    print(json.dumps(dict(vehicle=r['vehicle'], mappings=[{k: e[k] for k in ('interaction_hash', 'normalized_node', 'preferred')} for e in r['entries']],
                          masks=sum(len(e['masks']) for e in r['entries']),
                          redirects=sum(x['redirected'] for e in r['entries'] for x in e['masks']),
                          strict_targets=[e['preferred'] for e in r['entries'] if not any(x['redirected'] for x in e['masks'])],
                          legacy=r['legacy_indices'])))
