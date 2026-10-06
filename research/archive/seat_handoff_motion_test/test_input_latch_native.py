"""Execute captured native vehicle input code with synthetic object tables.

This proves input-store behavior, not physical rotation in a running game.
External engine lookup, audio, network, hazards and renderer calls are stubbed.
"""
from pathlib import Path
import json
import os
import struct
import sys

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
sys.path.insert(0, str(WORK))
BUILD = os.environ.get('VSS_TEST_BUILD', '25480438')
os.environ['VSS_CAPTURE'] = str(WORK / 'reverse' / ('capture-' + BUILD))
from emulate_seats import StaticVM
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.x86_const import *

instance = StaticVM()
vm = instance.vm
driver, driver_rows, entities, entity = 0x10010000, 0x10011000, 0x10012000, 0x10013000
commands, driver_runtime, backend, fuel = 0x10014000, 0x10015000, 0x10018000, 0x10019000
vehicle, vehicle_rows, input_rows = 0x10020000, 0x10021000, 0x10022000
asset, engine, unit_api, actor_api = 0x10030000, 0x10031000, 0x10032000, 0x10033000
motors, motor_map, motor_rows = 0x10040000, 0x10041000, 0x10042000
audio_api = 0x10043000
index, collection, unit = 1, 9, 909
input_address = input_rows + index * 16
command_address = commands + index * 48

def u32(address, value):
    vm.mem_write(address, struct.pack('<I', value))
def u64(address, value):
    vm.mem_write(address, struct.pack('<Q', value))
def f32(address, value):
    vm.mem_write(address, struct.pack('<f', value))

u64(0x3326668, driver)
u64(driver + 0x38, driver_rows)
u32(driver + 0x40, 4)
u32(driver + 0x44, 0xffffffff)
u32(driver + 0x48, 1)
for row in range(4):
    u32(driver_rows + row * 8, 0xffffffff)
u32(driver_rows + 8, collection)
u32(driver_rows + 12, index)
u64(driver + 0x50, entities)
u64(entities + index * 8, entity)
u64(driver + 0x58, commands)
u64(driver + 0x60, backend)
u64(driver + 0x68, driver_runtime)
u64(driver + 0x70, fuel)
u32(backend + index * 8 + 4, 1)
f32(fuel + index * 8 + 4, 100.0)
u32(entity + 8, collection)
u32(entity + 12, unit)
u32(entity + 20, 1)

u64(0x3326458, vehicle)
u64(vehicle + 0x40, vehicle_rows)
u32(vehicle + 0x48, 4)
u32(vehicle + 0x4c, 0xffffffff)
u32(vehicle + 0x50, 1)
u32(vehicle + 0x34, 2)
for row in range(4):
    u32(vehicle_rows + row * 8, 0xffffffff)
u32(vehicle_rows + 8, collection)
u32(vehicle_rows + 12, index)
u64(vehicle + 0x60, input_rows)

u64(0x3326308, engine)
u64(engine + 0x18, unit_api)
for offset in [0x88, 0x6d8]:
    u64(unit_api + offset, 0x10090000 + offset)
u64(0x3326310, actor_api)
u64(actor_api, 0x10091000)
u64(0x3326318, audio_api)
u64(audio_api, 0x10044000)

u64(0x3326a28, motors)
u64(motors + 0x18, motor_map)
u32(motors + 0x20, 4)
u32(motors + 0x24, 0xffffffff)
u32(motors + 0x28, 1)
for row in range(4):
    u32(motor_map + row * 8, 0xffffffff)
u32(motor_map + 8, collection)
u32(motor_map + 12, index)
u64(motors + 0x38, motor_rows)
u32(motor_rows + index * 0x2c, 4)

native_addresses = [0xaac300, 0xaac7d0, 0x6fe480, 0x5b8790]
allowed = [instance.mod.function(address)[:2] for address in native_addresses]
calls, writes = [], []

