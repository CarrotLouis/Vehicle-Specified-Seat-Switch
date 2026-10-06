-- Real input/operation modules; native effects and OS delivery are simulated.
local fixture=assert(loadfile('work/seat_motion_loan_test/input_race_fixture.lua'))()
local dir=assert(os.getenv('VSS_INPUT_RACE_DIR'));local NEW='seat_motion_loan_test';local cases=0
local function fresh(source,host,absent)
 local f=fixture(NEW,source or 2,host or 'friend',true,dir,'outside')
 if absent then f.friend.seat=nil end
 return f
end
local function grant(f)f.c.owner.owner='self';f.c.owner.vehicle.owned_local=true;f.c.native.owned=true end
local function trigger(f,target,binding,tap)
 f:press(binding);f:tick();assert(f.dispatcher.queued and not f.probe.pending)
 if tap then f:release()end
 f:enqueue(binding,target);f:tick();assert(f.probe.pending and not f.dispatcher.queued)
end
local function friend_unchanged(f,held)
 assert(f.friend.id==8 and f.friend.unit==88 and f.friend.network_unit==808 and f.friend.seat==held)
 assert(not f.friend.vehicle_input and not f.friend.owned_local and f.c.owner.avatars[8].owner=='friend')
 if held then assert(held.collection==0 and held.role==0 and held.current==0 and held.reserved==0)end
end
-- Every non-normal vacant target, both host roles, canonical/missing seat slot.
for _,host in ipairs({'self','friend'})do for _,absent in ipairs({false,true})do for source=1,4 do for target=0,4 do
 local normal=(source==1 and target==0)or(source==2 and target==3)or(source==3 and target==2)
 if source~=target and not normal then
  local f=fresh(source,host,absent);local a,c=f.adapter,f.c;local held=f.friend.seat;local t=a:ticket(c,target)
  assert(t.outside_owner and not t.seated_owner and not t.local_authority and t.remote_network_unit==808 and t.driver_acquire==(target==0))
  assert(a:eligible(c,source,false,t,target));a:request(c,t);assert(t.request_invoked and f.transfers==1)
  a:execute(c,t);assert(a:confirmed(c,t,true)and f.mutations==1 and f.sends==1)
  if target~=0 then a:return_owned(c,t);assert(t.return_invoked and f.transfers==2 and c.owner.owner=='friend'and a:confirmed(c,t,false))
  else assert(c.driver==c.avatar and c.owner.owner=='self'and f.transfers==1)end
  friend_unchanged(f,held);cases=cases+1
 end
end end end end
local old=assert(loadfile('work/seat_seated_owner_test/adapter.lua'))()
for _,target in ipairs({0,4})do
 local f=fresh();assert(not old.eligible(f.c,2,false,nil,target)and f.adapter:eligible(f.c,2,false,nil,target));cases=cases+1
end
-- Full six-step route using actual poller/gate/dispatcher/probe/adapter.
for _,host in ipairs({'self','friend'})do for _,tap in ipairs({false,true})do for _,absent in ipairs({false,true})do
 local f=fresh(2,host,absent);local held=f.friend.seat
 for i,step in ipairs({{4,1026},{3,1112},{4,1026},{0,88},{2,1114},{0,88}})do
  trigger(f,step[1],step[2],tap);f:tick();assert(f.c.seat==step[1]);f:finish()
  if i<=3 then assert(f.c.owner.owner=='friend'and f.transfers==i*2)
  else assert(f.c.owner.owner=='self'and f.transfers==7)end
  friend_unchanged(f,held);f:release();f:tick(.5)
 end
 assert(f.mutations==6 and f.sends==6 and f:count('integrated_operation_complete')==6)
 assert(f:count('integrated_ownership_return_confirmed')==3 and f:count('integrated_driver_authority_retained')==1 and f:count('integrated_local_authority_preserved')==2)
 cases=cases+1
end end end
-- Canonical outside state, peer ownership and ticket identity must all agree.
for _,target in ipairs({0,4})do for _,change in ipairs({
 function(f)f.friend.seat.collection=9 end,function(f)f.friend.seat.collection=19 end,
 function(f)f.friend.seat.role=1 end,function(f)f.friend.seat.entry_role=1 end,
 function(f)f.friend.seat.transition_type=26 end,function(f)f.friend.seat.entrance=3 end,
 function(f)f.friend.seat.current=-1 end,function(f)f.friend.seat.reserved=-1 end,
 function(f)f.friend.seat.target=0 end,function(f)f.friend.seat.action=0 end,
 function(f)f.friend.seat.transitioning=1 end,function(f)f.friend.seat.queued_exit=1 end,
 function(f)f.friend.vehicle_input=true end,function(f)f.friend.owned_local=true end,
 function(f)f.friend.is_local=nil end,function(f)f.friend.owned_local=nil end,
 function(f)f.friend.id=99 end,function(f)f.friend.unit=99 end,function(f)f.friend.network_unit=99 end,
 function(f)f.c.owner.avatars[8].owner='self'end,function(f)f.c.owner.avatars[8]=nil end,
 function(f)f.c.owner.coordinator='changed'end,function(f)f.c.owner.members.friend=nil end,
 function(f)f.c.owner.busy=true end,function(f)f.c.sample.player_count=3 end,
 function(f,t)f.c.native.occupied[t.target]=true end,function(f,t)f.c.native.occupied[t.target]=nil end,
 function(f)f.c.native.identity='changed'end
})do
 local f=fresh();local t=f.adapter:ticket(f.c,target);change(f,t)
 assert(not pcall(f.adapter.request,f.adapter,f.c,t)and not t.request_invoked and f.transfers==0 and f.mutations==0);cases=cases+1
