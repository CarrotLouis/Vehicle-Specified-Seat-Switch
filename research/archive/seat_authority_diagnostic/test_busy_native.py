"""Native caller selects entity+10h; execute it and the busy lookup offline."""
from pathlib import Path
import sys,struct,json
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent))
from reverse import Module
from unicorn import Uc,UC_ARCH_X86,UC_MODE_64,UC_HOOK_CODE
from unicorn.x86_const import *
results=[]
for build in ('25327279','25480438'):
 m=Module('game.dll',R.parent/'reverse'/('capture-'+build));vm=Uc(UC_ARCH_X86,UC_MODE_64)
 vm.mem_map(0,0x5000000)
 for address,data in m.sections:vm.mem_write(address,data)
 vm.mem_map(0x10000000,0x100000)
 E,MANAGER,ROWS,ENTITY,ROOT,SERVICES=0x10010000,0x10020000,0x10030000,0x10040000,0x10050000,0x10060000
 STOP=0x100ff000;STACK=0x100f0008;LOCK=STOP+0x10;UNLOCK=STOP+0x20
 def put(a,fmt,*v):vm.mem_write(a,struct.pack(fmt,*v))
 def relative(rva):return rva+7+struct.unpack('<i',m.read(rva+3,4))[0]
 def ret(value=0):
  sp=vm.reg_read(UC_X86_REG_RSP);dest=struct.unpack('<Q',vm.mem_read(sp,8))[0]
  vm.reg_write(UC_X86_REG_RAX,value);vm.reg_write(UC_X86_REG_RSP,sp+8);vm.reg_write(UC_X86_REG_RIP,dest)
 mode='caller';observed=[]
 def hook(vm,a,size,user):
  if a==0xfd9d40:ret(ENTITY)
  elif a==0xfde390 and mode=='caller':
   observed.append(vm.reg_read(UC_X86_REG_RDX));vm.emu_stop()
  elif a in (LOCK,UNLOCK):ret()
 vm.hook_add(UC_HOOK_CODE,hook)
 put(relative(0x6373ad),'<Q',ROOT);put(ROOT+8,'<Q',MANAGER)
 put(relative(0xfde3b0),'<Q',SERVICES)
 put(SERVICES+0x70,'<Q',LOCK);put(SERVICES+0x78,'<Q',UNLOCK);put(MANAGER,'<Q',E)
 put(ENTITY,'<QIIII',0,829,8391232,4112,1)
 def start():
  vm.reg_write(UC_X86_REG_RSP,STACK);put(STACK,'<Q',STOP)
 for flag in (0,1):
  for collision in (False,True):
   mode='caller';start();vm.reg_write(UC_X86_REG_R8,829)
   vm.emu_start(0x637360,STOP,count=1000)
   assert vm.reg_read(UC_X86_REG_RIP)==0xfde390 and observed[-1]==4112
   assert vm.reg_read(UC_X86_REG_RCX)==MANAGER
   put(MANAGER+0xb020,'<QIII',ROWS,8,0xffffffff,1)
   for i in range(8):put(ROWS+i*8,'<II',0xffffffff,0xffffffff)
   # The wrong unit key is either absent or points to the opposite flag.
   slot=1 if collision else 0
   if collision:put(ROWS,'<II',8391232,4)
   put(ROWS+slot*8,'<II',4112,3)
   put(MANAGER+0x201c+3,'<B',flag);put(MANAGER+0x201c+4,'<B',1-flag)
   mode='lookup';start();vm.reg_write(UC_X86_REG_RCX,MANAGER);vm.reg_write(UC_X86_REG_RDX,observed[-1])
   vm.emu_start(0xfde390,STOP,count=1000)
   assert vm.reg_read(UC_X86_REG_RIP)==STOP and vm.reg_read(UC_X86_REG_RAX)==flag
   results.append(dict(build=build,network_key=4112,unit_key=8391232,collision=collision,busy=flag))
(R/'native_busy_tests.json').write_text(json.dumps(results,indent=2))
print('PASS',len(results),'native seat caller + busy lookup cases; distinct id/unit/network_unit, true/false, collision/decoy')
