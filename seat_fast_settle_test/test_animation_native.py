"""Captured native wrapper and dynamic event lookup, serializer boundary intercepted.
No network delivery or rendering is simulated. Boolean low byte is the native
value; active Lua descriptors additionally initialize its three padding bytes.
"""
from pathlib import Path
import sys,os,struct,json
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
BUILD=os.environ.get('VSS_TEST_BUILD','25480438')
os.environ['VSS_CAPTURE']=str(W/'reverse'/('capture-'+BUILD))
from emulate_seats import StaticVM
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
v=StaticVM();u=v.vm;records=[];index=17
def w(a,f,*x):u.mem_write(a,struct.pack(f,*x))
def reg(r):return u.reg_read(r)
def ret(value=0):
 sp=reg(UC_X86_REG_RSP);pc=struct.unpack('<Q',u.mem_read(sp,8))[0]
 u.reg_write(UC_X86_REG_RAX,value);u.reg_write(UC_X86_REG_RSP,sp+8);u.reg_write(UC_X86_REG_RIP,pc)
dictionary,rows,net=0x10010000,0x10020000,0x10030000
w(0x3326de8,'<Q',dictionary);w(dictionary+8,'<QIII',rows,16,0xffffffff,1)
for i in range(16):w(rows+i*8,'<II',0xffffffff,0xffffffff)
w(rows+4*8,'<II',0xdab88e64,index);w(net,'<I',1007)
cookie=v.mod.function(0xbedb90);code=list(v.mod.md.disasm(v.mod.read(cookie[0],cookie[1]-cookie[0]),cookie[0]))
cookie_check=int([i.op_str for i in code if i.mnemonic=='call'][-1],16)
def hook(u,at,size,_):
 if at==0xfd9a40:assert reg(UC_X86_REG_RCX)==7;ret(net)
 elif at==cookie_check:ret()
 elif at==0xbde430:
  assert reg(UC_X86_REG_RCX)==0xbde53653 and reg(UC_X86_REG_RDX)==0xfedcba9876543210 and reg(UC_X86_REG_R9)==3
  got=[]
  for i in range(3):
   t,n,p=struct.unpack('<IIQ',u.mem_read(reg(UC_X86_REG_R8)+i*16,16));raw=bytes(u.mem_read(p,n))
   got.append((t,n,raw[0] if i==2 else struct.unpack('<I',raw)[0]))
  assert got==[(1,4,1007),(1,4,index),(0,4,0)],got
  records.append(got);ret()
u.hook_add(UC_HOOK_CODE,hook)
for index in (17,1396):
 w(rows+4*8+4,'<I',index)
 # Dirty home area demonstrates why the explicit Lua descriptors zero all bytes.
 u.mem_write(0x10080008+0x20,b'\xaa'*4)
 v.run(0xbedb90,0xfedcba9876543210,7,0xdab88e64,0)
(R/('animation-native-'+BUILD+'.json')).write_text(json.dumps(dict(build=BUILD,boundary=__doc__,records=records),indent=2))
print('PASS',BUILD,'native event wrapper + real dictionary lookup at two indices; exact serializer descriptor equivalence')
