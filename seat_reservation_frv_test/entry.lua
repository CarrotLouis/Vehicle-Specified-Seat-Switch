local tag='VehicleSeatNetworkDiagnostic'
if rawget(_G,tag)then return end
local state={version='0.27.0',status='starting',passive=false,native_hooks=false,data_hooks=true}
rawset(_G,tag,state)
local loader=rawget(_G,'CowboyBingusModLoader')
local previous,previous_shutdown=update,shutdown
local frames,started,trace_started=0,false,false
local api,game,resolver,reader,writer,statusfile,trace,probe,owner_reader,dispatcher,resolved_profile
local animation,input_priority,fall_pose
local fleet_observer,steering_observer,motion_observer
local pose_calls
local next_poll,next_sample,next_probe,last_preflight=0,0,0,nil
local function status(value)
 if state.status==value then return end
 state.status=value
 if statusfile then
  local ok=pcall(function()assert(statusfile:write(value..'\n'));statusfile:flush()end)
  if not ok then state.logging_failed=true end
 end
end
local function emit(e)
 if not writer or writer.closed then state.logging_failed=true;return end
 local ok=pcall(function()assert(writer:write(e,api.now()));writer.file:flush()end)
 if not ok then state.logging_failed=true end
end
local function init()
 assert(loader and loader.api==1 and loader.version>=16,'Bingus_Shared_Loader_v16_required')
 statusfile=assert(loader.open_log('VehicleSeatIntegratedDiagnostic.log'))
 api=pages(platform(module_hash));game=assert(api.module('game.dll'))
 resolver=compat.start(api,game,profile,compat_spec,'enhanced',status)
 status('checking_interfaces')
