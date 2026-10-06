-- New occupied-passenger context through the actual adapter/probe/dispatcher.
-- Engine transactions and network delivery are simulated; no game is launched.
local prefix='work/seat_multi_vehicle_fix/'
local function load(name)return assert(loadfile(prefix..name..'.lua'))()end
local M=load('adapter')
local function seat(n)return {collection=9,current=n,reserved=n,role=n==0 and 1 or n==4 and 2 or 3,target=-1,action=-1,transitioning=0,queued_exit=0}end
local function fixture(source,target,remote_node,host)
 local av={id=7,unit=77,is_local=true,owned_local=true,vehicle_input=true,seat=seat(source)}
 local friend={id=8,unit=88,is_local=false,owned_local=false,vehicle_input=true,seat=seat(remote_node)}
 local c={identity='v',seat=source,avatar=av,driver=source==0 and av or nil,destination='friend',sample={player_count=2,local_count=1,avatars={av,friend}},
  native={identity='av',vehicle='m102',transition=26,profile={roles={1,3,3,3,2}},player_count=2,peer_count=2,owned=true,avatar=7,avatar_unit=77,node=source,occupied={}},
  owner={owner='self',selfpeer='self',coordinator=host,members={self=true,friend=true},peer_count=2,vehicle={id=9,owned_local=true},avatars={[7]={owner='self'},[8]={owner='friend'}}}}
 local function position(n)
  for i=0,4 do c.native.occupied[i]=false end
  c.seat=n;c.native.node=n;c.native.occupied[n]=true;c.native.occupied[friend.seat.current]=true;av.seat=seat(n);c.driver=n==0 and av or nil
 end
 position(source)
 local calls={};local now,physical,consumed=0,{},{}
 local api={now=function()return now end,input_allowed=function()return true end,focused=function()return true end,down=function(k)return physical[k]end,
  control_down=function(k)return physical[k]and not consumed[k]end}
 local tx={prepare=function(_,s,t)assert(s.avatar==7 and s.node~=remote_node and t~=remote_node);calls[#calls+1]='prepare'
  return function()calls[#calls+1]='switch';position(t)end end}
 local sender={prepare=function(_,o,dest,s,t)
  assert(o.owner=='self'and dest=='friend'and s.avatar==7 and t~=remote_node)
  return function()calls[#calls+1]='sync'end end}
 local snapshot={current=function()return true end,predictions=function()return nil,nil end}
 local a=M.new(api,0,{},nil,{summary=function()return {}end,send=function()error('own chassis must never borrow/return')end},snapshot,tx,sender,{active=true,health=function()end},function()end,function()return ''end)
 a.capture=function()return c end
 local function time(dt)now=now+dt end
 return c,a,a:ticket(c,target),calls,tx,sender,api,time,physical,consumed,position,snapshot
end
local cases=0
for _,host in ipairs({'self','friend'})do for remote=1,3 do for source=0,4 do for target=0,4 do
 if source~=target and source~=remote and target~=remote then
  local c,a,t,calls=fixture(source,target,remote,host)
  local friend=c.sample.avatars[2];local held=friend.seat
  assert(M.eligible(c,source,true,t)and t.remote_aboard and t.remote_node==remote)
  assert(not pcall(a.request,a,c,t)and not pcall(a.return_owned,a,c,t))
  a:execute(c,t);assert(t.sync_returned and table.concat(calls,',')=='prepare,switch,sync')
  assert(friend.seat==held and friend.id==8 and friend.unit==88 and friend.seat.current==remote,'remote seat/identity must not change')
  assert(a:confirmed(c,t,true))
  cases=cases+1
 end
end end end end
for _,change in ipairs({
 function(c)c.native.occupied[4]=true end,function(c)c.native.occupied[4]=nil end,
 function(c)c.owner.avatars[8].owner='self'end,function(c)c.owner.avatars[8]=nil end,
 function(c)c.sample.avatars[2].unit=99 end,function(c)c.sample.avatars[2].id=88 end,
 function(c)c.sample.avatars[2].seat=seat(2);c.native.occupied[2]=true end,
 function(c)c.sample.avatars[2].seat.collection=-1 end,
 function(c)c.sample.avatars[2].seat=seat(0);c.driver=c.sample.avatars[2]end,
 function(c)c.sample.avatars[2].seat=seat(4);c.native.occupied[4]=true end,
 function(c)c.sample.avatars[2].seat.target=2 end,function(c)c.sample.avatars[2].seat.reserved=2 end,
 function(c)c.sample.avatars[2].seat.action=17 end,function(c)c.sample.avatars[2].seat.transitioning=1 end,
 function(c)c.sample.avatars[2].seat.queued_exit=1 end,function(c)c.native.occupied[1]=false end,
 function(c)c.sample.player_count=3 end,function(c)c.owner.coordinator='newhost'end
})do
 local c,a,t,calls=fixture(0,4,1,'self');change(c)
 assert(not M.eligible(c,0,true,t));assert(not pcall(a.execute,a,c,t)and not t.mutation_started and #calls==0)
end
-- Changes during transaction preparation must be caught before any mutation.
for _,change in ipairs({
 function(c)c.sample.avatars[2].unit=99 end,
 function(c)c.sample.avatars[2].seat=seat(2);c.native.occupied[2]=true end,
 function(c)c.native.occupied[4]=true end,
 function(c)c.owner.avatars[8].owner='self'end
})do
 local c,a,t,calls,tx=fixture(0,4,1,'self');local old=tx.prepare
 tx.prepare=function(...)local f=old(...);change(c);return f end
 assert(not pcall(a.execute,a,c,t)and not t.mutation_started and table.concat(calls,',')=='prepare')
end
-- Full three-step driver -> gunner -> rear -> driver, both host identities.
local input=assert(loadfile('work/seat_switch/src/input.lua'))()
local config=assert(loadfile('work/seat_switch/src/config.lua'))()
local policy=assert(loadfile('work/seat_switch/src/policy.lua'))()
for _,host in ipairs({'self','friend'})do
 local c,a,_,calls,_,_,api,time,physical,consumed,_,snapshot=fixture(0,4,1,host)
 local probe=load('probe').new(a,function()end,function()end,nil,true)
 local edge={};local gate={active=true,pulse=function()end,take=function()local v=edge;edge={};return v end}
 local keys=config.parse('[m102]\ndriver=X\nfront_passenger=Z\nrear_left=Ctrl+Z\nrear_right=Ctrl+X\ngunner=Ctrl+MOUSE2')
 local d=load('dispatcher').new(api,keys,input,policy,snapshot,{},probe,function()end,gate)
 local function tick(dt)time(dt or .016);return d:update(c.native)end
 tick();tick(.3)
 for _,step in ipairs({{4,1026,2},{2,1114,90},{0,88,88}})do
  local n=#calls;physical[162]=step[2]>=256 or nil;physical[step[3]]=true;consumed[step[3]]=true;edge[step[2]]=true
  tick();assert(probe.pending and not d.queued);tick();assert(c.seat==step[1]and #calls==n+3)
  for _=1,60 do tick()end
  assert(not probe.pending and probe.phase~='stopped'and c.owner.owner=='self')
  assert(c.sample.avatars[2].seat.current==1 and c.native.occupied[1])
  physical[162]=nil;physical[step[3]]=nil;consumed[step[3]]=nil;tick(.5)
 end
 local n=#calls;edge[90]=true;tick();assert(#calls==n and c.seat==0 and not probe.pending,'occupied front must refuse without requesting authority')
end
print('PASS '..cases..' local-owner/aboard passenger pairs x host identities; unchanged remote avatar, no transfers, occupancy/owner/seat/identity/race guards; real held-input three-step flow and occupied refusal')
