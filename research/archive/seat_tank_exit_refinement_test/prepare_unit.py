"""Adapt fixtures to the expanded scope, preserving rejected/changed-state tests."""
from pathlib import Path
R=Path(__file__).resolve().parent;A=R.parent/'seat_reservation_test';B=R.parent/'seat_pose_trace_test'
def base(name):return (A/name).read_text().replace('work/seat_reservation_test/','work/seat_tank_exit_refinement_test/')
s=base('test_probe.lua')
s=s.replace("local M=assert(loadfile('work/seat_tank_exit_refinement_test/probe.lua'))()", "local scope=assert(loadfile('work/seat_tank_exit_refinement_test/scope.lua'))()\nlocal M=assert(loadfile('work/seat_tank_exit_refinement_test/probe.lua'))()(scope)")
s=s.replace('profile={roles={1,3,3,3,2}}','profile={row=8,roles={1,3,3,3,2}}')
s=s.replace('local events={}','local events={};local mounted_ready=true')
s=s.replace('local adapter={capture=', "local mounted={prepare=function(_,ctx,target)if ctx.native.profile.roles[target+1]==2 then return {target=target}end end,ready=function()return mounted_ready end}\n local adapter={mounted=mounted,capture=")
s=s.replace('assert(slot==1 or slot==2)', 'assert(slot>=1 and slot<=4)')
s=s.replace('c.avatar.seat.reserved=target','c.avatar.seat.reserved=target;c.avatar.seat.role=c.native.profile.roles[target+1]')
s=s.replace('quiet=function(value)quiet=value end,','quiet=function(value)quiet=value end,mounted_ready=function(value)mounted_ready=value end,')
s=s.replace('for target=0,4,4 do','for _,target in ipairs({0,5})do')
s+='''
-- Expanded model/role cases and both hosting roles: authentic owner stays driver.
local cases=0
for _,name in ipairs({'m102','m103','m104'})do for _,host in ipairs({'driver','installer'})do
 local roles=name=='m102'and {1,3,3,3,2}or name=='m103'and {1,3,3,3}or {1,3,2}
 for source=1,#roles-1 do for target=1,#roles-1 do if source~=target then
  f=fixture();local c=f.c;c.native.vehicle=name;c.native.transition=({m102=26,m103=27,m104=28})[name];c.native.profile.roles=roles
  c.owner.coordinator=host=='driver'and 'driver!!'or 'selfpeer';c.native.node=source;c.seat=source
  c.avatar.seat.current=source;c.avatar.seat.reserved=source;c.avatar.seat.role=roles[source+1]
  c.native.mask=0;for i=0,4 do c.native.occupied[i]=i==0 or i==source;if i>0 and i<#roles and i~=source then c.native.mask=bit.bor(c.native.mask,2^i)end end
  assert(f.step(target));f.reply(2,target);f.reserve(target)
  if roles[target+1]==2 then
   f.mounted_ready(false);f.step(nil,10.1);a,r,w=f.numbers();assert(w==0 and f.probe.pending)
   f.mounted_ready(true)
  end
  f.step(nil,10.2);f.step(nil,10.3);a,r,w,releases,sends=f.numbers()
  assert(w==1 and sends==1 and releases==1 and not f.probe.pending and c.seat==target and c.owner.serial==3)
  cases=cases+1
 end end end
end end
print('PASS '..cases..' three-FRV/both-host/role2-role3 grant barriers and exact old-source releases; zero chassis ownership changes')
'''
(R/'test_probe.lua').write_text(s)
s=base('test_entrance.lua')
s=s.replace('for i=1,5 do','for i=1,#rows do').replace('mem[0x20000+40]=b','mem[0x20000+#rows*8]=b')
s=s.replace('assert(typ==26 and id==9 and e<=7)','assert(typ>=26 and typ<=28 and id==9 and e<=7)').replace('typ==26 and node>=5 and node<=9','typ>=26 and typ<=28 and node>=#rows and node<#rows*2')
extra="""
-- Different row counts still derive entrance IDs from the actual lookup.
mem[0x20000+40]=nil
s.vehicle='m103';s.transition=27;s.profile.roles={1,3,3,3};rows={3,1,0,2};map={4,5,6,7};setrows();setasset(4)
assert(obj:find(s,2)==3)
mem[0x20000+32]=nil
s.vehicle='m104';s.transition=28;s.profile.roles={1,3,2};rows={2,0,1};map={3,4,5};setrows();setasset(3)
assert(obj:find(s,2)==0)
print('PASS actual dynamic entrance inversion for 5/4/3-row FRV layouts; no assumed entrance order')
"""
s=s.replace('for _,f in pairs(keep)do f:free()end',extra+'\nfor _,f in pairs(keep)do f:free()end')
s=s.replace("local factory=", "local scope=assert(loadfile('work/seat_tank_exit_refinement_test/scope.lua'))()\nlocal factory=",1)
s=s.replace("local map={", "local stride=8\nlocal map={",1)
s=s.replace("bytes('int32_t',-1)end;mem[0x20000+#rows*8]=b", "bytes('int32_t',-1)..(stride==12 and bytes('int32_t',-1)or '')end;mem[0x20000+#rows*stride]=b")
s=s.replace('typ>=26 and typ<=28', '(typ>=26 and typ<=28 or typ==43 or typ==44)')
s=s.replace('node*8+(badptr and 8 or 0)', 'node*stride+(badptr and stride or 0)')
s=s.replace('events[#events+1]=e end)', 'events[#events+1]=e end,scope)')
s=s.replace('for _,f in pairs(keep)do f:free()end', '''
stride=12;rows={0,2,1,3};map={4,5,6,7};setrows();setasset(4)
s.vehicle='bastion';s.transition=43;s.profile.row=12;s.profile.roles={1,2,3,3};assert(obj:find(s,0)==0)
s.vehicle='maelstrom';s.transition=44;assert(obj:find(s,0)==0)
print('PASS tank twelve-byte entry tables, actual driver entrance inversion; no guessed ordinal')
for _,f in pairs(keep)do f:free()end''')
(R/'test_entrance.lua').write_text(s)
s=base('test_motion.lua')
s=s.replace("local factory=", "local scope=assert(loadfile('work/seat_tank_exit_refinement_test/scope.lua'))()\nlocal factory=",1)
s=s.replace('events[#events+1]=e end)','events[#events+1]=e end,scope)')
s=s.replace("native={vehicle='m102'}","native={vehicle='m102',transition=26,profile={row=8,roles={1,3,3,3,2}}}")
(R/'test_motion.lua').write_text(s)
s=(B/'test_binding_sender.lua').read_text().replace('work/seat_pose_trace_test/binding_sender.lua','work/seat_tank_exit_refinement_test/binding_sender.lua')
extra="""
-- A nonowner requires the authenticated grant at preparation AND send.
s.vehicle='m102';s.transition=26;s.profile=profiles.m102;s.node=4;s.owned=false
after=false;before_weapon=80;before_rotation=0;slot2=0;selected=90
local previous=#calls;assert(sender:preflight(s,dest,1)and #calls==previous)
assert(not pcall(sender.prepare,sender,s,dest,1)and #calls==previous)
local valid=true;local grant={source=4,target=1,check=function()return valid end}
local prepared=sender:prepare(s,dest,1,grant);after=true;valid=false
assert(not pcall(prepared.send,function()end)and #calls==previous);valid=true
prepared.send(function()end);assert(#calls==previous+2)
print('PASS nonowned gunner personal sync requires genuine grant and complete local restoration; dry preflight sends nothing')
"""
s=s.replace('cb.send:free()',extra+'\ncb.send:free()');(R/'test_binding.lua').write_text(s)
print('PASS expanded role/fleet/host fixtures; actual binding ABI negative controls preserved')
