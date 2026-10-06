"""Offline all-vehicle cross-area receiver matrix; no game/network calls.

Real snapshot/transition/tick/route instructions execute; ALL action dispatch is stubbed.
Avatar lookup, attachment actions, role side effects and exit helpers are stubbed.
This tests seat fields and branches, not remote rendering or wire acceptance.
"""
from pathlib import Path
import json, os, struct, sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent))
BUILD=os.environ.get('VSS_TEST_BUILD','25480438')
os.environ['VSS_CAPTURE']=str(R.parent/'reverse'/('capture-'+BUILD))
from emulate_seats import StaticVM
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
v=StaticVM();vm=v.vm
def w(a,f,*x):vm.mem_write(a,struct.pack(f,*x))
def n(a):return struct.unpack('<i',vm.mem_read(a,4))[0]
def reg(r):return vm.reg_read(r)
def ret(value=0):
    sp=reg(UC_X86_REG_RSP);target=struct.unpack('<Q',vm.mem_read(sp,8))[0]
    vm.reg_write(UC_X86_REG_RAX,value);vm.reg_write(UC_X86_REG_RSP,sp+8);vm.reg_write(UC_X86_REG_RIP,target)
def map_(manager,off,rows,key):
    w(manager+off,'<QIII',rows,2,0xffffffff,1)
    w(rows,'<4I',0xffffffff,0xffffffff,0xffffffff,0xffffffff)
    w(rows+(key%2)*8,'<II',key,0)
sm,cm,am,ss,cs=0x10010000,0x10011000,0x10012000,0x10013000,0x10014000
w(0x3326d88,'<Q',cm);w(0x3326d20,'<Q',am);w(0x3483c20,'<I',0xffffffff)
map_(sm,0x20,0x10015000,7);map_(cm,0x20,0x10015100,9);map_(am,0xf8,0x10015200,7)
w(sm+0x48,'<Q',ss);w(cm+0x48,'<Q',cs)
w(sm+0x38,'<Q',0x10016000);w(0x10016000,'<Q',0x10016100);w(0x10016108,'<I',7)
w(0x3326348,'<Q',0x10017000);w(0x10017018,'<Q',100)
calls=[]
stubs={0x5a3020,0x61f6f0,0x119c9a0,0x63dd10,0x63bc60,0x63d500,0xfd9d40,0x119f910,0x2088770,0x20886a0}
# FRV diagnostic logger is external to state/action logic and relocates across captures.
stubs.add(0x1188005+struct.unpack('<i',v.mod.read(0x1188001,4))[0])
def hook(vm,address,size,user):
    if address==0x119b0a0:
        action=reg(UC_X86_REG_R8)&0xffffffff
        calls.append(('action',action))
        ret();return # Matrix covers seat fields only, not vehicle-specific action dispatch.
        # Unlike the earlier64case test, execute actual dispatch when action=-1.
        return
    if address not in stubs:return
    calls.append((hex(address),reg(UC_X86_REG_R8)&0xffffffff))
    if address==0x63dd10:w(ss+8,'<I',reg(UC_X86_REG_R8)&0xffffffff)
    ret(0x10016100 if address==0xfd9d40 else 0x10021000 if address==0x119f910 else 0)
vm.hook_add(UC_HOOK_CODE,hook)
results=[]
for layout,roles in ((26,[1,3,3,3,2]),(27,[1,3,3,3]),(28,[1,3,2]),(43,[1,2,3,3]),(44,[1,2,3,3]),(33,[1,2])):
    w(cs,'<I',layout)
    for source,target in ((a,b)for a in range(len(roles))for b in range(len(roles))if a!=b):
        w(0x10001000,'<I',source)
        route=v.run(0x1196dc0,layout,0x10001000,target)&0xffffffff
        if route!=0xffffffff:continue # Existing native routes remain the Normal path.
        for mode in ('no_seat_rpc','snapshot_only','transition_only','snapshot_then_transition'):
            vm.mem_write(ss,bytes(64));calls.clear()
            w(ss,'<IIIIiiii',9,layout,roles[source],roles[source],0,source,-1,source);w(ss+0x20,'<i',-1)
            if mode in ('snapshot_only','snapshot_then_transition'):
                w(0x10080008+0x28,'<I',target);w(0x10080008+0x30,'<I',0)
                v.run(0x63eb10,sm,0,7,9)
            if mode in ('transition_only','snapshot_then_transition'):
                w(0x10080008+0x28,'<I',target);w(0x10080008+0x30,'<i',-1);w(0x10080008+0x38,'<f',0)
                v.run(0x63ecc0,sm,0,7,target)
            v.run(0x639b40,sm,0)
            current,role,reserved=n(ss+0x14),n(ss+8),n(ss+0x1c)
            expected={
                'no_seat_rpc':(source,roles[source],source),
                'snapshot_only':(target,roles[source],target),
                'transition_only':(target,roles[target],source),
                'snapshot_then_transition':(target,roles[target],target)}[mode]
            assert (current,role,reserved)==expected,(layout,mode,current,role,reserved)
            assert n(ss)==9 and n(ss+0x18)==-1 and vm.mem_read(ss+0x30,1)==b'\0'
            assert not any(c[0]=='0x63bc60'for c in calls)
            results.append(dict(build=BUILD,layout=layout,source=source,target=target,mode=mode,
                current=current,role=role,reserved=reserved,exit_called=False,calls=calls.copy()))
out=R/('all-vehicle-receiver-matrix-'+BUILD+'.json')
out.write_text(json.dumps(dict(boundary=__doc__,cases=results),indent=2))
print('PASS',len(results),BUILD,'all-vehicle cross-area field matrix, actions stubbed; no rendering/network claim')