end
local function finish_init(p)
 assert(p.capabilities and p.capabilities.enhanced,'sync_enhanced_interfaces_unavailable '..tostring(p.capabilities and p.capabilities.enhanced_reason))
 resolved_profile=p
 local text;local base=os.getenv('APPDATA')
 local f=base and io.open(base..'/Arrowhead/Helldivers2/VehicleSeatSwitch.ini','rb')
 if f then text=f:read(131073);f:close();assert(text and #text<=131072,'config_too_large')end
 local keys,issues=config.parse(text)
 local now=api.now();state.filename='VehicleSeatIntegrated-'..os.date('%Y%m%d-%H%M%S')..'-'..api.pid()..'-'..math.floor(now*1000)..'.log'
 writer=recorder.new(assert(loader.open_log(state.filename)),now)
 -- Keep a pending reply gate alive if its evidence log fails.
 local raw_write=writer.write
 function writer:write(event,time)
  if self.closed then return false end
  local ok,result=pcall(raw_write,self,event,time)
  if not ok then
   state.logging_failed=true;self.closed=true;pcall(self.file.close,self.file)
   return false
  end
  return result
 end
 api.experiment_allowed=function()return not writer.closed and not state.logging_failed and not(animation and animation.failed)and not(input_priority and input_priority.failed)end
 local ok,digest=pcall(api.hash_module,game)
 emit({event='start',version=state.version,loader=loader.version,compatibility=p.compatibility,schema=p.layout_schema,
  game_sha256=ok and digest or 'unavailable',key_issues=#issues,config_issues=issues,settle_seconds=.2,post_complete_cooldown_seconds=.35,input_priority='own_window_messages',
  scope='two_player_frv_remote_driver_non_driver_owner_reservation; no_chassis_loan',network_packets_captured=false,
  multi_peer_cross_switch_enabled=false,multi_peer_live_validation_pending=true,fleet_observation_read_only=false,
  physical_motion_observation=true,physical_motion_short_windows_only=true,physical_motion_scope='m102_only',native_actor_read_api_calls=true,ownership_loan_only=false,chassis_authority_requested=false,cross_region_seat_mutation_enabled=true,seat_notifications_enabled=true,physics_writes_enabled=false,
  handoff_property_observation=true,handoff_properties_read_only=true,handoff_property_windows_only=true,
  downstream_steering_observation=false,
  native_motion_call_observation=false,exact_own_pending_accepted_gate=true,mounted_weapon_authority_barrier=true,
  moving_hitch_unresolved=true,tank_spin_unresolved=true})
 reader=sampler.new(api,game,p)
 trace=transport(api,game,p,loader,writer,reader,observer,routing.new(api,game,p,messages),messages,helper)
 owner_reader=authority_observe.new(api,game,p,compat_spec,compat,reader,trace)
 local physical_reader=motion_tools.physics_reader(api,game,p,compat)
 local property_reader=motion_tools.handoff_reader(api,game,p,compat)
 motion_observer=reservation_tools.motion_watch(api,reader,physical_reader,property_reader,emit,reservation_tools.scope)
 animation=animation_watch(api,p,emit)
 local function observed_pose(a,profile_)
  local base_pose=pose(a,profile_)
  return {check=function(s)
   local result=base_pose.check(s);animation:arm(s);return result
  end,apply=function(s,target)
   animation:sample('before_pose_apply')
   local result=base_pose.apply(s,target)
   animation:sample('after_pose_apply');return result
  end}
 end
 local local_switch=transaction(api,game,p,observed_pose,personal,emit,reservation_tools.scope)
 local inspector=animation_inspect.new(api,game,p,routing.new(api,game,p,{[0xbde53653]='animation_event'}))
 local anim_send=animation_sender(api,game,p,compat_spec,compat,inspector,trace,sync_adapter.layout)
 local weapon_inspector=binding_inspect.new(api,game,p)
 local weapon_route=routing.new(api,game,p,{[0x423a4034]='weapon_channel_clear',[0x2671dec5]='weapon_channel_bind'})
 local weapon_send=binding_sender(api,game,p,compat_spec,compat,weapon_inspector,weapon_route,trace,personal,sync_adapter.layout)
 local send=sender(api,game,p,compat_spec,compat,trace,anim_send,weapon_send,sync_adapter.layout)
 local adapter=sync_adapter.new(api,game,p,reader,owner_reader,snapshot,local_switch,send,trace,emit,recorder.encode)
 adapter.motion=motion_observer
 adapter.mounted=reservation_tools.mounted_reader(api,game,p,compat_spec,compat,weapon_inspector,reservation_tools.scope,emit)
 function adapter:eligible(c,source,owned,ticket,target)
  return reservation_tools.probe.eligible(c,source,owned,ticket,target)
 end
 local reserve_entry=reservation_tools.entrance(api,game,p,compat_spec,compat,trace,emit)
 probe=reservation_tools.probe.new(adapter,api,snapshot,trace,reserve_entry,local_switch,send,emit,
  function(label)state.probe_status=label;status(label..' '..state.filename)end)
 local normal_native=bind_native(api,game,p,nil,nil,nil,'normal')
 input_priority=input_gate(api,loader,input_helper,policy,snapshot,function(...)return adapter:eligible(...)end,emit)
 api.control_down=function(key)return input_priority:control_down(key)end
 api.tank_driver_exit_allowed=function(s)
  local d=sync_adapter.layout(s)
  return p.functions.tank_driver_active and d and d.tank and s.node==0 and s.owned and not s.active and s.player_count>=2 and s.player_count<=4 and s.peer_count==s.player_count
 end
 dispatcher=seat_dispatcher.new(api,keys,input,policy,snapshot,normal_native,probe,emit,input_priority)
 status('waiting_for_transport '..state.filename)
end
local function step()
 frames=frames+1;if frames<180 then return end
 if not started then started=true;init()end
 if resolver then local p,why=resolver.step();if not p then return end;resolver=nil;finish_init(p)end
 if not writer then return end
 if pose_calls then pose_calls:update()end
 if writer.closed or state.logging_failed then
  if probe and probe.pending then probe:cancel('log_unavailable; reservation_cancelled')
  else if pose_calls then pcall(pose_calls.close,pose_calls,'log_closed')end;if trace and trace.active then trace:stop('log_closed')end;status('log_closed_experiment_disabled');return end
 end
 assert(not rawget(_G,'VehicleSeatSwitch'),'disable_gameplay_companion_for_standalone_test')
 assert(not rawget(_G,'Hd2TankSeatSwitch')and not rawget(_G,'Hd2TankSeatRoles'),'disable_TankSeatKit_before_testing')
 if trace and not trace_started and frames>=600 then
  local ok,s=pcall(reader.capture,reader)
  if not ok or not s or s.state~='not_in_mission'then status('waiting_for_ship_before_protocol');return end
  trace_started=true;trace:start();state.transport_ready=true
  status('transport_ready '..state.filename)
 end
 if not trace or not trace.active then return end
 trace:health();trace:drain()
 local now=api.now();if now<next_poll then return end;next_poll=now+.016
 local focused=api.input_allowed()
 if animation.failed and probe.pending then probe:cancel('animation_read_gap; reservation_cancelled')end
 if input_priority.failed and probe.pending then probe:cancel('input_priority_failed; reservation_cancelled')end
 if now>=next_sample and not writer.closed and not state.logging_failed then
  next_sample=now+.1;local ok,s,why=pcall(reader.capture,reader)
  if ok and s then
   local recorded=pcall(writer.sample,writer,s,now,frames);if not recorded then state.logging_failed=true end
   if not state.logging_failed then
    motion_observer:update(s,probe)
   end
  else emit({event='read_gap',reason=ok and why or tostring(s)})end
 end
 if writer.closed or state.logging_failed then
  if probe and probe.pending then probe:cancel('log_unavailable; reservation_cancelled')
  else trace:stop('log_closed');status('log_closed_experiment_disabled');return end
 end
 local good,s,reason=pcall(snapshot.capture,api,game,resolved_profile)
 if not good then reason=tostring(s);s=nil end
 dispatcher:update(s,reason)
 if now>=next_probe then
  next_probe=now+.1
  if owner_reader.evidence then
   local encoded=recorder.encode(owner_reader.evidence)
   if encoded~=last_preflight then last_preflight=encoded;emit({event='authority_interface_preflight',data=owner_reader.evidence})end
  end
 end
end
local function pack(...)return {n=select('#',...),...}end
if type(previous)~='function'then status('missing_update');return end
update=function(...)
 if animation and not state.logging_failed then animation:sample('before_update')end
 local values=pack(previous(...))
 if state.status~='disabled'then
  local ok,err=pcall(step)
  if not ok then
   state.error=tostring(err);pcall(status,'disabled')
    if input_priority then pcall(input_priority.close,input_priority)end
   if pose_calls then pcall(pose_calls.close,pose_calls,'error')end
   if probe then pcall(probe.close,probe,'diagnostic_error')end
   if trace then pcall(trace.stop,trace,'error')end
   if statusfile then pcall(function()statusfile:write(state.error..'\n');statusfile:flush()end)end
   if writer then pcall(writer.close,writer,api.now(),'error')end
   state.status='disabled'
  end
 end
 if animation and not state.logging_failed then animation:sample('after_update')end
 return unpack(values,1,values.n)
end
shutdown=function(...)
 if pose_calls then pcall(pose_calls.close,pose_calls,'shutdown')end
 if input_priority then pcall(input_priority.close,input_priority)end
 if animation then pcall(animation.close,animation)end
 if probe then pcall(probe.close,probe,'shutdown')end
 if trace then pcall(trace.stop,trace,'shutdown')end
 if writer then pcall(writer.close,writer,api.now(),'shutdown')end
 if statusfile then pcall(function()statusfile:close()end);statusfile=nil end
 if previous_shutdown then return previous_shutdown(...)end
end
