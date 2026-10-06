-- Use the real poller, input gate, dispatcher, adapter and operation lifecycle.
-- Native seat changes/network delivery alone are simulated; no game is launched.
local fixture=assert(loadfile('work/seat_motion_loan_test/input_race_fixture.lua'))()
local dir=assert(os.getenv('VSS_INPUT_RACE_DIR'));local NEW='seat_motion_loan_test';local cases=0
local function fresh(source,host)return fixture(NEW,source or 2,host or 'friend',true,dir,4)end
local function grant(f)
 f.c.owner.owner='self';f.c.owner.vehicle.owned_local=true;f.c.native.owned=true
end
local function trigger(f,target,binding,tap)
 f:press(binding);f:tick();assert(f.dispatcher.queued and not f.probe.pending)
 if tap then f:release()end
 f:enqueue(binding,target);f:tick();assert(f.probe.pending and not f.dispatcher.queued)
end
local function request(f)
 local t=f.adapter:ticket(f.c,0)
 assert(t.driver_acquire and not t.local_authority and t.remote_node==4 and t.remote_unit==88)
 assert(f.adapter:eligible(f.c,f.c.seat,false,t,0))
 f.adapter:request(f.c,t);assert(t.request_invoked and f.transfers==1)
 return t
end
-- Held and tapped input on either rear seat, with installer or friend host.
for _,host in ipairs({'self','friend'})do for _,source in ipairs({2,3})do for _,tap in ipairs({false,true})do
 local f=fresh(source,host);local held=f.friend.seat
 trigger(f,0,88,tap);assert(f.transfers==1 and f.mutations==0)
 f:tick();assert(f.c.seat==0 and f.c.driver==f.c.avatar and f.probe.phase=='awaiting_driver_confirmation')
 f:finish();assert(f.c.owner.owner=='self'and f.transfers==1 and f.mutations==1 and f.sends==1)
 assert(f:count('integrated_driver_authority_retained')==1 and f:count('integrated_ownership_return_confirmed')==0)
 local completed=false
 for _,e in ipairs(f.events)do if e.event=='integrated_operation_complete'and e.authority_path=='acquired_retained'then completed=true end end
 assert(completed and f.friend.seat==held and held.current==4 and held.reserved==4 and held.role==2)
 -- Subsequent local driver/rear movements use the accepted no-transfer path.
 f:release();f:tick(.5)
 for _,step in ipairs({{source,source==2 and 1114 or 1112},{0,88}})do
  trigger(f,step[1],step[2],tap);f:tick();f:finish();f:release();f:tick(.5)
 end
 assert(f.mutations==3 and f.sends==3 and f.transfers==1 and f:count('integrated_operation_complete')==3)
 assert(f.friend.seat==held and f.c.native.occupied[4]and f.c.owner.avatars[8].owner=='friend')
 f:press(1026);f:tick();assert(not f.probe.pending and not f.dispatcher.queued and f.mutations==3)
 cases=cases+1
end end end
-- The prior release must reject this exact formerly-disabled boundary.
local f=fresh();local old=assert(loadfile('work/seat_remote_gunner_test/adapter.lua'))()
assert(not old.eligible(f.c,2,false,nil,0)and f.adapter:eligible(f.c,2,false,nil,0));cases=cases+1
-- Guard every driver acquisition dependency before making an ownership request.
local faults={
 function(f)f.c.native.occupied[0]=true end,function(f)f.c.native.occupied[0]=nil end,
 function(f)f.friend.id=99 end,function(f)f.friend.unit=99 end,
 function(f)f.friend.seat.collection=-1 end,function(f)f.friend.seat.current=1 end,
 function(f)f.friend.seat.reserved=1 end,function(f)f.friend.seat.role=3 end,
 function(f)f.friend.seat.target=4 end,function(f)f.friend.seat.action=20 end,
 function(f)f.friend.seat.transitioning=1 end,function(f)f.friend.seat.queued_exit=1 end,
 function(f)f.c.native.occupied[4]=false end,function(f)f.c.owner.avatars[8].owner='self'end,
 function(f)f.c.owner.busy=true end,function(f)f.c.sample.player_count=3 end,
 function(f)f.c.owner.coordinator='unknown'end,function(f)f.c.owner.members.friend=nil end,
 function(f)f.c.native.identity='changed'end,function(f)f.c.avatar.seat.reserved=1 end,
 function(f)f.c.driver=f.friend end,function(f)f.c.native.owned=true end,
 function(f,t)t.source=1 end,function(f,t)t.target=3 end
}
for _,change in ipairs(faults)do
 local f=fresh();local t=f.adapter:ticket(f.c,0);change(f,t)
 assert(not pcall(f.adapter.request,f.adapter,f.c,t)and not t.request_invoked and f.transfers==0 and f.mutations==0)
 cases=cases+1
