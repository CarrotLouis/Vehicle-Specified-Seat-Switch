local make=assert(loadfile('work/seat_driver_observer_fix/watch.lua'))()
local now,reads,arms,disarms,events,owner,serial=0,0,0,0,{},'DRIVER',1
local fail,body_fail=false,false
local v={id=451,unit=4198352,network_unit=289,name='m102',resource='cc21c7ffd3ebefb9',transition_type=26,seat_count=5,owned_local=true}
local a={id=33,unit=44,is_local=true,owned_local=true,seat={collection=v.id,current=0,transitioning=0}}
local s={state='mission',mission_value=42,player_count=2,peer_count=2,local_count=1,avatars={a},vehicles={v}}
local api={now=function()return now end}
local physical={read_vehicle=function()
 reads=reads+1;if fail then error('synthetic_physical_gap')end
 return {collection=v.id,unit=v.unit,actor_handle=0xa0001234,physical_position={now*10,0,0},native_speed=10}
end}
local context={read=function()return {local_peer_hex='DRIVER',coordinator_hex='DRIVER',selfpeer='D',coordinator='D',read_count=23}end}
local handoff={read_vehicle=function()return {engine_owner_hex=owner,engine_serial=serial}end}
local body={read=function()if body_fail then error('optional_flag_gap')end;return {flags=65674}end}
local calls={arm_driver=function(_,vehicle,snapshot,avatar,p)
 assert(vehicle==v and snapshot==s and avatar==a and p.actor_handle==0xa0001234);arms=arms+1
end,disarm=function()disarms=disarms+1 end}
local function new()return make(api,physical,handoff,context,body,calls,function(e)events[#events+1]=e end)end
local w=new();w:update(nil);s.state='not_in_mission';w:update(s);s.state='mission'
assert(reads==0 and arms==0 and disarms==0,'no out-of-scope physics or helper calls')
w:update(s);assert(arms==1 and events[1].event=='driver_watch_started')
now=.05;owner='INSTALLER';serial=2;v.owned_local=false;w:update(s)
assert(events[#events].driver_owns_chassis==false and events[#events-1].event=='driver_authority_observed_change')
now=.10;owner='DRIVER';serial=3;v.owned_local=true;w:update(s);assert(events[#events].driver_owns_chassis)
now=1.5;w:update(s);assert(arms==2)
body_fail=true;now=1.55;w:update(s);assert(events[#events-1].event=='body_flags_gap');body_fail=false
now=121;local prior=reads;w:update(s);assert(reads==prior and disarms==1 and events[#events].event=='driver_watch_expired')
now=122;w:update(s);assert(reads==prior and disarms==1,'expired window stays idle')
a.seat.current=1;w:update(s);assert(disarms==2)
a.seat.current=0;w:update(s);assert(arms==3,'reentry allows bounded fresh segment')
w:gap('snapshot_gap');assert(disarms==3)
for _,fault in ipairs({function()s.player_count=3 end,function()s.peer_count=3 end,function()s.local_count=2 end,
 function()a.is_local=false end,function()a.owned_local=false end,function()a.seat.transitioning=1 end,
 function()v.resource='wrong'end,function()v.transition_type=1 end,function()v.seat_count=4 end,
 function()a.seat.collection=999 end})do
 s.player_count=2;s.peer_count=2;s.local_count=1;a.is_local=true;a.owned_local=true;a.seat.transitioning=0;a.seat.collection=v.id
 v.resource='cc21c7ffd3ebefb9';v.transition_type=26;v.seat_count=5
 local test=new();fault();local count=reads;test:update(s);assert(count==reads,'invalid scope must not read physics')
end
s.player_count=2;s.peer_count=2;s.local_count=1;a.is_local=true;a.owned_local=true;a.seat.transitioning=0;a.seat.collection=v.id
v.resource='e9cd1d0d118886af';v.transition_type=26;v.seat_count=5
w=new();w:update(s);assert(arms==4,'both captured M102 resource variants supported')
fail=true;now=123;w:update(s);assert(events[#events].event=='driver_watch_gap');local count=reads;fail=false;w:update(s);assert(reads==count)
assert(disarms==4,'critical failure must disarm promptly')
print('PASS passive watcher: 10 scope barriers, both M102 variants, loaned driver still captured, owner transitions, renewal/expiry/reentry, optional/critical failures, no idle physical reads')
