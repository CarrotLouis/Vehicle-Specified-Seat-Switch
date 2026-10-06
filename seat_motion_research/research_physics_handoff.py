"""Offline actor/control handoff paths in immutable code, no process access."""
from pathlib import Path
import sys,json,struct,re
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
from reverse import Module
from capstone.x86 import X86_OP_MEM,X86_REG_RIP
D=R/'native-physics-handoff';D.mkdir(exist_ok=True)
cap=W/'reverse/capture-25480438'
g,e=Module('game.dll',cap),Module('helldivers2.exe',cap)
g.md.detail=e.md.detail=True
def save(m,a,size=None):
 f=m.function(a);length=size if size else min(f[1]-f[0],12000)if f else 256
 start=a if size or not f else f[0]
 (D/f'{"game"if m==g else"engine"}-{a:x}.txt').write_text(m.dis(start,length),encoding='utf-8')
 return dict(requested=hex(a),function=[hex(x)for x in f]if f else None,decoded_start=hex(start),bytes=length)
refs=[]
for at in (0x713f50,0x7152f0,0x719a20,0x71b410,0x71b060):
 f=g.function(at);body=g.read(f[0],min(f[1]-f[0],16000))
 for i in g.md.disasm(body,f[0]):
  if i.mnemonic=='mov'and len(i.operands)>1 and i.operands[1].type==X86_OP_MEM and i.operands[1].mem.base==X86_REG_RIP:
   target=i.address+i.size+i.operands[1].mem.disp
   if 0x3326300<=target<=0x3326700:refs.append(dict(at=hex(i.address),global_=hex(target),instruction=i.mnemonic+' '+i.op_str))
actors=[0x799540,0x7999a0,0x799de0,0x7951b0]
xrefs=e.xrefs(actors)
index=dict(game_actor_refs=refs,engine_actor_function_refs=[(hex(a),hex(t),[hex(x)for x in f]if f else None)for a,t,f in xrefs],
 engine_actor_callers=e.callers(actors))
fn=[]
for _,_,f in xrefs:
 if f and f[0]not in fn:fn.append(f[0]);save(e,f[0])
# Relevant engine strings only; scan saved sections, not live memory.
strings=[]
for r,b in e.sections:
 for m in re.finditer(rb'[ -~]{5,}',b):
  s=m.group().decode('ascii')
  if re.search(r'^(Actor\.(set_|get_)|set_kinematic|set_dynamic|.*ownership.*|.*kinematic.*)$',s,re.I):
   if len(s)<180:strings.append([hex(r+m.start()),s])
index['strings']=strings
api_base=0x27cd910
bindings=[]
instructions=list(e.md.disasm(e.read(0x7800b8,0x780352-0x7800b8),0x7800b8))
for a,b in zip(instructions,instructions[1:]):
 if a.mnemonic=='lea'and b.mnemonic=='mov'and a.op_str.startswith('rax, [rip')and b.op_str.endswith(', rax'):
  value=a.address+a.size+a.operands[1].mem.disp
  slot=b.address+b.size+b.operands[0].mem.disp-api_base
  bindings.append(dict(slot=hex(slot),function=hex(value),rva_function=e.function(value)))
  if slot in (0x70,0xa0,0xb8,0x98,0xa8):save(e,value)
index['actor_api_bindings']=bindings
save(g,0x799790)
(D/'index.json').write_text(json.dumps(index,indent=2),encoding='utf-8')
print(json.dumps(dict(actor_api_bindings=bindings,engine_actor_refs=index['engine_actor_function_refs'],strings=strings[:65]),indent=2))