end
for _,source in ipairs({1,4})do
 local f=fresh(source);assert(not f.adapter:eligible(f.c,source,false,nil,0));cases=cases+1
end
-- Re-read the vacant seat and focus at the final request call boundary.
for _,change in ipairs({
 function(f)f.focused=false end,function(f)f.snapshot_valid=false end
})do
 local f=fresh();local t=f.adapter:ticket(f.c,0);local send=f.owner_reader.send
 f.owner_reader.send=function(...)change(f);return send(...)end
 assert(not pcall(f.adapter.request,f.adapter,f.c,t)and not t.request_invoked and f.transfers==0);cases=cases+1
end
-- Preparation races after the grant must not mutate any seat; return once.
for _,change in ipairs({
 function(f)f.friend.unit=99 end,function(f)f.friend.seat.queued_exit=1 end,
 function(f)f.c.native.occupied[0]=true end,function(f)f.c.native.occupied[0]=nil end
})do
 local f=fresh();local prepare=f.tx.prepare
 f.tx.prepare=function(...)local perform=prepare(...);change(f);return perform end
 trigger(f,0,88);f:tick();for _=1,65 do f:tick()end
 assert(f.probe.phase=='stopped'and f.mutations==0 and f.sends==0 and f.transfers==2 and f.c.owner.owner=='friend')
 assert(f:count('integrated_aborted_and_returned')==1);cases=cases+1
end
-- Cancellation/late grant never converts a failed input into a later switch.
for _,kind in ipairs({'focus','logging','occupied','late_grant','cancel_before_grant'})do
 local f=fresh();f.defer_grant=true;trigger(f,0,88);assert(f.transfers==1)
 if kind=='focus'then f.focused=false
 elseif kind=='logging'then f.probe:cancel('experiment_logging_unavailable')
 elseif kind=='occupied'then f.c.native.occupied[0]=true
 elseif kind=='late_grant'then f:tick(6)
 elseif kind=='cancel_before_grant'then f.probe:cancel('user_cancelled');f:tick()end
 grant(f);f:tick();for _=1,65 do f:tick()end
 assert(f.probe.phase=='stopped'and f.mutations==0 and f.sends==0 and f.transfers==2 and f.c.owner.owner=='friend')
 assert(f:count('integrated_aborted_and_returned')==1 and f:count('integrated_operation_complete')==0);cases=cases+1
end
-- A busy grant remains pending without switching or making another request.
local f=fresh();f.defer_grant=true;trigger(f,0,88);grant(f);f.c.owner.busy=true
 for _=1,10 do f:tick()end
 assert(f.probe.pending and f.mutations==0 and f.transfers==1)
 f.c.owner.busy=false;f:tick();f:finish();assert(f.mutations==1 and f.transfers==1);cases=cases+1
-- Partial driver mutation must not run again, or hand away the occupied driver.
local f=fresh();local prepare=f.tx.prepare
f.tx.prepare=function(...)local perform=prepare(...);return function()perform();error('post-mutation injected failure')end end
trigger(f,0,88);f:tick();for _=1,65 do f:tick()end
assert(f.probe.pending and f.c.seat==0 and f.c.driver==f.c.avatar and f.mutations==1 and f.sends==0 and f.transfers==1)
assert(f:count('integrated_operation_complete')==0 and f:count('integrated_cancelled')==1)
-- Cleanup is allowed after a user exits normally; the mod never exits for them.
f.c.driver=nil;f.c.native=nil;f.c.avatar.seat.collection=-1
for _=1,65 do f:tick()end
assert(f.probe.phase=='stopped'and f.transfers==2 and f.mutations==1 and f.c.owner.owner=='friend');cases=cases+1
print('PASS '..cases..' vacant-driver acquisition cases: both rear seats/hosts/held-tapped input; retain genuine grant; no repeated mutation; existing local routes; occupied gunner; preparation/focus/late-grant cleanup; partial-driver failure cannot hand away control')
