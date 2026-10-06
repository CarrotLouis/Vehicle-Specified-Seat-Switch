"""Execute captured FRV action/complete dispatch, record boundary calls.

Offline only. Engine/avatar helpers are stubs, so this proves emitted commands,
not rendering, attachment correctness or multiplayer acceptance.
"""
from pathlib import Path
import os, sys, json, struct
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent))
BUILD=os.environ.get('VSS_TEST_BUILD','25480438')
os.environ['VSS_CAPTURE']=str(R.parent/'reverse'/('capture-'+BUILD))
from emulate_seats import StaticVM
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
v=StaticVM(); vm=v.vm
avatar, context, api, table=0x10030000,0x10031000,0x10032000,0x10033000
def w(a,f,*x): vm.mem_write(a,struct.pack(f,*x))
w(avatar+8,'<III',7,123,0)
w(context+8,'<I',9)
w(0x3326308,'<Q',api); w(api+0x18,'<Q',table)
for off in (0x260,): w(table+off,'<Q',0x10034000+off)
ranges=[v.mod.function(x)[:2] for x in (0x1187fb0,0x1189380)]
records=[]; calls=[]
def hook(vm,address,size,user):
    if any(a<=address<b for a,b in ranges) or address==0x20000000:return
    args=[vm.reg_read(r) for r in (UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9)]
    calls.append(dict(function=hex(address),args=args))
    result=avatar if address==0xfd9d40 else context if address==0x119f910 else 0
    sp=vm.reg_read(UC_X86_REG_RSP)
    target=struct.unpack('<Q',vm.mem_read(sp,8))[0]
    vm.reg_write(UC_X86_REG_RAX,result);vm.reg_write(UC_X86_REG_RSP,sp+8);vm.reg_write(UC_X86_REG_RIP,target)
vm.hook_add(UC_HOOK_CODE,hook)
names=json.loads((R.parent/'reverse/thin_names.json').read_text())
for action in range(24):
    calls.clear();v.run(0x1187fb0,7,action,2)
    action_calls=calls.copy();calls.clear();v.run(0x1189380,7,action)
    events=[names.get(hex(c['args'][1]),hex(c['args'][1])) for c in action_calls if c['function']=='0x119fec0']
    complete=[names.get(hex(c['args'][1]),hex(c['args'][1])) for c in calls if c['function']=='0x119fec0']
    records.append(dict(action=action,events=events,complete_events=complete,action_calls=action_calls,complete_calls=calls.copy()))
    print(action,events,'complete',complete)
(R/('animation-actions-'+BUILD+'.json')).write_text(json.dumps(dict(boundary=__doc__,records=records),indent=2))
