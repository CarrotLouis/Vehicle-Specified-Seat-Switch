"""Execute only the native role-to-state-mask helper in an offline emulator.

The state-application function is stubbed: this proves its argument, not network
delivery, attachment, or another client's seat state.
"""
from pathlib import Path
import json, struct, sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parents[1]))
from reverse import Module
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64, UC_HOOK_CODE
from unicorn.x86_const import *

results=[]
for build in ('25327279','25480438'):
    m=Module('game.dll',R.parents[1]/'reverse'/('capture-'+build))
    vm=Uc(UC_ARCH_X86,UC_MODE_64)
    vm.mem_map(0,0x5000000)
    for address,data in m.sections:vm.mem_write(address,data)
    vm.mem_map(0x10000000,0x100000)
    stack,actor,stop=0x100f0008,0x10010000,0x100ff000
    calls=[]
    def return_from_stub():
        sp=vm.reg_read(UC_X86_REG_RSP)
        target=struct.unpack('<Q',vm.mem_read(sp,8))[0]
        vm.reg_write(UC_X86_REG_RSP,sp+8);vm.reg_write(UC_X86_REG_RIP,target)
    def hook(uc,address,size,user):
        if address==0xaa0aa0:
            pointer=uc.reg_read(UC_X86_REG_RDX)
            calls.append((uc.reg_read(UC_X86_REG_RCX),struct.unpack('<QQQ',uc.mem_read(pointer,24))))
            return_from_stub()
        elif address==0x2088770:return_from_stub()
    vm.hook_add(UC_HOOK_CODE,hook)
    for role,bit in [(0,None),(1,29),(2,30),(3,28),(4,31)]:
        calls.clear()
        vm.reg_write(UC_X86_REG_RSP,stack);vm.mem_write(stack,struct.pack('<Q',stop))
        vm.reg_write(UC_X86_REG_RCX,actor);vm.reg_write(UC_X86_REG_RDX,role)
        vm.emu_start(0xa80de0,stop,count=300)
        assert vm.reg_read(UC_X86_REG_RIP)==stop
        expected=[] if bit is None else [(actor+0x50,(1<<bit,0,0))]
        assert calls==expected,(build,role,calls)
        results.append(dict(build=build,role=role,flag_bit=bit,state_application_calls=len(calls)))
(R/'role-flags-results.json').write_text(json.dumps(results,indent=2))
print('PASS',len(results),'native role-mask cases; no network or live game execution')
