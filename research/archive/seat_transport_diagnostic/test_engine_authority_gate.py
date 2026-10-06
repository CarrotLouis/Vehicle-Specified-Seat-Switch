"""Offline execution of the engine's owner-message sender gate.

Stops at the gate: passing is NOT proof the entity transfer will be accepted.
Bit decoding is stubbed; fixed-width header reads and native gate execute.
No engine objects, actual peer IDs, live process, sockets or packets are used.
"""
from pathlib import Path
import os,sys,struct,json,itertools
R=Path(__file__).resolve().parent; W=R.parent
os.environ['VSS_CAPTURE']=str(W/'reverse/capture-25480438');sys.path.insert(0,str(W))
from reverse import Module
from unicorn import Uc,UC_ARCH_X86,UC_MODE_64,UC_HOOK_CODE
from unicorn.x86_const import *
m=Module('helldivers2.exe');vm=Uc(UC_ARCH_X86,UC_MODE_64)
vm.mem_map(0,0x5000000)
for address,data in m.sections:vm.mem_write(address,data)
vm.mem_map(0x10000000,0x100000);vm.mem_map(0x20000000,0x1000)
S=0x10010000;MODE=0x10020000;READER=0x10021000;PAYLOAD=0x10022000
NETWORK=0x10023000;VTABLE=0x10024000;STOP=0x20000000;REJECT=STOP+0x100
SELF=0xfedcba9876543211;HOST=0xabcdef0123456789;THIRD=0x987654321abcdef0
def put(a,fmt,*v):vm.mem_write(a,struct.pack(fmt,*v))
def get(a,fmt='<I'):return struct.unpack(fmt,vm.mem_read(a,struct.calcsize(fmt)))[0]
def reg(r):return vm.reg_read(r)
def ret(value=0):
    sp=reg(UC_X86_REG_RSP);dest=get(sp,'<Q')
    vm.reg_write(UC_X86_REG_RAX,value);vm.reg_write(UC_X86_REG_RSP,sp+8);vm.reg_write(UC_X86_REG_RIP,dest)
bits=[];admitted=False;rejected=False
def hook(vm,address,size,ctx):
    global admitted,rejected
    if address==0x28c3f0:
        value,width=bits.pop(0);assert reg(UC_X86_REG_RDX)==width
        ret(value)
    elif address==0x299a79:
        admitted=True;vm.emu_stop()
    elif address==REJECT:
        assert reg(UC_X86_REG_RCX)==NETWORK
        rejected=True;ret()
vm.hook_add(UC_HOOK_CODE,hook)
results=[]
for mode,coordinator,sender,target,epoch_matches in itertools.product(
        (1,2),(HOST,SELF),(HOST,SELF,THIRD),(HOST,SELF,THIRD),(True,False)):
    admitted=rejected=False;bits=[(77 if epoch_matches else 76,16),(4118,15),(0,1)]
    vm.mem_write(S,bytes(0x7000));vm.mem_write(READER,bytes(0x40))
    put(S+0x18,'<Q',MODE);put(MODE,'<I',mode)
    put(S+0x20,'<Q',SELF);put(S+0x130,'<Q',coordinator);put(S+0x60e4,'<I',77)
    put(S+0x10,'<Q',NETWORK);put(NETWORK,'<Q',VTABLE);put(VTABLE+0x90,'<Q',REJECT)
    put(READER,'<Q',PAYLOAD);put(READER+8,'<Q',PAYLOAD);put(READER+0x10,'<I',18)
    put(PAYLOAD,'<QQH',target,0,1)
    for register in (UC_X86_REG_RAX,UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9):vm.reg_write(register,0)
    vm.reg_write(UC_X86_REG_RCX,S);vm.reg_write(UC_X86_REG_RDX,sender);vm.reg_write(UC_X86_REG_R8,READER)
    vm.reg_write(UC_X86_REG_RSP,0x10080008);put(0x10080008,'<Q',STOP)
    vm.emu_start(0x299890,STOP,count=5000)
    allowed=(sender==coordinator if mode==1 else
             (sender==coordinator and (target==SELF or SELF==coordinator)) or
             (sender==target and sender!=SELF))
    assert admitted==(allowed and epoch_matches)
    assert rejected==((not allowed) and epoch_matches)
    assert bits==[]
    assert admitted or reg(UC_X86_REG_RIP)==STOP,'unexpected incomplete execution'
    assert get(READER+0x14)==int(rejected)
    alias={SELF:'self',HOST:'other1',THIRD:'other2'}
    results.append(dict(mode=mode,coordinator=alias[coordinator],sender=alias[sender],
                        target=alias[target],epoch_matches=epoch_matches,
                        admitted_to_next_gate=admitted,rejection_callback=rejected))
(R/'authority-20260926'/'engine-gate-tests.json').write_text(json.dumps(dict(boundary=__doc__,cases=results),indent=2))
print(f'PASS {len(results)} engine sender/epoch gate cases; entity transfer and network delivery not executed.')
