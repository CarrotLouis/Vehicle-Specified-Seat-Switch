local M=assert(loadfile('work/seat_physics_motion_test/adapter.lua'))()
local function fixture(source,target,host)
 local function seat(n)return {collection=9,current=n,reserved=n,role=n==0 and 1 or n==4 and 2 or 3,target=-1,action=-1,transitioning=0,queued_exit=0}end
 local av={id=7,unit=77,is_local=true,owned_local=true,vehicle_input=true,seat=seat(source)}
 local friend={id=8,unit=88,is_local=false,seat={collection=-1}}
 local c={identity='v',seat=source,avatar=av,driver=source==0 and av or nil,destination='friend',sample={player_count=2,local_count=1,avatars={av,friend}},
 native={identity='av',vehicle='m102',transition=26,profile={roles={1,3,3,3,2}},player_count=2,peer_count=2,owned=true,avatar=7,avatar_unit=77,node=source,occupied={[0]=false,[1]=false,[2]=false,[3]=false,[4]=false}},
 owner={owner='self',selfpeer='self',coordinator=host or'self',members={self=true,friend=true},peer_count=2,vehicle={id=9,owned_local=true},avatars={[7]={owner='self'}}}}
 c.native.occupied[source]=true
 local calls={};local api={input_allowed=function()return true end,down=function()return false end}
 local tx={prepare=function(_,s,t)calls[#calls+1]='prepare';assert(t==target);return function()
 calls[#calls+1]='switch';c.native.occupied[source]=false;c.native.occupied[target]=true;c.seat=target;c.native.node=target;av.seat=seat(target);c.driver=target==0 and av or nil end end}
 local sender={prepare=function(_,o,dest,s,t)assert(o.owner=='self'and dest=='friend'and t==target);return function()calls[#calls+1]='sync'end end}
 local a=M.new(api,0,{},nil,{summary=function()return {}end,send=function()error('no transfers')end},{current=function()return true end},tx,sender,{active=true,health=function()end},function()end,function()return ''end)
 a.capture=function()return c end
 return c,a,a:ticket(c,target),calls,api,tx,sender
end
for _,host in ipairs({'self','friend'})do for _,pair in ipairs({{0,4},{4,0},{0,2},{2,0},{0,3},{3,0}})do
 local c,a,t,calls=fixture(pair[1],pair[2],host)
 assert(M.eligible(c,pair[1],true,t)and not M.eligible(c,pair[1],false,t))
 assert(t.local_authority and t.original=='self'and t.destination=='friend')
 assert(not pcall(a.request,a,c,t)and not pcall(a.return_owned,a,c,t)and #calls==0)
 a:execute(c,t);assert(t.sync_returned and table.concat(calls,',')=='prepare,switch,sync')
 assert(M.eligible(c,pair[2],true,t))
end end
for _,change in ipairs({
 function(c)c.native.occupied[4]=true end,function(c)c.native.occupied[4]=nil end,function(c)c.native.owned=false end,
 function(c)c.owner.owner='friend'end,function(c)c.owner.busy=true end,function(c)c.sample.player_count=3 end,
 function(c)c.avatar.owned_local=false end,function(c)c.owner.avatars[7].owner='friend'end,function(c)c.driver=nil end,
 function(c)c.avatar.seat.queued_exit=1 end,function(c)c.sample.avatars[2].seat.collection=9 end,function(c)c.sample.avatars[2]=nil end,
 function(c)c.identity='new'end,function(c)c.native.identity='respawn'end,function(c)c.owner.coordinator='friend'end,
 function(c)c.native.vehicle='m104'end,function(c)c.native.active=true end
})do local c,a,t,calls=fixture(0,4);change(c);assert(not M.eligible(c,0,true,t));assert(not pcall(a.execute,a,c,t)and not t.mutation_started and #calls==0)end
local c,a,t,calls,api,tx,sender=fixture(4,0);c.driver=c.sample.avatars[2];assert(not M.eligible(c,4,true,t))
c,a,t,calls,api,tx,sender=fixture(0,4);local old=tx.prepare;tx.prepare=function(...)local f=old(...);c.native.occupied[4]=true;return f end
assert(not pcall(a.execute,a,c,t)and not t.mutation_started and table.concat(calls,',')=='prepare')
c,a,t,calls,api,tx,sender=fixture(0,4);sender.prepare=function()error('sync_preflight')end
assert(not pcall(a.execute,a,c,t)and not t.mutation_started)
c,a,t,calls,api=fixture(0,4);api.down=function(k)return k==65 end;assert(not pcall(a.execute,a,c,t)and #calls==0)
print('PASS host/guest x six driver pairs; outside friend; ownership/occupancy/identity/migration/race/input guards; zero transfers')
