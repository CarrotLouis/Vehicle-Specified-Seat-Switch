local factory=assert(loadfile('work/seat_handoff_motion_test/motion_watch.lua'))()
local encode=assert(loadfile('work/seat_network_diagnostic/recorder.lua'))().encode
local now,reads=0,0;local events={};local reader={peers={self='P1',friend='P2',third='P3'}}
local api={now=function()return now end,replace=function()error('No writes')end}
local v={id=9,unit=99,network_unit=909,name='m102',resource='car',owned_local=false}
local seat=function(node,role)return {collection=9,current=node,reserved=node,role=role,target=-1,action=-1,transitioning=0,queued_exit=0}end
local s={state='mission',mission_value=1,player_count=3,peer_count=3,vehicles={v},avatars={
 {id=7,is_local=true,seat=seat(1,3)},{id=8,unit=88,network_unit=808,is_local=false,seat=seat(0,1)}}}
local driver={read_vehicle=function(self,x)assert(x==v);reads=reads+1;if self.fail then error('bounded read gap')end
 return {command_floats_offset_00_to_28={1,0,0,0,0,0,0,0,1,0,0},driver_active=1,driver_command_hex='fixture'}end}
local probe={count=0,phase='waiting',pending=false,observed_at=0,observed={owner={vehicle=v,owner='friend',selfpeer='self',coordinator='third',serial=4,busy=false}}}
local watch=factory(api,reader,driver,function(e)events[#events+1]=e end)
local before=encode(s)
for i=1,5 do now=i*.1;watch:update(s,probe)end
assert(#events==0 and reads==5)
probe.count=1;probe.pending=true;probe.phase='awaiting_acquire';now=.6;watch:update(s,probe)
assert(events[1].event=='motion_watch_started'and #events[1].pre_samples==5 and events[2].event=='motion_watch_sample')
assert(events[2].last_probe_owner.owner=='P2'and events[2].last_probe_owner.coordinator=='P3'and encode(s)==before)
probe.phase='awaiting_return';v.owned_local=true;s.avatars[1].seat=seat(4,2);now=.7;watch:update(s,probe)
assert(events[#events].owned_local and events[#events].local_seat.current==4 and driver.read_vehicle)
driver.fail=true;now=.8;watch:update(s,probe);assert(events[#events].event=='motion_watch_gap')
assert(probe.pending and probe.phase=='awaiting_return','A telemetry gap must not cancel or write a transaction')
driver.fail=false;probe.pending=false;v.owned_local=false;now=3;watch:update(s,probe);assert(events[#events].event=='motion_watch_ended')
local n=#events;now=3.1;watch:update(s,probe);assert(#events==n)
s.avatars[1].seat=seat(2,3);now=3.2;watch:update(s,probe);assert(events[#events-1].trigger=='native_or_untracked_seat_change')
s.avatars[2].seat.current=4;now=3.3;watch:update(s,probe);assert(events[#events].reason=='remote_driver_missing')
print('PASS read-only moving-car command windows: five pre-samples, request/seat triggers, owner handoff/return and both roles, bounded gap isolation, timeout/driver leave; inputs never labelled as speed; no send/write')
local c={owner={vehicle=v,owner='friend',serial=9},driver=s.avatars[2],avatar=s.avatars[1]}
local t={source=1,target=4,identity='same-car/'..string.char(0x80,0xff,0)};driver.fail=false
watch:boundary('before_seat_mutation',c,t)
assert(events[#events].event=='motion_boundary'and events[#events].stage=='before_seat_mutation'and events[#events].snapshot_owner=='P2')
assert(not encode(events[#events]):find('[\128-\255]')and events[#events].operation_identity_hex:find('80ff00',1,true))
driver.fail=true;watch:boundary('before_authority_return',c,t)
assert(events[#events].event=='motion_boundary_gap'and probe.pending==false,'Read gap must not touch transaction')
c.driver.is_local=true;local before=#events;watch:boundary('irrelevant',c,t);assert(#events==before)
print('PASS transaction-boundary command reads cover short loans between background samples; read gaps remain isolated, own driver excluded')
