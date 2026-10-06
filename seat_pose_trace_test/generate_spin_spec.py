"""Relocatable steering witnesses from two frozen images; no live scan."""
from pathlib import Path
import json
import struct
import sys

R = Path(__file__).resolve().parent
W = R.parent
sys.path.insert(0, str(W))
from reverse import Module
from capstone.x86 import X86_OP_MEM, X86_REG_RIP, X86_OP_IMM

captures = ['25327279', '25480438']
modules = [Module('game.dll', W / 'reverse' / ('capture-' + build)) for build in captures]
definitions = {
    'spin_driver_tick': 0x6fef80,
    'spin_driver_export': 0xaac300,
    'spin_vehicle_tick': 0x7152f0,
    'spin_physics_export': 0x713dc0,
}

def lua(value):
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return '{' + ','.join(map(lua, value)) + '}'
    return '{' + ','.join('[' + lua(key) + ']=' + lua(item) for key, item in value.items()) + '}'

records, edges, evidence = {}, [], []
for name, rva in definitions.items():
    module = modules[-1]
    module.md.detail = True
    start, end, _ = module.function(rva)
    assert start == rva
    length = end - start
    assert length < 0x10000
    body = module.read(rva, length)
    mask = bytearray(b'\1' * length)
    for instruction in module.md.disasm(body, rva):
        if any(operand.type == X86_OP_MEM and operand.mem.base == X86_REG_RIP
               for operand in instruction.operands):
            offset = instruction.address - rva + instruction.disp_offset
            mask[offset:offset + instruction.disp_size] = bytes(instruction.disp_size)
        if (instruction.group(1) or instruction.group(2)) and instruction.operands and instruction.operands[0].type == X86_OP_IMM:
            target = instruction.operands[0].imm
            if not rva <= target < end:
                offset = instruction.address - rva + instruction.imm_offset
                mask[offset:offset + instruction.imm_size] = bytes(instruction.imm_size)
            for target_name, target_rva in definitions.items():
                if target == target_rva:
                    edges.append(dict(**{'from': name}, to=target_name,
                                      offset=instruction.address-rva, disp=instruction.imm_offset,
                                      width=instruction.imm_size, size=instruction.size))
    chunks = []
    offset = 0
    while offset < length:
        if not mask[offset]:
            offset += 1
            continue
        stop = offset + 1
        while stop < length and mask[stop]:
            stop += 1
        chunks.append(dict(offset=offset, hex=body[offset:stop].hex()))
        offset = stop
    needle = None
    for chunk in sorted(chunks, key=lambda item: len(item['hex']), reverse=True):
        sequence = bytes.fromhex(chunk['hex'])
        for offset in range(max(1, len(sequence)-15)):
            key = sequence[offset:offset+32]
            if len(key) >= 12 and all(module.code.count(key) == 1 for module in modules):
                needle = dict(offset=chunk['offset']+offset, hex=key.hex())
                break
        if needle:
            break
    assert needle, name
    locations = []
    for module in modules:
        key = bytes.fromhex(needle['hex'])
        location = module.base+module.code.find(key)-needle['offset']
        actual = module.read(location, length)
        assert all(actual[chunk['offset']:chunk['offset']+len(bytes.fromhex(chunk['hex']))].hex() == chunk['hex']
                   for chunk in chunks), (name, hex(location))
        locations.append(location)
    records[name] = dict(module='game', hint=rva, length=length, chunks=chunks, needle=needle)
    evidence.append(dict(name=name, locations=locations, length=length, unique_in_both=True))

refs = {
    'driver_manager': dict(record='tank_driver_active', offset=0x29, disp=3, size=7),
    'vehicle_manager': dict(record='spin_driver_export', offset=0x93, disp=3, size=7),
    'vehicle_input_manager': dict(record='spin_driver_export', offset=0x378, disp=3, size=7),
}
for key, reference in refs.items():
    rva = 0x6fe480 if reference['record'] == 'tank_driver_active' else definitions[reference['record']]
    expected = 0x3326668 if key == 'driver_manager' else 0x3326458
    for module in modules:
        at = rva+reference['offset']
        instruction = module.read(at, reference['size'])
        assert instruction[:3] in [bytes.fromhex(value) for value in ['4c8b35', '488b05']], (key, instruction.hex())
        assert at+reference['size']+struct.unpack_from('<i', instruction, reference['disp'])[0] == expected
    reference['opcode_hex'] = instruction[:3].hex()
    reference['expected_rva_in_captures'] = expected

source = 'return function(profile,spec)\nlocal records='+lua(records)+'\n'
source += 'for name,d in pairs(records)do spec.records[name]=d;spec.core[#spec.core+1]=name;profile.functions[name]={rva=d.hint}end\n'
source += 'for _,e in ipairs('+lua(edges)+')do spec.edges[#spec.edges+1]=e end\n'
source += 'profile.spin={records=records,refs='+lua(refs)+'}\nreturn profile,spec\nend\n'
(R/'spin_spec.lua').write_text(source, encoding='utf-8')
(R/'spin-native-evidence.json').write_text(json.dumps(dict(captures=captures, witnesses=evidence,
    edges=edges, refs=refs, boundary='Full native code witnesses verified offline. Runtime input and physics remain unverified.'), indent=2), encoding='utf-8')
print('PASS four relocatable steering witnesses,', len(edges), 'call edges and three manager references in both frozen captures')
