"""Execute captured clear receiver/dispatcher in Unicorn; engine effects are stubbed.
Proves argument routing and no rebroadcast, NOT visual repair or live acceptance.
"""
from pathlib import Path
import os,sys,struct,json
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent))
from emulate_seats import StaticVM
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
v=StaticVM();vm=v.vm
def w(a,f,*x):vm.mem_write(a,struct.pack(f,*x))
def reg(r):return vm.reg_read(r)
def ret(value=0):
 sp=reg(UC_X86_REG_RSP);target=struct.unpack('<Q',vm.mem_read(sp,8))[0]
 vm.reg_write(UC_X86_REG_RAX,value);vm.reg_write(UC_X86_REG_RSP,sp+8);vm.reg_write(UC_X86_REG_RIP,target)
manager,rows,hub,desc,net,channel=0x10010000,0x10011000,0x10020000,0x10030000,0x10031000,0x10031008
w(manager+0x30,'<QIII',rows,2,0xffffffff,1)
w(rows,'<4I',0xffffffff,0xffffffff,7,0)
w(0x3483c20,'<I',0xffffffff)
w(0x3326e68,'<Q',hub);w(hub+0x5f88,'<I',1);w(hub+0x5f90,'<QI',manager,0xb0)
w(desc+8,'<Q',net);w(desc+0x18,'<Q',channel);w(net,'<I',107)
clears=[];sends=[];binds=[]
def hook(vm,a,size,user):
 if a==0xfd9ba0:
  ref=reg(UC_X86_REG_RDX);assert ref in (107,190);w(reg(UC_X86_REG_RCX),'<I',7 if ref==107 else 90);ret();return
 if a==0x785de0:
  sp=reg(UC_X86_REG_RSP)
  binds.append([reg(UC_X86_REG_RCX),reg(UC_X86_REG_RDX),reg(UC_X86_REG_R8),reg(UC_X86_REG_R9),struct.unpack('<I',vm.mem_read(sp+0x28,4))[0]])
  ret();return
 if a==0xfd9a40:
  assert reg(UC_X86_REG_RCX)==7;ret(net);return
 if a==0x7853d0:
  clears.append([reg(UC_X86_REG_RCX),reg(UC_X86_REG_RDX),reg(UC_X86_REG_R8)])
  ret();return
 if a==0xbde430:
  hash_=reg(UC_X86_REG_RCX);dest=reg(UC_X86_REG_RDX);n=reg(UC_X86_REG_R9);p=reg(UC_X86_REG_R8)
  payload=[]
  for i in range(n):
   kind,length,ptr=struct.unpack('<IIQ',vm.mem_read(p+i*16,16));payload.append([kind,length,struct.unpack('<I',vm.mem_read(ptr,4))[0]])
  sends.append([hash_,dest,payload]);ret();return
vm.hook_add(UC_HOOK_CODE,hook)
cases=[]
for c in (0,1):
 clears.clear();sends.clear();w(channel,'<I',c)
 v.run(0xbaab40,0,desc)
 assert clears==[[manager,0,c]] and not sends
 cases.append({'kind':'receiver','channel':c,'clear_calls':len(clears),'sends':0})
 clears.clear();sends.clear();v.run(0x785c10,manager,7,c,1)
 assert clears==[[manager,0,c]]
 assert sends==[[0x423a4034,0xfffffffffffffffe,[[1,4,107],[1,4,c]]]]
 cases.append({'kind':'native_send','channel':c,'hash':hex(sends[0][0]),'payload':sends[0][2]})
clears.clear();sends.clear();v.run(0x785c10,manager,8,0,1)
assert not clears and not sends
w(0x3483c34,'<I',0);w(hub+0x5f70,'<I',1);w(hub+0x5f78,'<QI',manager,0xb0)
w(desc+0x28,'<Q',net+0x10);w(net+0x10,'<I',190);w(channel,'<I',0)
v.run(0xba7090,0,desc)
assert binds==[[manager,7,0,90,0]] and not sends
cases.append({'kind':'bind_receiver','avatar':7,'channel':0,'weapon':90,'rebroadcast':False})
# Capture identifies the actual local clear leaf; remote body never enters a seat routine.
text=v.mod.dis(0x11a7f80)
assert 'call     0x7853d0' in text and 'call     0x785c10' not in text
out={'boundary':__doc__,'build':os.environ['VSS_TEST_BUILD'],'cases':cases,'missing_avatar_noop':True}
(R/('native-clear-'+os.environ['VSS_TEST_BUILD']+'.json')).write_text(json.dumps(out,indent=2))
print('PASS native weapon clear adapter/dispatcher channels0/1, sender payload, no rebroadcast, missing avatar no-op')
