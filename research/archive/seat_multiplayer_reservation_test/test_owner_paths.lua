-- Actual new protocol factory; engine/sender effects are declared doubles.
local scope=assert(loadfile('work/seat_multiplayer_reservation_test/scope.lua'))()
local membership=assert(loadfile('work/seat_multiplayer_reservation_test/membership.lua'))()
local M=assert(loadfile('work/seat_multiplayer_reservation_test/probe.lua'))()(scope,membership)
local profiles=assert(loadfile('work/seat_switch/src/profile.lua'))().tables
local bit=require('bit')
local function fixture(name,source,owned,host)
 local profile=profiles[name];local roles=profile.roles
 local av={id=7,unit=701,network_unit=4107,is_local=true,owned_local=true,vehicle_input=true,
  seat={collection=9,current=source,reserved=source,role=roles[source+1],target=-1,action=-1,transitioning=0,queued_exit=0}}
 local friend={id=8,unit=801,network_unit=4207,is_local=false,owned_local=false,vehicle_input=false,
  seat={collection=0,current=0,reserved=0,role=0,target=-1,action=-1,transitioning=0,queued_exit=0}}
 local c={identity='world/car',seat=source,destination='remote!!',sample={player_count=2,local_count=1,avatars={av,friend}},avatar=av,
  native={identity='avatar/car',avatar=7,avatar_unit=701,vehicle=name,transition=profile.transition,profile=profile,
   node=source,owned=owned,active=false,player_count=2,peer_count=2,mask=0,occupied={}},
  owner={owner=owned and 'selfpeer'or'remote!!',selfpeer='selfpeer',coordinator=host=='installer'and'selfpeer'or'remote!!',
   serial=3,peer_count=2,members={selfpeer=true,['remote!!']=true},avatars={[7]={owner='selfpeer'},[8]={owner='remote!!'}},
   vehicle={id=9,unit=901,network_unit=4123,owned_local=owned}}}
 for n=0,#roles-1 do c.native.occupied[n]=n==source;if n~=source then c.native.mask=bit.bor(c.native.mask,2^n)end end
 if source==0 then c.driver=av end
 local state,cookie,arm,requests,local_calls,writes,releases,sends=nil,0,0,0,0,0,0,0
 local held,events={},{}
 local trace={active=true,health=function()end}
 function trace:gate_arm(peer,car,avatar,from,to)
  assert(peer=='remote!!'and car==4123 and avatar==4107 and not state)
  cookie=cookie+1;arm=arm+1;state={cookie=cookie,peer_key=peer,car=car,avatar=avatar,source=from,target=to,status=1,guard_lost=0,chosen=4294967295};return cookie
 end
 function trace:gate_peek(key)assert(state.cookie==key);return state end
 function trace:gate_finish(key)assert(state.cookie==key and state.status==2);state=nil end
 local api={input_allowed=function()return true end,control_down=function(k)return held[k]end,experiment_allowed=function()return true end}
 local snapshot={current=function()return true end}
 local function move(target,local_owner)
  writes=writes+1
  c.seat=target;c.native.node=target;av.seat.current=target;av.seat.reserved=target;av.seat.role=roles[target+1]
  c.driver=target==0 and av or nil
  if local_owner then
   c.native.occupied[source]=false;c.native.occupied[target]=true
   c.native.mask=bit.band(bit.bor(c.native.mask,2^source),bit.bnot(2^target))
   c.owner.serial=c.owner.serial+1 -- legitimate native local-owner refresh
  end
 end
 local adapter={capture=function()return c end,
  mounted={prepare=function(_,_,target)if roles[target+1]==2 then return {target=target}end end,ready=function()return true end},
  owned_transaction={prepare=function(_,s,target)
   assert(s.owned and c.owner.owner=='selfpeer'and s.occupied[target]==false)
   local_calls=local_calls+1;return function()move(target,true)end
  end},
  release_acquired={prepare=function(_,s,slot,grant)
   assert(s.owned and grant.target==0 and slot==source and grant:check())
   return function()assert(grant:check());releases=releases+1;c.native.occupied[slot]=false;c.native.mask=bit.bor(c.native.mask,2^slot)end
  end}}
 local entrance={prepare_request=function(_,_,target)return function()assert(state.status==1);requests=requests+1 end,2 end,
  prepare_release=function()error('new driver must release through its OWN native manager, never former owner')end}
 local tx={preflight=function()return true end,prepare=function(_,s,target,grant)
  assert(s.owned and target==0 and grant:check());return function()assert(grant:check());move(target,false)end
 end}
 local sender={preflight=function()return true end,prepare=function(_,o,peer,s,target,grant)
  assert(peer=='remote!!'and o.owner=='selfpeer')
  return function()if grant then assert(grant:check())end;sends=sends+1 end
 end}
 sender.preflight_all=function(self,o,destinations,s,target)assert(#destinations==1);return self:preflight(o,destinations[1],s,target)end
 sender.prepare_all=function(self,o,destinations,s,target,grant)assert(#destinations==1);return self:prepare(o,destinations[1],s,target,grant)end
 local probe=M.new(adapter,api,snapshot,trace,entrance,tx,sender,function(e)events[#events+1]=e end,function()end)
 return {c=c,probe=probe,held=held,events=events,step=function(key,now)return probe:step(key,now or 10,true)end,
  reply=function()state.status=2;state.chosen=state.target;state.tick=123;c.native.occupied[state.target]=true;c.native.mask=bit.band(c.native.mask,bit.bnot(2^state.target))end,
  transfer=function()c.owner.owner='selfpeer';c.owner.serial=4;c.owner.vehicle.owned_local=true;c.native.owned=true end,
  counts=function()return arm,requests,local_calls,writes,releases,sends end}
end
local owned_count,acquire_count=0,0
for _,name in ipairs({'m102','m103','m104','bastion','maelstrom'})do
 for _,host in ipairs({'installer','friend'})do
  local roles=profiles[name].roles
  for source=0,#roles-1 do for target=0,#roles-1 do if source~=target then
   local f=fixture(name,source,true,host);assert(f.step(target))
   local a,r,l,w,rel,send=f.counts();assert(a==0 and r==0 and l==1 and w==1 and rel==0 and send==1)
   assert(not f.probe.pending and f.c.seat==target and f.c.owner.owner=='selfpeer'and f.c.owner.serial==4)
   owned_count=owned_count+1
  end end end
  for source=1,#roles-1 do
   local f=fixture(name,source,false,host);assert(f.step(0));f.reply();f.step(nil,10.1)
   local a,r,l,w,rel,send=f.counts();assert(a==1 and r==1 and l==0 and w==0 and rel==0 and send==0)
   f.transfer();f.step(nil,10.2);a,r,l,w,rel,send=f.counts();assert(w==1 and rel==1 and send==1 and f.probe.pending)
   f.step(nil,10.3);assert(not f.probe.pending and f.c.seat==0 and f.c.owner.owner=='selfpeer')
   acquire_count=acquire_count+1
  end
 end
end
-- Allow held A/D ONLY for an actual locally owned tank driver exit.
for _,k in ipairs({65,68})do
 local f=fixture('bastion',0,true,'friend');f.held[k]=true;assert(f.step(1))
 f=fixture('m102',0,true,'friend');f.held[k]=true;assert(not pcall(f.step,4));local _,_,_,w=f.counts();assert(w==0)
 f=fixture('bastion',2,false,'friend');f.held[k]=true;assert(not pcall(f.step,0));local _,r,_,w=f.counts();assert(r==0 and w==0)
end
for _,change in ipairs({function(f)f.c.native.occupied[0]=true end,
 function(f)f.c.owner.busy=true end,function(f)f.c.sample.player_count=3 end})do
 local f=fixture('bastion',2,false,'friend');change(f);assert(f.step(0)==false);local a,r,_,w=f.counts();assert(a==0 and r==0 and w==0)
end
for _,change in ipairs({function(f)f.c.owner.owner='unrelated'end,function(f)f.c.owner.serial=5 end,
 function(f)f.c.owner.coordinator='unknown!'end,function(f)f.c.avatar.unit=702 end,
 function(f)f.c.sample.avatars[2].unit=999 end})do
 local f=fixture('bastion',2,false,'friend');assert(f.step(0));f.reply();f.transfer();f.step(nil,10.1)
 -- Move has happened in this fixture; changes must still prevent any second
 -- transaction or release invocation and retain the matching gate on error.
 local _,_,_,before=f.counts();change(f);pcall(f.step,nil,10.2);local _,_,_,after=f.counts();assert(after==before)
end
-- Before first mutation, identity/coordinator/other-player drift stops with
-- zero local calls and zero release. The new driver's serial alone is legal.
for _,change in ipairs({function(f)f.c.owner.owner='unrelated'end,
 function(f)f.c.owner.coordinator='unknown!'end,function(f)f.c.avatar.unit=702 end,
 function(f)f.c.sample.avatars[2].unit=999 end})do
 local f=fixture('bastion',2,false,'friend');assert(f.step(0));f.reply();f.transfer();change(f);pcall(f.step,nil,10.1)
 local _,_,_,w,rel,send=f.counts();assert(w==0 and rel==0 and send==0,'drift allowed precommit mutation')
end
local f=fixture('maelstrom',2,false,'friend');assert(f.step(0));f.reply();f.step(nil,16)
local a,r,_,w,rel,send=f.counts();assert(f.probe.phase=='stopped'and a==1 and r==1 and w==0 and rel==0 and send==0)
print('PASS '..owned_count..' owner-local and '..acquire_count..' empty-driver acquisitions across five models/both host roles; real grant + new owner barrier, exact own source release, held-A/D scope and drift/occupied/timeout refusals')
