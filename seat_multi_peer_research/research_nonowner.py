"""Inspect preserved binaries only; no running process or game writes."""
from pathlib import Path
import json, struct, sys
R=Path(__file__).resolve().parent; W=R.parent
sys.path.insert(0,str(W))
from reverse import Module
from capstone.x86 import X86_OP_MEM, X86_REG_RIP
g=Module('game.dll',W/'reverse/capture-25480438');g.md.detail=True
e=Module('helldivers2.exe',W/'reverse/capture-25480438');e.md.detail=True
out=R/'native-nonowner';out.mkdir(exist_ok=True)
pairs={}
ins=list(e.md.disasm(e.read(0x1cce00,0x26e7),0x1cce00))
for a,b in zip(ins,ins[1:]):
 if (a.mnemonic=='lea' and b.mnemonic=='mov' and len(a.operands)==len(b.operands)==2
  and a.operands[1].type==X86_OP_MEM and a.operands[1].mem.base==X86_REG_RIP
  and b.operands[0].type==X86_OP_MEM and b.operands[0].mem.base==X86_REG_RIP
  and a.operands[0].reg==b.operands[1].reg):
  pairs[b.address+b.size+b.operands[0].mem.disp]=a.address+a.size+a.operands[1].mem.disp
authority=0x27cbb90
slots={hex(o):pairs[authority+o]for o in [0x168,0xa0,0xb8]}
print('API_SLOTS',json.dumps(slots))
for key,a in slots.items():
 text=e.dis(a);(out/('exe-api-'+key+'.txt')).write_text(text)
 print('API',key,hex(a),text)
 for i in e.md.disasm(e.read(a,e.function(a)[1]-a),a):
  if i.mnemonic=='call'and i.op_str.startswith('qword ptr [rax +'):
   off=i.operands[0].mem.disp
   pointer=struct.unpack('<Q',e.read(0x1675b70+off,8))[0]
   target=pointer-0x7ff696330000
   (out/('exe-virtual-'+key+'.txt')).write_text(e.dis(target))
   print('VIRTUAL',key,hex(off),hex(target))
for name,a in [('property_enqueue',0xfd97e0),('property_flush',0xfddec0)]:
 (out/(name+'.txt')).write_text(g.dis(a))
refs=g.xrefs([0x3326668])
starts=sorted({f[0]for a,t,f in refs if f and 0x6f0000<=a<0x720000})
print('DRIVER_FUNCTIONS',[(hex(a),hex(g.function(a)[1]-a))for a in starts])
for a in starts:(out/(f'driver-{a:x}.txt')).write_text(g.dis(a))
print('RESULT',str(out))
