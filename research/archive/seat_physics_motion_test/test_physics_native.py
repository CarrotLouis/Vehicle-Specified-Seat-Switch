"""Execute actual frozen engine actor lookup/velocity/position bridges.
Only the final virtual physics backend is stubbed. This validates ABI, handle
generation, selected-body identity, output size and no chassis-memory writes;
it does not simulate real motion, network state or ownership transfer.
"""
from pathlib import Path
import sys,os,json,struct
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
from reverse import Module
from unicorn import Uc,UC_ARCH_X86,UC_MODE_64,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
BUILD=os.environ.get('VSS_TEST_BUILD','25480438')
m=Module('helldivers2.exe',W/'reverse'/('capture-'+BUILD))
u=Uc(UC_ARCH_X86,UC_MODE_64);u.mem_map(0,0x4000000)
for r,b in m.sections:u.mem_write(r,b)
u.mem_map(0x10000000,0x100000);u.mem_map(0x20000000,0x10000)
def w(a,f,*v):u.mem_write(a,struct.pack(f,*v))
def n(a):return struct.unpack('<I',u.mem_read(a,4))[0]
def reg(r):return u.reg_read(r)
def ret(value=0):
 sp=reg(UC_X86_REG_RSP);pc=struct.unpack('<Q',u.mem_read(sp,8))[0]
 u.reg_write(UC_X86_REG_RAX,value);u.reg_write(UC_X86_REG_RSP,sp+8);u.reg_write(UC_X86_REG_RIP,pc)
def ref(at):return at+7+struct.unpack('<i',m.read(at+3,4))[0]
pools,units,worlds=ref(0x7951c4),ref(0x7e1c3a),ref(0x799576)
allowed=[];mutations=[];backend=[]
def code(u,at,size,_):
 if at in (0x12bc2b8,0x12bc32c):ret()
 elif at==0x20001000:
  assert reg(UC_X86_REG_RCX)==0x10050000 and reg(UC_X86_REG_RDX)==0x222
  assert reg(UC_X86_REG_R8)%16==0 and reg(UC_X86_REG_R9)%16==0
  w(reg(UC_X86_REG_R8),'<4f',3,4,5,0);w(reg(UC_X86_REG_R9),'<4f',.1,.2,.3,0)
  backend.append('velocity');ret()
 elif at==0x20002000:
  assert reg(UC_X86_REG_RCX)==0x10050000 and reg(UC_X86_REG_RDX)==0x222
  backend.append('position');ret(0x10060000)
def write(u,access,at,size,value,_):
 if not any(lo<=at and at+size<=hi for lo,hi in allowed):mutations.append((at,size))
u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
def run(at,*args):
 allowed[:]=[(0x1007f000,0x10090000),(0x10070000,0x10070100)]
 mutations.clear()
 for r in [UC_X86_REG_RAX,UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9,UC_X86_REG_R10,UC_X86_REG_R11]:u.reg_write(r,0)
 for r,a in zip([UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9],args):u.reg_write(r,a)
 u.reg_write(UC_X86_REG_RSP,0x10080008);w(0x10080008,'<Q',0x20000000)
 u.emu_start(at,0x20000000,count=30000)
 assert reg(UC_X86_REG_RIP)==0x20000000 and not mutations,mutations
 return reg(UC_X86_REG_RAX)
results=[]
for world in range(4):
 for inline in [False,True]:
  aid=world*2**30+0x10000000+0x10007;unit=0x800042;name=0x513720fa
  pool=pools+(world*10+1)*64;rows=0x10020000;actor=rows+7*32
  w(pool,'<Q',rows);w(pool+0x1c,'<I',32);w(pool+0x24,'<II',16,15);w(pool+0x34,'<I',0x10000)
  w(actor,'<7I',aid,0x55,0,unit,0x66,0x222,name)
  w(units,'<Q',0x10030000);ur=0x10030000+(unit&0x3fffff)*24
  w(ur,'<II',unit,0xc0000001 if inline else 0x40000001)
  if inline:w(ur+8,'<I',aid)
  else:w(ur+8,'<Q',0x10040000);w(0x10040000,'<I',aid)
  w(worlds+world*0xb0,'<Q',0x10050000);w(0x10050000,'<Q',0x10051000)
  w(0x10051000+0x98,'<Q',0x20001000);w(0x10051000+0x88,'<Q',0x20002000)
  w(0x10060000+0x30,'<4f',100,200,300,0)
  found=run(0x799de0,unit,name,0);assert found==aid,(world,inline,hex(found))
  assert run(0x7951b0,aid)==actor
  run(0x799540,aid,0x10070000,0x10070010)
  assert struct.unpack('<3f',u.mem_read(0x10070000,12))==(3,4,5)
  run(0x7999a0,aid,0x10070020)
  assert struct.unpack('<3f',u.mem_read(0x10070020,12))==(100,200,300)
  before=len(backend);w(actor,'<I',aid+1)
  assert run(0x7951b0,aid)==0
  assert run(0x799de0,unit,name,0)==0xffffffff
  run(0x799540,aid,0x10070000,0x10070010)
  assert struct.unpack('<3f',u.mem_read(0x10070000,12))==(0,0,0)and len(backend)==before
  results.append(dict(world=world,inline=inline,selected_handle=aid,real_resolver_and_lookup=True,invalid_generation_rejected=True,body_writes=0))
(R/('physics-native-'+BUILD+'.json')).write_text(json.dumps(dict(build=BUILD,boundary=__doc__,results=results),indent=2),encoding='utf8')
print('PASS',BUILD,'eight real native actor lookup/generation/velocity/position bridge cases; backend stubs; no body writes')