def code_hook(emulator, address, size, user):
    if address == 0x20000000 or any(start <= address < end for start, end in allowed):
        return
    args = [emulator.reg_read(register) for register in
            (UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_R8, UC_X86_REG_R9)]
    result = 0
    if address == 0x4fa7a0:
        result = asset
    elif address == 0x6fea30:
        result = 0x10025000
    elif address == 0x10091000:
        assert args[:2] == [unit, 0x10]
        emulator.mem_write(args[2], struct.pack('<I', 1))
        result = 1
    else:
        assert address in [0x927050, 0x89d2b0, 0x7056f0,
                           (0x20886a0 if BUILD == '25327279' else 0x2088770),
                           0x100906d8, 0x10090088], (hex(address), args)
    calls.append(dict(function=hex(address), args=args))
    stack = emulator.reg_read(UC_X86_REG_RSP)
    target = struct.unpack('<Q', emulator.mem_read(stack, 8))[0]
    emulator.reg_write(UC_X86_REG_RAX, result)
    emulator.reg_write(UC_X86_REG_RSP, stack + 8)
    emulator.reg_write(UC_X86_REG_RIP, target)

def write_hook(emulator, access, address, size, value, user):
    if input_address <= address < input_address + 16:
        writes.append(dict(pc=hex(emulator.reg_read(UC_X86_REG_RIP)),
                           offset=address-input_address, size=size, value=value))

vm.hook_add(UC_HOOK_CODE, code_hook)
vm.hook_add(UC_HOOK_MEM_WRITE, write_hook)

results = []
for sign in [-1.0, 1.0]:
    for name in ['held_valid', 'neutralized_invalid', 'neutralized_valid',
                 'canonical_exit_then_invalid', 'explicit_input_zero_then_invalid',
                 'native_pedal_cleanup']:
        vm.mem_write(input_rows, b'\x5a' * 48)
        before = struct.pack('<3f4B', sign, .5, .25, 0, 0, 0, 0)
        vm.mem_write(input_address, before)
        vm.mem_write(command_address, bytes(48))
        vm.mem_write(command_address + 0x2c, b'\1' if name in
                     ['held_valid', 'neutralized_valid'] else b'\0')
        f32(command_address + 0x20, sign if name == 'held_valid' else 0.0)
        vm.mem_write(driver_runtime + index * 0xd28 + 0xd18, b'\1')
        calls.clear()
        writes.clear()
        if name == 'canonical_exit_then_invalid':
            instance.run(0x6fe480, 0, collection, 0)
            assert vm.mem_read(driver_runtime + index * 0xd28 + 0xd18, 1) == b'\0'
            assert vm.mem_read(input_address, 16) == before
        if name == 'explicit_input_zero_then_invalid':
            f32(input_address, 0.0)
        if name == 'native_pedal_cleanup':
            instance.run(0xaac7d0, driver, index)
        else:
            vm.reg_write(UC_X86_REG_XMM2, int.from_bytes(struct.pack('<f', .016), 'little'))
            instance.run(0xaac300, driver, index)
        after = bytes(vm.mem_read(input_address, 16))
        values = struct.unpack('<3f4B', after)
        expected_steer = 0.0 if name in ['neutralized_valid', 'explicit_input_zero_then_invalid'] else sign
        assert values == (expected_steer, 0.0, 0.0, 0, 0, 0, 0), (name, values, writes)
        assert vm.mem_read(input_rows, 16) == b'\x5a' * 16
        assert vm.mem_read(input_rows + 32, 16) == b'\x5a' * 16
        results.append(dict(case=name, sign=sign, before=list(struct.unpack('<3f4B', before)),
                            after=list(values), input_writes=writes.copy(), external_calls=calls.copy()))

(HERE / f'native-input-latch-{BUILD}.json').write_text(json.dumps(dict(
    build=BUILD, native_code_executed=True, external_effects_stubbed=True,
    boundary=__doc__, cases=results), indent=2), encoding='utf-8')
print('PASS', BUILD, len(results), 'native input-latch cases; invalid command preserves old steer, canonical driver exit does not change downstream input, neighbors preserved; physical effects not emulated')
