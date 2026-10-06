local scope=assert(loadfile('work/seat_multiplayer_reservation_test/scope.lua'))()
local factory=assert(loadfile('work/seat_multiplayer_reservation_test/motion_watch.lua'))()
local now,count,handoff_count=10,0,0;local events={};local fail=false
local watch=factory({now=function()return now end},{peers={driver='P1'}},
 {read_vehicle=function(_,v)assert(v.id==9);count=count+1;if fail then error('missing_physics')end;return {speed=12}end},
 {read_vehicle=function()handoff_count=handoff_count+1;return {motion_speed=12}end},function(e)events[#events+1]=e end,scope)
local c={native={vehicle='m102',transition=26,profile={row=8,roles={1,3,3,3,2}}},sample={player_count=2},seat=1,owner={owner='driver',selfpeer='user',coordinator='driver',serial=3,vehicle={id=9,network_unit=4123}}}
local probe={count=0,observed=c}
for i=1,60 do now=now+.016;watch:update(nil,probe)end;assert(count==0)
probe.count=1;watch:boundary('before_request',c,{source=1,target=2});watch:update(nil,probe)
local start=count
for i=1,200 do now=now+.016;watch:update(nil,probe)end
assert(count-start<=30 and count-start>=25 and handoff_count==count)
local last=count;now=now+10;watch:update(nil,probe);assert(count==last)
fail=true;watch:boundary('read_failure',c);assert(events[#events].event=='reservation_physics_gap'and events[#events].speed==nil)
fail=false;for n=3,4 do c.sample.player_count=n;last=count;watch:boundary('room_expanded',c);assert(count==last+1)end
c.sample.player_count=5;last=count;watch:boundary('outside_scope',c);assert(count==last)
print('PASS no idle physics polling; single-car ten-Hz bounded window; missing reads remain gaps, never zero speed')
