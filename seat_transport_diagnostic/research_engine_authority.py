"""Recover authority API relationships from preserved code, not a live process.

The concrete engine vtable is a statically identified implementation. It has
NOT yet been observed through session+B390 in this multiplayer capture.
"""
from pathlib import Path
import os, sys, struct, json, hashlib
R=Path(__file__).resolve().parent; W=R.parent
os.environ['VSS_CAPTURE']=str(W/'reverse/capture-25480438')
sys.path.insert(0,str(W))
from reverse import Module
from capstone.x86 import X86_OP_MEM, X86_REG_RIP
m=Module('helldivers2.exe'); m.md.detail=True
out=R/'authority-20260926'; out.mkdir(exist_ok=True)
instructions=list(m.md.disasm(m.read(0x1cce00,0x26e7),0x1cce00))
pairs={}
for a,b in zip(instructions,instructions[1:]):
    if (a.mnemonic=='lea' and b.mnemonic=='mov' and len(a.operands)==len(b.operands)==2
        and a.operands[1].type==X86_OP_MEM and a.operands[1].mem.base==X86_REG_RIP
        and b.operands[0].type==X86_OP_MEM and b.operands[0].mem.base==X86_REG_RIP
        and a.operands[0].reg==b.operands[1].reg):
        pairs[b.address+b.size+b.operands[0].mem.disp]=dict(
            target=a.address+a.size+a.operands[1].mem.disp,lea=a.address,store=b.address)
send_slot=next(k for k,v in pairs.items() if v['target']==0x3502c0)
send_table=send_slot-0x38
assert pairs[send_table+0x40]['target']==0x34ff40
services=next(k for k,v in pairs.items() if v['target']==send_table)-0x38
authority_table=pairs[services+0x40]['target']
slots={hex(o):pairs[authority_table+o] for o in (0x98,0x138,0x140,0x160)}
assert [x['target'] for x in slots.values()]==[0x34cbd0,0x34cd40,0x34cdc0,0x34cee0]
vtable=0x1675b70; base=0x7ff696330000
virtual={hex(o):struct.unpack('<Q',m.read(vtable+o,8))[0]-base
         for o in (0x68,0x98,0xf8,0x110,0x128,0x178)}
assert list(virtual.values())==[0x292bd0,0x292cc0,0x297aa0,0x290040,0x298a00,0x29aea0]
# Constructor explicitly installs this table. No inference from a pointer run.
lea=next(m.md.disasm(m.read(0x28d652,7),0x28d652))
assert lea.address+lea.size+lea.operands[1].mem.disp==vtable
assert m.read(0x28d667,3)==bytes.fromhex('488901')
definitions=[('engine-transfer',0x290040,None),('engine-request',0x298a00,None),
 ('engine-owner',0x29aea0,0x96),('engine-exists',0x297aa0,0x89),
 ('engine-owner-message-receiver',0x299890,None),
 ('engine-session-constructor',0x28d640,None),
 ('engine-local-peer',0x292bd0,5),('engine-coordinator-peer',0x292cc0,8)]
for key,d in slots.items():definitions.append(('engine-api-'+key,d['target'],None))
previous=Module('helldivers2.exe',W/'reverse/capture-25327279')
proofs=[]
for name,a,length in definitions:
    length=length if length is not None else m.function(a)[1]-a
    body=m.read(a,length); assert len(body)==length
    (out/(name+'.asm.txt')).write_text(m.dis(a,length))
    mask=bytearray(b'\1'*length)
    for instruction in m.md.disasm(body,a):
        if any(op.type==X86_OP_MEM and op.mem.base==X86_REG_RIP for op in instruction.operands):
            start=instruction.address-a+instruction.disp_offset
            mask[start:start+instruction.disp_size]=bytes(instruction.disp_size)
    old=previous.read(a,length)
    normalized_equal=len(old)==length and all(x==y or not keep for x,y,keep in zip(body,old,mask))
    assert normalized_equal,(name,'semantic bytes changed, investigate before reuse')
    proofs.append(dict(name=name,rva=hex(a),length=length,sha256=hashlib.sha256(body).hexdigest(),
                       exact_bytes_equal_previous_capture=old==body,
                       equal_after_masking_rip_displacements=normalized_equal,
                       boundary='same-address comparison of two captures; not yet a runtime resolver'))
result=dict(boundary='static relationships only; live concrete vtable and network acceptance unverified',
 services_table_rva=hex(services),send_table_rva=hex(send_table),authority_table_rva=hex(authority_table),
 slots=slots,concrete_vtable_rva=hex(vtable),virtual_slots=virtual,proofs=proofs)
(out/'engine-authority.json').write_text(json.dumps(result,indent=2))
print(json.dumps(dict(services=hex(services),authority_table=hex(authority_table),slots=slots,
                     proofs=len(proofs),unchanged=sum(p['exact_bytes_equal_previous_capture'] for p in proofs))))
