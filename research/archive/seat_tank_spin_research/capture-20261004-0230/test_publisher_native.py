"""Frozen native property queue -> validate -> copy/dirty, no live game.

Session access, unit existence/lookup and locks are mocked. Actual captured
FD97E0/FDDEC0/34C220/34BAB0/34C3E0/297BE0/174430 execute. No transport,
peer acceptance, body physics, ownership validity or live repair is asserted.
"""
from pathlib import Path
import json,os,struct,sys
R=Path(__file__).resolve().parent;W=R.parent.parent
sys.path.insert(0,str(W))
from reverse import Module
from unicorn import Uc,UC_ARCH_X86,UC_MODE_64,UC_HOOK_CODE
from unicorn.x86_const import *
BUILD=os.environ.get('VSS_TEST_BUILD','25480438');G=0x4000000
g=Module('game.dll',W/'reverse'/('capture-'+BUILD));e=Module('helldivers2.exe',W/'reverse'/('capture-'+BUILD))
u=Uc(UC_ARCH_X86,UC_MODE_64);u.mem_map(0,0x10000000)
for r,b in e.sections:u.mem_write(r,b)
for r,b in g.sections:u.mem_write(G+r,b)
u.mem_map(0x10000000,0x100000);u.mem_map(0x20000000,0x1000)
BOX,STATE,SERV,ACCESS,API,CTX,VT,SM,TYPES,GLOBALS,INDICES,HASHES,PAYLOAD,RAW,VALUE,QUEUE=[0x10000000+i*0x1000 for i in range(16)]
unit=211;field_hash=0x5a8871e3;descriptor=TYPES+123*80;events=[]
stub={name:0x20000100+i*0x10 for i,name in enumerate(['access','exists','lock','unlock','schema','ownership','unit_meta','lookup','index'])}
def write(a,fmt,*v):u.mem_write(a,struct.pack(fmt,*v))
def read(a,fmt):return struct.unpack(fmt,u.mem_read(a,struct.calcsize(fmt)))
def ret(value=0):
 sp=u.reg_read(UC_X86_REG_RSP);u.reg_write(UC_X86_REG_RAX,value);u.reg_write(UC_X86_REG_RSP,sp+8);u.reg_write(UC_X86_REG_RIP,read(sp,'<Q')[0])
def code(uc,at,n,_):
 if at==stub['access']:ret(CTX)
 elif at==stub['exists']:ret(1)
 elif at in (stub['lock'],stub['unlock']):ret()
 elif at==stub['schema']:ret(SM)
 elif at in (stub['ownership'],stub['unit_meta']):ret(1)
 elif at==0x29ead0:ret(PAYLOAD)
 elif at==0x28d190:ret(0)
 elif at==stub['lookup']:
  write(uc.reg_read(UC_X86_REG_R8),'<I',123);ret()
 elif at in (0x34c220,0x34c3e0):
  events.append({'event':'validate'if at==0x34c220 else'copy_dirty','value_pointer':uc.reg_read(UC_X86_REG_R9)})
u.hook_add(UC_HOOK_CODE,code)
def run(at,*args):
 for reg in (UC_X86_REG_RAX,UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9,UC_X86_REG_R10,UC_X86_REG_R11):u.reg_write(reg,0)
 for reg,x in zip((UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9),args):u.reg_write(reg,x)
 u.reg_write(UC_X86_REG_RSP,0x10080008);write(0x10080008,'<Q',0x20000000)
 u.emu_start(at,0x20000000,count=20000);assert u.reg_read(UC_X86_REG_RIP)==0x20000000,hex(u.reg_read(UC_X86_REG_RIP))
def gr(at):return G+at+7+struct.unpack('<i',g.read(at+3,4))[0]
write(gr(0xfd97ee),'<Q',BOX);write(BOX+8,'<Q',STATE)
write(STATE+0x10,'<Q',QUEUE)
for at in [0xfd9823,0xfddecf]:write(gr(at),'<Q',SERV)
write(SERV+0x38,'<Q',ACCESS);write(ACCESS+8,'<Q',stub['access']);write(SERV+0x40,'<Q',API)
write(API+0x168,'<Q',stub['exists']);write(API+0xa0,'<Q',0x34c220);write(API+0xb8,'<Q',0x34c3e0)
write(gr(0xfd9882),'<Q',API);write(API+0x70,'<Q',stub['lock']);write(API+0x78,'<Q',stub['unlock'])
write(CTX,'<Q',VT);write(CTX+0x18,'<Q',SM)
for slot,name in [(8,'schema'),(0xf8,'ownership'),(0x170,'unit_meta'),(0xf0,'lookup')]:write(VT+slot,'<Q',stub[name])
write(VT+0x118,'<Q',0x297be0)
write(SM+0x18,'<Q',GLOBALS);write(SM+0x78,'<Q',TYPES)
write(GLOBALS+12,'<B',2);write(GLOBALS+8,'<f',0.001);write(GLOBALS+16,'<ff',-1,1)
write(descriptor+0x18,'<I',1);write(descriptor+0x20,'<Q',INDICES);write(descriptor+0x38,'<Q',HASHES)
write(INDICES,'<I',0);write(HASHES,'<I',field_hash);write(PAYLOAD+4,'<I',123);write(PAYLOAD+0x18,'<Q',RAW)

cases=[]
for batching in [False,True]:
 write(STATE+0x301c,'<B',int(batching));write(QUEUE,'<I',0);write(RAW,'<f',-1);write(PAYLOAD+0x20,'<II',7,7)
 write(VALUE,'<f',0);events.clear();run(G+0xfd97e0,unit,field_hash,VALUE)
 if batching:
  assert read(QUEUE,'<I')[0]==1 and read(QUEUE+16,'<Q')[0]==VALUE and read(RAW,'<f')[0]==-1
  # Demonstrate pointer lifetime: a queued value is not copied at enqueue.
  write(VALUE,'<f',.25);run(G+0xfddec0,0,QUEUE)
  assert read(RAW,'<f')[0]==.25
 else:assert read(RAW,'<f')[0]==0
 assert read(QUEUE,'<I')[0]==0 and read(PAYLOAD+0x20,'<II')==(8,8)
 assert [x['event']for x in events]==['validate','copy_dirty']
 cases.append({'batched':batching,'raw_after':read(RAW,'<f')[0],'versions_after':read(PAYLOAD+0x20,'<II'),
               'actual_stage_calls':list(events),'queued_value_is_pointer_not_copy':batching})
 # Republishing an unchanged value does not increment native versions.
 events.clear();run(G+0xfd97e0,unit,field_hash,VALUE)
 if batching:run(G+0xfddec0,0,QUEUE)
 assert read(PAYLOAD+0x20,'<II')==(8,8)
 cases.append({'batched':batching,'unchanged_value_versions_after':read(PAYLOAD+0x20,'<II')})
(R/('publisher-native-'+BUILD+'.json')).write_text(json.dumps({'build':BUILD,'boundary':__doc__,'cases':cases},indent=2),encoding='utf-8')
print('PASS',BUILD,'4 actual queue/validate/copy/dirty cases; persistent pointer lifetime; no live sync/physics repair claim')
