"""Emulate captured native state routines OFFLINE; engine effects are intercepted.
This validates fields and branching only, not pose, weapons, network or live ABI.
"""
import sys,struct,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from emulate_seats import StaticVM
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
v=StaticVM();vm=v.vm
def write(a,f,*x):vm.mem_write(a,struct.pack(f,*x))
def u(a):return struct.unpack('<I',vm.mem_read(a,4))[0]
def reg(r):return vm.reg_read(r)
def map_(base,off,data,key):
 write(base+off,'<QIII',data,2,0xffffffff,1)
 for i in range(2):write(data+i*8,'<II',0xffffffff,0xffffffff)
 write(data+(key%2)*8,'<II',key,0)
sm,cm,am,ss,cs=0x10010000,0x10011000,0x10012000,0x10013000,0x10014000
write(0x3326d88,'<Q',cm);write(0x3326d20,'<Q',am);write(0x3483c20,'<I',0xffffffff)
map_(sm,0x20,0x10015000,7);map_(cm,0x20,0x10015100,9);map_(am,0xf8,0x10015200,7)
write(sm+0x48,'<Q',ss);write(cm+0x48,'<Q',cs)
write(sm+0x38,'<Q',0x10016000);write(0x10016000,'<Q',0x10016100);write(0x10016108,'<I',7)
write(0x3326348,'<Q',0x10017000);write(0x10017018,'<Q',100)
calls=[]
stubs={0x5a3020,0x61f6f0,0x119b0a0,0x119c9a0,0x63dd10,0x63bc60,0x63d500}
def intercept(vm,a,n,_):
 if a not in stubs:return
 calls.append((a,reg(UC_X86_REG_RCX),reg(UC_X86_REG_RDX),reg(UC_X86_REG_R8),reg(UC_X86_REG_R9)))
 if a==0x63dd10:write(ss+8,'<I',reg(UC_X86_REG_R8)&0xffffffff)
 rsp=reg(UC_X86_REG_RSP);ret=struct.unpack('<Q',vm.mem_read(rsp,8))[0]
 vm.reg_write(UC_X86_REG_RSP,rsp+8);vm.reg_write(UC_X86_REG_RIP,ret)
vm.hook_add(UC_HOOK_CODE,intercept)
matrix=json.loads(Path('work/reverse/seat_roles_25327279.json').read_text());checked=0
for name,d in matrix.items():
 t=d['transition'];write(cs,'<I',t)
 for source in d['seats']:
  for target in d['seats']:
   if source==target:continue
   vm.mem_write(ss,bytes(64));write(ss,'<IIIIiiii',9,t,source['role'],source['role'],0,source['node'],-1,source['node']);write(ss+0x20,'<i',-1)
   calls.clear()
   write(0x10080008+0x28,'<I',target['node']);write(0x10080008+0x30,'<I',0)
   v.run(0x63eb10,sm,0,7,9)
   assert u(ss)==9 and u(ss+0x14)==target['node'] and u(ss+0x1c)==target['node']
   assert u(ss+0x18)==0xffffffff and u(ss+0x20)==0xffffffff
   action=[c for c in calls if c[0]==0x119b0a0];assert len(action)==1
   assert action[0][1:]==(t,7,target['restore_action'],target['node'])
   assert not any(c[0]==0x63bc60 for c in calls)
   # A plain snapshot does NOT update role, proving why a second phase is needed.
   assert u(ss+8)==source['role']
   # Investigational sync sequence: mark current==target, no action to play.
   write(0x10080008+0x28,'<I',target['node']);write(0x10080008+0x30,'<i',-1);write(0x10080008+0x38,'<f',0)
   v.run(0x63ecc0,sm,0,7,target['node'])
   v.run(0x639b40,sm,0)
   assert u(ss)==9 and u(ss+8)==target['role'] and u(ss+0x18)==0xffffffff
   assert vm.mem_read(ss+0x30,1)==b'\0' and not any(c[0]==0x63bc60 for c in calls)
   checked+=1
print(f'PASS: {checked} native restore/role-completion cases, no exit branch. Engine effects intercepted; multiplayer protocol remains unverified.')
