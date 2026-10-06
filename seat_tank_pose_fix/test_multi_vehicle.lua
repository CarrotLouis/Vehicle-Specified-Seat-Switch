-- Actual input/gate/dispatcher/probe/adapter. Native effects/network mocked.
local NEW='seat_tank_pose_fix';local root='work/'..NEW..'/'
local fixture=assert(loadfile(root..'input_race_fixture.lua'))()
local M=assert(loadfile(root..'adapter.lua'))()
local profiles=assert(loadfile('work/seat_switch/src/profile.lua'))().tables
local policy=assert(loadfile('work/seat_switch/src/policy.lua'))()
local dir=assert(os.getenv('VSS_INPUT_RACE_DIR'));local cases=0
local vehicles={'m102','m103','m104','bastion','maelstrom'}
local function fresh(v,source,host,kind,remote)
 return fixture(NEW,source,host,kind~='local',dir,kind=='driver'and 0 or remote or 'outside',v)
end
local function normal(v,source,target)
 local names=policy.seats[v];return policy.check('normal',v,names[source+1],names[target+1],false)
end
local function binding(f,target)return f.keys[policy.seats[f.c.native.vehicle][target+1]]end
local function trigger(f,target,tap)
 local code=binding(f,target);f:press(code);f:tick();assert(f.dispatcher.queued and not f.probe.pending)
 if tap then f:release()end
 f:enqueue(code,target);f:tick();assert(f.probe.pending and not f.dispatcher.queued)
end
-- Every vacant cross-region pair, both hosts, all four ownership contexts.
for _,v in ipairs(vehicles)do for _,host in ipairs({'self','friend'})do
 local roles=profiles[v].roles
 for source=0,#roles-1 do for target=0,#roles-1 do if source~=target and not normal(v,source,target)then
  for _,kind in ipairs({'local','driver','outside','seated'})do
   local remote
   if kind=='seated'then for n=1,#roles-1 do if n~=source and n~=target then remote=n;break end end end
   if kind=='local'or kind=='driver'and source>0 and target>0 or kind=='outside'and source>0 or kind=='seated'and source>0 and remote then
    local f=fresh(v,source,host,kind,remote);local a,c=f.adapter,f.c;local held=f.friend.seat
    local t=a:ticket(c,target);assert(a:eligible(c,source,kind=='local',t,target),v..'/'..kind..'/'..source..'/'..target)
    assert(t.driver_acquire==(kind~='local'and kind~='driver'and target==0))
    if kind~='local'then a:request(c,t);assert(t.request_invoked and f.transfers==1)end
    a:execute(c,t);assert(a:confirmed(c,t,true)and f.mutations==1 and f.sends==1)
    if kind~='local'and target~=0 then a:return_owned(c,t);assert(a:confirmed(c,t,false)and f.transfers==2)
    else assert(c.owner.owner=='self'and f.transfers==(kind=='local'and 0 or 1))end
    assert(f.friend.seat==held and f.friend.id==8 and f.friend.unit==88 and f.friend.network_unit==808)
    cases=cases+1
   end
  end
 end end end
end end
-- Full batched manual routes, held/tapped input, both hosts, exact-once effects.
local routes={m102={2,4,3,4,0,2,0},m103={2,1,3,0,2,0},m104={1,2,0,2,1},
 bastion={1,0,2,0,1,0,3,0},maelstrom={1,0,2,0,1,0,3,0}}
for _,v in ipairs(vehicles)do for _,host in ipairs({'self','friend'})do for _,tap in ipairs({false,true})do
 local route=routes[v];local f=fresh(v,route[1],host,'outside');local held=f.friend.seat
 for i=2,#route do trigger(f,route[i],tap);f:tick();f:finish();f:release();f:tick(.5)end
 assert(f.mutations==#route-1 and f.sends==#route-1 and f.native_calls==0 and f.friend.seat==held)
 assert(f:count('integrated_driver_authority_retained')==1 and f.c.owner.owner=='self')
 cases=cases+1
end end end
-- Layout, occupancy, peer and identity changes must block BEFORE acquisition.
for _,v in ipairs(vehicles)do
 local route=routes[v];local source,target=route[1],route[2]
 for _,change in ipairs({
  function(f)f.c.native.transition=99 end,function(f)f.c.native.vehicle='tanker'end,
  function(f)f.c.native.occupied[target]=true end,function(f)f.c.native.occupied[target]=nil end,
  function(f)f.c.sample.player_count=3 end,function(f)f.c.native.peer_count=3 end,
  function(f)f.c.owner.coordinator='unknown'end,function(f)f.c.owner.avatars[7].owner='friend'end,
  function(f)f.c.owner.avatars[8].owner='self'end,function(f)f.friend.seat.transitioning=1 end,
  function(f)f.friend.unit=999 end,function(f)f.friend.network_unit=999 end,
  function(f)f.c.native.identity='changed'end,
 })do
  local f=fresh(v,source,'friend','outside');local t=f.adapter:ticket(f.c,target);change(f)
  assert(not pcall(f.adapter.request,f.adapter,f.c,t)and not t.request_invoked and f.transfers==0 and f.mutations==0)
  cases=cases+1
 end
 -- Late grants and third-peer changes return original authority with no mutation.
 for _,kind in ipairs({'focus','logging','late','third_peer','occupied'})do
  local f=fresh(v,source,'friend','outside');f.defer_grant=true;trigger(f,target,false)
  if kind=='focus'then f.focused=false elseif kind=='logging'then f.probe:cancel('logging_unavailable')
  elseif kind=='late'then f:tick(6)elseif kind=='third_peer'then f.c.sample.player_count=3
  else f.c.native.occupied[target]=true end
  f.c.owner.owner='self';f.c.owner.vehicle.owned_local=true;f.c.native.owned=true
  for _=1,65 do f:tick()end
  assert(f.probe.phase=='stopped'and f.c.owner.owner=='friend'and f.transfers==2 and f.mutations==0)
  cases=cases+1
 end
 -- Occupied driver cannot be acquired, even with a mounted role at a new index.
 local f=fresh(v,source,'friend','driver');assert(not f.adapter:eligible(f.c,source,false,nil,0));cases=cases+1
end
-- Existing native groups remain first, including BOTH tanker directions.
for _,v in ipairs({'m102','m103','m104','bastion','maelstrom','tanker'})do
 for source=0,#profiles[v].roles-1 do for target=0,#profiles[v].roles-1 do if normal(v,source,target)then
  local f=fresh(v,source,'self','local');local code=binding(f,target)
  f:press(code);f:tick();f:release();f:tick(.1)
  assert(f.c.seat==target and f.native_calls==1 and f.mutations==0 and f.sends==0 and f.transfers==0)
  cases=cases+1
 end end end
end
print('PASS '..cases..' batched vehicle cases: five layouts/all vacant cross pairs/both hosts/four authority contexts; held-tap routes; identity/occupancy/peer/late-grant cleanup; tanker and all Normal groups remain native')
