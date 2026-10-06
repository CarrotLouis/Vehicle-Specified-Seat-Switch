"""Execute frozen Actor.set_world_pose queue/callback/velocity wrappers offline.

The allocator, actor lookup, deferred queue and physical backend are explicit
test doubles. Captured x64 code chooses the queue, branch, order and values.
This proves a native velocity-clearing mechanism, not its occurrence in a
live handoff or the unmodified friend's process. No game/process/network use.
"""
from pathlib import Path
import hashlib
import json
import os
import struct
import sys

R = Path(__file__).resolve().parent
W = R.parent
sys.path.insert(0, str(W))
from reverse import Module
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64, UC_HOOK_CODE
from unicorn.x86_const import *

BUILD = os.environ.get("VSS_TEST_BUILD", "25480438")
m = Module("helldivers2.exe", W / "reverse" / ("capture-" + BUILD))
u = Uc(UC_ARCH_X86, UC_MODE_64)
u.mem_map(0, 0x4000000)
for r, b in m.sections:
    u.mem_write(r, b)
u.mem_map(0x10000000, 0x100000)
u.mem_map(0x20000000, 0x1000)

WORLD, VT, BODY, ACTOR = 0x10000000, 0x10001000, 0x10002000, 0x10003000
ALLOC, SOURCE, HEAP, LIN, ANG = (0x10004000, 0x10005000, 0x10006000,
                               0x10007000, 0x10007100)
HANDLE, BODY_ID = 0xA0004002, 0xCAFE
STUBS = {"allocate": 0x20000100, "free": 0x20000110,
         "queue": 0x20000120, "body": 0x20000130, "pose": 0x20000140,
         "linear": 0x20000150, "angular": 0x20000160,
         "current_pose": 0x20000170}
events, queue = [], []
actor_valid = True
velocity = {"linear": [5.0, -12.0, 1.0], "angular": [0.0, 0.0, 0.8]}

def write(a, fmt, *v):
    u.mem_write(a, struct.pack(fmt, *v))

def read(a, fmt):
    return struct.unpack(fmt, u.mem_read(a, struct.calcsize(fmt)))

def ret(result=None):
    sp = u.reg_read(UC_X86_REG_RSP)
    if result is not None:
        u.reg_write(UC_X86_REG_RAX, result)
    u.reg_write(UC_X86_REG_RIP, read(sp, "<Q")[0])
    u.reg_write(UC_X86_REG_RSP, sp + 8)

def code(uc, at, size, _):
    cx, dx, r8, r9 = [uc.reg_read(r) for r in
                     (UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8, UC_X86_REG_R9)]
    if at == 0x7951B0:
        events.append({"event": "lookup", "handle": hex(cx), "valid": actor_valid})
        ret(ACTOR if actor_valid and cx == HANDLE else 0)
    elif at == STUBS["allocate"]:
        assert dx == 64 and r8 == 16, (dx, r8)
        events.append({"event": "allocate", "size": dx})
        ret(HEAP)
    elif at == STUBS["free"]:
        assert dx == HEAP
        events.append({"event": "free"})
        ret()
    elif at == 0x7952B8:
        events.append({"event": "queue_tail", "target": hex(read(uc.reg_read(UC_X86_REG_R10) + 0x280, "<Q")[0])})
    elif at == STUBS["queue"]:
        assert cx == WORLD + 0x18 and r8 == HANDLE and r9 == 0x795440
        assert dx in (0, HEAP)
        queue.append((dx, r8, r9))
        events.append({"event": "queue", "pose_pointer": dx, "callback": hex(r9)})
        ret()
    elif at == STUBS["body"]:
        assert cx == WORLD + 0x20 and dx == BODY_ID
        events.append({"event": "body_flags_read", "flags": read(BODY + 0x44, "<I")[0]})
        ret(BODY)
    elif at == STUBS["pose"]:
        assert cx == WORLD + 0x18 and dx == BODY_ID and r9 == 0
        events.append({"event": "pose_backend_call"})
        ret()
    elif at in (STUBS["linear"], STUBS["angular"]):
        assert cx == WORLD + 0x18 and dx == BODY_ID and r9 == 0
        kind = "linear" if at == STUBS["linear"] else "angular"
        value = list(read(r8, "<3f"))
        velocity[kind] = value
        events.append({"event": "set_" + kind, "value": value})
        ret()
    elif at == STUBS["current_pose"]:
        events.append({"event": "get_current_pose"})
        ret(SOURCE)
    elif at in (0x12BC2B8, 0x12BC32C):
        ret(0)

u.hook_add(UC_HOOK_CODE, code)

