local M=assert(loadfile('work/seat_weapon_sync_diagnostic/adapter.lua'))()
local function fixture()
 local function seat(node,role)return {collection=9,current=node,reserved=node,role=role,target=-1,action=-1,transitioning=0,queued_exit=0}end
 local c={identity='v',summary='v',sample={player_count=2,local_count=1},seat=1,
  native={identity='avatar_binding',vehicle='m102',transition=26,profile={roles={1,3,3,3,2}},player_count=2,peer_count=2,owned=false,avatar=7,node=1,active=false,occupied={[0]=true,[1]=true,[4]=false}},
  owner={owner='friend',selfpeer='self',coordinator='friend',members={friend=true,self=true},peer_count=2,busy=false,vehicle={id=9,owned_local=false},avatars={[7]={owner='self'},[8]={owner='friend'}}},
  avatar={id=7,unit=77,is_local=true,owned_local=true,vehicle_input=true,seat=seat(1,3)},driver={id=8,unit=88,is_local=false,seat=seat(0,1)},destination='friend'}
 local calls={};local api={input_allowed=function()return true end,down=function()return false end}
 local obs={send=function(_,o,dest,target,hook)calls[#calls+1]='transfer';hook()end,summary=function()return {}end}
 local tx={prepare=function()calls[#calls+1]='prepare';return function()
  calls[#calls+1]='switch';c.seat=4;c.native.node=4;c.avatar.seat=seat(4,2);c.native.occupied[1]=false;c.native.occupied[4]=true
 end end}
 local sender={prepare=function()return function()calls[#calls+1]='sync'end end}
 local trace={active=true,health=function()end}
 local snapshot={current=function()return true end}
 local a=M.new(api,0,{},nil,obs,snapshot,tx,sender,trace,function()end,function()return ''end)
 function a:capture()return c end
 local t=a:ticket(c)
 local function own()c.native.owned=true;c.owner.vehicle.owned_local=true;c.owner.owner='self'end
 return c,a,t,calls,own,api,tx,snapshot,sender
end
local c,a,t,calls,own,api,tx,snapshot=fixture();assert(M.eligible(c,1,false,t))
a:request(c,t);assert(t.request_invoked and #calls==1);own();assert(M.eligible(c,1,true,t));a:execute(c,t)
assert(t.sync_returned and table.concat(calls,',')=='transfer,prepare,switch,sync')
a:return_owned(c,t);assert(t.return_invoked);assert(not pcall(a.return_owned,a,c,t))
local changes={
 function(c)c.native.vehicle='m104'end,function(c)c.native.transition=28 end,
 function(c)c.sample.player_count=3 end,function(c)c.owner.selfpeer='friend'end,
 function(c)c.owner.busy=true end,function(c)c.native.owned=true end,
 function(c)c.native.active=true end,function(c)c.native.occupied[4]=true end,
 function(c)c.driver=nil end,function(c)c.driver.seat.target=2 end,
 function(c)c.owner.avatars[8].owner='self'end,function(c)c.owner.avatars[7].owner='friend'end,
 function(c)c.native.identity='respawn'end,function(c)c.driver.unit=99 end,
 function(c)c.avatar.seat.queued_exit=1 end,function(c)c.native=nil end}
for _,change in ipairs(changes)do c,a,t=fixture();change(c);assert(not M.eligible(c,1,false,t))end
-- Native seat reads or input focus are not prerequisites for returning a loan.
c,a,t,calls,own,api=fixture();own();c.native=nil;api.input_allowed=function()return false end;a:return_owned(c,t);assert(t.return_invoked)
-- A third player cancels switching yet preserves the return route.
c,a,t,calls,own=fixture();own();c.sample.player_count=3;c.owner.peer_count=3;c.destination=nil;c.owner.members.third=true
assert(a:context(c,t));assert(not M.eligible(c,1,true,t));a:return_owned(c,t);assert(t.return_invoked)
-- Never return a previous loan to a different session or underneath a new driver.
for _,change in ipairs({function(c)c.identity='other_session'end,function(c)c.driver.is_local=true end,function(c)c.driver.unit=99 end,function(c)c.owner.members.friend=nil end})do
 c,a,t,calls,own=fixture();own();change(c);assert(not pcall(a.return_owned,a,c,t));assert(not t.return_invoked and #calls==0)
end
-- A target claimed during prepare causes zero local mutation/sends.
c,a,t,calls,own,api,tx,snapshot=fixture();own();local original=tx.prepare;tx.prepare=function(...)local f=original(...);c.native.occupied[4]=true;return f end
assert(not pcall(a.execute,a,c,t));assert(not t.mutation_started and #calls==1)
-- Missing required logging prevents a new mutation, not cleanup.
c,a,t,calls,own,api=fixture();own();api.experiment_allowed=function()return false end
assert(not pcall(a.execute,a,c,t));assert(#calls==0);a:return_owned(c,t);assert(t.return_invoked)
print('PASS integrated adapter scope, fresh target race, respawn/driver/session guards, return with missing seat/focus/third peer/logging')

-- New notification preflight rejects BEFORE mutation; existing ownership cleanup still works.
local sender
c,a,t,calls,own,api,tx,snapshot,sender=fixture();own()
sender.prepare=function()error('animation_notification_avatar_membership')end
assert(not pcall(a.execute,a,c,t));assert(not t.mutation_started and table.concat(calls,',')=='prepare')
a:return_owned(c,t);assert(t.return_invoked and table.concat(calls,',')=='prepare,transfer')
print('PASS animation preflight refusal precedes local mutation; borrowed ownership remains returnable')
