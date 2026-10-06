local fixture=assert(loadfile('work/seat_multi_vehicle_test/input_race_fixture.lua'))()
local replay=assert(loadfile('work/seat_multi_vehicle_test/input_race_replay.lua'))()
local dir=assert(os.getenv('VSS_INPUT_RACE_DIR'))
local NEW,OLD='seat_multi_vehicle_test','seat_aboard_passenger_test'
local cases=0
-- Every captured poll-before-GUI cancellation: preserve real frame separation.
for _,row in ipairs(replay)do for _,version in ipairs({OLD,NEW})do
 local f=fixture(version,row.source,row.host,false,dir)
 f:press(row.binding);f:tick();assert(f.dispatcher.queued and not f.probe.pending)
 f:enqueue(row.binding,row.target,{tick=math.floor((f.now+row.delay_ms/1000)*1000)})
 f:tick(row.delay_ms/1000)
 if version==OLD then
  assert(not f.probe.pending and not f.dispatcher.queued and f:count('seat_input','cancelled_by_new_key')==1,'old version must reproduce captured lost intent')
 else
  assert(f.probe.pending and not f.dispatcher.queued and f:count('seat_input','matched_native_press')==1)
  f:tick();assert(f.mutations==1 and f.sends==1 and f.c.seat==row.target)
  f:finish();assert(f:count('integrated_operation_complete')==1 and f.transfers==0)
  assert(f:count('seat_input','cancelled_by_new_key')==0)
 end
 cases=cases+1
end end
-- Actual poller + gate metadata, held/tapped primary, both authority paths,
-- both host identities and one/two-frame arrival order. No same-frame shortcut.
for _,host in ipairs({'self','friend'})do for _,borrowed in ipairs({false,true})do
 for _,tap in ipairs({false,true})do for _,frames in ipairs({1,2})do
  local f=fixture(NEW,4,host,borrowed,dir)
  f:press(1114);f:tick();assert(f.dispatcher.queued and not f.probe.pending)
  for _=2,frames do f:tick();assert(not f.probe.pending)end
  if tap then f:release()end
  f:enqueue(1114,2);f:tick();assert(f.probe.pending and not f.dispatcher.queued)
  f:tick();assert(f.mutations==1 and f.sends==1 and f.c.seat==2)
  f:finish();assert(f.mutations==1 and f.sends==1 and f.transfers==(borrowed and 2 or 0))
  assert(f.friend.seat.current==(borrowed and 0 or 1))
  cases=cases+1
 end end
end end
-- A distinct key or genuinely new same-key physical edge still cancels.
for _,fault in ipairs({'different_key','repress','two_native_edges','too_late','generation','old_record','future_record','wrong_source','wrong_target','identity','source','occupied','focus','movement'})do
 local f=fixture(NEW,4,'friend',false,dir)
 f:press(1114);f:tick();assert(f.dispatcher.queued)
 if fault=='different_key'then f:press(1112);f:enqueue(1112,3)
 elseif fault=='repress'then f:release();f.physical[87]=true;f:tick();f:press(1114);f:enqueue(1114,2)
 elseif fault=='two_native_edges'then f:enqueue(1114,2);f:enqueue(1114,2)
 elseif fault=='too_late'then f:tick(.26);f:enqueue(1114,2)
 elseif fault=='generation'then f:enqueue(1114,2,{generation=f.armed.generation-1})
 elseif fault=='old_record'then f:enqueue(1114,2,{tick=math.floor((f.now-.3)*1000)})
 elseif fault=='future_record'then f:enqueue(1114,2,{tick=math.floor((f.now+.1)*1000)})
 elseif fault=='wrong_source'then f:enqueue(1114,2,{source=3})
 elseif fault=='wrong_target'then f:enqueue(1114,3)
 elseif fault=='identity'then f:enqueue(1114,2);f.c.native.identity='new-vehicle'
 elseif fault=='source'then f:enqueue(1114,2);f.c.native.node=3
 elseif fault=='occupied'then f:enqueue(1114,2);f.c.native.occupied[2]=true
 elseif fault=='focus'then f:enqueue(1114,2);f.focused=false
 else f.physical[87]=true;f:enqueue(1114,2)end
 f:tick()
 assert(not f.probe.pending and f.mutations==0 and f.transfers==0,fault..' must never request authority or mutate')
 if fault=='movement'then
  assert(f.dispatcher.queued);f.physical[87]=nil;f:tick();assert(f.probe.pending)
  f:tick();f:finish();assert(f.mutations==1)
 else assert(not f.dispatcher.queued,fault..' must clear the pending intent')end
 cases=cases+1
end
-- Recorded friend action20: remain strict, retain request, then execute once
-- after fresh settled state. Old version drops it before retrying.
for _,host in ipairs({'self','friend'})do for _,version in ipairs({OLD,NEW})do
 local f=fixture(version,4,host,false,dir)
 local rs=f.friend.seat;rs.action=20;rs.target=1;rs.transitioning=1
 f:tick(.12);assert(not f.armed.items[2],'transitional friend must not arm a native mutation')
 f:press(1114);f:tick();f:release();f:tick()
 assert(not f.probe.pending and f.mutations==0)
 if version==NEW then
  assert(f.dispatcher.queued and f.dispatcher.queued.deferred and f:count('seat_input','waiting_friend_retract')==1)
 else assert(not f.dispatcher.queued)end
 rs.action=-1;rs.target=-1;rs.transitioning=0;f:tick(.12)
 if version==NEW then
  assert(f.probe.pending and not f.dispatcher.queued);f:tick();f:finish()
  assert(f.c.seat==2 and f.mutations==1 and f.transfers==0 and rs.current==1)
 else assert(not f.probe.pending and f.mutations==0)end
 cases=cases+1
end end
-- Retraction timeout and context/vacancy changes cannot silently broaden scope.
for _,fault in ipairs({'timeout','unit','friend_seat','friend_exit','owner','host','occupied','reserved','action','queued_exit'})do
 local f=fixture(NEW,4,'friend',false,dir);local rs=f.friend.seat
 rs.action=20;rs.target=1;rs.transitioning=1;f:tick(.12)
 f:press(1114);f:tick();f:release();f:tick();assert(f.dispatcher.queued)
 if fault=='timeout'then f:tick(1.1)
 else
  rs.action=-1;rs.target=-1;rs.transitioning=0
  if fault=='unit'then f.friend.unit=99
  elseif fault=='friend_seat'then rs.current=3;rs.reserved=3;f.c.native.occupied[3]=true
  elseif fault=='friend_exit'then rs.collection=-1;f.c.native.occupied[1]=false
  elseif fault=='owner'then f.c.owner.owner='friend';f.c.owner.vehicle.owned_local=false;f.c.native.owned=false
  elseif fault=='host'then f.c.owner.coordinator='self'
  elseif fault=='occupied'then f.c.native.occupied[2]=true
  elseif fault=='reserved'then rs.reserved=2
  elseif fault=='action'then rs.action=17
  elseif fault=='queued_exit'then rs.queued_exit=1 end
  f:tick(.12)
  assert(not f.probe.pending and f.mutations==0,'changed context must not mutate while stability resets')
  if f.dispatcher.queued then f:tick(.25)end
 end
 assert(not f.dispatcher.queued and not f.probe.pending and f.mutations==0 and f.sends==0 and f.transfers==0,fault..' must cancel deferred input')
 cases=cases+1
end
print('PASS '..cases..' input-race cases: captured old cancellations reproduced; delayed GUI/physical press matched once; hold/tap and both authority paths; fresh token/control/context guards; strict bounded friend retraction retry')
