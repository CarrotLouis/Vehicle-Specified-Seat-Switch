local factory=assert(loadfile('work/seat_multi_vehicle_test/probe.lua'))()
local function fixture(route)
 local c={identity='session_vehicle',summary='state',seat=1,owner={owner='friend',selfpeer='self',vehicle={owned_local=false},busy=false}}
 local calls,events={},{};local last_ticket
 local a={capture=function()return c end,context=function(_,x,t)return x.identity==t.identity end}
 function a:eligible(x,source,owned,t)
  if self.block then return false,self.block end
  return x.seat==source and x.owner.owner==(owned and 'self'or'friend'),'wrong_state'
 end
 function a:ticket(x,target)last_ticket={source=x.seat,target=target or(5-x.seat),identity=x.identity,selfpeer='self',original=x.owner.owner,local_authority=x.owner.owner=='self'};return last_ticket end
 function a:request(x,t)t.request_invoked=true;calls[#calls+1]='request'end
 function a:execute(x,t)calls[#calls+1]='switch';t.mutation_started=true;if self.fail_switch then error('partial_failure')end;x.seat=t.target;t.sync_returned=true end
 function a:return_owned(x,t)
  calls[#calls+1]='return_check'
  if self.fail_preflight then error('return_preflight')end
  t.return_invoked=true;calls[#calls+1]='return_send'
  if self.fail_return then error('ambiguous_return_failure')end
 end
 local p=factory.new(a,function(e)events[#events+1]=e end,function()end,route)
 local function own(who)c.owner.owner=who;c.owner.vehicle.owned_local=who=='self'end
 local function begin()p:step(false,0,true);p:step(true,3.1,true);assert(p.pending and calls[1]=='request')end
 return p,a,c,calls,events,own,begin,function()return last_ticket end
end
local p,a,c,calls,events,own,begin,ticket=fixture();begin();own('self');p:step(false,3.3,true)
assert(table.concat(calls,',')=='request,switch'and p.pending)
p:step(false,3.4,true);assert(ticket().return_invoked)
own('friend');p:step(false,3.6,true);p:step(false,4.2,true);assert(not p.pending and p.phase=='waiting_second_trigger')
p:step(true,8,true);assert(p.count==1);p:step(true,14.3,true);assert(p.count==2 and p.pending)
own('self');p:step(false,14.4,true);p:step(false,14.6,true);own('friend');p:step(false,14.8,true);p:step(false,15.4,true)
assert(p.phase=='finished');local count=#calls;p:step(true,30,true);assert(#calls==count and c.seat==1)
for _,reason in ipairs({'occupied','friend_left_driver','avatar_changed','third_player_joined','active_lean','seat_changed'})do
 p,a,c,calls,events,own,begin,ticket=fixture();begin();a.block=reason;own('self');p:step(false,3.3,true);p:step(false,3.5,true)
 assert(table.concat(calls,',')=='request,return_check,return_send')
 own('friend');p:step(false,3.7,true);p:step(false,4.3,true);assert(p.phase=='stopped'and ticket().return_confirmed)
end
-- Late grant is still returned, never used to perform the original switch.
p,a,c,calls,events,own,begin,ticket=fixture();begin();p:step(false,9,true);own('self');p:step(false,10,true);p:step(false,10.2,true)
assert(not ticket().mutation_started and ticket().return_invoked)
-- Losing focus after sending does not prevent cleanup.
p,a,c,calls,events,own,begin,ticket=fixture();begin();own('self');p:step(false,3.3,false);p:step(false,3.5,false);assert(not ticket().mutation_started and ticket().return_invoked)
-- Failed local switch must still return; no second switch attempt.
p,a,c,calls,events,own,begin,ticket=fixture();begin();a.fail_switch=true;own('self');p:step(false,3.3,true);p:step(false,3.5,true)
assert(ticket().mutation_started and ticket().return_invoked);assert(table.concat(calls,',')=='request,switch,return_check,return_send')
-- A preflight read failure can be rechecked, but native return invocation cannot repeat.
p,a,c,calls,events,own,begin,ticket=fixture();begin();own('self');p:step(false,3.3,true);a.fail_preflight=true;p:step(false,3.5,true)
assert(not ticket().return_invoked);a.fail_preflight=false;a.fail_return=true;p:step(false,3.7,true);p:step(false,10,true);p:step(false,20,true)
local n=0;for _,x in ipairs(calls)do if x=='return_send'then n=n+1 end end;assert(n==1 and p.pending)
-- Log loss explicitly cancels mutation but keeps ownership recovery alive.
p,a,c,calls,events,own,begin,ticket=fixture();begin();p:cancel('log_unavailable');own('self');p:step(false,3.3,true);p:step(false,3.5,true)
assert(not ticket().mutation_started and ticket().return_invoked)
-- Unknown context must never receive a return meant for an earlier vehicle/session.
p,a,c,calls,events,own,begin,ticket=fixture();begin();c.identity='new';own('self');p:step(false,3.3,true);assert(p.phase=='stopped'and #calls==1)
-- No self-owned flag / busy clear means no mutation despite table owner being self.
p,a,c,calls,events,own,begin,ticket=fixture();begin();c.owner.owner='self';p:step(false,3.3,true);assert(#calls==1)
own('self');c.owner.busy=true;p:step(false,3.5,true);assert(#calls==1)
-- Missing reads cannot lose a late grant or reset the ticket.
p,a,c,calls,events,own,begin,ticket=fixture();begin();local capture=a.capture;a.capture=function()return nil,'read_gap'end;p:step(false,9,true)
a.capture=capture;own('self');p:step(false,10,true);p:step(false,10.2,true);assert(ticket().return_invoked and not ticket().mutation_started)
print('PASS integrated workflow: two full operations; grant/return flags; occupancy/identity/focus/lategrant/log/partial-failure cleanup; no resend')
local route={1,4,2,4,3,4,1}
p,a,c,calls,events,own,begin,ticket=fixture(route)
for i=1,6 do
 local now=(i-1)*25
 p:step(false,now,true);p:step(true,now+3.1,true)
 assert(p.pending and ticket().source==route[i]and ticket().target==route[i+1])
 own('self');p:step(false,now+3.3,true);p:step(false,now+3.4,true)
 assert(ticket().return_invoked and c.seat==route[i+1])
 own('friend');p:step(false,now+3.6,true);p:step(false,now+4.2,true)
 assert(not p.pending and ticket().return_confirmed and p.count==i)
end
local n=#calls;p:step(true,200,true);assert(p.phase=='finished'and #calls==n and c.seat==1)
assert(not pcall(fixture,{1,2,4}))
print('PASS six-operation rear-seat route, per-operation authority return, seventh trigger ignored, non-gunner pair rejected')
-- Local authority must not send an acquisition request or hand chassis to the friend.
p,a,c,calls,events,own,begin,ticket=fixture(route);own('self')
for i=1,6 do
 local now=(i-1)*25;p:step(false,now,true);p:step(true,now+3.1,true)
 assert(ticket().local_authority and p.pending and #calls==i-1)
 p:step(false,now+3.3,true);p:step(false,now+3.4,true);p:step(false,now+4,true)
 assert(not p.pending and p.count==i and c.seat==route[i+1]and c.owner.owner=='self')
 assert(not ticket().request_invoked and not ticket().return_invoked)
end
assert(p.phase=='finished'and #calls==6)
for _,call in ipairs(calls)do assert(call=='switch')end
-- Authority loss, focus/log loss and partial failure never cause an unsolicited return.
for _,failure in ipairs({'owner','focus','log','partial','identity','occupied'})do
 p,a,c,calls,events,own,begin,ticket=fixture();own('self');p:step(false,0,true);p:step(true,3.1,true)
 if failure=='owner'then own('friend')elseif failure=='log'then p:cancel('log_unavailable')elseif failure=='partial'then a.fail_switch=true elseif failure=='identity'then c.identity='new'elseif failure=='occupied'then a.block='occupied'end
 p:step(false,3.3,failure~='focus');p:step(false,4,true)
 assert(p.phase=='stopped'and not ticket().request_invoked and not ticket().return_invoked)
 assert(#calls==(failure=='partial'and 1 or 0))
end
-- Ownership may legitimately differ at the start of a later operation.
p,a,c,calls,events,own,begin,ticket=fixture();own('self');p:step(false,0,true);p:step(true,3.1,true)
p:step(false,3.3,true);p:step(false,3.4,true);p:step(false,4,true);own('friend')
p:step(false,20,true);p:step(true,23.1,true);assert(not ticket().local_authority and ticket().request_invoked)
own('self');p:step(false,23.3,true);p:step(false,23.4,true);own('friend');p:step(false,23.6,true);p:step(false,24.2,true)
assert(p.phase=='finished'and ticket().return_confirmed)
print('PASS already-local six-step flow: zero ownership sends; owner/focus/log/identity/occupied/partial failure stops; mixed local/borrowed operations')
local dr={0,4,0,2,0,3,0}
p,a,c,calls,events,own,begin,ticket=fixture(dr);c.seat=0;own('self')
for i=1,6 do
 local now=(i-1)*25;p:step(false,now,true);p:step(true,now+3.1,true)
 assert(ticket().source==dr[i]and ticket().target==dr[i+1]and ticket().local_authority)
 p:step(false,now+3.3,true);p:step(false,now+3.4,true);p:step(false,now+4,true)
 assert(not p.pending and c.seat==dr[i+1]and not ticket().request_invoked and not ticket().return_invoked)
end
assert(p.phase=='finished'and #calls==6 and c.seat==0)
print('PASS full six-step driver route, zero acquisition/return')
