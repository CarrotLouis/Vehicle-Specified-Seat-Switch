-- Real new adapter/probe/policy, controlled observations and native-call mocks.
-- This verifies identities, order, vacancy and cleanup, not network/physics.
local M=assert(loadfile('work/seat_fleet_test/adapter.lua'))()
local fleet=assert(loadfile('work/seat_fleet_test/fleet_policy.lua'))();M.fleet=fleet
local probe_factory=assert(loadfile('work/seat_fleet_test/probe.lua'))()
local profiles=assert(loadfile('work/seat_switch/src/profile.lua'))().tables
local encode=assert(loadfile('work/seat_network_diagnostic/recorder.lua'))().encode
local PEERS={'00000001','00000002','00000003','00000004'}
local function copy(x)if type(x)~='table'then return x end;local y={};for k,v in pairs(x)do y[k]=copy(v)end;return y end
local function fixture(n,host,owner,name,source,target,remote_driver)
 local p=profiles[name];local d=M.layout({vehicle=name,transition=p.transition,profile=p})
 local function seat(col,node,role)return {collection=col,current=node,reserved=node,role=role,
  target=-1,action=-1,transitioning=0,queued_exit=0,entry_role=role,transition_type=p.transition,entrance=node}end
 local c={identity='carA',summary='carA',seat=source,sample={state='mission',player_count=n,peer_count=n,local_count=1,avatars={}},
  owner={selfpeer=PEERS[1],owner=PEERS[owner],coordinator=PEERS[host],peer_count=n,serial=3,busy=false,members={},avatars={},
   vehicle={id=9,unit=900,network_unit=909,resource='carA',name=name,transition_type=p.transition,seat_count=#p.roles,owned_local=owner==1}},
  native={identity='own/7/77',vehicle=name,transition=p.transition,profile=p,player_count=n,peer_count=n,owned=owner==1,
   avatar=7,avatar_unit=77,node=source,active=false,occupied={}}}
 for i=0,#p.roles-1 do c.native.occupied[i]=false end;c.native.occupied[source]=true
 for i=1,n do
  c.owner.members[PEERS[i]]=true
  local a={id=i+6,unit=70+i*7,network_unit=700+i,resource='avatar',is_local=i==1,owned_local=i==1,vehicle_input=i==1,
   seat=seat(i==1 and 9 or 99,i==1 and source or 0,i==1 and p.roles[source+1]or 1)}
  -- Remote peers drive a different car; changing it is unrelated to car A.
  -- This is local input permission: actual remote drivers have it false.
  c.sample.avatars[i]=a;c.owner.avatars[a.id]={owner=PEERS[i]}
 end
 c.avatar=c.sample.avatars[1]
 if source==0 then c.driver=c.avatar
 elseif remote_driver then
  assert(owner~=1);c.driver=c.sample.avatars[owner];c.driver.seat=seat(9,0,1);c.native.occupied[0]=true
 end
 c.destination=n==2 and PEERS[2]or owner~=1 and PEERS[owner]or PEERS[2]
 local log={calls={},events={}};local api={input_allowed=function()return true end,down=function()return false end}
 local observer={summary=function(_,o)return {serial=o.serial}end}
 function observer:send(o,destination,to,mark,options)
  assert(destination==c.owner.owner and c.owner.members[destination]and c.owner.members[to])
  if destination~=c.owner.selfpeer then
   assert(options and options.mode=='fleet_owner');options.validate();log.calls[#log.calls+1]='request:'..destination
  else log.calls[#log.calls+1]='return:'..to end
  mark()
 end
 local transaction={prepare=function(_,s,to)
  assert(s==c.native and to==target);log.calls[#log.calls+1]='prepare'
  return function()
   log.calls[#log.calls+1]='mutate';c.native.occupied[source]=false;c.native.occupied[target]=true
   c.native.node=target;c.seat=target;c.avatar.seat=seat(9,target,p.roles[target+1])
   c.driver=target==0 and c.avatar or remote_driver and c.sample.avatars[owner]or nil
  end
 end}
 local sender={prepare=function()error('Fleet must notify all verified peers')end}
 function sender:prepare_all(o,destinations,s,to)
  assert(#destinations==n-1 and s==c.native and to==target)
  return function()
   for i,peer in ipairs(destinations)do assert(peer~=o.selfpeer and o.members[peer]);log.calls[#log.calls+1]='notify:'..peer end
  end
 end
 local adapter=M.new(api,0,{},nil,observer,{current=function()return true end},transaction,sender,
  {active=true,health=function()end},function(e)log.events[#log.events+1]=e end,encode)
 function adapter:capture()return c end
 local function owner_to(i)c.owner.owner=PEERS[i];c.owner.vehicle.owned_local=i==1;c.native.owned=i==1;c.owner.serial=c.owner.serial+1 end
 return c,adapter,log,owner_to,api,transaction,sender
end
local count=0
for n=3,4 do for host=1,n do for owner=1,n do
 for _,name in ipairs({'m102','m103','m104','bastion','maelstrom'})do
  local source=2;local target=name=='m104'and 1 or 0
  local c,a,log,change=fixture(n,host,owner,name,source,target,false)
  local saved={};for i=2,n do saved[i]=encode(c.sample.avatars[i])end
  local good,why=M.eligible(c,source,owner==1,nil,target);assert(good,why)
  local probe=probe_factory.new(a,function(e)log.events[#log.events+1]=e end,function()end,nil,true)
  probe:step(nil,0,true);assert(probe:step(target,.3,true));local t=a:ticket(c,target)
  assert(t.fleet and #t.notifications==n-1 and #t.peers==n)
  if owner~=1 then change(1)end
  probe:step(nil,.32,true);assert(c.native.node==target and t.source==source)
  probe:step(nil,.34,true)
  if owner~=1 and target~=0 then change(owner)end
  probe:step(nil,.36,true);probe:step(nil,.91,true)
  assert(not probe.pending and probe.phase=='waiting_second_trigger',probe.phase)
  for i=2,n do assert(encode(c.sample.avatars[i])==saved[i],'Other avatar/other car changed')end
  local requested,returned,notified=0,0,0
  for _,call in ipairs(log.calls)do if call:sub(1,8)=='request:'then requested=requested+1 end
   if call:sub(1,7)=='return:'then returned=returned+1 end;if call:sub(1,7)=='notify:'then notified=notified+1 end end
  assert(requested==(owner==1 and 0 or 1)and returned==(owner~=1 and target~=0 and 1 or 0)and notified==n-1)
  assert(c.owner.owner==((owner==1 or target==0)and PEERS[1]or PEERS[owner]))
  count=count+1
 end
 -- Passenger/gunner while a remote driver keeps the chassis: same driver,
 -- exactly one loan and return; coordinator need not be either participant.
 if owner~=1 then
  local c,a,log,change=fixture(n,host,owner,'m102',1,4,true)
  local t=a:ticket(c,4);assert(M.eligible(c,1,false,t))
  a:request(c,t);change(1);a:execute(c,t);assert(t.sync_returned);a:return_owned(c,t)
  assert(t.return_invoked and c.driver.id==t.driver_id)
  count=count+1
 end
end end end
-- In a two-player room only the new actual-owner-in-another-car case opts in.
local c,a=fixture(2,2,2,'m102',2,0,false)
local t=a:ticket(c,0);assert(t.fleet and M.eligible(c,2,false,t));count=count+1
local mutations={
 function(c)c.sample.player_count=5 end,function(c)c.sample.peer_count=2 end,
 function(c)c.owner.peer_count=2 end,function(c)c.sample.local_count=2 end,
 function(c)c.owner.members[PEERS[3]]=nil end,function(c)c.owner.coordinator='foreign!'end,
 function(c)c.owner.owner='foreign!'end,function(c)c.owner.busy=true end,
 function(c)c.sample.avatars[3]=nil end,function(c)c.owner.avatars[9].owner=PEERS[2]end,
 function(c)c.avatar.owned_local=false end,function(c)c.avatar.vehicle_input=false end,
 function(c)c.native.occupied[4]=true end,function(c)c.native.active=true end,
 function(c)c.native.transition=99 end,function(c)c.native.identity='respawn'end,
 function(c)c.driver.unit=123 end,function(c)c.driver.seat.target=2 end,
 function(c)c.driver.seat.role=3 end,function(c)c.driver.network_unit=123 end,
 function(c)c.sample.avatars[3].seat.collection=9;c.sample.avatars[3].seat.current=3;c.sample.avatars[3].seat.reserved=3;c.sample.avatars[3].seat.role=3;c.native.occupied[3]=true end,
 function(c)c.identity='carB'end,
}
for _,mutate in ipairs(mutations)do
 local c,a,log=fixture(3,3,2,'m102',1,4,true);local t=a:ticket(c,4);mutate(c)
 assert(not M.eligible(c,1,false,t),'Unsafe fleet context accepted');assert(not t.mutation_started and #log.calls==0);count=count+1
end
-- A third/fourth player's independent-car seat changes are not this car's
-- occupant identity. Joining/departure pre-mutation still cancels the request.
c,a=fixture(4,3,2,'m102',1,4,true);t=a:ticket(c,4)
c.sample.avatars[3].seat.current=2;c.sample.avatars[3].seat.reserved=2;c.sample.avatars[3].seat.role=3
assert(M.eligible(c,1,false,t));count=count+1
local log,change
-- Same-car occupied passenger seats at three/four peers, including three
-- remote occupants on M102. Remote input permission remains false.
for n=3,4 do for _,name in ipairs({'m102','m103','m104','bastion','maelstrom'})do
 for _,direction in ipairs({{1,name=='m102'and 4 or 2},{name=='m102'and 4 or 2,1}})do
  local source,target=direction[1],direction[2]
  local x,b=fixture(n,n,2,name,source,target,true)
  local next_node=1
  for i=3,n do
   while next_node<#profiles[name].roles and (next_node==source or next_node==target)do next_node=next_node+1 end
   if next_node<#profiles[name].roles then
    local row=x.sample.avatars[i];row.seat.collection=9;row.seat.current=next_node;row.seat.reserved=next_node
    row.seat.role=profiles[name].roles[next_node+1];x.native.occupied[next_node]=true;next_node=next_node+1
   end
  end
  local u=b:ticket(x,target);assert(M.eligible(x,source,false,u))
  for i=2,n do assert(x.sample.avatars[i].vehicle_input==false)end
  local old=x.native.occupied[target];x.native.occupied[target]=true
  assert(not M.eligible(x,source,false,u));x.native.occupied[target]=old
  count=count+1
 end
end end
c,a,log,change=fixture(3,3,2,'m102',1,4,true);t=a:ticket(c,4);change(1)
c.sample.player_count=4;c.owner.members[PEERS[4]]=true
assert(a:context(c,t)and not M.eligible(c,1,true,t));a:return_owned(c,t);assert(t.return_invoked);count=count+1
-- Final fresh snapshot rejects a newly occupied target before local mutation.
c,a,log,change,api,transaction=fixture(4,3,2,'m102',1,4,true);t=a:ticket(c,4);change(1)
local prepare=transaction.prepare
transaction.prepare=function(...)local f=prepare(...);c.native.occupied[4]=true;return f end
assert(not pcall(a.execute,a,c,t)and not t.mutation_started and #log.calls==1);count=count+1
-- Real capture requests all-avatar owners only for stable fleet preflight.
-- A joining unreadable unrelated avatar must not obstruct tracked cleanup.
for n=3,4 do
 local c=fixture(n,n,2,'m102',1,4,true);c.owner.context='mock/session'
 c.native.collection=9;c.native.collection_unit=909;c.native.resource='carA'
 local need;local observer={capture=function(_,s,v,what)need=what;return c.owner end,summary=function()return {}end}
 local captured=M.new({},0,{}, {capture=function()return c.sample end},observer,
  {capture=function()return c.native end},nil,nil,nil,nil,encode)
 assert(captured:capture()and need=='all')
 local ticket={fleet=true,peers=fleet.keys(c.owner.members),vehicle=c.owner.vehicle,cancel_reason='roster_changed'}
 assert(captured:capture(ticket)and need==true)
 ticket.cancel_reason=nil;c.sample.player_count=n==3 and 4 or 3
 assert(captured:capture(ticket)and need==true);count=count+1
end
print('PASS '..count..' real fleet adapter/probe cases: all five models, every host/owner at 3/4 peers, same-car occupants, loan/return/retain/local, all-peer notifications, own avatar only, other moving car unaffected, race/roster/ownership/identity and tracked-cleanup guards; game calls mocked')
