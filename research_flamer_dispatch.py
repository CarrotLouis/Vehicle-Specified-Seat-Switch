"""Offline captured dispatch only; external avatar/engine effects stubbed."""
from pathlib import Path
import os,struct,json
W=Path(__file__).resolve().parent
os.environ['VSS_CAPTURE']=str(W/'reverse/capture-25480438')
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
for layout,action,seat in [(26,4,4),(28,2,2),(26,5,4),(28,3,2)]:
 calls.clear();v.run(0x119b0a0,layout,7,action,seat)
 rows.append(dict(layout=layout,action=action,seat=seat,calls=calls.copy()))
(W/'flamer-dispatch.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
