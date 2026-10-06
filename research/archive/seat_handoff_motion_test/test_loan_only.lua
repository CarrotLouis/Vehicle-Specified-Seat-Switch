local M=assert(loadfile('work/seat_handoff_motion_test/adapter.lua'))()
local function fixture()
 local function seat(node,role)return {collection=9,current=node,reserved=node,role=role,target=-1,action=-1,transitioning=0,queued_exit=0}end
 local c={identity='v',summary='v',sample={player_count=2,local_count=1},seat=1,
  native={identity='avatar_binding',vehicle='m102',transition=26,profile={roles={1,3,3,3,2}},player_count=2,peer_count=2,owned=false,avatar=7,node=1,active=false,occupied={[0]=true,[1]=true,[4]=false}},
  owner={owner='friend',selfpeer='self',coordinator='friend',members={friend=true,self=true},peer_count=2,busy=false,vehicle={id=9,owned_local=false},avatars={[7]={owner='self'},[8]={owner='friend'}}},
  avatar={id=7,unit=77,is_local=true,owned_local=true,vehicle_input=true,seat=seat(1,3)},driver={id=8,unit=88,is_local=false,seat=seat(0,1)},destination='friend'}
 c.sample.avatars={c.avatar,c.driver}
 local events={};local calls={};local api={input_allowed=function()return true end,down=function()return false end}
 local obs={send=function(_,o,dest,target,hook)calls[#calls+1]='transfer';hook()end,summary=function()return {}end}
 local tx={prepare=function()calls[#calls+1]='prepare';return function()
  calls[#calls+1]='switch';c.seat=4;c.native.node=4;c.avatar.seat=seat(4,2);c.native.occupied[1]=false;c.native.occupied[4]=true
 end end}
 local sender={prepare=function()return function()calls[#calls+1]='sync'end end}
 local trace={active=true,health=function()end}
 local snapshot={current=function()return true end}
 local a=M.new(api,0,{},nil,obs,snapshot,tx,sender,trace,function(e)events[#events+1]=e end,function()return ''end)
 function a:capture()return c end
 local t=a:ticket(c,4)
 local function own()c.native.owned=true;c.owner.vehicle.owned_local=true;c.owner.owner='self'end
 return c,a,t,calls,own,api,tx,snapshot,sender,events,trace
end

local isolate=assert(loadfile('work/seat_handoff_motion_test/ownership_loan_only.lua'))()
local Probe=assert(loadfile('work/seat_handoff_motion_test/probe.lua'))()
local cases=0
local function loan_fixture(host)
 local c,a,_,calls,own,api,tx,snapshot,sender,events,trace=fixture()
 c.owner.coordinator=host or 'friend'
 a=isolate(a,api,snapshot,trace,function(e)events[#events+1]=e end)
 local t=a:ticket(c,4)
 local function returned()c.native.owned=false;c.owner.vehicle.owned_local=false;c.owner.owner='friend'end
 return c,a,t,calls,own,api,snapshot,events,returned,trace
end
for _,host in ipairs({'self','friend'})do
 local c,a,t,calls,own,api,snapshot,events,returned=loan_fixture(host)
 local before=c.native.identity..'/'..c.avatar.seat.current..'/'..c.avatar.seat.role
 a:request(c,t);own();a:execute(c,t)
 assert(t.loan_only_complete and not t.sync_returned and not t.mutation_started)
 assert(table.concat(calls,',')=='transfer','No transaction prepare/mutation, sender or weapon/pose call')
 assert(c.native.identity..'/'..c.avatar.seat.current..'/'..c.avatar.seat.role==before)
 assert(c.seat==1 and c.native.node==1 and c.native.occupied[1] and not c.native.occupied[4])
 assert(a:confirmed(c,t,true))
 assert(not pcall(a.execute,a,c,t),'A completed loan read must never run twice')
 a:return_owned(c,t);assert(t.return_invoked);returned();assert(a:confirmed(c,t,false))
 assert(table.concat(calls,',')=='transfer,transfer')
 local e=events[#events];assert(e.event=='ownership_loan_only_verified'and e.seat==1 and e.seat_mutation==false and e.seat_notifications_sent==0)
 cases=cases+1
end
local invalid={
 function(c)c.sample.player_count=3;c.owner.peer_count=3 end,
 function(c)c.native.vehicle='m104';c.native.transition=28 end,
 function(c)c.native.node=2;c.seat=2;c.avatar.seat.current=2;c.avatar.seat.reserved=2 end,
 function(c)c.driver=nil end,
 function(c)c.driver.is_local=true end,
 function(c)c.driver.seat.target=2 end,
 function(c)c.native.occupied[4]=true end,
 function(c)c.native.occupied[4]=nil end,
 function(c)c.native.active=true end,
 function(c)c.avatar.vehicle_input=false end,
 function(c)c.owner.avatars[8].owner='foreign'end,
 function(c)c.owner.coordinator='foreign'end,
 function(c)c.identity='new_car'end,
 function(c)c.native.identity='respawn'end,
}
for _,change in ipairs(invalid)do
 local c,a,t,calls=loan_fixture();change(c)
 assert(not a:eligible(c,1,false,t,4))
 assert(not pcall(a.request,a,c,t)and #calls==0,'Rejected before ownership call')
 cases=cases+1
end
for _,target in ipairs({0,1,2,3})do
 local c,a,t,calls=loan_fixture();assert(not a:eligible(c,1,false,nil,target))
 assert(not pcall(a.ticket,a,c,target)and #calls==0);cases=cases+1
end
local c,a,t,calls,own=loan_fixture();own()
assert(not a:eligible(c,1,true,nil,4)and not pcall(a.ticket,a,c,4)and #calls==0);cases=cases+1
for _,change in ipairs({
 function(c,a,api,snapshot)c.native.occupied[4]=true end,
 function(c,a,api,snapshot)api.input_allowed=function()return false end end,
 function(c,a,api,snapshot)api.down=function(k)return k==87 end end,
 function(c,a,api,snapshot)snapshot.current=function()return false end end,
 function(c,a,api,snapshot)api.experiment_allowed=function()return false end end,
 function(c,a,api,snapshot)c.sample.player_count=3;c.owner.peer_count=3;c.owner.members.third=true end,
})do
 local c,a,t,calls,own,api,snapshot,events,returned=loan_fixture()
 a:request(c,t);own();change(c,a,api,snapshot)
 assert(not pcall(a.execute,a,c,t)and not t.loan_only_complete and not t.mutation_started and not t.sync_returned)
 a:return_owned(c,t);returned();assert(t.return_invoked and table.concat(calls,',')=='transfer,transfer')
 cases=cases+1
end
-- The real probe keeps its existing late-grant/one-shot return behavior. It
-- confirms the unchanged source and never claims a seat or sync completion.
for _,host in ipairs({'self','friend'})do
 local c,a,t,calls,own,api,snapshot,events,returned=loan_fixture(host)
 local probe=Probe.new(a,function(e)events[#events+1]=e end,function()end,nil,true)
 local now=0
 for repetition=1,2 do
  probe:step(nil,now,true);now=now+.25;assert(probe:step(4,now,true))
  assert(probe.pending);own();now=now+.02;probe:step(nil,now,true)
  assert(c.seat==1 and c.native.node==1 and probe.phase=='awaiting_return')
  now=now+.02;probe:step(nil,now,true);returned()
  now=now+.02;probe:step(nil,now,true);now=now+.51;probe:step(nil,now,true)
  assert(not probe.pending and probe.phase=='waiting_second_trigger')
  local last=events[#events]
  assert(last.event=='integrated_loan_operation_complete'and last.seat==1 and last.requested_target==4 and not last.seat_mutation and last.seat_notifications_sent==0)
  now=now+.4
 end
 assert(table.concat(calls,',')=='transfer,transfer,transfer,transfer');cases=cases+1
end
for _,mode in ipairs({'focus_loss','third_join','late_grant'})do
 local c,a,t,calls,own,api,snapshot,events,returned=loan_fixture()
 local probe=Probe.new(a,function(e)events[#events+1]=e end,function()end,nil,true)
 probe:step(nil,0,true);assert(probe:step(4,.25,true))
 if mode=='third_join'then c.sample.player_count=3;c.owner.peer_count=3;c.owner.members.third=true end
 local when=mode=='late_grant'and 6 or .27
 own();probe:step(nil,when,mode~='focus_loss');probe:step(nil,when+.02,false)
 returned();probe:step(nil,when+.04,false);probe:step(nil,when+.55,false)
 assert(not probe.pending and probe.phase=='stopped'and c.seat==1 and c.native.node==1)
 assert(table.concat(calls,',')=='transfer,transfer')
 for _,e in ipairs(events)do assert(e.event~='ownership_loan_only_verified'and e.event~='integrated_loan_operation_complete')end
 cases=cases+1
end
-- Actual dispatcher consumes the configured cross key without native switch.
-- Original-range requests keep their accepted native path.
local input=assert(loadfile('work/seat_switch/src/input.lua'))()
local policy=assert(loadfile('work/seat_switch/src/policy.lua'))()
local Dispatch=assert(loadfile('work/seat_handoff_motion_test/dispatcher.lua'))()
local c,a,t,calls,own,api,snapshot,events,returned=loan_fixture()
local now=0;local held={};api.now=function()return now end;api.down=function(k)return held[k]or false end
api.focused=api.input_allowed
local keys={m102={driver=112,front=113,rear_left=114,rear_right=115,gunner=116}}
local probe=Probe.new(a,function(e)events[#events+1]=e end,function()end,nil,true)
local native_calls=0;local native={next=function()native_calls=native_calls+1 end,previous=function()native_calls=native_calls+1 end}
local dispatcher=Dispatch.new(api,keys,input,policy,snapshot,native,probe,function(e)events[#events+1]=e end)
snapshot.predictions=function()return 0,0 end
c.native.seaters=123;c.native.avatar_unit=77
for _,dt in ipairs({0,.1,.25})do now=dt;dispatcher:update(c.native)end
held[116]=true;now=.27;dispatcher:update(c.native)
held[116]=nil;now=.3;dispatcher:update(c.native)
assert(probe.pending and #calls==1 and native_calls==0)
own();now=.32;dispatcher:update(c.native);now=.34;dispatcher:update(c.native);returned()
now=.36;dispatcher:update(c.native);now=.9;dispatcher:update(c.native)
assert(not probe.pending and c.seat==1 and native_calls==0 and #calls==2);cases=cases+1
local entry=assert(io.open('work/seat_handoff_motion_test/entry.lua'));local source=entry:read('*a');entry:close()
assert(source:find('adapter=ownership_loan_only',1,true)and source:find('ownership_loan_only=true',1,true))
assert(not source:find('fall_pose:update',1,true),'No background tank pose repair in an isolation package')
assert(source:find('function(...)return adapter:eligible(...)end',1,true),'GUI primary consumption must use isolation scope')
-- A failed physical preflight must stop before any ownership request.
local c,a,t,calls,own,api,snapshot,events,returned=loan_fixture()
a.motion={before_request=function()error('physical_data_missing')end}
assert(not pcall(a.request,a,c,t)and #calls==0 and not t.request_invoked)
cases=cases+1
-- Faulty telemetry after grant must leave the actual one-shot return intact.
local c,a,t,calls,own,api,snapshot,events,returned=loan_fixture()
local phases={};a.motion={before_request=function()end,boundary=function(_,stage)
 phases[#phases+1]=stage;error('telemetry_read_gap')
end}
local probe=Probe.new(a,function(e)events[#events+1]=e end,function()end,nil,true)
probe:step(nil,0,true);assert(probe:step(4,.25,true));own();probe:step(nil,.27,true);probe:step(nil,.3,true)
returned();probe:step(nil,.34,true);probe:step(nil,.9,true)
assert(not probe.pending and c.seat==1 and #calls==2 and probe.phase~='stopped')
assert(table.concat(phases,','):find('first_observed_authority_grant',1,true))
assert(table.concat(phases,','):find('first_observed_authority_return',1,true));cases=cases+1
print('PASS '..cases..' isolation cases: actual adapter/probe/dispatcher, host/guest, repeated no-seat loan, zero mutation/broadcast calls, occupied/scope/context refusal, physical preflight refusal, telemetry-fault return and late/third-join cleanup; live motion remains unverified')
-- Replay the 0.22.0 first-press failure through the actual dispatcher/probe.
-- Observation refusal must consume later chord presses too, with no implicit
-- retry, no native seat action and no loan until a fresh valid observation.
local c,a,t,calls,own,api,snapshot,events,returned=loan_fixture()
local now=0;local ready=false;local waiting_record=false;local pulses=0;local consumed=0
api.now=function()return now end;api.down=function()return false end;api.focused=api.input_allowed
api.control_down=function()return false end
a.motion={before_request=function()
 if not ready then error('mods/vehicle_seat_tools/network_diagnostic.lua:1756: motion_actor_count',0)end
end}
local probe=Probe.new(a,function(e)events[#events+1]=e end,function()end,nil,true)
local gate={active=true,pending=false,failed=false,generation=1}
function gate:pulse(s,observed,keys,enabled)if enabled then pulses=pulses+1 end;assert(enabled,'Preflight refusal must not dearm the input helper')end
function gate:take()
 if not waiting_record then return {},{},{}end
 waiting_record=false;consumed=consumed+1
 return {[1026]=true},{[1026]={count=1,source=1,target=4,generation=1,sequence=consumed}},{}
end
local native_calls=0;local native={next=function()native_calls=native_calls+1 end,previous=function()native_calls=native_calls+1 end}
local keys={m102={driver=112,front=113,rear_left=114,rear_right=115,gunner=1026}}
local dispatcher=Dispatch.new(api,keys,input,policy,snapshot,native,probe,function(e)events[#events+1]=e end,gate)
for _,when in ipairs({0,.1,.25})do now=when;dispatcher:update(c.native)end
for _,when in ipairs({.27,.8})do
 now=when;waiting_record=true;dispatcher:update(c.native)
 assert(not probe.pending and probe.phase=='waiting_second_trigger'and #calls==0 and native_calls==0)
 now=now+.02;dispatcher:update(c.native);assert(#calls==0,'No automatic retry of refused press')
  -- Real frame updates continue between human presses and re-establish the
  -- existing 0.2-second stable-seat guard after a rejected observation.
  now=when+.11;dispatcher:update(c.native);now=when+.32;dispatcher:update(c.native)
end
ready=true;now=1.4;waiting_record=true;dispatcher:update(c.native)
assert(probe.pending and #calls==1 and consumed==3 and native_calls==0)
own();now=1.42;dispatcher:update(c.native);now=1.44;dispatcher:update(c.native);returned()
now=1.46;dispatcher:update(c.native);now=2;dispatcher:update(c.native)
assert(not probe.pending and probe.phase=='waiting_second_trigger'and c.seat==1 and #calls==2 and pulses>5)
local refusals=0;for _,e in ipairs(events)do if e.event=='integrated_physical_preflight_refused'then refusals=refusals+1;assert(e.fresh_press_required and not e.ownership_request_invoked)end end
assert(refusals==2)
-- The new narrow recovery path must refuse all ambiguous or post-invocation
-- failures, including loss of focus/logging and stale identity/occupancy.
local counterexamples={
 function(c,a,t,api)t.request_invoked=true end,
 function(c,a,t,api)t.acquired=true end,
 function(c,a,t,api)t.mutation_started=true end,
 function(c,a,t,api)t.loan_only_complete=true end,
 function(c,a,t,api)t.physical_preflight_refused=false end,
 function(c,a,t,api)api.input_allowed=function()return false end end,
 function(c,a,t,api)api.experiment_allowed=function()return false end end,
 function(c,a,t,api)c.identity='different_car'end,
 function(c,a,t,api)c.owner.owner='self';c.owner.vehicle.owned_local=true end,
 function(c,a,t,api)c.native.occupied[4]=true end,
}
for _,change in ipairs(counterexamples)do
 local c,a,t,calls,own,api,snapshot=loan_fixture();t.physical_preflight_refused=true
 change(c,a,t,api);assert(not a:resume_after_physical_refusal(c,t)and #calls==0)
end
print('PASS captured 0.22.0 refusal replay: two consumed mouse chords stay armed, third fresh valid press completes genuine loan/return; ten unsafe-recovery counterexamples refused')
