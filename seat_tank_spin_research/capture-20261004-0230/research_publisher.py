"""Frozen native publisher disassembly and direct-call metadata, no live access."""
from pathlib import Path
import hashlib
import json
import re
import struct
import sys

R=Path(__file__).resolve().parent
W=R.parent.parent
sys.path.insert(0,str(W))
from reverse import Module
from capstone.x86 import X86_OP_MEM,X86_REG_RIP

report=[]
out=R/'native'
out.mkdir(exist_ok=True)
for build in ['25327279','25480438']:
    module=Module('game.dll',W/'reverse'/('capture-'+build))
    rows=[]
    for address in [0xfd97e0,0xfddec0,0xa7d700]:
        function=module.function(address)
        assert function and function[0]==address,(hex(address),function)
        length=function[1]-function[0]
        assert length<=0x10000
        body=module.read(address,length)
        destination=out/f'{build}-{address:x}.txt'
        destination.write_text(module.dis(address,length),encoding='utf-8')
        calls=[]
        module.md.detail=True
        for instruction in module.md.disasm(body,address):
            if instruction.mnemonic in ['call','jmp'] and instruction.op_str.startswith('0x'):
                target=int(instruction.op_str,16)
                if not address<=target<function[1]:
                    calls.append(dict(at=instruction.address,target=target,function=module.function(target)))
        rows.append(dict(address=address,length=length,sha256=hashlib.sha256(body).hexdigest(),
                         path=str(destination),calls=calls,callers=module.callers([address])))
        print(build,hex(address),'bytes',length,'direct_calls',len(calls),
              'first_calls',[(hex(row['at']),hex(row['target']))for row in calls[:8]])
    report.append(dict(build=build,functions=rows))
    engine=Module('helldivers2.exe',W/'reverse'/('capture-'+build))
    engine.md.detail=True
    instructions=list(engine.md.disasm(engine.read(0x1cce00,0x26e7),0x1cce00))
    pairs={}
    for a,b in zip(instructions,instructions[1:]):
        if (a.mnemonic=='lea'and b.mnemonic=='mov'and len(a.operands)==len(b.operands)==2
            and a.operands[1].type==X86_OP_MEM and a.operands[1].mem.base==X86_REG_RIP
            and b.operands[0].type==X86_OP_MEM and b.operands[0].mem.base==X86_REG_RIP
            and a.operands[0].reg==b.operands[1].reg):
            pairs[b.address+b.size+b.operands[0].mem.disp]=a.address+a.size+a.operands[1].mem.disp
    api_table=0x27cbb90
    slots={hex(offset):pairs[api_table+offset]for offset in [0x168,0xa0,0xb8]}
    property_setter=slots['0xa0']
    setter_function=engine.function(property_setter)
    setter_calls=[instruction.operands[0].imm for instruction in engine.md.disasm(
        engine.read(property_setter,setter_function[1]-property_setter),property_setter)
        if instruction.mnemonic=='call'and instruction.op_str.startswith('0x')]
    assert len(setter_calls)==1,setter_calls
    engine_functions=[]
    captured_report=(W/'reverse'/('capture-'+build)/'capture.txt').read_text(encoding='utf-8')
    captured_base=int(re.search(r'helldivers2.exe base=0x([0-9a-f]+)',captured_report)[1],16)
    virtuals={hex(offset):struct.unpack('<Q',engine.read(0x1675b70+offset,8))[0]-captured_base
              for offset in [8,0xf0,0xf8,0x118,0x170]}
    for address in sorted(set(slots.values())|set(setter_calls)|set(virtuals.values())|{0x29c840,0x297be0,0x174430}):
        fn=engine.function(address)
        if fn:
            assert fn[0]==address,(hex(address),fn)
            length=fn[1]-fn[0]
        else:
            length=32
            assert engine.read(address,length),(hex(address),'missing leaf bytes')
        assert length<=0x10000
        destination=out/f'{build}-engine-{address:x}.txt'
        destination.write_text(engine.dis(address,length),encoding='utf-8')
        engine_functions.append(dict(address=address,length=length,path=str(destination)))
    report[-1]['engine_api_slots']=slots
    report[-1]['engine_property_setter_helper']=setter_calls[0]
    report[-1]['captured_engine_base']=captured_base
    report[-1]['engine_network_virtuals']=virtuals
    report[-1]['engine_functions']=engine_functions
    print(build,'network_api_slots',slots,'engine_functions',[(hex(row['address']),row['length'])for row in engine_functions])
(R/'publisher-native-index.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
