local factory=assert(loadfile('work/seat_physics_motion_test/physics_watch.lua'))()
local now,failed,reads=0,false,0;local events={};local api={now=function()return now end}
local reader={peers={self='P1',friend='P2'}}
local physics={read_vehicle=function(_,v)
 reads=reads+1;if failed then error('invalid actor')end
 return {actor_handle=5,physical_position={now*10,0,0},native_speed=10,linear_velocity={10,0,0},read_only=true}
end}
local v={id=9,unit=22,resource='car',name='m102'}
local c={owner={vehicle=v,owner='friend',selfpeer='self',coordinator='self',serial=2},seat=1}
local t={identity='id',source=1,target=4}
local sample={state='mission',mission_value=2,player_count=2,peer_count=2,vehicles={v},avatars={{is_local=true,seat={current=1,collection=9}}}}
local probe={observed=c,count=0};local watch=factory(api,reader,physics,nil,function(e)events[#events+1]=e end)
for i=1,12 do now=i/10;watch:update(sample,probe)end
watch:before_request(c,t);assert(events[#events].stage=='request_preflight')
probe.count=1;now=1.3;watch:update(sample,probe)
assert(events[#events-1].event=='physics_motion_window'and #events[#events-1].pre_samples==10)
assert(math.abs(events[#events].position_delta_native_per_second-10)<.001)
for _,stage in ipairs({'before_authority_request','first_observed_authority_grant','ownership_loan_only_check','before_authority_return','first_observed_authority_return'})do
 now=now+.02;watch:boundary(stage,c,t);assert(events[#events].stage==stage and events[#events].actual_seat==1)
end
failed=true;assert(not pcall(watch.before_request,watch,c,t),'Missing physics data refuses a new loan')
assert(events[#events].event=='physics_motion_gap')
watch:boundary('first_observed_authority_return',c,t);assert(events[#events].event=='physics_motion_gap','Return telemetry failure is contained')
failed=false;sample.mission_value=3;now=5;watch:update(sample,probe)
assert(not events[#events].position_delta_seconds or events[#events].position_delta_seconds<=1)
print('PASS motion boundaries, bounded pre/post windows, physical displacement comparison and preflight gap refusal')
