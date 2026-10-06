"""Execute the preserved game authority handler in Unicorn, OFFLINE.

Engine API, locks, entity lookup and network sends are intercepted. This tests
native branching and queued-record draining, NOT real multiplayer acceptance.
"""
from pathlib import Path
import os, sys, struct, json
R=Path(__file__).resolve().parent; W=R.parent
os.environ['VSS_CAPTURE']=str(W/'reverse/capture-25480438')
sys.path.insert(0,str(W))
from emulate_seats import StaticVM
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import *
v=StaticVM(); vm=v.vm
# Synthetic storage; no captured heap pointers are dereferenced.
S=0x10010000; SERVICES=0x10020000; API=0x10021000; NETAPI=0x10022000
ENTITY=0x30000000; HASH=0x10023000; EHASH=0x10024000
QUEUE=0x10030000; PENDING=0x10025000; REGISTRY=0x10040000
ARGS=0x10050000; VALUES=0x10051000
vm.mem_map(ENTITY,0x1000000)
def put(a,fmt,*x):vm.mem_write(a,struct.pack(fmt,*x))
def get(a,fmt='<I'):return struct.unpack(fmt,vm.mem_read(a,struct.calcsize(fmt)))[0]
def reg(r):return vm.reg_read(r)
def ret(value=0):
    sp=reg(UC_X86_REG_RSP);dest=get(sp,'<Q')
    vm.reg_write(UC_X86_REG_RSP,sp+8);vm.reg_write(UC_X86_REG_RAX,value);vm.reg_write(UC_X86_REG_RIP,dest)
STUBS={0x20000100:'exists',0x20000110:'owner',0x20000120:'transfer',
       0x20000130:'lock',0x20000140:'unlock',0x20000150:'network',
       0x20000160:'flush',0x20000170:'request',0xfd9ba0:'entity'}
calls=[];exists=True;owner=0;entityid=721
def hook(vm,address,size,ctx):
    if address not in STUBS:return
    name=STUBS[address];args=tuple(reg(r) for r in [UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9])
    calls.append((name,args))
    if name=='exists':ret(int(exists))
    elif name=='owner':ret(owner)
    elif name=='network':ret(0x123456)
    elif name=='entity':put(args[0],'<I',entityid);ret(args[0])
    else:ret()
vm.hook_add(UC_HOOK_CODE,hook)
put(0x3326308,'<Q',SERVICES);put(SERVICES+0x40,'<Q',API)
put(SERVICES+0x38,'<Q',NETAPI);put(NETAPI+8,'<Q',0x20000150)
put(0x33263e8,'<Q',SERVICES)
for offset,address in [(0x98,0x20000100),(0x160,0x20000110),(0x140,0x20000120),
                       (0xb8,0x20000160),(0x138,0x20000170)]:put(API+offset,'<Q',address)
put(SERVICES+0x70,'<Q',0x20000130);put(SERVICES+0x78,'<Q',0x20000140)
put(0x346bf98,'<Q',ENTITY);put(0x3326e68,'<Q',REGISTRY)
SELF=0xfedcba9876543211; OTHER=0xabcdef0123456789; THIRD=0x987654321abcdef0
UNIT=4118; NET=0x77770000
def reset():
    calls.clear();vm.mem_write(S,bytes(0x10000));vm.mem_write(REGISTRY,bytes(0x8000))
    put(S+0xb390,'<Q',NET);put(S+0xb398,'<Q',SELF);put(S+0x350,'<Q',0x456789)
    put(S+0xb370,'<QIII',HASH,2,0xffffffff,1)
    put(HASH,'<IIII',UNIT,0,0xffffffff,0xffffffff)
    put(ENTITY+0xf1aeb0,'<QIII',EHASH,2,0xffffffff,1)
    put(EHASH,'<IIII',0xffffffff,0xffffffff,entityid,9)
    put(ENTITY+0xf3ef18,'<I',0);put(ENTITY+0xf3ef20,'<Q',PENDING)
    put(S+0x358,'<I',0);put(S+0x360,'<Q',QUEUE)
def names():return [c[0] for c in calls]
results=[]
for label,present,current,target,pending in [
    ('missing_unit',False,SELF,OTHER,False),
    ('already_owned_by_target',True,OTHER,OTHER,False),
    ('receiver_not_current_owner',True,THIRD,OTHER,False),
    ('pending_entity',True,SELF,OTHER,True),
    ('owner_can_delegate',True,SELF,OTHER,False),
    ('owner_can_delegate_to_third_peer',True,SELF,THIRD,False),
]:
    reset();exists=present;owner=current
    if pending:put(ENTITY+0xf3ef18,'<I',1);put(PENDING,'<I',9)
    v.run(0x134f270,S,UNIT,target)
    should_transfer=present and current!=target and current==SELF and not pending
    assert ('transfer' in names())==should_transfer,(label,calls)
    if should_transfer:
        assert names()==['exists','owner','entity','lock','network','unlock','transfer']
        assert calls[-1][1]==(NET,UNIT,target,S+0xb3c0)
        assert get(S+0x236c,'<B')==1
    else:assert not any(n in names() for n in ['lock','flush','transfer'])
    results.append(dict(case=label,transfer_called=should_transfer,calls=names()))

# Draining swaps the last record into each removed slot: two matching records
# separated by another unit must both be flushed without losing the other one.
reset();exists=True;owner=SELF
put(S+0x358,'<I',1);put(QUEUE,'<I',3)
for i,(unit,kind,payload) in enumerate([(UNIT,11,0x1111),(99,22,0x2222),(UNIT,33,0x3333)]):
    put(QUEUE+8+i*16,'<IIQ',unit,kind,payload)
v.run(0x134f270,S,UNIT,OTHER)
flushed=[c[1][1:] for c in calls if c[0]=='flush']
assert flushed==[(UNIT,11,0x1111),(UNIT,33,0x3333)]
assert get(QUEUE)==1 and get(QUEUE+8)==99
assert names().index('unlock')>max(i for i,n in enumerate(names()) if n=='flush')
assert names()[-1]=='transfer'
results.append(dict(case='drain_only_matching_unit',calls=names(),remaining_unit=99))

# Execute both actual adapters with a one-system registry. Untagged entries
# must not call an engine API; E29 does not consult current-owner in this layer.
for label,address,offset,tag,present in [
    ('request_exists',0xbbfa60,0x6ea0,0x10f,True),
    ('request_missing_unit',0xbbfa60,0x6ea0,0x10f,False),
    ('request_wrong_system_tag',0xbbfa60,0x6ea0,0x10e,True),
    ('owned_adapter',0xbc2640,0x6eb8,0x10f,True),
]:
    reset();exists=present;owner=SELF
    put(REGISTRY+offset,'<I',1);put(REGISTRY+offset+8,'<QI',S,tag)
    put(ARGS+8,'<Q',VALUES);put(ARGS+0x18,'<Q',VALUES+8)
    put(VALUES,'<I',UNIT);put(VALUES+8,'<Q',OTHER)
    v.run(address,0,ARGS)
    expected=('transfer' if address==0xbc2640 else 'request') if present and tag==0x10f else None
    assert [n for n in names() if n in ('request','transfer')]==([expected] if expected else [])
    if expected:assert calls[-1][1]==(NET,UNIT,OTHER,S+0xb3c0)
    results.append(dict(case=label,calls=names()))
out=R/'authority-20260926'/'native-branch-tests.json'
out.write_text(json.dumps(dict(boundary=__doc__,cases=results),indent=2))
print(f'PASS {len(results)} native handler/adapter cases. Engine APIs intercepted; no network-acceptance claim.')
