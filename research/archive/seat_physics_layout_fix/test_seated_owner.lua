-- Actual operation/input modules; simulate OS queue and native/network effects.
local fixture=assert(loadfile('work/seat_physics_layout_fix/input_race_fixture.lua'))()
local dir=assert(os.getenv('VSS_INPUT_RACE_DIR'));local NEW='seat_physics_layout_fix';local cases=0
local function fresh(source,host,remote)return fixture(NEW,source or 2,host or 'friend',true,dir,remote or 1)end
local function grant(f)f.c.owner.owner='self';f.c.owner.vehicle.owned_local=true;f.c.native.owned=true end
local function trigger(f,target,binding,tap)
 f:press(binding);f:tick();assert(f.dispatcher.queued and not f.probe.pending)
 if tap then f:release()end
 f:enqueue(binding,target);f:tick();assert(f.probe.pending and not f.dispatcher.queued)
end
local function same_friend(f,held,node)
 assert(f.friend.id==8 and f.friend.unit==88 and f.friend.seat==held and held.current==node and held.reserved==node)
 assert(held.role==(node==4 and 2 or 3)and f.c.native.occupied[node]and f.c.owner.avatars[8].owner=='friend')
end
-- Every available non-normal cross pair with a seated original owner.
-- Driver target retains the actual grant; other targets return it once.
for _,host in ipairs({'self','friend'})do for remote=1,4 do for source=1,4 do for target=0,4 do
 local normal=(source==1 and target==0)or(source==2 and target==3)or(source==3 and target==2)
 if source~=remote and target~=remote and source~=target and not normal then
  local f=fresh(source,host,remote);local a,c=f.adapter,f.c;local held=f.friend.seat;local t=a:ticket(c,target)
  assert(t.seated_owner and t.driver_acquire==(target==0)and not t.local_authority and t.remote_node==remote)
  assert(a:eligible(c,source,false,t,target));a:request(c,t);assert(t.request_invoked and f.transfers==1)
  assert(a:eligible(c,source,true,t,target));a:execute(c,t);assert(a:confirmed(c,t,true))
  if target~=0 then a:return_owned(c,t);assert(t.return_invoked and f.transfers==2 and c.owner.owner=='friend');assert(a:confirmed(c,t,false))
  else assert(c.driver==c.avatar and c.owner.owner=='self'and f.transfers==1)end
  assert(f.mutations==1 and f.sends==1 and t.sync_returned);same_friend(f,held,remote);cases=cases+1
 end
end end end end
-- Recorded0.15.0 supported only driver acquisition with remote gunner.
local old=assert(loadfile('work/seat_driver_acquire_test/adapter.lua'))()
for _,target in ipairs({0,4})do
 local f=fresh();assert(not old.eligible(f.c,2,false,nil,target)and f.adapter:eligible(f.c,2,false,nil,target));cases=cases+1
end
-- Full input path with original owner in each passenger seat, both hosts/tap modes.
-- Borrow/return through gunner and passengers, acquire from gunner into driver,
-- then preserve local authority through driver/passenger changes.
for _,host in ipairs({'self','friend'})do for remote=1,3 do for _,tap in ipairs({false,true})do
 local source=remote==2 and 3 or 2;local opposite=remote==3 and 1 or 3
 local f=fresh(source,host,remote);local held=f.friend.seat
 local bindings={[0]=88,[1]=90,[2]=1114,[3]=1112,[4]=1026}
 local route={4,opposite,4,0,source,0}
 for i,target in ipairs(route)do
  trigger(f,target,bindings[target],tap);f:tick();assert(f.c.seat==target);f:finish()
  if i<=3 then assert(f.c.owner.owner=='friend'and f.transfers==i*2)
  else assert(f.c.owner.owner=='self'and f.transfers==7)end
  same_friend(f,held,remote);f:release();f:tick(.5)
 end
 assert(f.mutations==6 and f.sends==6 and f:count('integrated_operation_complete')==6)
 assert(f:count('integrated_ownership_return_confirmed')==3 and f:count('integrated_driver_authority_retained')==1 and f:count('integrated_local_authority_preserved')==2)
 f:press(bindings[remote]);f:tick();assert(not f.probe.pending and not f.dispatcher.queued and f.mutations==6 and f.transfers==7)
 same_friend(f,held,remote);cases=cases+1
