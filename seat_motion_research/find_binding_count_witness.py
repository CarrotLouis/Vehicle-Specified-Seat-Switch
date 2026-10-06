"""Static image-only references to the already-known weapon manager global."""
import os,sys,re,json
from pathlib import Path
W=Path(__file__).resolve().parent.parent
os.environ['VSS_CAPTURE']=str(W/'reverse/capture-25480438');sys.path.insert(0,str(W))
from emulate_seats import StaticVM
m=StaticVM().mod;m.md.detail=True
i=next(m.md.disasm(m.read(0x11a7f9d,15),0x11a7f9d));root=i.address+i.size+i.disp
found=[]
for base,data in m.sections:
 for hit in re.finditer(rb'[\x48\x4c]\x8b[\x05\x0d\x15\x1d\x25\x2d\x35\x3d].{4}',data,re.S):
  at=base+hit.start();raw=hit.group()
  if at+7+int.from_bytes(raw[3:7],'little',signed=True)!=root:continue
  reg=next(m.md.disasm(m.read(at,7),at)).op_str.split(',')[0]
  instructions=list(m.md.disasm(m.read(at,180),at))
  relevant=[z for z in instructions if re.search(r'\['+reg+r' \+ 0x(18|1c|20)\]',z.op_str)]
  if relevant:
   body='\n'.join(f'{z.address:08x}: {z.mnemonic:8} {z.op_str}'for z in instructions)
   found.append({'rva':at,'reg':reg,'body':body})
print('weapon_root',hex(root),'count_witnesses',len(found))
(W/'seat_motion_research/binding-count-witnesses.json').write_text(json.dumps(found,indent=2))
for row in found[:6]:print(row['body'])
