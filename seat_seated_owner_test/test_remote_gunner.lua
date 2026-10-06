-- Only own engine/RPC effects are mocked; use actual input and operation modules.
local fixture=assert(loadfile('work/seat_seated_owner_test/input_race_fixture.lua'))()
local dir=assert(os.getenv('VSS_INPUT_RACE_DIR'));local NEW='seat_seated_owner_test';local cases=0
local function gunner_unchanged(f,seat)
 assert(f.friend.id==8 and f.friend.unit==88 and f.friend.seat==seat and seat.current==4 and seat.reserved==4 and seat.role==2)
 assert(f.c.owner.avatars[8].owner=='friend'and f.c.native.occupied[4])
end
-- Every vacant source/target pair while an unmodded friend remains gunner.
for _,host in ipairs({'self','friend'})do for source=0,3 do for target=0,3 do
 if source~=target then
  local f=fixture(NEW,source,host,false,dir,4);local a,c=f.adapter,f.c
  local t=a:ticket(c,target);local held=f.friend.seat
  assert(a:eligible(c,source,true,t,target));assert(t.remote_node==4 and t.remote_unit==88)
  a:execute(c,t);assert(t.sync_returned and c.seat==target and f.mutations==1 and f.sends==1 and f.transfers==0)
  assert(a:confirmed(c,t,true));gunner_unchanged(f,held);cases=cases+1
 end
end end end
-- Compare old scope refusal, using the real old adapter before the new extension.
local old=assert(loadfile('work/seat_input_race_fix/adapter.lua'))()
local f=fixture(NEW,0,'friend',false,dir,4)
assert(not old.eligible(f.c,0,true,nil,2)and f.adapter:eligible(f.c,0,true,nil,2));cases=cases+1
-- Held key reaches this new context through poll-first/GUI-later input ordering.
for _,host in ipairs({'self','friend'})do
 local f=fixture(NEW,0,host,false,dir,4);local held=f.friend.seat
 for _,step in ipairs({{2,1114},{1,90},{3,1112},{0,88}})do
  f:press(step[2]);f:tick();assert(f.dispatcher.queued and not f.probe.pending)
  f:enqueue(step[2],step[1]);f:tick();assert(f.probe.pending and not f.dispatcher.queued)
  f:tick();assert(f.c.seat==step[1]);f:finish();gunner_unchanged(f,held)
  f:release();f:tick(.5)
 end
 assert(f.mutations==4 and f.sends==4 and f.transfers==0 and f:count('integrated_operation_complete')==4)
 f:press(1026);f:tick();assert(f.c.seat==0 and not f.probe.pending and not f.dispatcher.queued,'occupied gunner refuses')
 assert(f.mutations==4 and f.transfers==0);gunner_unchanged(f,held);cases=cases+1
end
-- Fresh guards must prevent moving the original gunner or taking their seat.
for _,change in ipairs({
 function(f)f.friend.unit=99 end,function(f)f.friend.id=99 end,
 function(f)f.friend.seat.current=3;f.friend.seat.reserved=3;f.friend.seat.role=3;f.c.native.occupied[3]=true end,
 function(f)f.friend.seat.collection=-1 end,function(f)f.friend.seat.role=3 end,
 function(f)f.friend.seat.reserved=2 end,function(f)f.friend.seat.target=2 end,
 function(f)f.friend.seat.action=20;f.friend.seat.target=4;f.friend.seat.transitioning=1 end,
 function(f)f.friend.seat.role=3;f.friend.seat.action=20;f.friend.seat.target=4;f.friend.seat.transitioning=1 end,
 function(f)f.friend.seat.transitioning=1 end,function(f)f.friend.seat.queued_exit=1 end,
 function(f)f.c.owner.avatars[8].owner='self'end,function(f)f.c.native.occupied[4]=false end,
 function(f)f.c.native.occupied[2]=true end,function(f)f.c.native.occupied[2]=nil end,
 function(f)f.c.owner.busy=true end,function(f)f.c.owner.owner='friend'end,
 function(f)f.c.sample.player_count=3 end,function(f)f.c.owner.coordinator='new-host'end
})do
 local f=fixture(NEW,0,'friend',false,dir,4);local t=f.adapter:ticket(f.c,2);change(f)
 local ready,_,retry=f.adapter:eligible(f.c,0,true,t,2)
 assert(not ready and not retry,'arbitrary gunner transitions must never be treated as passenger retraction')
 assert(not pcall(f.adapter.execute,f.adapter,f.c,t)and not t.mutation_started and f.mutations==0 and f.sends==0 and f.transfers==0)
 cases=cases+1
end
-- State changes after preparation and before the final fresh guard are caught.
for _,change in ipairs({
 function(f)f.friend.unit=99 end,function(f)f.friend.seat.queued_exit=1 end,
 function(f)f.friend.seat.role=3 end,function(f)f.c.native.occupied[2]=true end
})do
 local f=fixture(NEW,0,'self',false,dir,4);local t=f.adapter:ticket(f.c,2);local prepare=f.tx.prepare
 f.tx.prepare=function(...)local perform=prepare(...);change(f);return perform end
 assert(not pcall(f.adapter.execute,f.adapter,f.c,t)and not t.mutation_started and f.mutations==0 and f.sends==0 and f.transfers==0)
 cases=cases+1
end
print('PASS '..cases..' remote-gunner context cases: both host roles/all own non-gunner pairs; held/delayed four-step real input; no authority transfer; remote seat/identity retained; occupied gunner and fresh transition/preparation races refuse')
