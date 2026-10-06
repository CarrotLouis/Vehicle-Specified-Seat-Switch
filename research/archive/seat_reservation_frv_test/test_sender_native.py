"""Actual reservation wrappers, mocked net-ref/transport backend; no packets."""
from pathlib import Path
import os,sys,struct,json
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
BUILD=os.environ.get('VSS_TEST_BUILD','25480438');os.environ['VSS_CAPTURE']=str(W/'reverse'/('capture-'+BUILD))
from emulate_seats import StaticVM
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
v=StaticVM();u=v.vm;events=[];PEER=0xfedcba9876543211
def reg(r):return u.reg_read(r)
def w(a,f,*values):u.mem_write(a,struct.pack(f,*values))
def ret(value=0):
 sp=reg(UC_X86_REG_RSP);address=struct.unpack('<Q',u.mem_read(sp,8))[0]
 u.reg_write(UC_X86_REG_RAX,value);u.reg_write(UC_X86_REG_RSP,sp+8);u.reg_write(UC_X86_REG_RIP,address)
def hook(vm,address,size,_):
 if address==0xfd9a40:
  entity=reg(UC_X86_REG_RCX);assert entity in(7,9);ptr=0x10040000+entity*4;w(ptr,'<I',4107 if entity==7 else 4123);ret(ptr)
 elif address==0xbde430:
  assert reg(UC_X86_REG_RDX)==PEER
  rows=[]
  for i in range(reg(UC_X86_REG_R9)):
   typ,size,ptr=struct.unpack('<IIQ',u.mem_read(reg(UC_X86_REG_R8)+16*i,16));assert typ==1 and size==4
   rows.append(struct.unpack('<I',u.mem_read(ptr,4))[0])
  events.append({'hash':hex(reg(UC_X86_REG_RCX)&0xffffffff),'values':rows});ret()
u.hook_add(UC_HOOK_CODE,hook)
v.run(0xbe36a0,PEER,9,7,2);v.run(0xbee380,PEER,9,1)
assert events==[{'hash':'0x3a44e090','values':[4123,4107,2]},{'hash':'0xc698216f','values':[4123,1]}]
assert not any(x['hash']in('0xe29b4d18','0xf8a9d630')for x in events)
(R/('sender-native-'+BUILD+'.json')).write_text(json.dumps({'boundary':__doc__,'build':BUILD,'events':events},indent=2))
print('PASS',BUILD,'native entry/release wire descriptors, uint64 peer and net refs, no chassis-ownership packets')
