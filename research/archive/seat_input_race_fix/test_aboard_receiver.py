"""Actual captured seat receivers with TWO mapped occupants in one chassis.

Tests snapshot/transition targeting and unrelated seater bytes. External engine
APIs, attachment and role side effects remain stubbed; not a rendering/network
or complete two-avatar physics proof. No game process is touched.
"""
from pathlib import Path
import json,struct
R=Path(__file__).resolve().parent
setup=(R/'test_receiver_native.py').read_text(encoding='utf-8').split('results=[]',1)[0]
setup=setup.replace("if address==0x63dd10:w(ss+8,'<I',reg(UC_X86_REG_R8)&0xffffffff)",
 "if address==0x63dd10:\n        assert reg(UC_X86_REG_RCX)==sm and reg(UC_X86_REG_RDX)==0,'role helper must target only own mapped seater'\n        w(ss+8,'<I',reg(UC_X86_REG_R8)&0xffffffff)")
scope={'__file__':str(R/'test_receiver_native.py')}
exec(compile(setup,str(R/'test_receiver_native.py'),'exec'),scope)
v,vm,w,n,sm,am,ss,cs,calls=[scope[k] for k in ('v','vm','w','n','sm','am','ss','cs','calls')]
# Real hash lookup resolves7->slot0 and8->slot1 instead of a singleton fixture.
w(sm+0x20,'<QIII',0x10015000,2,0xffffffff,1)
w(sm+8,'<III',2,2,0) # Both mapped seaters are active; ownership side effects stubbed.
w(0x10015000,'<IIII',8,1,7,0)
w(sm+0x38,'<Q',0x10016000);w(0x10016000,'<QQ',0x10016100,0x10016200)
w(0x10016200,'<IIIIII',0,0,8,0,1008,0)
roles=[1,3,3,3,2];results=[]
for remote in (1,2,3):
 for source in range(5):
  for target in range(5):
   if source==target or remote in (source,target):continue
   w(0x10001000,'<I',source)
   if v.run(0x1196dc0,26,0x10001000,target)&0xffffffff!=0xffffffff:continue
   vm.mem_write(ss,bytes(128));calls.clear();w(cs,'<I',26)
   for at,node in ((ss,source),(ss+64,remote)):
    w(at,'<IIIIiiii',9,26,roles[node],roles[node],0,node,-1,node);w(at+0x20,'<i',-1)
   # Distinct meaningful adjacent state bytes detect writes past the own slot.
   vm.mem_write(ss+64+0x38,b'FRIEND!!')
   held=bytes(vm.mem_read(ss+64,64));identity=bytes(vm.mem_read(0x10016200,24))
   w(0x10080008+0x28,'<I',target);w(0x10080008+0x30,'<I',0)
   v.run(0x63eb10,sm,0,7,9)
   assert bytes(vm.mem_read(ss+64,64))==held
   w(0x10080008+0x28,'<I',target);w(0x10080008+0x30,'<i',-1);w(0x10080008+0x38,'<f',0)
   v.run(0x63ecc0,sm,0,7,target)
   v.run(0x639b40,sm,0)
   assert (n(ss+0x14),n(ss+8),n(ss+0x1c))==(target,roles[target],target),(remote,source,target,n(ss+0x14),n(ss+8),n(ss+0x1c),calls)
   assert bytes(vm.mem_read(ss+64,64))==held and bytes(vm.mem_read(0x10016200,24))==identity
   assert not any(x[0]=='0x63bc60' for x in calls),'no exit helper'
   results.append(dict(source=source,target=target,remote_passenger=remote,remote_state_unchanged=True,remote_entity_unchanged=True))
(R/('aboard-receiver-'+scope['BUILD']+'.json')).write_text(json.dumps(dict(boundary=__doc__,build=scope['BUILD'],cases=results),indent=2))
print('PASS',len(results),scope['BUILD'],'real two-mapped-occupant receiver cases; own slot only; remote seat/entity bytes unchanged; external effects stubbed')
