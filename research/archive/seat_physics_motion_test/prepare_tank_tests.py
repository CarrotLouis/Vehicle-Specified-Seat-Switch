from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parent
src=(W/'seat_switch/tests/test_pose.lua').read_text().replace('work/seat_switch/src/pose.lua','work/seat_physics_motion_test/pose.lua')
old="""  assert(id==7 and states[32]==14);writes=writes+1
  for i=0,13 do if i==0 or i==13 then current[i]=tonumber(states[i]) else assert(states[i]==-1) end end"""
new="""  assert(id==7 and (states[32]==14 or states[32]==9));writes=writes+1
  for i=0,tonumber(states[32])-1 do
   if states[32]==14 and(i==0 or i==13)or states[32]==9 and i==8 then current[i]=tonumber(states[i])
   else assert(states[i]==-1)end
  end"""
assert old in src;src=src.replace(old,new)
src=src.replace('return object end end','return not api.unit_dead and object or nil end end')
src=src.replace('assert(id==7);for i=0,30 do states[i]=current[i] end;', 'api.states_get_calls=(api.states_get_calls or 0)+1;assert(id==7);for i=0,30 do states[i]=current[i] end;')
tail=r'''
-- Full captured animation states, real extracted resource, actual new pose
-- module. Engine setters simulated; this is not a visual/network-success test.
profile=assert(loadfile('work/seat_physics_motion_test/tank_spec.lua'))()(profile,{records={},core={},edges={},globals={driver={}}})
put(object,0,'uintptr_t',number(exe+profile.animation.unit_vtable));accessor_ok=true
local repaired_pose=assert(loadfile('work/seat_physics_motion_test/pose.lua'))()(api,profile)
local records=assert(loadfile('work/seat_physics_motion_test/captured_pose_cases.lua'))()
local cases,affected,samples=0,0,0
local function assign(values)for i=0,30 do current[i]=values[i+1]end end
for _,row in ipairs(records)do for _,node in ipairs({2,3})do
 assign(row.values)
 local s={vehicle=row.vehicle,avatar_unit=7,profile=profile.tables[row.vehicle],transition=profile.tables[row.vehicle].transition,node=node}
 local expected=row.vehicle=='bastion'and(current[8]==237 or current[8]==238)and
  (current[0]==123 and current[13]==102 or current[0]==122 and current[13]==99)
 local old=writes;local before={};for i=0,30 do before[i]=current[i]end
 local cleared=repaired_pose.clear_fall(s)
 assert(cleared==(expected or false)and writes-old==(expected and 1 or 0))
 for i=0,30 do assert(current[i]==(expected and i==8 and 0 or before[i]))end
 assert(not repaired_pose.clear_fall(s)and writes==old+(expected and 1 or 0))
 cases=cases+1;samples=samples+row.occurrences
 if expected then affected=affected+1 end
end end
assert(affected>0)
-- Reproduce the old retained overlay, then exercise real cross-pose application.
local ss={vehicle='bastion',avatar_unit=7,profile=profile.tables.bastion,transition=43,node=0}
current[7]=3;current[17]=18;current[8]=238
local previous_pose=assert(loadfile('work/seat_physics_motion_test/regression_0182_pose.lua'))()(api,profile)
assert(previous_pose.check(ss));previous_pose.apply(ss,2);assert(current[8]==238)
assert(repaired_pose.check(ss));repaired_pose.apply(ss,2);assert(current[8]==0 and current[0]==123 and current[13]==102)
-- Wrong overlay identity, foreign action, auxiliary transition and layer count.
for _,state in ipairs(profile.animation.bastion_fall.states)do
 local at=assert(source:find(state.hash,1,true));local old=resource[at-1];resource[at-1]=(old+1)%256
 current[8]=237;local n=writes
 assert(not pcall(repaired_pose.clear_fall,setmetatable({node=2},{__index=ss}))and writes==n)
 resource[at-1]=old
end
current[0]=122;current[13]=99;current[8]=100
local n=writes;assert(not repaired_pose.clear_fall(setmetatable({node=2},{__index=ss}))and writes==n)
current[8]=238;current[7]=0
assert(not pcall(repaired_pose.clear_fall,setmetatable({node=2},{__index=ss}))and writes==n);current[7]=3
local getter_calls=api.states_get_calls;api.unit_dead=true
assert(not pcall(repaired_pose.fall_present,setmetatable({node=2},{__index=ss}))and api.states_get_calls==getter_calls and writes==n,
 'Expired unit must refuse BEFORE the engine animation getter')
api.unit_dead=false
-- Native-route helper: settles in a passenger seat while chassis remains remote.
local selfpeer,destination='SELFPEER','FRIEND01';local s=setmetatable({node=2,identity='own/vehicle',avatar=700,
 collection=9,player_count=2,peer_count=2,owned=false},{__index=ss})
local function context()
 return {identity='session/vehicle',destination=destination,native=s,sample={player_count=2,local_count=1},
 owner={peer_count=2,busy=false,selfpeer=selfpeer,coordinator=destination,members={[selfpeer]=true,[destination]=true},
 avatars={[700]={owner=selfpeer}},session=1,engine=2},
 avatar={id=700,unit=7,is_local=true,owned_local=true,vehicle_input=true,
 seat={collection=9,current=s.node,reserved=s.node,role=3,target=-1,action=-1,transitioning=0,queued_exit=0}}}
end
local c=context();local sends,reads=0,0;local events={}
local adapter={capture=function()reads=reads+1;return c end}
api.ffi.copy=ffi.copy
local expected_peer=ffi.new('uint64_t[1]');ffi.copy(expected_peer,destination,8)
local send={prepare_fall=function(_,snap,dest)
 assert(snap==s and dest==expected_peer[0])
 return {check=function()end,send=function()sends=sends+1 end}
end}
local stable=true;local snapshot={current=function()return stable end}
api.experiment_allowed=function()return true end
local function new_helper()
 return assert(loadfile('work/seat_physics_motion_test/fall_repair.lua'))()(api,profile,
  assert(loadfile('work/seat_physics_motion_test/pose.lua'))(),adapter,send,snapshot,
  assert(loadfile('work/seat_physics_motion_test/adapter.lua'))().layout,{health=function()end},function(e)events[#events+1]=e end)
end
current[0]=122;current[13]=99;current[8]=238
local helper=new_helper();n=writes;helper:update(s)
assert(writes==n+1 and sends==1 and current[0]==122 and current[13]==99 and current[8]==0)
current[8]=238;helper:update(s);assert(writes==n+1 and sends==1,'Do not repeatedly clear a returned overlay in one visit')
helper:update(nil);helper:update(s);assert(writes==n+2 and sends==2)
-- Empty overlay: one check per visit, no getters/peer lookups each frame.
local empty=new_helper();current[8]=0;local g=api.states_get_calls
assert(empty:needs_check(s));empty:update(s);assert(not empty:needs_check(s))
local after_get=api.states_get_calls;assert(after_get>g)
for i=1,60 do empty:update(s)end;assert(api.states_get_calls==after_get)
empty:update(nil);assert(empty:needs_check(s))
for _,count in ipairs({1,3,4})do
 s.player_count=count;s.peer_count=count;current[8]=238;local a,b,g=writes,sends,api.states_get_calls
 local outside=new_helper();assert(not outside:needs_check(s));outside:update(s)
 assert(writes==a and sends==b and api.states_get_calls==g,'Known non-two-player scope skips without engine call or exception')
end
s.player_count=2;s.peer_count=2
for _,change in ipairs({function()c.owner.peer_count=3 end,function()c.sample.local_count=2 end,
 function()c.destination=selfpeer end,function()c.owner.avatars[700].owner=destination end,
 function()c.avatar.unit=8 end,function()c.avatar.seat.transitioning=1 end,
 function()c.avatar.seat.current=3 end,function()c.avatar.owned_local=false end,function()c.owner.busy=true end})do
 c=context();change();current[8]=238;local a,b=writes,sends
 assert(not pcall(new_helper().update,new_helper(),s)and writes==a and sends==b)
end
c=context();current[8]=238;stable=false;n=writes;new_helper():update(s);assert(writes==n);stable=true
api.experiment_allowed=function()return false end
assert(not pcall(new_helper().update,new_helper(),s)and writes==n)
print('PASS '..cases..' recorded pose replays ('..samples..' observed samples), '..affected..' matching fall cases; old retained-overlay reproduction, cross and native lean preservation, named resource checks, one reset per visit, foreign/session/role/log guards without writes. Engine effects mocked.')
'''
(R/'test_tank_pose.lua').write_text(src+tail)
print('Prepared captured pose/resource/native-route regression test')
