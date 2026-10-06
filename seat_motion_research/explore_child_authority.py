"""Read-only captured-code investigation; no live process access."""
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
from reverse import Module
m=Module('game.dll',W/'reverse/capture-25480438')
report=[]
for name,at in [('mounted_joint_tags',0x119a2a0),('related_weapon_lookup',0x5a8870)]:
 bounds=m.function(at)
 if bounds:start,end=bounds[:2]
 else:
  start=at;raw=m.read(at,0x1000);pad=raw.find(b'\xcc'*8);assert pad>=0,'leaf boundary not found';end=at+pad
 body=m.read(start,end-start)
 instructions=list(m.md.disasm(body,start))
 (R/'native-nonowner'/(name+'.txt')).write_text('\n'.join(f'{i.address:08x}: {i.mnemonic:8} {i.op_str}'for i in instructions))
 report.append({'name':name,'rva':hex(start),'length':end-start,'calls':[i.op_str for i in instructions if i.mnemonic=='call'],
  'writes':[f'{i.address:08x}: {i.mnemonic} {i.op_str}'for i in instructions if i.mnemonic.startswith(('mov','stos','xchg'))and '['in i.op_str.split(',')[0]and not any(x in i.op_str.split(',')[0]for x in('rsp','rbp'))]})
print(json.dumps(report,indent=2))
