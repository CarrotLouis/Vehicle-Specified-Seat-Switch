"""Exercise captured equip-current code; intercept engine effects, never a live game."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from emulate_seats import StaticVM
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *

v=StaticVM(); vm=v.vm
def w(a, fmt, *x): vm.mem_write(a, struct.pack(fmt,*x))
def read(a, fmt): return struct.unpack(fmt,vm.mem_read(a,struct.calcsize(fmt)))
def reg(r): return vm.reg_read(r)
inventory, avatar, states, rows, entities = [0x10010000+i*0x1000 for i in range(5)]
engine, unitapi, player, weaponmanager, controls = [0x10020000+i*0x1000 for i in range(5)]
w(0x3326738,'<Q',inventory);w(0x3326468,'<Q',player)
w(0x3326308,'<Q',engine);w(engine+0x18,'<Q',unitapi)
w(unitapi+0x350,'<Q',0x20000100)
w(0x3326660,'<Q',weaponmanager);w(0x3326420,'<Q',controls)
for a in [0x3483c20,0x3483c34,0x3483c4c]:w(a,'<I',0xffffffff)
w(inventory+0x28,'<QIII',rows,2,0xffffffff,1)
w(rows,'<4I',0xffffffff,0xffffffff,7,0)
w(inventory+0x40,'<Q',entities);w(entities,'<Q',avatar)
w(inventory+0x50,'<Q',states);w(avatar+8,'<II',7,21)
w(states,'<6I',111,222,333,444,555,0xffffffff)
calls=[];bound={0:0xffffffff,1:0xffffffff}
stubs={0x8c2010,0x785de0,0x20000100,0x8c0e90,0xb4d890}
def intercept(uc,a,size,_):
 if a not in stubs:return
 args=tuple(reg(r) for r in [UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9])
 calls.append((a,*args))
 if a==0x785de0:
  assert args[:3]==(controls,7,0)
  assert read(reg(UC_X86_REG_RSP)+0x28,'<I')[0]==0
  bound[args[2]]=args[3]
 if a==0x8c0e90:assert args[2]==0 and reg(UC_X86_REG_XMM3)==0
 uc.reg_write(UC_X86_REG_RAX,0)
 rsp=reg(UC_X86_REG_RSP);ret=read(rsp,'<Q')[0]
 uc.reg_write(UC_X86_REG_RSP,rsp+8);uc.reg_write(UC_X86_REG_RIP,ret)
vm.hook_add(UC_HOOK_CODE,intercept)
for slot in range(1,5):
 calls.clear();bound.update({0:0xffffffff,1:0xffffffff})
 w(states+0x1c,'<II',slot,1)
 # 0.2.1's visual notification does not restore the firing controller.
 v.run(0x11b1070,avatar)
 assert bound[0]==0xffffffff and [c[0] for c in calls]==[0xb4d890]
 calls.clear()
 # Actual native same-group completion re-equips the CURRENT personal slot.
 v.run(0x11a7900,avatar)
 assert read(states+0x1c,'<II')==(slot,1),'Selection/holster unexpectedly changed'
 assert bound=={0:[111,222,333,555][slot-1],1:0xffffffff},'Must not rebind the old turret/coax'
 assert len([c for c in calls if c[0]==0x785de0])==1
 assert calls[-1][0]==0x8c0e90 and calls[-1][2]==[111,222,333,555][slot-1]
print('PASS: captured native current-weapon equip restores channel 0 for all 4 personal slots without changing selection/holster or restoring channel 1; old notification alone does not. Engine effects intercepted.')

# Regression: cross-group -> FRV driver -> NATIVE front passenger. Run actual
# group action dispatch, intercepting engine effects but observing any unbind.
from reverse import Module
m=Module();vehicle=0x10030000;w(vehicle+8,'<I',9)
actions=[(0x1187fb0,12),(0x1189c30,9),(0x118b300,8)]
effects={0x11a7f80,0x11a7ba0}
for start,_ in actions:
 for instruction in m.md.disasm(m.read(start,m.function(start)[1]-start),start):
  if instruction.mnemonic=='call' and instruction.op_str.startswith('0x'):
   effects.add(int(instruction.op_str,16))
effects-=stubs
def vehicle_effect(uc,a,size,_):
 if a not in effects:return
 if a in [0x11a7f80,0x11a7ba0]:raise AssertionError('Native driver->passenger changes weapon binding')
 result=avatar if a==0xfd9d40 else vehicle if a in [0x119f910,0x11b52b0] else 0
 uc.reg_write(UC_X86_REG_RAX,result)
 rsp=reg(UC_X86_REG_RSP);ret=read(rsp,'<Q')[0]
 uc.reg_write(UC_X86_REG_RSP,rsp+8);uc.reg_write(UC_X86_REG_RIP,ret)
hook=vm.hook_add(UC_HOOK_CODE,vehicle_effect)
for start,action in actions:
 for slot in range(1,5):
  w(states+0x1c,'<II',slot,1);bound[0]=0xffffffff
  # 0.2.2 after cross-group driver restoration: channel stays unbound.
  v.run(start,7,action,1);assert bound[0]==0xffffffff
  # 0.2.3 equips at the FRV driver destination before the subsequent native hop.
  v.run(0x11a7900,avatar)
  v.run(start,7,action,1)
  assert bound[0]==[111,222,333,555][slot-1] and bound[1]==0xffffffff
print('PASS: captured M102/M103/M104 native driver->front-passenger actions preserve the repaired current weapon for all four slots; reproduce the missing binding without the repair. Engine effects intercepted.')
