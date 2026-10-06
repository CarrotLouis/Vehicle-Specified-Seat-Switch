local factory=assert(loadfile('work/seat_weapon_clear_diagnostic/probe.lua'))()
local function fixture()
 local c={identity='session_vehicle',summary='state',seat=1,owner={owner='friend',selfpeer='self',vehicle={owned_local=false},busy=false}}
 local calls,events={},{};local last_ticket
 local a={capture=function()return c end,context=function(_,x,t)return x.identity==t.identity end}
 function a:eligible(x,source,owned,t)
  if self.block then return false,self.block end
  return x.seat==source and x.owner.owner==(owned and 'self'or'friend'),'wrong_state'
 end
 function a:ticket(x)last_ticket={source=x.seat,target=5-x.seat,identity=x.identity,selfpeer='self',original='friend'};return last_ticket end
 function a:request(x,t)t.request_invoked=true;calls[#calls+1]='request'end
 function a:execute(x,t)calls[#calls+1]='switch';t.mutation_started=true;if self.fail_switch then error('partial_failure')end;x.seat=t.target;t.sync_returned=true end
 function a:return_owned(x,t)
  calls[#calls+1]='return_check'
  if self.fail_preflight then error('return_preflight')end
  t.return_invoked=true;calls[#calls+1]='return_send'
  if self.fail_return then error('ambiguous_return_failure')end
 end
 local p=factory.new(a,function(e)events[#events+1]=e end,function()end)
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
