local tag='VehicleSeatNetworkDiagnostic'
if rawget(_G,tag)then return end
local state={version='0.7.3',status='starting',passive=false,native_hooks=false,data_hooks=true}
rawset(_G,tag,state)
local loader=rawget(_G,'CowboyBingusModLoader')
local previous,previous_shutdown=update,shutdown
local frames,started,trace_started=0,false,false
local api,game,resolver,reader,writer,statusfile,trace,probe,owner_reader,trigger_keys,conflict
local animation
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
 local text;local base=os.getenv('APPDATA')
 local f=base and io.open(base..'/Arrowhead/Helldivers2/VehicleSeatSwitch.ini','rb')
 if f then text=f:read(131073);f:close();assert(text and #text<=131072,'config_too_large')end
 local keys,issues=config.parse(text)
 for _,map in pairs(keys)do for _,binding in pairs(map)do if binding==1316 then conflict=true end end end
 trigger_keys=input.new({probe={trigger=1316}},api)
 local now=api.now();state.filename='VehicleSeatIntegrated-'..os.date('%Y%m%d-%H%M%S')..'-'..api.pid()..'-'..math.floor(now*1000)..'.log'
 writer=recorder.new(assert(loader.open_log(state.filename)),now)
 -- A disk failure must not unwind the ownership-return state machine.
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
 api.experiment_allowed=function()return not writer.closed and not state.logging_failed and not(animation and animation.failed)end
 local ok,digest=pcall(api.hash_module,game)
 emit({event='start',version=state.version,loader=loader.version,compatibility=p.compatibility,schema=p.layout_schema,
  game_sha256=ok and digest or 'unavailable',key_issues=#issues,key_conflict=conflict or false,
  scope='guest_M102_front_passenger_rear_left; acquire_switch_sync_return; max_two_manual_operations',network_packets_captured=false})
 reader=sampler.new(api,game,p)
 trace=transport(api,game,p,loader,writer,reader,observer,routing.new(api,game,p,messages),messages,helper)
 owner_reader=authority_observe.new(api,game,p,compat_spec,compat,reader,trace)
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
 local local_switch=transaction(api,game,p,observed_pose,personal,emit)
 local inspector=animation_inspect.new(api,game,p,routing.new(api,game,p,{[0xbde53653]='animation_event'}))
 local anim_send=animation_sender(api,game,p,compat_spec,compat,inspector,trace)
 local send=sender(api,game,p,compat_spec,compat,trace,anim_send)
 local adapter=sync_adapter.new(api,game,p,reader,owner_reader,snapshot,local_switch,send,trace,emit,recorder.encode)
 probe=sync_probe.new(adapter,emit,function(label)state.probe_status=label;status(label..' '..state.filename)end)
 status('waiting_for_transport '..state.filename)
end
local function step()
 frames=frames+1;if frames<180 then return end
 if not started then started=true;init()end
 if resolver then local p,why=resolver.step();if not p then return end;resolver=nil;finish_init(p)end
 if not writer then return end
 if writer.closed or state.logging_failed then
  if probe and probe.pending then probe:cancel('log_unavailable; returning_ownership')
  else if trace and trace.active then trace:stop('log_closed')end;status('log_closed_experiment_disabled');return end
 end
 assert(not rawget(_G,'Hd2TankSeatSwitch')and not rawget(_G,'Hd2TankSeatRoles'),'disable_TankSeatKit_before_testing')
 if trace and not trace_started and frames>=600 then
  local gameplay=rawget(_G,'VehicleSeatSwitch')
  if not gameplay then status('waiting_for_gameplay_0.2.4');return end
  assert(gameplay.version=='0.2.4','gameplay_0.2.4_required')
  assert(gameplay.mode=='normal','sync_requires_gameplay_Normal')
  assert(gameplay.status~='disabled_after_error','gameplay_disabled')
  if gameplay.status=='starting'or gameplay.status=='checking_interfaces'then status('waiting_for_gameplay_initialization');return end
  local ok,s=pcall(reader.capture,reader)
  if not ok or not s or s.state~='not_in_mission'then status('waiting_for_ship_before_protocol');return end
  trace_started=true;trace:start();state.transport_ready=true
  status('transport_ready '..state.filename)
 end
 if not trace or not trace.active then return end
 trace:health();trace:drain()
 local now=api.now();if now<next_poll then return end;next_poll=now+.016
 local focused=api.input_allowed()
 local trigger=trigger_keys:poll(focused and not conflict and api.experiment_allowed())[1316]
 if animation.failed and probe.pending then probe:cancel('animation_read_gap; returning_ownership')end
 if trigger and probe.phase=='finished'then emit({event='integrated_trigger_ignored',reason='two_operation_limit'})end
 if now>=next_sample and not writer.closed and not state.logging_failed then
  next_sample=now+.1;local ok,s,why=pcall(reader.capture,reader)
  if ok and s then local recorded=pcall(writer.sample,writer,s,now,frames);if not recorded then state.logging_failed=true end else emit({event='read_gap',reason=ok and why or tostring(s)})end
 end
 if writer.closed or state.logging_failed then
  if probe and probe.pending then probe:cancel('log_unavailable; returning_ownership')
  else trace:stop('log_closed');status('log_closed_experiment_disabled');return end
 end
 if conflict then status('Ctrl_Shift_Home_conflicts_with_seat_binding');return end
 if trigger or now>=next_probe then
  next_probe=now+.1;probe:step(trigger,now,focused)
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
 if animation then pcall(animation.close,animation)end
 if probe then pcall(probe.close,probe,'shutdown')end
 if trace then pcall(trace.stop,trace,'shutdown')end
 if writer then pcall(writer.close,writer,api.now(),'shutdown')end
 if statusfile then pcall(function()statusfile:close()end);statusfile=nil end
 if previous_shutdown then return previous_shutdown(...)end
end
