"""Actual M102/M104 action dispatch and leaf-call arguments; engine effects stubbed.
No live game, no network/rendering proof. Confirms preparation event and restore branch.
"""
from pathlib import Path
import os,struct,json,sys
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
BUILD=os.environ.get('VSS_TEST_BUILD','25480438')
os.environ['VSS_CAPTURE']=str(W/'reverse'/('capture-'+BUILD))
from emulate_seats import StaticVM
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
v=StaticVM();vm=v.vm;calls=[];allowed=[v.mod.function(x)[:2]for x in (0x119b0a0,0x1187fb0,0x118b300)]
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
for layout,action,seat,prepare in [(26,4,4,True),(28,2,2,True),(26,5,4,False),(28,3,2,False)]:
 calls.clear();v.run(0x119b0a0,layout,7,action,seat)
 events=[c['args'][1]for c in calls if c['function']=='0x119fec0']
 assert events==([0xe86f3c8c]if prepare else [])
 cameras=[c['args'][2]for c in calls if c['function']=='0x119fc60']
 assert cameras==([281788028]if prepare else [776314404]),cameras
 assert any(c['function']=='0x11b5550'for c in calls)==(not prepare)
 rows.append(dict(layout=layout,action=action,seat=seat,events=events,calls=calls.copy()))
# M104 action2 has the same relevant camera/body/event calls as M102 action4.
omit={'0xfd9d40','0x119f910'}
left=[c for c in rows[0]['calls']if c['function']not in omit and c['function']!='0x'+hex(0x1188005+struct.unpack('<i',v.mod.read(0x1188001,4))[0])[2:]]
right=[c for c in rows[1]['calls']if c['function']not in omit]
assert left==right
(R/('flamer-dispatch-'+BUILD+'.json')).write_text(json.dumps(dict(boundary=__doc__,build=BUILD,cases=rows),indent=2))
print('PASS',BUILD,'M104 action2 preparation matches M102 action4; action3 restore has no entry event')
