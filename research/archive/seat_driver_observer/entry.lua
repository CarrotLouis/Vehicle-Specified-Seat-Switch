local tag='VehicleSeatDriverObserver'
if rawget(_G,tag)then return end
local state={version='0.25.0',status='starting',observation_only=true,physics_writes_enabled=false}
rawset(_G,tag,state)
local loader=rawget(_G,'CowboyBingusModLoader')
local previous,previous_shutdown=update,shutdown
local api,game,resolver,reader,writer,statusfile,watcher,pose_calls
local frames,started,next_poll=0,false,0
local function status(value)
 if state.status==value then return end
 state.status=value
 if statusfile then assert(statusfile:write(value..'\n'));assert(statusfile:flush())end
end
local function emit(e)
 if writer and not writer.closed then assert(writer:write(e,api.now()),state.logging_error or'driver_log_closed')end
end
local function check_companions()
 assert(not rawget(_G,'VehicleSeatNetworkDiagnostic'),'disable_installer_diagnostic_on_driver_observer_machine')
 assert(not rawget(_G,'VehicleSeatSwitch'),'disable_gameplay_companion_for_standalone_test')
 assert(not rawget(_G,'Hd2TankSeatSwitch')and not rawget(_G,'Hd2TankSeatRoles'),'disable_TankSeatKit_before_testing')
end
local function init()
 assert(loader and loader.api==1 and loader.version>=16,'Bingus_Shared_Loader_v16_required')
 statusfile=assert(loader.open_log('VehicleSeatDriverObserverDiagnostic.log'))
 api=pages(platform(module_hash));game=assert(api.module('game.dll'))
 resolver=compat.start(api,game,profile,compat_spec,'enhanced',status)
 status('checking_interfaces')
end
local function finish(p)
 assert(p.capabilities and p.capabilities.enhanced,'driver_observer_interfaces_unavailable')
 local now=api.now();state.filename='VehicleSeatDriverObserver-'..os.date('%Y%m%d-%H%M%S')..'-'..api.pid()..'-'..math.floor(now*1000)..'.log'
 writer=recorder.new(assert(loader.open_log(state.filename)),now)
 -- Mark a failed data log closed before observers attempt to drain/restore.
 -- Cleanup can then finish without another emit throwing into native stop.
 local raw_write=writer.write
 function writer:write(event,time)
  if self.closed then return false end
  local ok,value=pcall(raw_write,self,event,time)
  if not ok then
   state.logging_error=tostring(value);self.closed=true;pcall(self.file.close,self.file);return false
  end
  return value
 end
 local good,digest=pcall(api.hash_module,game)
 emit({event='start',version=state.version,loader=loader.version,compatibility=p.compatibility,
  game_sha256=good and digest or'unavailable',schema=p.layout_schema,
  scope='two_player_m102_local_driver_passive; pair_with_installer_0.24.0',
  observation_only=true,authority_calls_enabled=false,seat_switch_enabled=false,physics_writes_enabled=false,
  ini_access=false,input_hooks=false,network_hooks=false,native_motion_call_observation=true,
  motion_call_originals_forwarded=true,sampling_hz_limit=20,max_driver_window_seconds=120,
  limitation='API_entry_and_polling; not_deferred_callback_completion_or_packet_capture'})
 reader=sampler.new(api,game,p)
 local physical=physics_reader(api,game,p,compat)
 local properties=handoff_reader(api,game,p,compat)
 local ctx=driver_context(api,game,p)
 pose_calls=pose_trace(api,game,p,compat,loader,motion_helper,emit)
 local ok,body=pcall(body_flags_reader,api,game,p,compat)
 if not ok then emit({event='body_flags_init_gap',reason=tostring(body),read_only=true});body=nil end
 watcher=driver_watch(api,physical,properties,ctx,body,pose_calls,emit)
 status('ready_passive_driver_observer '..state.filename)
end
local function step()
 frames=frames+1;if frames<180 then return end
 check_companions()
 if not started then started=true;init()end
 if resolver then local p=resolver.step();if not p then return end;resolver=nil;finish(p)end
 if not writer then return end
 if writer.closed then
  if watcher then watcher:close('log_closed')end
  if pose_calls then pose_calls:close('log_closed');pose_calls=nil end
  status('log_closed_observer_disabled');return
 end
 if pose_calls then pose_calls:update()end
 local now=api.now();if now<next_poll then return end;next_poll=now+.05
 local ok,s,reason=pcall(reader.capture,reader)
 if ok and s then
  writer:sample(s,now,frames)
  if not writer.closed then watcher:update(s)end
 else watcher:gap('snapshot_gap');emit({event='read_gap',reason=ok and reason or tostring(s),read_only=true})end
end
local function pack(...)return {n=select('#',...),...}end
local function close(reason)
 if watcher then pcall(watcher.close,watcher,reason)end
 if pose_calls then pcall(pose_calls.close,pose_calls,reason);pose_calls=nil end
 if writer then pcall(writer.close,writer,api.now(),reason)end
end
if type(previous)~='function'then state.status='missing_update';return end
update=function(...)
 local values=pack(previous(...))
 if state.status~='disabled'then
  local ok,err=pcall(step)
  if not ok then
   state.error=tostring(err);close('error');state.status='disabled'
   if statusfile then pcall(function()statusfile:write('disabled '..state.error..'\n');statusfile:flush()end)end
  end
 end
 return unpack(values,1,values.n)
end
shutdown=function(...)
 close('shutdown')
 if statusfile then pcall(statusfile.close,statusfile);statusfile=nil end
 if previous_shutdown then return previous_shutdown(...)end
end
