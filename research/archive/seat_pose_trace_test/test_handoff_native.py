"""Replay captured property offsets and serializer source selection.

No process access or networking. The terminal bit writer is intercepted so
this validates selected values/ABI, not actual network delivery or motion.
"""
from pathlib import Path
import json
import os
import struct
import sys

R = Path(__file__).resolve().parent
W = R.parent
sys.path.insert(0, str(W))
from reverse import Module
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.x86_const import *

BUILD = os.environ.get("VSS_TEST_BUILD", "25480438")
m = Module("helldivers2.exe", W / "reverse" / ("capture-" + BUILD))
u = Uc(UC_ARCH_X86, UC_MODE_64)
u.mem_map(0, 0x4000000)
for r, b in m.sections:
    u.mem_write(r, b)
u.mem_map(0x10000000, 0x100000)
u.mem_map(0x20000000, 0x1000)

def write(a, fmt, *v):
    u.mem_write(a, struct.pack(fmt, *v))

def read(a, fmt):
    return struct.unpack(fmt, u.mem_read(a, struct.calcsize(fmt)))

selected, mutations = [], []
def code(uc, at, size, user):
    if at == 0x29BCF0:
        prop = uc.reg_read(UC_X86_REG_R8)
        value = uc.reg_read(UC_X86_REG_R9)
        sp = uc.reg_read(UC_X86_REG_RSP)
        selected.append({"kind": read(prop + 12, "<B")[0], "value_pointer": value,
                         "hash": read(sp + 0x30, "<I")[0]})
        uc.reg_write(UC_X86_REG_RIP, read(sp, "<Q")[0])
        uc.reg_write(UC_X86_REG_RSP, sp + 8)

def memory_write(uc, access, at, size, value, user):
    if not (0x1007F000 <= at and at + size <= 0x10090000 or at == 0x10050018):
        mutations.append([hex(at), size])

u.hook_add(UC_HOOK_CODE, code)
u.hook_add(UC_HOOK_MEM_WRITE, memory_write)

def run(at, *args):
    selected.clear()
    mutations.clear()
    for reg in [UC_X86_REG_RAX, UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8,
                UC_X86_REG_R9, UC_X86_REG_R10, UC_X86_REG_R11]:
        u.reg_write(reg, 0)
    for reg, value in zip([UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8, UC_X86_REG_R9], args):
        u.reg_write(reg, value)
    u.reg_write(UC_X86_REG_RSP, 0x10080008)
    write(0x10080008, "<Q", 0x20000000)
    u.emu_start(at, 0x20000000, count=40000)
    assert u.reg_read(UC_X86_REG_RIP) == 0x20000000 and not mutations, mutations
    return u.reg_read(UC_X86_REG_RAX)

sm, global_types, types = 0x10000000, 0x10001000, 0x10002000
indices, hashes, payload, raw = 0x10030000, 0x10031000, 0x10040000, 0x10041000
context, stream = 0x10042000, 0x10050000
cache, offsets, values = 0x10060000, 0x10061000, 0x10062000
descriptor = types + 123 * 80
write(sm + 0x18, "<Q", global_types)
write(sm + 0x78, "<Q", types)
for k in range(13):
    write(global_types + k * 24 + 12, "<B", k)
write(global_types + 10 * 24 + 16, "<II", 2, 3)
write(context + 0x18, "<Q", sm)
write(payload + 4, "<I", 123)
write(payload + 0x18, "<Q", raw)
write(descriptor + 0x20, "<Q", indices)
write(descriptor + 0x38, "<Q", hashes)
write(descriptor + 0x18, "<I", 1)

size_expected = [4, 4, 4, 12, 16, 0, 4, 8, 8, 8, 16, 12, 8]
for k, size in enumerate(size_expected):
    write(indices, "<I", k)
    assert run(0x173DE0, sm, descriptor, 1) == size, (k, size)

# Two levels of arrays ahead of the five monitored fields. Their offsets are
# produced by actual captured machine code, not by the Lua implementation.
write(global_types + 11 * 24 + 12, "<B", 10)
write(global_types + 11 * 24 + 16, "<II", 10, 2)
list_indices = [0, 11, 9, 2, 3, 10, 3, 4]
list_hashes = [0x100, 0x200, 0x791943F0, 0x91F98CEC, 0x7615F45D, 0x300, 0xEEB1225E, 0xCCA43D10]
write(indices, "<8I", *list_indices)
write(hashes, "<8I", *list_hashes)
write(descriptor + 0x18, "<I", 8)
expected_offsets = [0, 4, 40, 48, 52, 64, 80, 92]
for i, expected in enumerate(expected_offsets):
    assert run(0x173DE0, sm, descriptor, i) == expected, (i, expected)

results = []
for use_cache in [False, True]:
    write(payload + 0x228, "<Q", cache if use_cache else 0)
    write(cache, "<QQ", sm, descriptor)
    write(cache + 0x18, "<Q", values)
    write(cache + 0x28, "<Q", offsets)
    for i in range(8):
        write(offsets + i * 12 + 4, "<I", i * 64)
    for k in [2, 3, 4]:
        write(global_types + k * 24 + 14, "<B", 1)
    run(0x29C840, context, sm, payload, stream)
    assert len(selected) == 8
    for i, row in enumerate(selected):
        interpolated = list_indices[i] in [2, 3, 4]
        expected = values + i * 64 + 8 if use_cache and interpolated else raw + expected_offsets[i]
        assert row["value_pointer"] == expected and row["hash"] == list_hashes[i], (i, row, expected)
    results.append({"cache_present": use_cache, "selected": list(selected), "unexpected_state_writes": 0})

(R / ("handoff-native-" + BUILD + ".json")).write_text(
    json.dumps({"build": BUILD, "boundary": __doc__, "primitive_cases": 13,
                "nested_offset_cases": 8, "serializer_cases": results}, indent=2), encoding="utf-8")
print("PASS", BUILD, "actual native 13 property sizes, 8 nested offsets, raw/cache serializer selection; terminal bit writer intercepted, no network/game execution")
