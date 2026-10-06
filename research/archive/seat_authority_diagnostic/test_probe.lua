local M=assert(loadfile('work/seat_authority_diagnostic/probe.lua'))()
local function copy(v)if type(v)~='table'then return v end;local t={};for k,x in pairs(v)do t[k]=copy(x)end;return t end
local v={id=721,unit=8391232,network_unit=4118,resource='fixture',name='m102',seat_count=5,free_mask=0x3ffffc,owned_local=false}
local function avatar(id,local_,seat,role)
 return {id=id,is_local=local_,vehicle_input=true,seat={collection=721,current=seat,reserved=seat,role=role,target=-1,action=-1,transitioning=0,queued_exit=0}}
end
local s0={state='mission',local_count=1,player_count=2,avatars={avatar(11,true,1,3),avatar(22,false,0,1)}}
local o0={vehicle=v,owner='friend',selected='friend',selfpeer='self',coordinator='friend',peer_count=2,
 members={self=true,friend=true},avatars={[11]={owner='self',selected='self'},[22]={owner='friend',selected='friend'}},
 serial=1,busy=false,context='room1'}
local function new()
 local s,o=copy(s0),copy(o0);local events,calls={},{}
 local obs={summary=function(_,x)return {owner=x.owner,selected=x.selected,busy=x.busy,serial=x.serial,owned_local=x.vehicle.owned_local}end,
 send=function(_,x,d,t)calls[#calls+1]={d,t,x.vehicle.network_unit}end}
 local p=M.new(obs,function(e)events[#events+1]=e end,function()end)
 local function tick(now,pressed)p:step(s,o,nil,pressed,now)end
 local function arm()tick(0);tick(3);assert(p.phase=='armed')end
 return p,s,o,events,calls,tick,arm,obs
end
local p,s,o,e,c,t,arm=new();arm();assert(#c==0);t(3.1,true);assert(#c==1 and p.used)
for i=1,8 do t(3.1+i/10,true)end;assert(#c==1)
o.owner='self';o.selected='self';o.vehicle.owned_local=true;o.serial=2;t(4)
assert(#c==2 and c[1][1]=='friend'and c[1][2]=='self'and c[2][1]=='self'and c[2][2]=='friend')
-- A partial return must not count as success.
o.owner='friend';t(4.1);t(5);assert(p.phase=='awaiting_return')
o.selected='friend';o.vehicle.owned_local=false;o.serial=3;t(5.1);t(5.7)
assert(p.phase=='complete');t(10,true);assert(#c==2)

-- Rejected/late requests do not generate retries; a late grant still returns.
p,s,o,e,c,t,arm=new();arm();t(3.1,true);t(8.2);assert(p.phase=='late_grant_watch'and #c==1)
t(100,true);assert(#c==1);o.owner='self';o.selected='self';o.vehicle.owned_local=true;t(101);assert(#c==2)
t(107);assert(p.phase=='return_not_confirmed'and #c==2);t(110,true);assert(#c==2)
o.owner='friend';o.selected='friend';o.vehicle.owned_local=false;t(120);t(121);assert(p.phase=='complete')

local mutations={
 function(s,o)s.player_count=1 end,function(s,o)o.peer_count=3 end,function(s,o)o.selfpeer='friend'end,
 function(s,o)o.busy=true end,function(s,o)o.owner='unknown'end,function(s,o)o.vehicle.owned_local=true end,
 function(s,o)s.avatars[1].seat.current=0 end,function(s,o)s.avatars[1].seat.transitioning=1 end,
 function(s,o)s.avatars[2].seat.collection=0 end,function(s,o)o.avatars[22].owner='self'end,
 function(s,o)o.vehicle.free_mask=0x3ffffd end,function(s,o)o.vehicle.name='bastion'end,
 function(s,o)s.avatars[1].vehicle_input=false end,function(s,o)o.members.friend=nil end,
}
for _,change in ipairs(mutations)do
 p,s,o,e,c,t,arm=new();change(s,o);t(0,true);t(4,true);assert(not p.used and #c==0)
end
p,s,o,e,c,t,arm=new();t(0,true);t(2.9,true);assert(#c==0);t(3,true);assert(#c==1)

-- Loss of observation never assumes success; changed room never receives stale sends.
p,s,o,e,c,t,arm=new();arm();t(3.1,true);p:step(nil,nil,'read_gap',false,4);assert(#c==1)
o.context='room2';t(5);assert(p.phase=='ended'and #c==1)
p,s,o,e,c,t,arm=new();arm();t(3.1,true);o.members.friend=nil;t(4);assert(p.phase=='ended'and #c==1)
p,s,o,e,c,t,arm=new();arm();t(3.1,true);s.state='not_in_mission';t(4);assert(p.phase=='ended'and #c==1)

-- User leaving a seat after requesting must not suppress the return of a late grant.
p,s,o,e,c,t,arm=new();arm();t(3.1,true);s.avatars[1].seat.collection=0
o.owner='self';o.selected='self';o.vehicle.owned_local=true;t(4);assert(#c==2)
-- A thrown native adapter consumes its attempt. Never retry a potentially sent request.
local obs
p,s,o,e,c,t,arm,obs=new();obs.send=function()error('synthetic preflight rejection')end
arm();t(3.1,true);assert(p.used and p.phase=='send_failed');t(4,true);assert(#c==0)
-- Changing conditions after arming disarms the UI as well as suppressing sends.
p,s,o,e,c,t,arm=new();arm();o.busy=true;t(3.1,true);assert(p.phase=='idle'and not p.used)
print('PASS authority state machine: exact eligibility, one-shot, two-phase ownership, late grants, return timeout, room/peer changes and failed sends')
