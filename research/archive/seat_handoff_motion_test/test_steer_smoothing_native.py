"""Replay the captured smoothing block with synthetic controls, not physics."""
from pathlib import Path
import json
import os
import struct
import sys

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
BUILD = os.environ.get('VSS_TEST_BUILD', '25480438')
os.environ['VSS_CAPTURE'] = str(WORK/'reverse'/('capture-'+BUILD))
sys.path.insert(0, str(WORK))
from emulate_seats import StaticVM
from unicorn.x86_const import *

instance = StaticVM()
vm, module = instance.vm, instance.mod
manager, replicated, input_row, asset, frame = [0x10010000+i*0x1000 for i in range(5)]
vm.mem_write(manager+0x78, struct.pack('<Q', replicated))
vm.mem_write(frame-0x68, struct.pack('<Q', manager))
vm.mem_write(asset+0x16c, struct.pack('<f', 1.0))
module.md.detail = True
instruction = next(module.md.disasm(module.read(0x7153b5, 15), 0x7153b5))
constant = instruction.address+instruction.size+instruction.disp
absolute_mask = int.from_bytes(module.read(constant, 8), 'little')

def smooth(input_value, replicated_value):
    vm.mem_write(input_row, struct.pack('<f', input_value))
    vm.mem_write(replicated+0x34, struct.pack('<f', replicated_value))
    for register, value in [(UC_X86_REG_RBP, frame), (UC_X86_REG_RSI, input_row),
                            (UC_X86_REG_R12, asset), (UC_X86_REG_R15, 0),
                            (UC_X86_REG_XMM10, absolute_mask),
                            (UC_X86_REG_XMM11, int.from_bytes(struct.pack('<f', .016), 'little'))]:
        vm.reg_write(register, value)
    vm.emu_start(0x7158c7, 0x715926, count=1000)
    assert vm.reg_read(UC_X86_REG_RIP) == 0x715926
    return struct.unpack('<f', vm.mem_read(input_row, 4))[0]

cases = []
for sign in [-1.0, 1.0]:
    first = smooth(0.0, sign)
    assert abs(first-sign*.984) < 1e-6, (sign, first)
    # The later native owned tick copies input+0 into replicated+34. With
    # command+2C false, AAC300 retains the input that smoothing just wrote.
    second = smooth(first, first)
    assert second == first
    both_zero = smooth(0.0, 0.0)
    assert both_zero == 0.0
    cases.append(dict(previous_steer=sign, first_tick_after_input_only_zero=first,
                      following_tick_without_valid_command=second,
                      after_input_and_replica_zero=both_zero))
(HERE/f'native-steer-smoothing-{BUILD}.json').write_text(json.dumps(dict(build=BUILD,
    native_block_executed=True, dt=.016, synthetic_steering_rate=1.0,
    no_physics_emulated=True, cases=cases), indent=2), encoding='utf-8')
print('PASS', BUILD, '2 signs x 3 native smoothing cases; input-only zero is re-latched from replicated steer; exact input+replica zero stays zero. Not a live fix validation.')
