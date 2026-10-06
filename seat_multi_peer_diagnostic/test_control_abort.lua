-- Actual input/adapter/probe/gate/dispatcher; OS delivery/native effects mocked.
local root='work/seat_multi_peer_diagnostic/'
local fixture=assert(loadfile(root..'input_race_fixture.lua'))()
local dir=assert(os.getenv('VSS_INPUT_RACE_DIR'))
local profiles=assert(loadfile('work/seat_switch/src/profile.lua'))().tables
local vehicles={'m102','m103','m104','bastion','maelstrom'}
local routes={m102={2,4},m103={1,2},m104={2,0},bastion={1,0},maelstrom={1,0}}
local controls={1,2,4,5,6,32,65,68,69,81,83,87}
local function fresh(name,host,borrowed)
 return fixture('seat_multi_peer_diagnostic',routes[name][1],host,borrowed,dir,'outside',name)
end
local function trigger(f,target)
 local name=f.c.native.vehicle;local binding=f.keys[f.policy.seats[name][target+1]]
 f:press(binding);f:tick();f:enqueue(binding,target);f:tick();return binding
end
local function grant(f)
 f.c.owner.owner='self';f.c.owner.vehicle.owned_local=true;f.c.native.owned=true
end
for _,host in ipairs({'self','friend'})do
 local f=fixture('seat_multi_peer_diagnostic',1,host,true,dir,'outside','maelstrom',
  {adapter='regression_0181_adapter',probe='regression_0181_probe'})
 f.defer_grant=true;trigger(f,0);f.physical[1]=true;grant(f);f:tick()
 for _=1,80 do f:tick()end
 assert(f.probe.phase=='stopped'and f.c.owner.owner=='friend'and f.mutations==0 and f.transfers==2)
 f:release();f:tick(.5);f.c.native.vehicle='tanker';f.c.native.profile=profiles.tanker;f.c.native.transition=33;f.position(0)
 f:press(6);f:tick();f:release();f:tick(.5)
 assert(f.c.seat==0 and f.native_calls==0,'0.18.1 reproduces native tanker input disabled after safe Maelstrom abort')
end
print('PASS 2 frozen0.18.1 Maelstrom grant/control-race/confirmed-return/permanent-stop/tanker-input failure reproductions')
local cases=0
for _,name in ipairs(vehicles)do for _,host in ipairs({'self','friend'})do
 for _,borrowed in ipairs({false,true})do for _,key in ipairs(controls)do
  local f=fresh(name,host,borrowed);f.defer_grant=borrowed;trigger(f,routes[name][2])
  assert(f.probe.pending and f.mutations==0)
  f.physical[key]=true;f.suppressed[key]=nil
  if borrowed then grant(f)end
  f:tick();for _=1,80 do f:tick()end
  assert(not f.probe.pending and f.probe.phase=='waiting_second_trigger')
  assert(f.c.seat==routes[name][1]and f.mutations==0 and f.sends==0)
  assert(f:count('integrated_control_abort')==1 and f:count('integrated_input_abort_recovered')==1)
  assert(f:count('integrated_operation_complete')==0 and f.transfers==(borrowed and 2 or 0))
  assert(f.c.owner.owner==(borrowed and 'friend'or'self'))
  -- A held/cancelled carrier cannot silently retry after recovery.
  for _=1,25 do f:tick()end;assert(f.mutations==0)
  f:release();f:tick(.5);f.defer_grant=false;trigger(f,routes[name][2]);f:tick();f:finish()
  assert(f.mutations==1 and f.sends==1 and f:count('integrated_operation_complete')==1)
  cases=cases+1
 end end
 -- A control change before request/inside the final callback invokes no RPC.
 for _,at in ipairs({'request','validate'})do
  local f=fresh(name,host,true);local target=routes[name][2]
  if at=='request'then
   local original=f.adapter.request
   f.adapter.request=function(self,c,t)f.physical[65]=true;return original(self,c,t)end
  else
   local original=f.owner_reader.send
   f.owner_reader.send=function(...)f.physical[65]=true;return original(...)end
  end
  trigger(f,target);f:finish()
  assert(f.transfers==0 and f.mutations==0 and f.sends==0 and f.c.owner.owner=='friend')
  assert(f:count('integrated_input_abort_recovered')==1)
  cases=cases+1
 end
 -- Only the known input error can resume, and only after verified return.
 for _,fault in ipairs({'friend_unit','occupied','log','partial','no_return_ack'})do
  local f=fresh(name,host,true);f.defer_grant=true;local target=routes[name][2]
  if fault=='partial'then
   local original=f.adapter.execute
   f.adapter.execute=function(self,c,t)t.control_abort=true;return original(self,c,t)end
   f.tx.prepare=function()return function()f.mutations=f.mutations+1;error('partial_native_effect')end end
  end
  trigger(f,target)
  if fault~='partial'then f.physical[65]=true end
  grant(f);f:tick()
  if fault=='friend_unit'then f.friend.unit=999
  elseif fault=='occupied'then f.c.native.occupied[target]=true
  elseif fault=='log'then f.api.experiment_allowed=function()return false end
  elseif fault=='no_return_ack'then
   local original=f.owner_reader.send
   f.owner_reader.send=function(self,o,from,to,hook,options)
    if to=='friend'then f.transfers=f.transfers+1;hook();return end
    return original(self,o,from,to,hook,options)
   end
  end
  for _=1,80 do f:tick()end
  assert(f:count('integrated_input_abort_recovered')==0)
  assert(f.mutations==(fault=='partial'and 1 or 0)and f.sends==0)
  if fault=='no_return_ack'then assert(f.probe.pending and f.c.owner.owner=='self'and f.transfers==2)
  else assert(f.probe.phase=='stopped'and not f.probe.pending and f.c.owner.owner=='friend')end
  cases=cases+1
 end
end end
-- Exact reported Maelstrom acquisition failure followed by native tanker keys.
for _,host in ipairs({'self','friend'})do
 local f=fresh('maelstrom',host,true);f.defer_grant=true;trigger(f,0)
 f.physical[1]=true;grant(f);f:tick();for _=1,80 do f:tick()end
 assert(f:count('integrated_input_abort_recovered')==1 and f.mutations==0 and f.c.owner.owner=='friend')
 f:release();f:tick(.5)
 f.c.native.vehicle='tanker';f.c.native.profile=profiles.tanker;f.c.native.transition=33
 f.c.owner.vehicle.name='tanker';f.c.owner.vehicle.transition_type=33;f.c.owner.vehicle.seat_count=2
 f.position(0);f.keys={driver=5,gunner=6};f:tick(.5)
 for _,target in ipairs({1,0})do
  local binding=target==0 and 5 or 6;f:press(binding);f:tick();f:release();f:tick(.5)
  assert(f.c.seat==target and not f.probe.pending)
 end
 assert(f.native_calls==2 and f.mutations==0 and f.transfers==2)
 cases=cases+1
end
print('PASS '..cases..' real control-abort recovery cases: five models/both hosts/local-borrowed/all12 guarded controls; pre-request/final-callback/grant races; zero writes, exact return, fresh press only, partial/log/identity/occupied/unconfirmed return stays blocked; Maelstrom abort then native tanker')
