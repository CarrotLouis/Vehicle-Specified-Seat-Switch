local factory=assert(loadfile('work/seat_sync_diagnostic/probe.lua'))()
local function fixture()
 local events,calls={},{};local c={identity='one',seat=0,summary='one'}
 local a={capture=function()return c end,eligible=function()return true end}
 function a:execute(value,target)calls[#calls+1]=target;c.seat=target end
 local p=factory.new(a,function(e)events[#events+1]=e end,function()end)
 return p,a,c,calls,events
end
local p,a,c,calls=fixture()
p:step(true,0,true);assert(#calls==0)
p:step(true,3.1,true);assert(#calls==1 and calls[1]==1)
p:step(false,3.2,true);p:step(false,3.8,true)
p:step(true,7,true);assert(#calls==1)
p:step(true,13.2,true);assert(#calls==2 and calls[2]==0)
p:step(false,13.3,true);p:step(false,14,true)
assert(p.phase=='finished_local_only')
for t=15,30 do p:step(true,t,true)end;assert(#calls==2)
for _,failure in ipairs({'owner_lost','occupied','busy','friend_entered','wrong_peer_count'})do
 p,a,c,calls=fixture();p:step(false,0,true);p:step(true,4,true)
 a.eligible=function()return false,failure end;p:step(true,5,true)
 assert(p.phase=='stopped'and #calls==1)
end
p,a,c,calls=fixture();p:step(false,0,true);a.execute=function()error('partial_native_failure')end
p:step(true,4,true);assert(p.phase=='stopped'and p.count==1);p:step(true,20,true);assert(p.count==1)
p,a,c,calls=fixture();p:step(false,0,true);p:step(true,4,true);c.identity='new_session';p:step(true,20,true)
assert(p.phase=='stopped'and #calls==1)
p,a,c,calls=fixture();p:step(false,0,true);p:step(true,4,true);a.capture=function()return nil,'read_gap'end
p:step(false,13,true);assert(p.phase=='stopped')
p,a,c,calls=fixture();p:step(false,0,true);p:step(true,4,false);assert(#calls==0)
p:step(true,5,true);assert(#calls==0);p:step(true,9,true);assert(#calls==1)
print('PASS probe two-operation bound, cooldown, focus, ownership/occupancy/session failures, partial failure no retry')
