"""Offline test of the actual 0xbde53653 notification receiver, not its request sibling.

Captured adapter and animation-manager instructions execute. Entity-ref lookup
and engine animation APIs are stubbed. This verifies calls and no retransmission,
not rendering, packet ordering, remote peer authority or delivered messages.
"""
from pathlib import Path
import os,sys,struct,re,json
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
BUILD=os.environ.get('VSS_TEST_BUILD','25480438')
root=W/'reverse'/('capture-'+BUILD);os.environ['VSS_CAPTURE']=str(root)
from emulate_seats import StaticVM
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
v=StaticVM();u=v.vm
def w(a,f,*x):u.mem_write(a,struct.pack(f,*x))
def reg(r):return u.reg_read(r)
def ret(value=0):
 sp=reg(UC_X86_REG_RSP);pc=struct.unpack('<Q',u.mem_read(sp,8))[0]
 u.reg_write(UC_X86_REG_RAX,value);u.reg_write(UC_X86_REG_RSP,sp+8);u.reg_write(UC_X86_REG_RIP,pc)
module_base=int(re.search(r'game.dll base=(0x[0-9a-f]+)',(root/'capture.txt').read_text())[1],16)
table=0xbc2d1d+struct.unpack('<i',v.mod.read(0xbc2d19,4))[0]
target=struct.unpack('<Q',v.mod.read(table+443*8,8))[0]-module_base
assert target==0xbba250 and target!=0xbbd440
hub,manager,rows,objects,entity,dictionary,hashes,api,methods,args,values=[0x10010000+i*0x8000 for i in range(11)]
w(0x3326e68,'<Q',hub);w(hub+0x3e58,'<I',1);w(hub+0x3e60,'<QI',manager,7)
w(manager+0x48,'<QIII',rows,2,0xffffffff,1);w(rows,'<IIII',0xffffffff,0xffffffff,7,0)
w(manager+0x60,'<Q',objects);w(objects,'<Q',entity);w(entity+8,'<IIII',7,123,1007,0)
w(0x3483c20,'<I',0xffffffff)
w(0x3326de8,'<Q',dictionary);w(dictionary+0x20,'<QI',hashes,4119);w(hashes+1396*4,'<I',0xdab88e64)
w(0x3326308,'<Q',api);w(api+0x18,'<Q',methods)
for off in (0x720,0x350,0x370):w(methods+off,'<Q',0x100e0000+off)
for i,(typ,val)in enumerate(((1,1007),(1,1396),(0,0))):
 w(values+i*8,'<I',val);w(args+i*16,'<IIQ',typ,4,values+i*8)
events=[];unexpected=[]
def hook(u,at,size,_):
 if at==0xfd9ba0:
  assert reg(UC_X86_REG_RDX)==1007;w(reg(UC_X86_REG_RCX),'<I',7);ret()
 elif at==0x100e0720:assert reg(UC_X86_REG_RCX)==123;ret(1)
 elif at==0x100e0350:assert reg(UC_X86_REG_RCX)==123;ret(int(reg(UC_X86_REG_RDX)==0xdab88e64))
 elif at==0x100e0370:events.append((reg(UC_X86_REG_RCX),reg(UC_X86_REG_RDX)));ret()
 elif at in (0xbedb90,0xbde430,0xfdd750):unexpected.append(hex(at));ret()
u.hook_add(UC_HOOK_CODE,hook)
results=[]
for owned in (0,1):
 for present in (False,True):
  for index in (1396,4119):
   events.clear();unexpected.clear();w(entity+0x14,'<I',owned)
   w(rows+8,'<II',7 if present else 0xffffffff,0)
   w(values+8,'<I',index);v.run(target,0,args)
   expected=[(123,0xdab88e64)]if present and index==1396 else []
   assert events==expected,(owned,present,index,events)
   assert not unexpected,unexpected
   results.append(dict(owned=owned,present=present,event_index=index,events=events.copy(),extra_calls=unexpected.copy()))
# Resource-level consequences on the two selected vehicle layers only.
layers=json.loads((W/'animation_resources/avatar_states.json').read_text())
poses=[]
for source,event,final in (([112,68],'frv_enter_boot',[104,60]),([104,60],'frv_enter_front_right',[112,68])):
 actual=[]
 for li,st in zip((0,13),source):
  st=layers[li]['states'][st]['transitions'][event]['target']
  end=layers[li]['states'][st]['transitions'].get('action_end')
  if end:st=end['target']
  actual.append(st)
 assert actual==final;poses.append(dict(source=source,event=event,after_entry_then_end=actual))
out=dict(build=BUILD,boundary=__doc__,registry_index=443,actual_adapter=hex(target),previous_wrong_adapter='0xbbd440',cases=results,resource_vehicle_layers=poses)
(R/('notify-receiver-'+BUILD+'.json')).write_text(json.dumps(out,indent=2))
print('PASS',BUILD,'actual notification receiver8 cases: own/remote, missing entity, event index bounds, no forwarding for false flag; resource vehicle-layer endpoints')

