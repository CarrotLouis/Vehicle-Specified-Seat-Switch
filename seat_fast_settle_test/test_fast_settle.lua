local probe=assert(loadfile('work/seat_fast_settle_test/probe.lua'))()
local function fixture(owned)
 local c={identity='v',seat=1,summary='state',native={},owner={owner=owned and'self'or'friend',selfpeer='self',vehicle={owned_local=owned}}}
 local calls,events={},{}
 local a={capture=function()return c end,context=function()return true end,eligible=function(_,c,source)return c.seat==source,'wrong_seat'end}
 function a:ticket(c,target)return {source=c.seat,target=target,selfpeer='self',original=c.owner.owner,local_authority=c.owner.owner=='self'}end
 function a:request(_,t)calls[#calls+1]='request';t.request_invoked=true end
 function a:execute(c,t)calls[#calls+1]='switch';t.sync_returned=true;t.mutation_started=true;c.seat=t.target end
 function a:return_owned(_,t)calls[#calls+1]='return';t.return_invoked=true end
 local p=probe.new(a,function(e)events[#events+1]=e end,function()end,nil,true)
 return p,c,calls,events
end
for _,owned in ipairs({false,true})do
 local p,c,calls=fixture(owned)
 p:step(nil,0,true);assert(p.ready_at==.2)
 p:step(4,.15,true);assert(not p.pending and #calls==0)
 p:step(4,.21,true);assert(p.pending)
 if owned then assert(#calls==0)else assert(calls[1]=='request');c.owner.owner='self';c.owner.vehicle.owned_local=true end
 p:step(nil,.25,true);assert(calls[owned and 1 or 2]=='switch')
 p:step(nil,.3,true)
 if not owned then c.owner.owner='friend';c.owner.vehicle.owned_local=false;p:step(nil,.4,true)end
 p:step(nil,1,true);assert(not p.pending)
 -- Existing cooldown remains10s despite the shorter settling interval.
 p:step(nil,1.1,true);p:step(1,1.4,true);assert(not p.pending)
end
for _,gap in ipairs({'active','missing','busy','identity','owner','seat','focus'})do
 local p,c,calls=fixture(false);p:step(nil,0,true)
 if gap=='active'then c.native.active=true elseif gap=='missing'then c.native=nil
 elseif gap=='busy'then c.owner.busy=true elseif gap=='identity'then c.identity='v2'
 elseif gap=='owner'then c.owner.owner='other'elseif gap=='seat'then c.seat=2 end
 p:step(nil,.15,gap~='focus');c.native={};c.owner.busy=false
 p:step(nil,.16,true);p:step(4,.25,true);assert(not p.pending and #calls==0,gap..' must reset fresh stability')
 p:step(4,.37,true);assert(p.pending,gap..' stable observations resume only after .2s')
end
print('PASS dynamic .2s timer: no request before fresh stability, active/missing/busy/identity/owner/seat/focus reset, both authority contexts and10s cooldown preserved')
