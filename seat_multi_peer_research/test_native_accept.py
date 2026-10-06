"""Actual native accepted/tick state evolution; external effects are stubbed."""
from pathlib import Path
import os,sys,struct,json
R=Path(__file__).resolve().parent; W=R.parent
base=W/'seat_multi_peer_diagnostic/test_receiver_native.py'
setup=base.read_text().split('results=[]',1)[0]
scope={'__file__':str(base)}
exec(compile(setup,str(base),'exec'),scope)
v,vm,w,n,sm,ss,cs,calls=[scope[k]for k in ['v','vm','w','n','sm','ss','cs','calls']]
scope['stubs'].update([0x607040,0x8399e0,0xbfc950,0x63b120])
result=[]
for owned in (0,1):
 for source,target in [(1,4),(4,1),(4,2),(0,4),(2,0)]:
  vm.mem_write(ss,bytes(64));w(cs,'<I',26);calls.clear()
  role=1 if source==0 else 2 if source==4 else 3
  w(ss,'<IIIIiiii',9,26,role,role,0,source,-1,source);w(ss+0x20,'<i',-1)
  w(0x10016100+0x14,'<I',owned)
  w(0x10080008+0x28,'<I',target)
  v.run(0x63e1a0,sm,0,9,7)
  def seat():return [n(ss+o)for o in (0,4,8,0x14,0x18,0x1c,0x20)]+[bytes(vm.mem_read(ss+0x30,1)).hex()]
  after=seat()
  v.run(0x639b40,sm,0)
  result.append({'owned_avatar':owned,'source':source,'target':target,'after_accept':after,'after_tick':seat(),'calls':calls.copy()})
(R/'native-accept.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
