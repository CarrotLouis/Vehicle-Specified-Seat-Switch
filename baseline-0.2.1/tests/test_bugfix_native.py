"""Captured native control/animation branches in an offline synthetic VM.
Engine side effects are intercepted; this is NOT an in-game rendering test.
"""
import sys,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from emulate_seats import StaticVM
from reverse import Module
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
v=StaticVM();vm=v.vm
def w(a,f,*args):vm.mem_write(a,struct.pack(f,*args))
def read(a,f):return struct.unpack(f,vm.mem_read(a,struct.calcsize(f)))
def reg(r):return vm.reg_read(r)
def map_(base,off,rows,key):
 w(base+off,'<QIII',rows,2,0xffffffff,1)
 w(rows,'<4I',0xffffffff,0xffffffff,key,0)
controls,avatar,states,rows=0x10010000,0x10011000,0x10012000,0x10013000
w(avatar+8,'<I',7);w(0x3326420,'<Q',controls);w(0x3483c20,'<I',0xffffffff);w(0x3483c34,'<I',0xffffffff)
map_(controls,0x30,rows,7);w(controls+0x60,'<Q',states)
for i,weapon in enumerate([111,222,333]):w(states+80*i,'<I',weapon)
calls=[]
stubs={0x776010,0x775000,0x7853d0,0xa3f220,0x20886a0,0x54b490}
def intercept(uc,a,size,_):
 if a not in stubs:return
 args=tuple(reg(x) for x in [UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9])
 calls.append((a,*args))
 if a==0x776010:uc.reg_write(UC_X86_REG_RAX,1)
 if a==0x7853d0:w(states+args[2]*80,'<I',0xffffffff)
 if a==0x54b490:
  assert reg(UC_X86_REG_XMM3)==0,'Nonzero blend time'
  assert read(reg(UC_X86_REG_RSP)+0x28,'<B')[0]==0
 rsp=reg(UC_X86_REG_RSP);ret=read(rsp,'<Q')[0]
 uc.reg_write(UC_X86_REG_RSP,rsp+8);uc.reg_write(UC_X86_REG_RIP,ret)
vm.hook_add(UC_HOOK_CODE,intercept)
for slot,weapon in enumerate([111,222]):
 calls.clear();v.run(0x11a7f80,avatar,slot)
 assert [x[0] for x in calls]==[0x776010,0x775000,0x7853d0]
 assert calls[1][2]==weapon and calls[2][3]==slot
assert read(states,'<I')[0]==read(states+80,'<I')[0]==0xffffffff
assert read(states+160,'<I')[0]==333
# The specific Maelstrom driver flag is removed without clearing the seat input bit.
am=0x30000000;vm.mem_map(am,0x600000);w(0x3326d20,'<Q',am)
map_(am,0xf8,rows+0x100,7);w(avatar+20,'<I',1)
flags=am+0x53d900+0xf80;original=(1<<44)|(1<<50)|(1<<2)
w(flags,'<QQQ',original,0x80,0x400)
calls.clear();v.run(0x11b11f0,avatar,44)
assert read(flags,'<QQQ')==(original&~(1<<44),0x80,0x400)
assert any(c[0]==0xa3f220 and c[3]==0 for c in calls)
# Run the actual engine setter: -1 skips a layer and selected layers use zero blend.
exe=Module('helldivers2.exe');vm.mem_write(0x554440,exe.read(0x554440,0x8a))
resource=Path('work/animation_resources/4d1c334d294dfa97.state_machine.main').read_bytes()
root=0x40000000;vm.mem_map(root,0x1000000);vm.mem_write(root,resource)
machine,values=0x10020000,0x10021000;w(machine+0x28,'<Q',root)
for base,upper in [(108,64),(112,68),(106,62),(110,66),(104,60),(123,102),(121,96)]:
 ids=[-1]*14;ids[0]=base;ids[13]=upper;w(values,'<14i',*ids)
 calls.clear();v.run(0x554440,machine,values,14)
 assert len(calls)==2 and [c[2] for c in calls]==[0,13]
 group=root+read(root+8,'<I')[0]
 for c,index in zip(calls,[base,upper]):
  layer=group+read(group+4+c[2]*4,'<I')[0]
  assert c[3]==layer+read(layer+12+index*4,'<I')[0]
print('PASS: native stop-before-unbind for both weapon channels; flag 44 removal preserves other flags; actual engine setter selects only layers 0/13 with zero blend. Game effects intercepted.')
