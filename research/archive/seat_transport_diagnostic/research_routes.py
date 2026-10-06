"""Inspect immutable build25480438 capture and emulate pure route lookups only."""
from pathlib import Path
import os,sys,json,struct,hashlib
W=Path(__file__).resolve().parent.parent
os.environ['VSS_CAPTURE']=str(W/'reverse/capture-25480438')
sys.path.insert(0,str(W))
from reverse import Module
from emulate_seats import StaticVM
out=Path(__file__).resolve().parent/'multiplayer-20260925-152652';out.mkdir(exist_ok=True)
m=Module();vm=StaticVM();proofs={}
for label,rva in [('accepted_adapter',0xba8020),('accepted_handler',0x63e1a0),('switch_adapter',0xbb6f90),('switch_dispatch',0xb86840),('state_update',0x639b40),('join_state_sender',0x63eda0),('snapshot_restore',0x63eb10),('transition_restore',0x63ecc0),('entry_reserve',0x636a30)]:
 f=m.function(rva);assert f[0]==rva
 data=m.read(f[0],f[1]-f[0]);ins=list(m.md.disasm(data,rva))
 calls=[int(i.op_str,16)for i in ins if i.mnemonic=='call'and i.op_str.startswith('0x')]
 proofs[label]=dict(rva=hex(rva),end=hex(f[1]),sha256=hashlib.sha256(data).hexdigest(),calls=[hex(c)for c in calls])
 (out/(label+'.asm.txt')).write_text(m.dis(rva),encoding='utf-8')
assert '0x63e1a0'in proofs['accepted_adapter']['calls']
assert all(c in proofs['switch_dispatch']['calls']for c in ['0x636430','0x6365b0','0x6349b0','0x6344d0','0xbe22b0','0x635710'])
assert '0x1196dc0'in proofs['state_update']['calls']and '0x63dd10'in proofs['state_update']['calls']
assert '0x63dd10'not in proofs['snapshot_restore']['calls']
routes={};missing=valid=0
for name,kind,n in [('m102',26,5),('m103',27,4),('m104',28,3),('bastion',43,4),('maelstrom',44,4),('tanker',33,2)]:
 rows=[]
 for src in range(n):
  for dst in range(n):
   if src==dst:continue
   vm.vm.mem_write(0x10001000,struct.pack('<I',src))
   a=vm.run(0x1196dc0,kind,0x10001000,dst)&0xffffffff
   nxt=struct.unpack('<I',vm.vm.mem_read(0x10001000,4))[0]
   if a==0xffffffff:missing+=1
   else:valid+=1
   rows.append(dict(source=src,target=dst,next_node=nxt,action=a if a<0x80000000 else a-0x100000000))
 routes[name]=rows
report=dict(capture='25480438',proofs=proofs,routes=routes,valid_routes=valid,missing_routes=missing)
assert valid==24 and missing==40
(out/'static-evidence.json').write_text(json.dumps(report,indent=2))
print(json.dumps(dict(valid_routes=valid,missing_routes=missing,evidence=str(out/'static-evidence.json'))))