end end end
-- State/identity/session/vacancy faults must refuse BEFORE the native request.
for _,target in ipairs({0,4})do for _,change in ipairs({
 function(f)f.friend.unit=99 end,function(f)f.friend.id=99 end,
 function(f)f.friend.seat.collection=-1 end,function(f)f.friend.seat.current=3 end,
 function(f)f.friend.seat.reserved=3 end,function(f)f.friend.seat.role=2 end,
 function(f)f.friend.seat.target=1 end,function(f)f.friend.seat.action=20 end,
 function(f)f.friend.seat.transitioning=1 end,function(f)f.friend.seat.queued_exit=1 end,
 function(f)f.c.native.occupied[1]=false end,function(f)f.c.owner.avatars[8].owner='self'end,
 function(f)f.c.owner.busy=true end,function(f)f.c.sample.player_count=3 end,
 function(f)f.c.owner.members.friend=nil end,function(f)f.c.owner.coordinator='new-host'end,
 function(f,t)f.c.native.occupied[t.target]=true end,function(f,t)f.c.native.occupied[t.target]=nil end,
 function(f)f.c.native.identity='changed'end,function(f)f.c.avatar.seat.reserved=3 end,
 function(f)f.c.native.owned=true end,function(f)f.c.driver=f.friend end
})do
 local f=fresh();local t=f.adapter:ticket(f.c,target);change(f,t)
 assert(not pcall(f.adapter.request,f.adapter,f.c,t)and not t.request_invoked and f.transfers==0 and f.mutations==0)
 cases=cases+1
end end
-- Preparation can race after a genuine grant; no mutation, original return once.
for _,target in ipairs({0,4})do for _,change in ipairs({
 function(f)f.friend.unit=99 end,function(f)f.friend.seat.current=3 end,
 function(f)f.friend.seat.queued_exit=1 end,function(f)f.c.native.occupied[target]=true end
})do
 local f=fresh();local prepare=f.tx.prepare
 f.tx.prepare=function(...)local perform=prepare(...);change(f);return perform end
 trigger(f,target,target==0 and 88 or 1026);f:tick();for _=1,65 do f:tick()end
 assert(f.probe.phase=='stopped'and f.c.owner.owner=='friend'and f.mutations==0 and f.sends==0 and f.transfers==2)
 assert(f:count('integrated_aborted_and_returned')==1);cases=cases+1
end end
-- Late/cancelled grants retain only cleanup privileges, with either target type.
for _,target in ipairs({0,4})do for _,kind in ipairs({'focus','cancel','late','third_peer','occupied'})do
 local f=fresh();f.defer_grant=true;trigger(f,target,target==0 and 88 or 1026)
 if kind=='focus'then f.focused=false elseif kind=='cancel'then f.probe:cancel('logging_unavailable')
 elseif kind=='late'then f:tick(6)elseif kind=='third_peer'then f.c.sample.player_count=3
 elseif kind=='occupied'then f.c.native.occupied[target]=true end
 grant(f);f:tick();for _=1,65 do f:tick()end
 assert(f.probe.phase=='stopped'and f.mutations==0 and f.transfers==2 and f.c.owner.owner=='friend')
 assert(f:count('integrated_operation_complete')==0);cases=cases+1
end end
-- Known passenger retraction is retryable but NEVER mutation-eligible.
local f=fresh();local t=f.adapter:ticket(f.c,4)
f.friend.seat.target=1;f.friend.seat.action=20;f.friend.seat.transitioning=1
local ready,reason,retry=f.adapter:eligible(f.c,2,false,t,4)
assert(not ready and reason=='friend_passenger_retracting'and retry)
assert(not pcall(f.adapter.request,f.adapter,f.c,t)and f.transfers==0 and f.mutations==0);cases=cases+1
-- A malformed outside state is still blocked; the new canonical exit is separate.
local f=fresh();f.friend.seat.collection=-1
assert(not f.adapter:eligible(f.c,2,false,nil,4)and not f.adapter:eligible(f.c,2,false,nil,0));cases=cases+1
print('PASS '..cases..' seated-original-owner cases: both hosts/all passenger-gunner pairs; held/tapped six-step actual input; borrow-return vs driver-retain; unchanged remote occupant; vacant and occupied targets; late/focus/peer/preparation cleanup; strict retry and malformed outside refusal')
