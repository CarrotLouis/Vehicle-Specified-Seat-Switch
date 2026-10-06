-- Actual consumed-input/gate/dispatcher/adapter/probe paths. Native effects
-- and network delivery simulated; does not prove the physical tank stops.
local root='work/seat_fleet_test/'
local fixture=assert(loadfile(root..'input_race_fixture.lua'))()
local dir=assert(os.getenv('VSS_INPUT_RACE_DIR'))
local M=assert(loadfile(root..'adapter.lua'))()
local f=assert(io.open(root..'entry.lua'));local source=f:read('*a');f:close()
local definition=assert(source:match('api.tank_driver_exit_allowed=(function%(s%).-\n end)'))
local permission=assert(loadstring('return '..definition));setfenv(permission,{p={functions={tank_driver_active={}}},sync_adapter=M})
local allowed=permission();local cases=0
for _,name in ipairs({'bastion','maelstrom'})do for _,host in ipairs({'self','friend'})do
 for _,key in ipairs({65,68})do for target=1,3 do for _,tap in ipairs({false,true})do
  local x=fixture('seat_fleet_test',0,host,false,dir,'outside',name);x.api.tank_driver_exit_allowed=allowed
  local binding=x.keys[x.policy.seats[name][target+1]]
  x.physical[key]=true;x:press(binding);x:tick()
  if tap then x.physical[binding%256]=nil end
  x:enqueue(binding,target);x:tick();x:finish()
  assert(x.mutations==1 and x.sends==1 and x.transfers==0 and x.c.seat==target and x.c.owner.owner=='self')
  assert(x:count('integrated_control_abort')==0 and x.physical[key]and x.friend.seat.collection==0)
  cases=cases+1
 end end end
 -- The old dispatcher ignores the new permission and keeps waiting while A/D
 -- is held. Preserve this observed input-level difference separately from
 -- the earlier, user-reported physical steering latch.
 local x=fixture('seat_fleet_test',0,host,false,dir,'outside',name,
  {adapter='regression_0182_adapter',dispatcher='regression_0182_dispatcher'})
 x.api.tank_driver_exit_allowed=allowed;x.physical[65]=true
 local binding=x.keys.passenger_left;x:press(binding);x:tick();x:enqueue(binding,2);x:tick()
 for _=1,50 do x:tick()end
 assert(x.mutations==0 and x.dispatcher.queued and not x.probe.pending)
end end
for _,name in ipairs({'bastion','maelstrom'})do
 for _,key in ipairs({1,2,4,5,6,32,69,81,83,87})do
  local x=fixture('seat_fleet_test',0,'friend',false,dir,'outside',name);x.api.tank_driver_exit_allowed=allowed
  local binding=x.keys.passenger_left;x.physical[key]=true;x:press(binding);x:tick();x:enqueue(binding,2);x:tick()
  for _=1,25 do x:tick()end
  assert(x.mutations==0 and not x.probe.pending)
  cases=cases+1
 end
 for _,change in ipairs({function(s)s.owned=false end,function(s)s.node=2 end,function(s)s.transition=99 end,
  function(s)s.player_count=3 end,function(s)s.peer_count=3 end,function(s)s.active=true end})do
  local x=fixture('seat_fleet_test',0,'self',false,dir,'outside',name);change(x.c.native)
  assert(not allowed(x.c.native));cases=cases+1
 end
end
local x=fixture('seat_fleet_test',0,'self',false,dir,'outside','m102');assert(not allowed(x.c.native))
print('PASS '..cases..' actual steering input cases: both tanks/both hosts/all3 exits/held-tap/A-D; zero ownership transfer; other controls/roles/ownership/layout/count refused; four frozen old wait reproductions. Native motion mocked.')
