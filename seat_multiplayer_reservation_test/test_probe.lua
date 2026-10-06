local scope=assert(loadfile('work/seat_multiplayer_reservation_test/scope.lua'))()
local membership=assert(loadfile('work/seat_multiplayer_reservation_test/membership.lua'))()
local M=assert(loadfile('work/seat_multiplayer_reservation_test/probe.lua'))()(scope,membership)
local bit=require('bit')
local function clone(x)if type(x)~='table'then return x end;local t={};for k,v in pairs(x)do t[k]=clone(v)end;return t end
local BASE={identity='car_session_identity',seat=1,destination='driver!!',sample={player_count=2,local_count=1},
 native={identity='own_avatar_binding',avatar=7,avatar_unit=701,vehicle='m102',transition=26,owned=false,player_count=2,peer_count=2,node=1,active=false,
  mask=28,occupied={[0]=true,[1]=true,[2]=false,[3]=false,[4]=false},profile={row=8,roles={1,3,3,3,2}}},
 owner={owner='driver!!',selfpeer='selfpeer',serial=3,peer_count=2,coordinator='driver!!',members={['driver!!']=true,selfpeer=true},
  vehicle={id=9,unit=901,network_unit=4123,owned_local=false},avatars={[7]={owner='selfpeer'},[8]={owner='driver!!'}}},
 avatar={id=7,unit=701,network_unit=4107,is_local=true,owned_local=true,vehicle_input=true,seat={collection=9,current=1,reserved=1,role=3,target=-1,action=-1,transitioning=0,queued_exit=0}},
 driver={id=8,unit=801,network_unit=4207,is_local=false,owned_local=false,seat={collection=9,current=0,reserved=0,role=1,target=-1,action=-1,transitioning=0,queued_exit=0}}}
