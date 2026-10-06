-- Real probe and membership policies. Engine, ACK and physics are declared
-- effect doubles; passing this file establishes no real 3/4-player result.
local scope=assert(loadfile('work/seat_multiplayer_reservation_test/scope.lua'))()
local membership=assert(loadfile('work/seat_multiplayer_reservation_test/membership.lua'))()
local M=assert(loadfile('work/seat_multiplayer_reservation_test/probe.lua'))()(scope,membership)
local profiles=assert(loadfile('work/seat_switch/src/profile.lua'))().tables
local bit=require('bit')
local keys={'selfpeer','remote!!','third!!!','fourth!!'}
local function seat(car,node,role)
 return {collection=car,current=node,reserved=node,role=role,target=-1,action=-1,transitioning=0,queued_exit=0}
end
local function fixture(n,name,source,owner_index,host_index,empty_driver)
 local profile=profiles[name];local roles=profile.roles
 local avatars,members,owners={},{},{}
 for i=1,n do
  local a={id=6+i,unit=700+i,network_unit=4100+i,is_local=i==1,owned_local=i==1,
   vehicle_input=false,seat=seat(0,0,0)}
  avatars[i]=a;members[keys[i]]=true;owners[a.id]={owner=keys[i]}
 end
 local own=owner_index==1;local av=avatars[1];av.seat=seat(9,source,roles[source+1]);av.vehicle_input=true
 local driver
 if source==0 then driver=av
 elseif not own and not empty_driver then driver=avatars[owner_index];driver.seat=seat(9,0,1);driver.vehicle_input=true end
 local c={identity='room/car',seat=source,destination=own and keys[2]or keys[owner_index],avatar=av,driver=driver,
  sample={player_count=n,local_count=1,avatars=avatars},
  owner={owner=keys[owner_index],selfpeer=keys[1],coordinator=keys[host_index],peer_count=n,members=members,avatars=owners,
   serial=3,vehicle={id=9,unit=901,network_unit=4123,owned_local=own}},
  native={identity='own/car',vehicle=name,transition=profile.transition,profile=profile,avatar=av.id,avatar_unit=av.unit,
   node=source,owned=own,active=false,player_count=n,peer_count=n,occupied={},mask=0}}
 for node=0,#roles-1 do
  local occupied=node==source or driver and driver~=av and node==0 or false
  c.native.occupied[node]=occupied;if not occupied then c.native.mask=bit.bor(c.native.mask,2^node)end
 end
 local gate;local events={};local requests,writes,releases,notifications=0,0,0,0
 local trace={active=true,health=function()end}
 function trace:gate_arm(peer,car,avatar,from,to)
  assert(not gate and peer==keys[owner_index]and car==4123 and avatar==4101)
  gate={cookie=1,peer_key=peer,car=car,avatar=avatar,source=from,target=to,status=1,chosen=0xffffffff,guard_lost=0};return 1
 end
 function trace:gate_peek(cookie)assert(gate and cookie==1);return gate end
 function trace:gate_finish(cookie)assert(gate and cookie==1 and gate.status==2);gate=nil end
 local function move(target,local_owner,from)
  writes=writes+1;c.seat=target;c.native.node=target;av.seat=seat(9,target,roles[target+1])
  if target==0 then c.driver=av elseif c.driver==av then c.driver=nil end
  if local_owner then
   c.native.occupied[from]=false;c.native.occupied[target]=true
   c.native.mask=bit.band(bit.bor(c.native.mask,2^from),bit.bnot(2^target));c.owner.serial=c.owner.serial+1
  end
 end
 local function release(slot)
  releases=releases+1;c.native.occupied[slot]=false;c.native.mask=bit.bor(c.native.mask,2^slot)
 end
 local adapter={capture=function()return c end,
  owned_transaction={prepare=function(_,s,target)assert(s.owned);local from=s.node;return function()move(target,true,from)end end},
  release_acquired={prepare=function(_,s,slot,grant)assert(s.owned and grant:check());return function()assert(grant:check());release(slot)end end},
  mounted={prepare=function(_,_,target)if roles[target+1]==2 then return {target=target}end end,ready=function()return true end}}
 local tx={preflight=function()return true end,prepare=function(_,s,target,grant)
  assert(grant:check());return function()assert(grant:check());move(target,false)end
 end}
 local entrance={prepare_request=function(_,_,target)return function()assert(gate.status==1);requests=requests+1 end,2 end,
  prepare_release=function(_,_,slot)return function()release(slot)end end}
 local sender={preflight_all=function(_,o,destinations)assert(#destinations==n-1);return true end,
  prepare_all=function(_,o,destinations,s,target,grant)
   assert(#destinations==c.sample.player_count-1)
   for _,peer in ipairs(destinations)do assert(peer~=o.selfpeer and o.members[peer])end
   return function()if grant then assert(grant:check())end;notifications=notifications+#destinations end
  end}
 local api={input_allowed=function()return true end,control_down=function()return false end}
 local probe=M.new(adapter,api,{current=function()return true end},trace,entrance,tx,sender,function(e)events[#events+1]=e end,function()end)
 return {c=c,probe=probe,events=events,step=function(t,now)return probe:step(t,now or 10,true)end,
  reply=function()
   gate.status=2;gate.chosen=gate.target;gate.tick=123;c.native.occupied[gate.target]=true
   c.native.mask=bit.band(c.native.mask,bit.bnot(2^gate.target))
  end,
  acquire=function()c.owner.owner=keys[1];c.owner.serial=4;c.owner.vehicle.owned_local=true;c.native.owned=true end,
  counts=function()return requests,writes,releases,notifications end,gate=function()return gate end}
end
local operations,negatives=0,0
for n=2,4 do for host=1,n do for owner=1,n do
 for _,name in ipairs({'m102','m103','m104','bastion','maelstrom'})do
  local roles=profiles[name].roles
  if owner==1 then
   for source=0,#roles-1 do for target=0,#roles-1 do if source~=target then
    local f=fixture(n,name,source,owner,host);assert(f.step(target));local r,w,rel,send=f.counts()
    assert(r==0 and w==1 and rel==0 and send==n-1 and not f.probe.pending and f.c.owner.owner==keys[1]);operations=operations+1
   end end end
  else
   for source=1,#roles-1 do for target=1,#roles-1 do if source~=target then
    local f=fixture(n,name,source,owner,host);assert(f.step(target));f.reply();f.step(nil,10.1);f.step(nil,10.2)
    local r,w,rel,send=f.counts();assert(r==1 and w==1 and rel==1 and send==n-1 and not f.probe.pending)
    assert(f.c.owner.owner==keys[owner]and f.c.owner.serial==3);operations=operations+1
   end end end
   -- Genuine driver authority can come from any non-host member.
   local f=fixture(n,name,#roles-1,owner,host,true);assert(f.step(0));f.reply();f.step(nil,10.1)
   local r,w,rel,send=f.counts();assert(w==0 and rel==0 and send==0)
   f.acquire();f.step(nil,10.2);f.step(nil,10.3);r,w,rel,send=f.counts()
   assert(r==1 and w==1 and rel==1 and send==n-1 and not f.probe.pending and f.c.driver==f.c.avatar);operations=operations+1
  end
 end
end end end
for n=3,4 do for _,field in ipairs({'current','reserved','target'})do
 local f=fixture(n,'m102',1,2,1);local a=f.c.sample.avatars[3];a.seat=seat(9,3,3);a.seat[field]=2
 assert(f.step(2)==false);local r,w,rel,send=f.counts();assert(r==0 and w==0 and rel==0 and send==0);negatives=negatives+1
end end
for _,change in ipairs({
 function(c)c.sample.player_count=4 end,
 function(c)c.owner.members[keys[3]]=nil end,
 function(c)c.owner.coordinator=keys[3]end,
 function(c)c.sample.avatars[3].unit=999 end,
 function(c)c.owner.avatars[9].owner=keys[2]end,
 function(c)c.sample.avatars[3].seat=seat(9,2,3)end,
 function(c)c.native.peer_count=4 end})do
 local f=fixture(3,'m102',1,2,1);assert(f.step(2));f.reply();change(f.c);pcall(f.step,nil,10.1)
 local _,w,rel,send=f.counts();assert(w==0 and rel==0 and send==0 and f.gate(),'changed room mutated/released or dropped pending gate');negatives=negatives+1
end
-- Another car's driver/seat changes need not freeze this vehicle.
local f=fixture(4,'m102',1,3,2);f.c.sample.avatars[2].seat=seat(99,0,1)
assert(f.step(2));f.reply();f.c.sample.avatars[2].seat=seat(99,2,3);f.step(nil,10.1);f.step(nil,10.2)
local _,w,rel,send=f.counts();assert(w==1 and rel==1 and send==3 and not f.probe.pending);operations=operations+1
-- Same-car peer begins a competing seat transition while waiting: reject.
f=fixture(4,'m102',1,3,2);f.c.sample.avatars[2].seat=seat(9,3,3);assert(f.step(2));f.reply()
f.c.sample.avatars[2].seat.target=4;assert(not pcall(f.step,nil,10.1));_,w,rel,send=f.counts();assert(w==0 and rel==0 and send==0);negatives=negatives+1
-- Stable join/leave BETWEEN completed requests is usable without a restart.
f=fixture(3,'m102',1,1,1);assert(f.step(2));assert(f.step(1,11))
local c=f.c;c.sample.avatars[4]={id=10,unit=704,network_unit=4104,is_local=false,owned_local=false,seat=seat(88,0,1)}
c.sample.player_count=4;c.native.player_count=4;c.native.peer_count=4;c.owner.peer_count=4
c.owner.members[keys[4]]=true;c.owner.avatars[10]={owner=keys[4]};assert(f.step(2,12))
c.sample.avatars[4]=nil;c.sample.player_count=3;c.native.player_count=3;c.native.peer_count=3;c.owner.peer_count=3
c.owner.members[keys[4]]=nil;c.owner.avatars[10]=nil;assert(f.step(1,13));operations=operations+4
print('PASS '..operations..' actual probe cases for 2/3/4 players, five models, all host/owner combinations, all peer notifications, genuine acquisitions, other cars and settled joins/leaves; '..negatives..' drift/occupancy/concurrent-slot refusals; engine/ACK effects simulated')
