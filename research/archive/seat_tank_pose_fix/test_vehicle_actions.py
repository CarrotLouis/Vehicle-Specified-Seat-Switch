"""Actual dispatcher and five vehicle action bodies; external engine effects stubbed.
This proves action/camera/animation arguments, not live rendering or network acceptance.
"""
from pathlib import Path
import os,struct,json,sys
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
BUILD=os.environ.get('VSS_TEST_BUILD','25480438')
os.environ['VSS_CAPTURE']=str(W/'reverse'/('capture-'+BUILD))
from emulate_seats import StaticVM
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
v=StaticVM();vm=v.vm;calls=[]
defs=[('m102',26,0x1187fb0,[0,1,2,3,5]),('m103',27,0x1189c30,[0,1,2,3]),
 ('m104',28,0x118b300,[0,1,3]),('bastion',43,0x11926d0,[0,1,2,3]),('maelstrom',44,0x1193bf0,[0,1,2,3])]
allowed=[v.mod.function(x)[:2]for x in [0x119b0a0]+[d[2]for d in defs]]
avatar,context=0x10030000,0x10031000
vm.mem_write(avatar+8,struct.pack('<III',7,123,0));vm.mem_write(context+8,struct.pack('<I',9))
vm.mem_write(0x3326308,struct.pack('<Q',0x10032000));vm.mem_write(0x10032018,struct.pack('<Q',0x10033000));vm.mem_write(0x10033260,struct.pack('<Q',0x10034260))
def hook(vm,at,size,user):
 if at==0x20000000 or any(a<=at<b for a,b in allowed):return
 args=[vm.reg_read(r)for r in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9)]
 calls.append(dict(function=hex(at),args=args))
 result=avatar if at==0xfd9d40 else context if at==0x119f910 else 0
 sp=vm.reg_read(UC_X86_REG_RSP);target=struct.unpack('<Q',vm.mem_read(sp,8))[0]
 vm.reg_write(UC_X86_REG_RAX,result);vm.reg_write(UC_X86_REG_RSP,sp+8);vm.reg_write(UC_X86_REG_RIP,target)
vm.hook_add(UC_HOOK_CODE,hook)
rows=[]
for name,layout,body,restores in defs:
 for seat,action in enumerate(restores):
  calls.clear();v.run(0x119b0a0,layout,7,action,seat)
  assert calls and any(c['function']=='0xfd9d40'and c['args'][0]==7 for c in calls)
  events=[c['args'][1]for c in calls if c['function']=='0x119fec0']
  rows.append(dict(vehicle=name,layout=layout,seat=seat,action=action,events=events,calls=calls.copy()))
prepared=[]
for name,layout,action,seat in [('m102',26,4,4),('m104',28,2,2)]:
 calls.clear();v.run(0x119b0a0,layout,7,action,seat)
 events=[c['args'][1]for c in calls if c['function']=='0x119fec0']
 assert events==[0xe86f3c8c]
 assert [c['args'][2]for c in calls if c['function']=='0x119fc60']==[281788028]
 prepared.append(dict(vehicle=name,action=action,seat=seat,events=events,calls=calls.copy()))
for row in rows:
 if row['vehicle'] in('m102','m104')and row['seat']==(4 if row['vehicle']=='m102'else 2):
  assert row['events']==[] and any(c['function']=='0x11b5550'for c in row['calls'])
(R/('vehicle-actions-'+BUILD+'.json')).write_text(json.dumps(dict(boundary=__doc__,build=BUILD,restores=rows,prepared=prepared),indent=2))
print('PASS',BUILD,len(rows),'real five-vehicle restore actions plus two FRV mounted preparations; external effects stubbed')
for row in rows:
 if row['vehicle'] in('bastion','maelstrom'):
  print(row['vehicle'],row['seat'],'native animation events:',[hex(x)for x in row['events']])
