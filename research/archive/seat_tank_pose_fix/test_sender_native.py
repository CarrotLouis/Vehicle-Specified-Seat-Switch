"""Actual captured wrappers in Unicorn; transport and ID resolver intercepted.
Checks Win64 argument placement and serializer descriptors, not wire delivery.
"""
from pathlib import Path
import os,sys,struct,json
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
BUILD=os.environ.get('VSS_TEST_BUILD','25480438')
os.environ['VSS_CAPTURE']=str(W/'reverse'/('capture-'+BUILD))
from emulate_seats import StaticVM
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
v=StaticVM();vm=v.vm;events=[]
peer=0xfedcba9876543210
def reg(r):return vm.reg_read(r)
def w(a,f,*x):vm.mem_write(a,struct.pack(f,*x))
def ret(value=0):
 sp=reg(UC_X86_REG_RSP);pc=struct.unpack('<Q',vm.mem_read(sp,8))[0]
 vm.reg_write(UC_X86_REG_RAX,value);vm.reg_write(UC_X86_REG_RSP,sp+8);vm.reg_write(UC_X86_REG_RIP,pc)
def hook(vm,a,size,_):
 if a==0xfd9a40:
  eid=reg(UC_X86_REG_RCX)&0xffffffff;assert eid in (7,9)
  at=0x10040000+eid*4;w(at,'<I',eid+1000);ret(at)
 elif a==0xbde430:
  assert reg(UC_X86_REG_RDX)==peer
  n=reg(UC_X86_REG_R9);assert n in(4,5)
  at=reg(UC_X86_REG_R8);rows=[]
  for i in range(n):
   t,size,p=struct.unpack('<IIQ',vm.mem_read(at+i*16,16));assert size==4
   rows.append((t,size,struct.unpack('<I',vm.mem_read(p,4))[0]))
  events.append((reg(UC_X86_REG_RCX)&0xffffffff,rows));ret()
 elif a==0x20886a0:ret()
vm.hook_add(UC_HOOK_CODE,hook)
for target in (1,4):
 w(0x10080008+0x28,'<I',0)
 v.run(0xbf0760,peer,7,9,target)
 w(0x10080008+0x28,'<i',-1);w(0x10080008+0x30,'<f',0)
 v.run(0xbf12e0,peer,7,target,target)
 assert events[-2]==(0xd4f97316,[(1,4,1007),(1,4,1009),(1,4,target),(0,4,0)])
 assert events[-1]==(0xdcc32107,[(1,4,1007),(1,4,target),(1,4,target),(1,4,0xffffffff),(2,4,0)])
(R/('sender-native-'+BUILD+'.json')).write_text(json.dumps(dict(build=BUILD,boundary=__doc__,events=events),indent=2))
print('PASS',BUILD,'actual sender wrappers, both directions, uint64 peer and int/float ABI')