def run(at, *args):
    for reg in (UC_X86_REG_RAX, UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8,
                UC_X86_REG_R9, UC_X86_REG_R10, UC_X86_REG_R11):
        u.reg_write(reg, 0)
    for reg, value in zip((UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8, UC_X86_REG_R9), args):
        u.reg_write(reg, value)
    u.reg_write(UC_X86_REG_RSP, 0x10080008)
    write(0x10080008, "<Q", 0x20000000)
    u.emu_start(at, 0x20000000, count=40000)
    assert u.reg_read(UC_X86_REG_RIP) == 0x20000000, hex(u.reg_read(UC_X86_REG_RIP))

# RIP-relative references are derived from the frozen instructions.
def rip(at):
    return at + 7 + struct.unpack("<i", m.read(at + 3, 4))[0]

write(rip(0x795243) + (HANDLE >> 30) * 0xB0, "<Q", WORLD)
write(WORLD + 0x18, "<Q", VT)
write(WORLD + 0x20, "<Q", VT)
for slot, stub in ((0x70, "body"), (0x80, "pose"), (0xB0, "linear"),
                   (0xB8, "angular"), (0x280, "queue")):
    write(VT + slot, "<Q", STUBS[stub])
write(rip(0x79525E), "<Q", ALLOC)
write(ALLOC + 0x58, "<Q", STUBS["allocate"])
write(ALLOC + 0x60, "<Q", STUBS["free"])
service = 0x10008000
write(rip(0x79548A), "<Q", service)
write(service + 0x18, "<Q", VT)
write(VT + 0x90, "<Q", STUBS["current_pose"])
write(ACTOR + 0xC, "<I", 73)
write(ACTOR + 0x10, "<I", 1)
write(ACTOR + 0x14, "<I", BODY_ID)
write(SOURCE, "<16f", 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 20, 30, 40, 1)
write(LIN, "<3f", 5, -12, 1)
write(ANG, "<3f", 0, 0, 0.8)

cases = []
for flags in (0, 1, 2, 3):
    for with_pose in (True, False):
        events.clear(); queue.clear()
        velocity.update(linear=[5.0, -12.0, 1.0], angular=[0.0, 0.0, 0.8])
        write(BODY + 0x44, "<I", flags)
        run(0x797CB0, HANDLE, SOURCE if with_pose else 0)
        assert len(queue) == 1 and not any(e["event"].startswith("set_") for e in events), (flags, with_pose, events)
        if with_pose:
            assert bytes(u.mem_read(HEAP, 64)) == bytes(u.mem_read(SOURCE, 64))
        # Process the captured callback later; the queue itself does not mutate motion.
        pose, handle, callback = queue.pop()
        run(callback, WORLD, pose, handle)
        set_events = [e["event"] for e in events if e["event"].startswith("set_")]
        expected = [] if flags & 1 else ["set_angular", "set_linear"]
        assert set_events == expected, (flags, with_pose, events)
        if flags & 1:
            assert velocity["linear"] == [5, -12, 1] and velocity["angular"] == [0, 0, 0.8]
        else:
            assert velocity["linear"] == [0, 0, 0] and velocity["angular"] == [0, 0, 0]
        cases.append({"flags": flags, "provided_pose": with_pose, "events": list(events),
                      "backend_model_motion_after": dict(velocity)})

for condition in ("missing_actor", "no_unit", "inactive_actor"):
    events.clear(); queue.clear()
    actor_valid = condition != "missing_actor"
    write(ACTOR + 0xC, "<I", 0 if condition == "no_unit" else 73)
    write(ACTOR + 0x10, "<I", 0 if condition == "inactive_actor" else 1)
    run(0x797CB0, HANDLE, SOURCE)
    if queue:
        pose, handle, callback = queue.pop()
        run(callback, WORLD, pose, handle)
    assert not any(e["event"] == "pose_backend_call" or e["event"].startswith("set_") for e in events)
    cases.append({"guard": condition, "events": list(events)})

# Captured velocity wrapper still passes supplied vectors unmodified. It does
# not schedule a callback and cannot defeat a later queued pose reset.
actor_valid = True
write(ACTOR + 0xC, "<I", 73)
write(ACTOR + 0x10, "<I", 1)
events.clear()
run(0x799030, HANDLE, LIN, ANG)
assert [e["event"] for e in events if e["event"].startswith("set_")] == ["set_linear", "set_angular"]
assert velocity["linear"] == [5, -12, 1]
cases.append({"case": "velocity_wrapper_abi", "events": list(events)})

result = {"build": BUILD, "boundary": __doc__, "cases": cases,
          "code_sha256": {hex(a): hashlib.sha256(m.read(a, n)).hexdigest()
                          for a, n in ((0x797CB0, 0x40), (0x795220, 0x9F),
                                       (0x795440, 0x17D), (0x799030, 0x134))}}
(R / ("native-pose-queue-" + BUILD + ".json")).write_text(json.dumps(result, indent=2), encoding="utf-8")
print("PASS", BUILD, len(cases), "actual pose queue/callback/velocity ABI cases; backend/actor/queue mocked, no live handoff claim")