end end
-- Changes between preparation and final fresh guard cannot mutate the local seat.
for _,target in ipairs({0,4})do for _,change in ipairs({
 function(f)f.friend.unit=99 end,function(f)f.friend.network_unit=99 end,
 function(f)f.friend.vehicle_input=true end,function(f)f.friend.seat.transitioning=1 end,
 function(f)f.c.native.occupied[target]=true end
})do
 local f=fresh();local prepare=f.tx.prepare
 f.tx.prepare=function(...)local perform=prepare(...);change(f);return perform end
 trigger(f,target,target==0 and 88 or 1026);f:tick();for _=1,65 do f:tick()end
 assert(f.probe.phase=='stopped'and f.c.owner.owner=='friend'and f.mutations==0 and f.transfers==2)
 assert(f:count('integrated_aborted_and_returned')==1);cases=cases+1
end end
for _,target in ipairs({0,4})do for _,kind in ipairs({'focus','cancel','late','third_peer','occupied'})do
 local f=fresh();f.defer_grant=true;trigger(f,target,target==0 and 88 or 1026)
 if kind=='focus'then f.focused=false elseif kind=='cancel'then f.probe:cancel('logging_unavailable')
 elseif kind=='late'then f:tick(6)elseif kind=='third_peer'then f.c.sample.player_count=3
 elseif kind=='occupied'then f.c.native.occupied[target]=true end
 grant(f);f:tick();for _=1,65 do f:tick()end
 assert(f.probe.phase=='stopped'and f.mutations==0 and f.transfers==2 and f.c.owner.owner=='friend')
 assert(f:count('integrated_operation_complete')==0);cases=cases+1
end end
-- Partial driver mutation never repeats or returns ownership under that driver.
local f=fresh();local prepare=f.tx.prepare
f.tx.prepare=function(...)local perform=prepare(...);return function()perform();error('partial driver failure')end end
trigger(f,0,88);f:tick();for _=1,65 do f:tick()end
assert(f.probe.pending and f.mutations==1 and f.transfers==1 and f.c.driver==f.c.avatar and f.c.owner.owner=='self')
assert(f:count('integrated_operation_complete')==0)
f.c.driver=nil;f.c.native=nil;f.c.avatar.seat.collection=0
for _=1,65 do f:tick()end
assert(f.probe.phase=='stopped'and f.transfers==2 and f.mutations==1 and f.c.owner.owner=='friend');cases=cases+1
-- Actual adapter.capture asks for both owners in two-player scope, but skips
-- unrelated new peers during cleanup. Zero current outside is not a driver.
local f=fresh();local c=f.c;c.sample.state='mission';c.owner.context='fixture'
c.owner.vehicle.unit=99;c.owner.vehicle.network_unit=999;c.owner.vehicle.resource='fixture'
c.native.collection=9;c.native.collection_unit=999;c.native.resource='fixture'
local requested={};local owner={capture=function(_,s,v,need)requested[#requested+1]=need;return c.owner end,summary=function()return {}end}
local reader={capture=function()return c.sample end};local snapshot={capture=function()return c.native end}
local M=assert(loadfile('work/seat_motion_loan_test/adapter.lua'))()
local adapter=M.new({},0,{},reader,owner,snapshot,nil,nil,nil,nil,function()return ''end)
local captured=assert(adapter:capture());assert(requested[#requested]=='all'and captured.driver==nil and captured.avatar==c.avatar)
c.sample.player_count=3;c.sample.avatars[3]={id=10,is_local=false,unit=999,network_unit=0,seat=nil}
assert(adapter:capture());assert(requested[#requested]==true,'third unrelated peer must not require outside ownership lookup for cleanup');cases=cases+1
print('PASS '..cases..' outside-original-owner cases: both hosts/all non-normal targets/canonical or missing seat; exact-once held-tap six-step input; borrow-return vs driver-retain; original avatar unchanged; strict exit/identity/ownership/vacancy races; late/focus/peer cleanup; partial driver protected; all-avatar observation limited to two players')
