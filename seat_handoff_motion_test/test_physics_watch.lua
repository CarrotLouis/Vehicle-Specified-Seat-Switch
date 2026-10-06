local factory=assert(loadfile('work/seat_handoff_motion_test/physics_watch.lua'))()
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
local gaps={};now=0
local missing={last_read={actor_count=0,unit_flags=0x40000000,unit_record_hex=string.rep('00',24)},read_vehicle=function()error('count zero',0)end}
local watch=factory(api,reader,missing,nil,function(e)gaps[#gaps+1]=e end)
for i=1,8 do now=i/10;watch:update(sample,probe)end
assert(#gaps==1 and gaps[1].layout.actor_count==0 and #gaps[1].layout.unit_record_hex==48)
assert(not pcall(watch.before_request,watch,c,t));assert(#gaps==2 and gaps[2].stage=='request_preflight')
assert(not pcall(watch.before_request,watch,c,t));assert(#gaps==3,'Every explicit preflight refusal stays visible')
now=1;watch:update(sample,probe);now=2.1;watch:update(sample,probe)
assert(#gaps==5 and gaps[5].stage=='background')
watch:boundary('before_authority_return',c,t);assert(#gaps==6 and gaps[6].stage=='before_authority_return')
print('PASS bounded failed-layout metadata, background gap rate and unthrottled request/return boundary evidence')
local property_reads,property_bad=0,false
local handoff={last_read={read_count=0},read_vehicle=function(_,vehicle,owner)
 assert(vehicle==v and owner==c.owner);property_reads=property_reads+1
 if property_bad then error('synthetic property schema fault')end
 return {read_only=true,properties={linear_velocity={serializer_source='raw_engine'}},read_count=25}
end}
events={};now=0;sample.mission_value=2;probe.count=0
local property_watch=factory(api,reader,physics,nil,function(e)events[#events+1]=e end,handoff)
for i=1,12 do now=i/10;property_watch:update(sample,probe)end
assert(property_reads==0,'no expensive property collection in idle ring')
property_watch:before_request(c,t);assert(property_reads==1 and events[#events].handoff_properties.read_count==25)
probe.count=1;now=1.3;property_watch:update(sample,probe)
now=1.4;property_watch:update(sample,probe);assert(property_reads==2,'only short active window')
assert(events[#events].handoff_properties.read_start_ms==1400)
now=4;property_watch:update(sample,probe);assert(property_reads==2,'window expires')
property_bad=true;property_watch:boundary('before_authority_return',c,t)
assert(events[#events].event=='physics_motion_sample'and not events[#events].handoff_properties,'property fault contains no loan failure')
assert(events[#events-1].event=='handoff_property_gap')
assert(pcall(property_watch.before_request,property_watch,c,t),'optional property telemetry never refuses a new loan')
sample.player_count=3;now=5;property_watch:update(sample,probe)
local previous=property_reads;now=5.1;property_watch:update(sample,probe);assert(property_reads==previous)
print('PASS optional handoff properties restricted to exact boundaries/short windows; idle and third-player gating; telemetry errors preserve original preflight/return behavior')