BASE.sample.avatars={BASE.avatar,BASE.driver}
local function fixture()
 local c=clone(BASE);c.sample.avatars={c.avatar,c.driver}
 local trace={active=true};local state,arm,cookie,requests,writes,releases,sends,bounds=nil,0,0,0,0,0,0,0
 local now,focus,current,quiet=10,true,true,true
 local events={};local mounted_ready=true
 local api={input_allowed=function()return focus end,control_down=function()return not quiet end,experiment_allowed=function()return true end}
 local mounted={prepare=function(_,ctx,target)if ctx.native.profile.roles[target+1]==2 then return {target=target}end end,ready=function()return mounted_ready end}
 local adapter={mounted=mounted,capture=function()return c end,motion={boundary=function()bounds=bounds+1 end}}
 local snapshot={current=function()return current end}
 function trace:health()assert(self.active)end
 function trace:gate_arm(peer,car,avatar,source,target)
  assert(peer=='driver!!'and car==4123 and avatar==4107);assert(not state);arm=arm+1;cookie=cookie+1
  state={cookie=cookie,status=1,peer_key=peer,car=car,avatar=avatar,source=source,target=target,chosen=4294967295,guard_lost=0,repeats=0}
  return cookie
 end
 function trace:gate_peek(key)assert(state and state.cookie==key);return clone(state)end
 function trace:gate_finish(key)assert(state.cookie==key and(state.status==2 or state.status==3));state=nil end
 local entrance={prepare_request=function(_,ctx,target)return function()requests=requests+1;assert(state and state.status==1)end,2 end,
 prepare_release=function(_,ctx,slot)return function()
  assert(slot>=1 and slot<=4);releases=releases+1
  c.native.mask=bit.bor(c.native.mask,2^slot);c.native.occupied[slot]=false
 end end}
 local tx={preflight=function()return true end,prepare=function(_,s,target,grant)
  assert(not s.owned and grant:check());return function()
   assert(grant:check());writes=writes+1;c.seat=target;c.native.node=target;c.avatar.seat.current=target;c.avatar.seat.reserved=target;c.avatar.seat.role=c.native.profile.roles[target+1]
  end
 end}
 local sender={preflight=function()return true end,prepare=function(_,o,peer,s,target,grant)
  assert(peer=='driver!!'and o.owner~='selfpeer'and not s.owned and grant:check());return function()assert(grant:check());sends=sends+1 end
 end}
 sender.preflight_all=function(self,o,destinations,s,target)assert(#destinations==1);return self:preflight(o,destinations[1],s,target)end
 sender.prepare_all=function(self,o,destinations,s,target,grant)assert(#destinations==1);return self:prepare(o,destinations[1],s,target,grant)end
 local probe=M.new(adapter,api,snapshot,trace,entrance,tx,sender,function(e)events[#events+1]=e end,function()end)
 return {probe=probe,c=c,trace=trace,events=events,
  step=function(trigger,t)return probe:step(trigger,t or now,focus)end,
  reply=function(status,chosen)state.status=status;state.chosen=chosen or state.target;state.tick=111;state.repeats=1 end,
  reserve=function(target)c.native.mask=bit.band(c.native.mask,bit.bnot(2^target));c.native.occupied[target]=true end,
  corrupt=function(key,value)state[key]=value end,
  focus=function(value)focus=value end,quiet=function(value)quiet=value end,mounted_ready=function(value)mounted_ready=value end,
  numbers=function()return arm,requests,writes,releases,sends,bounds end}
end
-- Genuine ACK arrives before property: no avatar change until master bit.
local f=fixture();assert(f.step(2));local a,r,w=f.numbers();assert(a==1 and r==1 and w==0)
f.reply(2,2);f.step(nil,10.1);a,r,w=f.numbers();assert(w==0 and f.probe.pending and f.c.seat==1)
f.reserve(2);f.step(nil,10.2);a,r,w=f.numbers();assert(w==1 and f.c.seat==2 and f.probe.pending)
f.step(nil,10.3);local releases,sends; a,r,w,releases,sends=f.numbers()
assert(not f.probe.pending and f.probe.phase=='waiting'and releases==1 and sends==1 and f.c.owner.owner=='driver!!'and f.c.owner.serial==3)
-- Return passenger2->1: second real grant, never borrow/return.
assert(f.step(1,11));f.reply(2,1);f.reserve(1);f.step(nil,11.1);f.step(nil,11.2)
a,r,w,releases,sends=f.numbers();assert(a==2 and r==2 and w==2 and releases==2 and sends==2 and not f.probe.pending and f.c.seat==1)
print('PASS two actual passenger directions, late reservation property barrier, exact old-slot release and unchanged owner/serial')
-- The authenticated native reply cannot be replaced by a fabricated Lua flag.
for _,change in ipairs({{'car',999},{'avatar',999},{'peer_key','another!'},{'source',3},{'target',3},{'guard_lost',1}})do
 f=fixture();assert(f.step(2));f.reply(2,2);f.reserve(2);f.corrupt(change[1],change[2]);pcall(f.step,nil,10.1)
 a,r,w,releases,sends=f.numbers();assert(w==0 and releases==0 and sends==0)
end
-- Owner fallback and contradictory replies stay gated for review, never
-- arbitrarily free fallback/driver seats or use a different requested seat.
for _,reply in ipairs({{2,4},{2,0},{4,2}})do
 f=fixture();assert(f.step(2));f.reply(reply[1],reply[2]);f.reserve(2);f.step(nil,10.1)
 a,r,w,releases,sends=f.numbers();assert(f.probe.phase=='stopped'and w==0 and releases==0 and sends==0)
end
-- True denial and timeout: no local mutation/retry. Late grant after timeout
-- never executes or releases another seat in this first prototype.
f=fixture();assert(f.step(2));f.reply(3);f.step(nil,10.1);assert(not f.probe.pending and f.probe.phase=='waiting')
f=fixture();assert(f.step(2));f.step(nil,16);assert(f.probe.pending);f.reply(2,2);f.reserve(2);f.step(nil,16.1)
a,r,w,releases,sends=f.numbers();assert(f.probe.phase=='stopped'and w==0 and r==1 and releases==0 and sends==0)
for _,change in ipairs({function(x)x.native.owned=true end,function(x)x.native.avatar_unit=702 end,function(x)x.sample.player_count=3 end,
 function(x)x.owner.avatars[8].owner='selfpeer'end,function(x)x.native.avatar=8 end,function(x)x.native.occupied[2]=true end,
 function(x)x.avatar.vehicle_input=false end})do
 f=fixture();change(f.c);local good=pcall(f.step,2);a,r,w=f.numbers();assert(r==0 and w==0)
end
for _,target in ipairs({0,5})do f=fixture();assert(f.step(target)==false);a,r,w=f.numbers();assert(r==0 and w==0)end
for _,change in ipairs({function(x)x.owner.serial=4 end,function(x)x.driver.unit=802 end,function(x)x.avatar.network_unit=4108 end})do
 f=fixture();assert(f.step(2));change(f.c);f.reply(2,2);f.reserve(2);pcall(f.step,nil,10.1);a,r,w,releases,sends=f.numbers();assert(w==0 and releases==0)
end
print('PASS corrupted/missing/fallback/conflicting grants, denials/timeouts, changed owner/avatar/driver/fleet and occupied/excluded seats refuse all writes')

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
