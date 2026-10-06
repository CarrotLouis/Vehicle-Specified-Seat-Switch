"""Execute the captured action dispatcher; external action effects are stubbed."""
from pathlib import Path
import os,struct,json,sys
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
BUILD=os.environ.get('VSS_TEST_BUILD','25480438')
os.environ['VSS_CAPTURE']=str(W/'reverse'/('capture-'+BUILD))
from emulate_seats import StaticVM
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
v=StaticVM();vm=v.vm;calls=[]
start,end,*_=v.mod.function(0x119b0a0)
avatar,context=0x10030000,0x10031000
vm.mem_write(avatar+8,struct.pack('<III',7,123,0));vm.mem_write(context+8,struct.pack('<I',9))
def hook(vm,at,size,user):
 if at==0x20000000 or start<=at<end:return
 args=[vm.reg_read(r)for r in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9)]
 calls.append(dict(function=hex(at),args=args))
 result=avatar if at==0xfd9d40 else context if at==0x119f910 else 0
 sp=vm.reg_read(UC_X86_REG_RSP);target=struct.unpack('<Q',vm.mem_read(sp,8))[0]
 vm.reg_write(UC_X86_REG_RAX,result);vm.reg_write(UC_X86_REG_RSP,sp+8);vm.reg_write(UC_X86_REG_RIP,target)
vm.hook_add(UC_HOOK_CODE,hook)
rows=[]
for name,layout in [('m102',26),('m103',27),('m104',28),('bastion',43),('maelstrom',44)]:
 calls.clear();v.run(0x119b0a0,layout,7,0,0)
 rows.append(dict(vehicle=name,layout=layout,calls=calls.copy()))
 print(name,[(c['function'],c['args'])for c in calls])
(R/'batch-dispatch.json').write_text(json.dumps(rows,indent=2))
