local ffi=require('ffi')
local profile=assert(loadfile('work/seat_switch/src/profile.lua'))()
local exe=ffi.cast('uint8_t *',0x10000000)
local object=ffi.new('uint8_t[1024]');local machine=ffi.new('uint8_t[1024]')
local world=ffi.new('uint8_t[0x171000]')
local f=assert(io.open('work/animation_resources/4d1c334d294dfa97.state_machine.main','rb'))
local source=f:read('*a');f:close()
local resource=ffi.new('uint8_t[?]',#source);ffi.copy(resource,source,#source)
local regions={{b=object,n=1024},{b=machine,n=1024},{b=resource,n=#source},{b=world,n=0x171000}}
local function number(p)return tonumber(ffi.cast('uintptr_t',p))end
local function put(b,o,t,v)local v1=ffi.new(t..'[1]',v);ffi.copy(b+o,v1,ffi.sizeof(v1))end
put(object,0,'uintptr_t',number(exe+profile.animation.unit_vtable))
put(object,0x178,'uintptr_t',number(machine));put(machine,0x28,'uintptr_t',number(resource))
put(object,0x18,'uintptr_t',number(world))
local registry={};for name,p in pairs(profile.engine_functions) do registry[number(exe+p.rva)]={name=name,bytes=p.bytes} end
local current={};for i=0,30 do current[i]=i end
local writes=0;local api={module=function()return exe end}
function api.read(a,n)
 local addr=number(a);local r=registry[addr];if r then return r.bytes:sub(1,n) end
 if addr==number(exe+profile.animation.unit_vtable+0x1b0) then
  return ffi.string(ffi.new('uintptr_t[1]',number(exe+profile.engine_functions.animation_component.rva)),8)
 end
 for _,r1 in ipairs(regions) do local start=number(r1.b)
  if addr>=start and addr+n<=start+r1.n then return ffi.string(r1.b+(addr-start),n) end
 end
end
function api.pointer(b,o)
 if not b then return nil end
 local x=ffi.new('uintptr_t[1]');ffi.copy(x,b:sub((o or 0)+1),8)
 return x[0]>65535 and ffi.cast('uint8_t *',x[0]) or nil
end
function api.replace(address,before,after)
 assert(#before==4 and #after==4 and api.read(address,4)==before)
 ffi.copy(address,after,4);return true
end
api.ffi={new=ffi.new,cast=function(t,a)
 local r=registry[number(a)]
 if not r then return ffi.cast(t,a) end
 if r.name=='unit' then return function(id)assert(id==7);return not api.unit_dead and object or nil end end
 if r.name=='animation_set_states' then return function(id,states)
  assert(id==7 and (states[32]==14 or states[32]==9));writes=writes+1
  for i=0,tonumber(states[32])-1 do
   if states[32]==14 and(i==0 or i==13)or states[32]==9 and i==8 then current[i]=tonumber(states[i])
   else assert(states[i]==-1)end
  end
 end end
 if r.name=='animation_get_states' then return function(states,id)
  api.states_get_calls=(api.states_get_calls or 0)+1;assert(id==7);for i=0,30 do states[i]=current[i] end;states[32]=31;return states
 end end
 error(r.name)
end}
local pose=assert(loadfile('work/seat_fleet_test/pose.lua'))()(api,profile)
local expected={m102={{108,64},{112,68},{106,62},{110,66},{104,60}},m104={{108,64},{112,68},{104,60}},
 bastion={{123,102},{121,96},{123,102},{123,102}},maelstrom={{123,102},{121,96},{123,102},{123,102}}}
for vehicle,seats in pairs(expected) do
 local s={vehicle=vehicle,avatar_unit=7};assert(pose.check(s))
 for target,pair in ipairs(seats) do
  assert(pose.apply(s,target-1):match('entry_action_skipped=true'))
  assert(current[0]==pair[1] and current[13]==pair[2])
  for i=1,30 do if i~=13 then assert(current[i]==i,'Unrelated animation layer reset') end end
 end
end
-- Pending entry events must not undo the immediate pose on the next frame.
local s1={vehicle='m104',avatar_unit=7};local q=profile.animation.queue
local function command(i,unit_id,event,kind)
 local b=world+q.records_offset+i*q.stride
 put(b,0,'uint32_t',unit_id);put(b,4,'uint32_t',event);put(b,0x50,'uint32_t',kind or 3)
end
command(0,7,0xe86f3c8c);put(world,q.count_offset,'uint32_t',1)
assert(pose.check(s1))
command(1,7,0xe86f3c8c);command(2,8,0xe86f3c8c);command(3,7,0x9b7741d3);command(4,7,0xe86f3c8c,4)
put(world,q.count_offset,'uint32_t',5)
local before_queue=ffi.string(world+q.records_offset,5*q.stride)
assert(pose.apply(s1,2):match('entry_events_replaced=1'))
local after_queue=ffi.string(world+q.records_offset,5*q.stride)
assert(after_queue==before_queue:sub(1,q.stride+4)..q.end_event..before_queue:sub(q.stride+9))
assert(pose.check(s1));put(world,q.count_offset,'uint32_t',0)
assert(not pcall(pose.apply,s1,2),'A consumed/reset command batch must be refused')
local s={vehicle='m102',avatar_unit=7};local before=writes
put(resource,4,'uint32_t',30);assert(not pcall(pose.check,s));put(resource,4,'uint32_t',31)
-- Even equal state counts are insufficient: a modded state index must be rejected.
local index=assert(source:find(profile.animation.states.frv_gunner[1].hash,1,true))
resource[index-1]=0;assert(not pcall(pose.check,s));resource[index-1]=source:byte(index)
put(object,0,'uintptr_t',number(exe+profile.animation.unit_vtable)+8);assert(not pcall(pose.check,s))
assert(writes==before)
-- A relocated vtable/accessor is accepted by its actual method and resource
-- identities, without relying on their previous RVAs.
profile.animation.runtime_vtable=true
profile.animation.getter_bytes=profile.engine_functions.animation_component.bytes:sub(1,8)
profile.engine_ranges={{rva=0x1000,size=0x2000000,readable=true,execute=true}}
local moved_vtable=exe+profile.animation.unit_vtable+0x100
local moved_getter=exe+profile.engine_functions.animation_component.rva+0x100
local previous_read=api.read
local accessor_ok=true
function api.read(a,n)
 if number(a)==number(moved_vtable+0x1b0) then return ffi.string(ffi.new('uintptr_t[1]',number(moved_getter)),8)end
 if number(a)==number(moved_getter) then return accessor_ok and profile.animation.getter_bytes or string.rep('\0',n)end
 return previous_read(a,n)
end
put(object,0,'uintptr_t',number(moved_vtable))
local flexible=assert(loadfile('work/seat_fleet_test/pose.lua'))()(api,profile)
assert(flexible.check(s));accessor_ok=false;assert(not pcall(flexible.check,s));accessor_ok=true
put(object,0,'uintptr_t',0x70000000);assert(not pcall(flexible.check,s))
assert(writes==before,'Compatibility checks must never mutate animation')
print('PASS: animation resource hashes and bounds, both FRV gunner poses, both tank poses, preservation of 29 other layers, and pre-write refusal of altered graphs. Engine calls are mocked.')
print('PASS: relocated animation accessor/vtable, changed method and out-of-image pointer refusal without writes.')

-- Full captured animation states, real extracted resource, actual new pose
-- module. Engine setters simulated; this is not a visual/network-success test.
profile=assert(loadfile('work/seat_fleet_test/tank_spec.lua'))()(profile,{records={},core={},edges={},globals={driver={}}})
put(object,0,'uintptr_t',number(exe+profile.animation.unit_vtable));accessor_ok=true
local repaired_pose=assert(loadfile('work/seat_fleet_test/pose.lua'))()(api,profile)
local records=assert(loadfile('work/seat_fleet_test/captured_pose_cases.lua'))()
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
local previous_pose=assert(loadfile('work/seat_fleet_test/regression_0182_pose.lua'))()(api,profile)
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
 return assert(loadfile('work/seat_fleet_test/fall_repair.lua'))()(api,profile,
  assert(loadfile('work/seat_fleet_test/pose.lua'))(),adapter,send,snapshot,
  assert(loadfile('work/seat_fleet_test/adapter.lua'))().layout,{health=function()end},function(e)events[#events+1]=e end)
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

-- Appended to the extracted graph/recorded-pose fixture by prepare_fleet_tests.
-- All engine effects are mocked; this does not prove live animation delivery.
local fleet=assert(loadfile('work/seat_fleet_test/fleet_policy.lua'))()
local peers={selfpeer,destination,'THIRD003','FOUR0004'}
local captures,replace_member=0,false
local function fleet_context(count,host)
 local row=context();row.sample.player_count=count;row.sample.peer_count=count;row.sample.avatars={row.avatar}
 row.owner.peer_count=count;row.owner.members={};row.owner.owner=destination;row.owner.coordinator=peers[host]
 row.owner.vehicle={id=9,unit=90,network_unit=900,owned_local=false}
 for i=1,count do
  row.owner.members[peers[i]]=true
  if i>1 then
   local a={id=699+i,unit=70+i,network_unit=700+i,is_local=false,owned_local=false,vehicle_input=false,
    seat={collection=0,current=0,reserved=0,role=0,target=-1,action=-1,transitioning=0,queued_exit=0}}
   row.sample.avatars[i]=a;row.owner.avatars[a.id]={owner=peers[i]}
  end
 end
 return row
end
local delivered={};local fleet_send={prepare_fall=function(_,snap,peer)
 assert(snap==s);local raw=ffi.string(ffi.new('uint64_t[1]',peer),8)
 assert(raw~=selfpeer and c.owner.members[raw])
 return {check=function()end,send=function()delivered[#delivered+1]=raw end}
end}
local fleet_adapter={capture=function()
 captures=captures+1
 if replace_member and captures==2 then
  c.owner.members[peers[3]]=nil;c.owner.members['NEWPEER3']=true;c.owner.avatars[702].owner='NEWPEER3'
 end
 return c
end}
local function new_fleet_helper()
 return assert(loadfile('work/seat_fleet_test/fall_repair.lua'))()(api,profile,
  assert(loadfile('work/seat_fleet_test/pose.lua'))(),fleet_adapter,fleet_send,snapshot,
  assert(loadfile('work/seat_fleet_test/adapter.lua'))().layout,{health=function()end},function(e)events[#events+1]=e end,fleet)
end
api.experiment_allowed=function()return true end
local fleet_cases=0
for count=3,4 do for host=1,count do
 s.player_count=count;s.peer_count=count;c=fleet_context(count,host);captures=0;replace_member=false;delivered={}
 current[0]=122;current[13]=99;current[8]=238;local old=writes
 local helper=new_fleet_helper();helper:update(s)
 assert(writes==old+1 and current[8]==0 and current[0]==122 and current[13]==99 and #delivered==count-1)
 local seen={};for _,peer in ipairs(delivered)do assert(not seen[peer]);seen[peer]=true end
 helper:update(s);assert(writes==old+1 and #delivered==count-1);fleet_cases=fleet_cases+1
end end
for count=3,4 do
 s.player_count=count;s.peer_count=count;c=fleet_context(count,1);captures=0;replace_member=true;delivered={}
 current[8]=238;local old=writes;local helper=new_fleet_helper()
 assert(pcall(helper.update,helper,s)and writes==old and #delivered==0 and current[8]==238,
  'Member replacement must defer repair without disabling normal seat input')
 fleet_cases=fleet_cases+1
end
for count=3,4 do
 s.player_count=count;s.peer_count=count;c=fleet_context(count,1);captures=0;replace_member=false;delivered={}
 local waiting=c.sample.avatars[count];c.sample.avatars[count]=nil;current[8]=238
 local old=writes;local helper=new_fleet_helper();assert(pcall(helper.update,helper,s)and writes==old and #delivered==0)
 c.sample.avatars[count]=waiting;helper:update(s);assert(writes==old+1 and #delivered==count-1)
 fleet_cases=fleet_cases+1
end
print('PASS '..fleet_cases..' three/four-peer Bastion native-route repairs over extracted graph: all coordinators, layer8 only/once, all other peers, same-count roster and incomplete join defer before writes without disabling input, then resume. Effects mocked.')
