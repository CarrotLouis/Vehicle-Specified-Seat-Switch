"""Run preserved tank exit/driver-completion and driver cleanup machine code.
External engine/audio/network effects are stubbed, not live physics evidence.
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
manager,rows,owners,entity,runtime,asset=0x10010000,0x10011000,0x10012000,0x10013000,0x10014000,0x10020000
engine,unit_api=0x10030000,0x10031000
def u(a,n):vm.mem_write(a,struct.pack('<I',n))
def q(a,n):vm.mem_write(a,struct.pack('<Q',n))
q(0x3326668,manager);q(manager+0x38,rows);u(manager+0x40,4);u(manager+0x44,0xffffffff);u(manager+0x48,1)
for i in range(4):u(rows+i*8,0xffffffff)
u(rows+8,9);u(rows+12,1);q(manager+0x50,owners);q(owners+8,entity);q(manager+0x68,runtime)
u(entity+8,9);u(entity+12,909)
q(0x3326308,engine);q(engine+0x18,unit_api)
for off in [0x88,0x6d8]:q(unit_api+off,0x10090000+off)
# Native 5b8790 owns the actual per-component scale loop; fill two unrelated
# motor records and prove only this vehicle's four active scalars are zeroed.
motors,mmap,mrows=0x10040000,0x10041000,0x10042000
q(0x3326a28,motors);q(motors+0x18,mmap);u(motors+0x20,4);u(motors+0x24,0xffffffff);u(motors+0x28,1)
for i in range(4):u(mmap+i*8,0xffffffff)
u(mmap+8,9);u(mmap+12,1);q(motors+0x38,mrows)
allowed=[v.mod.function(a)[:2]for a in [0x6fe480,0x5b8790]]
def hook(vm,at,size,user):
 if at==0x20000000 or any(a<=at<b for a,b in allowed):return
 args=[vm.reg_read(r)for r in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9)]
 calls.append(dict(function=hex(at),args=args))
 result=asset if at==0x4fa7a0 else 0x10025000 if at==0x6fea30 else 0
 sp=vm.reg_read(UC_X86_REG_RSP);target=struct.unpack('<Q',vm.mem_read(sp,8))[0]
 vm.reg_write(UC_X86_REG_RAX,result);vm.reg_write(UC_X86_REG_RSP,sp+8);vm.reg_write(UC_X86_REG_RIP,target)
vm.hook_add(UC_HOOK_CODE,hook)
results=[]
for active in [0,1]:
 vm.mem_write(runtime,b'\x5a'*(0xd28*2));vm.mem_write(runtime+0xd28+0xd18,bytes([active]))
 vm.mem_write(mrows,b'\x5a'*0x58);u(mrows,2);u(mrows+0x2c,4)
 vm.mem_write(mrows+0x2c+0x18,struct.pack('<4f',1,-1,.5,-.5))
 before=bytes(vm.mem_read(runtime,0xd28*2));mot_before=bytes(vm.mem_read(mrows,0x58));calls.clear()
 v.run(0x6fe480,0,9,0)
 after=bytes(vm.mem_read(runtime,0xd28*2));index=0xd28+0xd18
 assert after==before[:index]+b'\0'+before[index+1:]
 assert calls[-1]['function']=='0x7056f0'and calls[-1]['args'][1:3]==[9,0]
 mot_after=bytes(vm.mem_read(mrows,0x58))
 if active:
  at=0x2c+0x18;assert mot_after==mot_before[:at]+bytes(16)+mot_before[at+16:]
 else:assert mot_after==mot_before
 results.append(dict(before_active=active,after_active=0,motor_scales_zeroed=bool(active),calls=calls.copy()))

# Recover the normal driver-exit action from each native jump table; driver
# completion 0 re-enables it. External calls are inspected, not performed.
avatar,context=0x10050000,0x10051000;u(avatar+8,7);u(context+8,9)
for layout,action_body,complete in [(43,0x11926d0,0x1193300),(44,0x1193bf0,0x1194860)]:
 allowed[:]=[v.mod.function(a)[:2]for a in [action_body,complete]]
 # Replace the external resolver return for these two vehicle bodies.
 def resolver_hook(vm,at,size,user):
  if at==0x20000000 or any(a<=at<b for a,b in allowed):return
  args=[vm.reg_read(r)for r in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9)]
  calls.append(dict(function=hex(at),args=args))
  result=avatar if at==0xfd9d40 else context if at in [0x119f910,0x11b52b0]else 0
  sp=vm.reg_read(UC_X86_REG_RSP);target=struct.unpack('<Q',vm.mem_read(sp,8))[0]
  vm.reg_write(UC_X86_REG_RAX,result);vm.reg_write(UC_X86_REG_RSP,sp+8);vm.reg_write(UC_X86_REG_RIP,target)
 # Separate VM for action assertions so one handler owns external calls.
 a=StaticVM();av=a.vm
 av.mem_write(avatar+8,struct.pack('<I',7));av.mem_write(context+8,struct.pack('<I',9))
 av.mem_write(0x3326308,struct.pack('<Q',engine));av.mem_write(engine+0x18,struct.pack('<Q',unit_api))
 av.mem_write(unit_api+0x260,struct.pack('<Q',0x10090260))
 av.hook_add(UC_HOOK_CODE,resolver_hook)
 table=0x11932b8 if layout==43 else 0x119480c
 exits=[i for i in range(18)if struct.unpack('<I',a.mod.read(table+i*4,4))[0]==(0x1192b92 if layout==43 else 0x11940d9)]
 assert len(exits)==1
 calls.clear();a.run(action_body,7,exits[0],0)
 event=[c for c in calls if c['function']=='0x6fe480'];assert len(event)==1 and event[0]['args'][1:3]==[9,0]
 results.append(dict(layout=layout,native_driver_exit_action=exits[0],driver_active_argument=False))
 calls.clear();a.run(complete,7,0)
 event=[c for c in calls if c['function']=='0x6fe480'];assert len(event)==1 and event[0]['args'][1]==9 and event[0]['args'][2]&255==1,(layout,calls)
(R/('tank-native-'+BUILD+'.json')).write_text(json.dumps(dict(build=BUILD,boundary=__doc__,results=results),indent=2))
print('PASS',BUILD,'actual tank exit/completion false/true arguments, native driver active cleanup and four motor scalars, unrelated records preserved; external effects stubbed')
