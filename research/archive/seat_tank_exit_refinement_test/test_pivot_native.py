"""Execute captured pivot latch/load/exit/smoothing blocks, no live physics."""
from pathlib import Path
import json,os,struct,sys
R=Path(__file__).resolve().parent;W=R.parent
build=os.environ.get('VSS_TEST_BUILD','25480438')
os.environ['VSS_CAPTURE']=str(W/'reverse'/('capture-'+build));sys.path.insert(0,str(W))
from emulate_seats import StaticVM
from unicorn.x86_const import *
s=StaticVM();vm,m=s.vm,s.mod;m.md.detail=True
manager,replica,inputs,asset,frame,runtime=[0x10010000+i*0x2000 for i in range(6)]
def f(x):return int.from_bytes(struct.pack('<f',x),'little')
def store(a,x):vm.mem_write(a,struct.pack('<f',x))
vm.mem_write(manager+0x78,struct.pack('<Q',replica))
vm.mem_write(frame-0x68,struct.pack('<Q',manager));vm.mem_write(frame-0x50,struct.pack('<Q',replica))
vm.mem_write(asset+0x1c4,b'\1')
for o,value in [(0x16c,.45*5),(0x174,5),(0x17c,5)]:store(asset+o,value)
absolute_float=int.from_bytes(struct.pack('<4I',*[0x7fffffff]*4),'little')
absolute_double=int.from_bytes(struct.pack('<2Q',*[0x7fffffffffffffff]*2),'little')
def run(mode,previous=0,vertical=0,speed=0,steps=1,initial_steer=0,initial_throttle=0):
 vm.mem_write(replica+0x50,bytes([mode]));vm.mem_write(inputs,b'\0'*16)
 store(inputs,initial_steer);store(inputs+4,initial_throttle)
 vm.mem_write(replica+0x34,struct.pack('<3f',previous,0,0))
 observed=[]
 for _ in range(steps):
  for reg,value in [(UC_X86_REG_RBP,frame),(UC_X86_REG_RBX,manager),(UC_X86_REG_R12,asset),
   (UC_X86_REG_R15,0),(UC_X86_REG_RSI,inputs),(UC_X86_REG_R13,runtime),
   (UC_X86_REG_RDI,0),(UC_X86_REG_XMM11,f(.016)),(UC_X86_REG_XMM12,f(5)),
   (UC_X86_REG_XMM13,0),(UC_X86_REG_XMM14,f(speed)),(UC_X86_REG_XMM9,absolute_float),
   (UC_X86_REG_XMM10,absolute_double)]:vm.reg_write(reg,value)
  # Exact native +50 load; stop before external engine/body accessors.
  vm.emu_start(0x715571,0x71558d,count=30);assert vm.reg_read(UC_X86_REG_RIP)==0x71558d
  steer,throttle,brake=struct.unpack('<3f',vm.mem_read(inputs,12))
  for reg,value in [(UC_X86_REG_XMM6,f(steer)),(UC_X86_REG_XMM7,f(throttle)),
   (UC_X86_REG_XMM8,f(brake)),(UC_X86_REG_XMM2,f(vertical))]:vm.reg_write(reg,value)
  # Explicit engine double supplies the observed actor's up-vector component.
  store(frame+0xa44,1)
  vm.emu_start(0x715628,0x7159fb,count=1500);assert vm.reg_read(UC_X86_REG_RIP)==0x7159fb
  values=struct.unpack('<3f',vm.mem_read(inputs,12))
  observed.append(values)
  vm.mem_write(replica+0x34,struct.pack('<3f',*values))
  # Exact flag-store instruction; deliberately stop before property send.
  vm.reg_write(UC_X86_REG_RAX,replica);vm.reg_write(UC_X86_REG_R15,0);vm.reg_write(UC_X86_REG_RBP,frame)
  vm.emu_start(0x716036,0x71603f,count=10);assert vm.reg_read(UC_X86_REG_RIP)==0x71603f
 return {'final':observed[-1],'pivot_mode':vm.mem_read(replica+0x50,1)[0],'samples':observed}
cases=[]
for speed,vertical in [(0,0),(.6,0),(0,.4),(.6,.4)]:
 for mode in [0,1]:
  result=run(mode,speed=speed,vertical=vertical,steps=35)
  if mode==0:assert result['pivot_mode']==0 and result['final']==(0,0,0),result
  elif speed>=.5 or vertical>=.3:assert result['final'][0]>0 and result['final'][2]>0,result
  else:assert result['pivot_mode']==0 and result['final']==(0,0,0),result
  cases.append({'mode_before':mode,'synthetic_speed':speed,'synthetic_vertical':vertical,'result':result})
for previous in [-1,1]:
 result=run(1,previous=previous,speed=.6)
 assert result['final'][0]*previous>0 and result['final'][2]>0
 cases.append({'mode_before':1,'steer_history':previous,'result':result})
assert cases[3]['result']['samples'][0][0]>0
for mode in [0,1]:
 result=run(mode,speed=.6,initial_throttle=.6)
 assert (result['final'][0]==0 and result['final'][2]==0)if mode==0 else result['final'][0]>0 and result['final'][2]>0
 cases.append({'mode_before':mode,'actual_capture_like_throttle':.6,'synthetic_speed':.6,'result':result})
for sign in [-1,1]:
 result=run(0,previous=sign,initial_steer=sign)
 assert result['pivot_mode']==1 and result['final'][0]==sign
 cases.append({'mode_before':0,'new_normal_driver_steer':sign,'native_reenabled_pivot_mode':True,'result':result})
(R/f'native-pivot-{build}.json').write_text(json.dumps({'build':build,'actual_captured_instructions':True,
 'external_actor_inputs':'explicit doubles','real_physics_or_network':False,'cases':cases},indent=2))
print('PASS',build,len(cases),'native pivot load/branch/flag-store/smoothing cases: retained mode recreates RIGHT steer from zero above thresholds; mode clear keeps zero. Actual gameplay PENDING')
