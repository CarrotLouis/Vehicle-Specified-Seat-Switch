local probe=assert(loadfile('work/seat_aboard_passenger_test/probe.lua'))()
local A=assert(loadfile('work/seat_aboard_passenger_test/adapter.lua'))()
-- Own target may be leaning after the completed transaction; mutation still refuses it.
local function seat(n)return {collection=9,current=n,reserved=n,role=n==4 and 2 or 3,target=-1,action=-1,transitioning=0,queued_exit=0}end
local av={id=7,unit=77,is_local=true,owned_local=true,vehicle_input=true,seat=seat(1)}
local c={identity='v',seat=1,avatar=av,driver=nil,destination='friend',sample={player_count=2,local_count=1,avatars={av,{id=8,is_local=false,seat={collection=-1}}}},
 native={identity='binding',vehicle='m102',transition=26,profile={roles={1,3,3,3,2}},player_count=2,peer_count=2,owned=true,avatar=7,node=1,active=true,occupied={[4]=false}},
 owner={owner='self',selfpeer='self',coordinator='self',members={self=true,friend=true},peer_count=2,vehicle={id=9,owned_local=true},avatars={[7]={owner='self'}}}}
local t={identity='v',avatar_binding='binding',local_authority=true,selfpeer='self',original='self',destination='friend',coordinator='self',source=4,target=1}
assert(not A.eligible(c,1,true,t));assert(A.eligible(c,1,true,t,nil,true))
av.seat=seat(4);c.native.node=4;t.source=1;t.target=4;c.native.occupied[1]=false
assert(not A.eligible(c,4,true,t,nil,true),'gunner active flag must not be treated as a passenger lean')
av.seat=seat(1);c.native.node=1;t.source=4;t.target=1
-- Confirmation checks still reject wrong role, queued exit, actor identity, owner, target.
for _,change in ipairs({function()av.seat.role=2 end,function()av.seat.queued_exit=1 end,function()c.native.identity='respawn'end,function()c.owner.owner='friend'end,function()c.native.node=3 end})do
 av.seat=seat(1);c.native.identity='binding';c.owner.owner='self';c.native.node=1;change();assert(not A.eligible(c,1,true,t,nil,true))
end
for _,borrowed in ipairs({false,true})do
 local now,capture_reason=0,nil
 local c={identity='v',seat=4,native={},owner={owner=borrowed and'friend'or'self',selfpeer='self',vehicle={owned_local=not borrowed}},summary='s'}
 local events,mutations,transfers={},0,0
 local a={capture=function()return c end,context=function()return true end,eligible=function(_,c,source)return c.seat==source end}
 function a:ticket(c,target)return {identity='v',source=c.seat,target=target,selfpeer='self',original=c.owner.owner,local_authority=c.owner.owner=='self'}end
 function a:request(c,t)transfers=transfers+1;t.request_invoked=true;c.owner.owner='self';c.owner.vehicle.owned_local=true end
 function a:execute(c,t)mutations=mutations+1;t.mutation_started=true;t.sync_returned=true;c.seat=t.target end
 function a:return_owned(c,t)transfers=transfers+1;t.return_invoked=true;c.owner.owner='friend';c.owner.vehicle.owned_local=false end
 function a:confirmed(c,t,owned)if capture_reason then return false,capture_reason end;return c.seat==t.target end
 local p=probe.new(a,function(e)events[#events+1]=e end,function()end,nil,true)
 p:step(nil,0,true);p:step(1,3.1,true);p:step(nil,3.2,true)
 capture_reason='transition_in_progress';p:step(nil,3.3,true);p:step(nil,4,true);p:step(nil,4.6,true);assert(p.pending and p.phase~='stopped')
 capture_reason='transition_pending';p:step(nil,4.7,true);p:step(nil,5.3,true);assert(p.pending and mutations==1)
 capture_reason=nil;p:step(nil,5.4,true);p:step(nil,6,true);assert(not p.pending and p.phase~='stopped')
 assert(transfers==(borrowed and 2 or 0))
 local completes,returns=0,0;for _,e in ipairs(events)do if e.event=='integrated_operation_complete'then completes=completes+1 end;if e.event=='integrated_ownership_return_confirmed'then returns=returns+1 end end
 assert(completes==1 and returns==(borrowed and 1 or 0),'one completion/ownership-return event only')
 -- Unresolved transition expires; it cannot rerun the local operation or return.
 capture_reason=nil;c.seat=4;p=probe.new(a,function()end,function()end,nil,true)
 p:step(nil,10,true);p:step(1,13.1,true);p:step(nil,13.2,true);capture_reason='transition_in_progress'
 p:step(nil,13.3,true);p:step(nil,14,true);p:step(nil,14.7,true);p:step(nil,21,true)
 assert(p.phase=='stopped'and mutations==2 and transfers==(borrowed and 4 or 0))
end
print('PASS target pose confirmation waits only5s, permits settled lean, preserves mutation guards, single completion/return, no additional mutation/authority send')
