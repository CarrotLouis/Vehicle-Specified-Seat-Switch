-- One addon, one physical key poller, selectable native/solo/network routes.
local tag='VehicleSeatSwitch'
if rawget(_G,tag) then return end
local state={version='0.4.2',mode='normal',status='starting'}
rawset(_G,tag,state)
local loader=rawget(_G,'CowboyBingusModLoader')
local previous,previous_shutdown=update,shutdown
local frames,started,trace_started=0,false,false
local resolver_phase,normal_resolved='normal',nil
local api,game,resolver,p,logfile,reader,trace,probe,dispatcher,solo,normal,input_priority,keys,poller
local menus,enhanced_ready,active_mode,active_strategy,gate_route,performance_blocker
local last_route,next_poll,next_capture,next_protocol,cached_snapshot,cached_reason=nil,0,0,0,nil,nil
local function log(line)
 if logfile then
  local ok=pcall(function()assert(logfile:write(os.date('%Y-%m-%d %H:%M:%S')..' '..line..'\n'));logfile:flush()end)
  if not ok then state.log_unavailable=true;pcall(logfile.close,logfile);logfile=nil end
 end
end
local function status(value)
 if state.status~=value then state.status=value;log('state='..tostring(value))end
end
local significant={transport_ready=true,transport_stopped=true,transport_install_failure=true,
 reservation_request=true,reservation_operation_complete=true,reservation_local_owner_complete=true,
 reservation_owner_denied=true,reservation_cancelled=true,reservation_stopped=true,
 input_priority_failed=true,input_priority_install_failure=true,tank_steer_reset_partial_failure=true}
local function emit(e)
 if not significant[e.event] and not(e.event=='seat_input' and (e.reason=='native_complete' or e.reason=='network_trigger_refused')) then return end
 local values={tostring(e.event)}
 for _,name in ipairs({'operation','source','target','reason','detail','code','restore_flags'})do
  if e[name]~=nil then values[#values+1]=name..'='..tostring(e[name])end
 end
 log(table.concat(values,' '))
end
local function init()
 assert(loader and loader.api==1 and loader.version>=16,'Bingus_Shared_Loader_v16_API1_required')
 logfile=assert(loader.open_log('VehicleSeatSwitch.log'),'Cannot_create_VehicleSeatSwitch_log')
 log('Vehicle Specified Seat Switch '..state.version..' mode=menu_default_normal loader_runtime='..tostring(loader.version))
 assert(not rawget(_G,'VehicleSeatNetworkDiagnostic'),'disable_old_seat_diagnostic_before_using_release')
 assert(not rawget(_G,'Hd2TankSeatSwitch')and not rawget(_G,'Hd2TankSeatRoles'),'disable_other_seat_controller_before_using_release')
 api=pages(platform(module_hash));game=assert(api.module('game.dll'))
 resolver=normal_compat.start(api,game,profile,normal_compat_spec,'normal',log)
 menus=menu_integration.new(i18n(bingus_text),menu_locales,log);menus:update()
 performance_blocker=performance_data.new(api,performance_data_spec,log)
 status('checking_interfaces')
end
local function finish_init(resolved)
 p=resolved
 local issues,path,origin
 keys,issues,path,origin=config.load(api.config_directory(),loader.log_directory)
 state.config=path;log('key_config '..origin..' path='..path)
 for _,issue in ipairs(issues)do log(issue)end
 normal=bind_native(api,game,p,nil,nil,nil,'normal')
 poller=input_source.new(keys,api,input,policy,menus,menu_integration.ids);keys=poller.keys
  active_mode='normal';active_strategy='ini'
 if not(p.capabilities and p.capabilities.enhanced)then
  solo=Controller.new('normal',keys,api,normal,log);solo.input=poller
  state.effective_mode='normal';log('enhanced_unavailable; validated Normal retained: '..tostring(p.capabilities and p.capabilities.enhanced_reason))
  status('normal_fallback_ready');return
 end
 enhanced_ready=true;state.effective_mode='normal'
 api.experiment_allowed=function()return state.status~='disabled_after_error' and not(active_strategy=='ini' and input_priority and input_priority.failed)end
 reader=sampler.new(api,game,p)
 local writer={closed=false,write=function(_,event)emit(event)end}
 trace=transport(api,game,p,loader,writer,reader,observer,routing.new(api,game,p,messages),messages,helper)
 local owner_reader=authority_observe.new(api,game,p,compat_spec,compat,reader,trace)
 local local_switch=transaction(api,game,p,pose,personal,emit,reservation_tools.scope)
 local inspector=animation_inspect.new(api,game,p,routing.new(api,game,p,{[0xbde53653]='animation_event'}))
 local anim_send=animation_sender(api,game,p,compat_spec,compat,inspector,trace,reservation_tools.scope.layout)
 local weapon_inspector=binding_inspect.new(api,game,p)
 local weapon_route=routing.new(api,game,p,{[0x423a4034]='weapon_channel_clear',[0x2671dec5]='weapon_channel_bind'})
 local weapon_send=binding_sender(api,game,p,compat_spec,compat,weapon_inspector,weapon_route,trace,personal,reservation_tools.scope.layout)
 local send=sender(api,game,p,compat_spec,compat,trace,anim_send,weapon_send,reservation_tools.scope.layout)
 local adapter=sync_adapter.new(api,game,p,reader,owner_reader,snapshot,local_switch,send,trace,emit,function()return ''end)
 adapter.mounted=reservation_tools.mounted_reader(api,game,p,compat_spec,compat,weapon_inspector,reservation_tools.scope,emit)
 function adapter:eligible(c,source,owned,ticket,target)return reservation_tools.probe.eligible(c,source,owned,ticket,target)end
 local reserve_entry=reservation_tools.entrance(api,game,p,compat_spec,compat,trace,emit,reservation_tools.scope)
 local actual_probe=reservation_tools.probe.new(adapter,api,snapshot,trace,reserve_entry,local_switch,send,emit,
  function(value)state.probe_status=value end)
 probe=actual_probe
 local original_step=probe.step
 function probe:step(...)
  if not trace.active then self.ready_at=nil;self.observed=nil;return false,'multiplayer_initializing_wait_on_ship'end
  return original_step(self,...)
 end
 local steering_cleanup=reservation_tools.steering_reset(api,game,p,compat,reservation_tools.spin_reader,reservation_tools.scope,emit)
 adapter.owned_transaction=reservation_tools.owned_transaction(api,game,p,reservation_tools.owned_base,pose,personal,emit,
  reservation_tools.owned_driver,reservation_tools.scope,reservation_tools.owned_tank_driver,steering_cleanup)
 adapter.release_acquired=reservation_tools.release_acquired(api,game,p,reservation_tools.scope)
 adapter.steering_cleanup=steering_cleanup
 local solo_adapter=solo_native(api,game,p,normal,adapter.owned_transaction,pose,reservation_tools.scope)
 solo=Controller.new('enhanced',keys,api,solo_adapter,log);solo.input=poller
 input_priority=input_gate(api,loader,input_helper,runtime_policy,snapshot,function(...)return adapter:eligible(...)end,emit)
 api.control_down=function(key)return input_priority:control_down(key)end
 api.tank_driver_exit_allowed=function(s)
  local d=reservation_tools.scope.layout(s)
  return p.functions.tank_driver_active and d and d.tank and s.node==0 and s.owned and not s.active and s.player_count>=2 and s.player_count<=4 and s.peer_count==s.player_count
 end
 -- Native action bindings must reach the game; consuming their Windows
 -- messages here would also prevent ModBindingsMenu from reading them.
 gate_route={active=false,failed=false,pending=false}
 function gate_route:pulse(s,c,k,enabled)
  local use=active_strategy=='ini'
  input_priority:pulse(s,c,k,enabled and use)
  self.active=use and input_priority.active;self.failed=use and input_priority.failed
  self.pending=use and input_priority.pending;self.generation=input_priority.generation
 end
 function gate_route:take(s)return input_priority:take(active_strategy=='ini' and s or nil)end
 function gate_route:filter(pressed,consumed)
  if active_strategy=='ini'then input_priority:filter(pressed,consumed)end
 end
 dispatcher=seat_dispatcher.new(api,keys,input,runtime_policy,snapshot,normal,probe,emit,gate_route)
 dispatcher.poller=poller
 status('ready; multiplayer_protocol_waiting_on_ship')
end
local function apply_options()
 local mode=menus.mode=='enhanced' and enhanced_ready and not state.enhanced_fault and 'enhanced' or 'normal'
 local strategy=menus.strategy
 local busy=probe and probe.pending or solo and (solo.pending or solo.preparing) or
  dispatcher and dispatcher.pending
 state.requested_mode=menus.mode;state.requested_strategy=strategy
 state.settings_pending=busy and (mode~=active_mode or strategy~=active_strategy) or false
 if busy then return end
 if mode~=active_mode or strategy~=active_strategy then
  if dispatcher then dispatcher.queued=nil end -- unsent intent only
  -- A variant change only changes a Lua permission flag and resets edges.
  -- The same controller, input helper, adapter and receive gate stay resident.
  if strategy~=active_strategy then
   if input_priority then input_priority:pulse(nil,nil,keys,false);input_priority:take(nil)end
   poller:set_strategy(strategy)
  else poller:flush()end
  active_mode=mode;active_strategy=strategy
  api.native_binding_source=strategy=='menu'
  last_route=nil;next_capture=0
  log('settings_applied mode='..mode..' strategy='..strategy)
 end
 state.mode=active_mode;state.effective_mode=active_mode;state.input_strategy=active_strategy
end
local function read_snapshot(now,force)
 if force or now>=next_capture then
  local ok,s,why=pcall(snapshot.capture,api,game,p)
  cached_snapshot=ok and s or nil;cached_reason=ok and why or 'snapshot_unavailable'
  if not ok then state.last_snapshot_error=tostring(s)end
  next_capture=now+(cached_snapshot and .05 or .1)
 end
 return cached_snapshot,cached_reason
end
local function bootstrap()
 if frames<180 then return end
 if not started then started=true;init()end
 if resolver then
  local ok,resolved=pcall(resolver.step)
  if not ok and resolver_phase=='normal'then error(resolved)end
  if not ok then
   log('enhanced_interface_check_failed '..tostring(resolved))
   normal_resolved.capabilities.enhanced_reason=tostring(resolved)
   resolved=normal_resolved
  end
  if not resolved then return end
  if resolver_phase=='normal'then
   normal_resolved=resolved;resolver_phase='enhanced'
   resolver=compat.start(api,game,profile,compat_spec,'enhanced',log);return
  end
  resolver=nil;finish_init(resolved)
 end
end
local function menu_step()
 if menus then menus:update()end
 if poller then apply_options()end
 if performance_blocker then
  -- Keep native menu parsing and keyboard capture using the original names.
  local wanted=menus.available and menus.block_perf
  performance_blocker:update(wanted,wanted and api.input_allowed())
  state.performance_block=performance_blocker.status
 end
end
local function gameplay_step()
 if not solo then return end
 if not menus.available then
  if input_priority then input_priority:pulse(nil,nil,keys,false);input_priority:take(nil)end
  poller:flush()
  -- An already-issued transaction still needs its completion/cleanup service.
  if not(probe and probe.pending or dispatcher and dispatcher.pending or solo.pending or solo.preparing)then
   status('required_ModOptionsMenu_missing');return
  end
 end
 poller:sample_menu(api.input_allowed())
 local now=api.now()
 if trace and not trace_started and frames>=600 and now>=next_protocol then
  next_protocol=now+.25
  -- Same validated startup context as the accepted multiplayer package.
  local ok,s=pcall(reader.capture,reader)
  if ok and s and s.state=='not_in_mission'then trace:start();trace_started=true;state.transport_ready=true;log('multiplayer_protocol_ready; receive_gate_only; sampling_disabled')end
 end
 if now<next_poll then return end;next_poll=now+.016
 local working=probe and probe.pending or dispatcher and(dispatcher.pending or dispatcher.queued)or solo.pending or solo.preparing
 local s,reason=read_snapshot(now,working or poller:held())
 local network=dispatcher and not state.enhanced_fault and (probe.pending or s and s.player_count>=2)
 local route=network and 'multiplayer' or 'solo_or_fallback'
 if last_route and route~=last_route then
  -- Held inputs may not turn into a new edge when a peer joins/leaves.
  poller:flush();solo.pending=nil;solo.preparing=nil
  if dispatcher and not probe.pending then dispatcher.pending=nil;dispatcher.queued=nil end
 end
 last_route=route
 if network then
  if trace.active then trace:health()end
  local result=dispatcher:update(s,reason)
  if probe.phase=='stopped'then status('multiplayer_stopped_full_game_restart_required')else state.status=result end
 else
  if input_priority then input_priority:pulse(nil,nil,keys,false);input_priority:take(nil)end
  state.status=solo:update(s,reason)
 end
end
local function pack(...)return {n=select('#',...),...}end
if type(previous)~='function'then state.status='missing_update';return end
update=function(...)
 local values=pack(previous(...))
 frames=frames+1
 if not state.bootstrap_fault and(not started or resolver)then
  local ok,err=pcall(bootstrap)
  if not ok then state.bootstrap_fault=tostring(err);state.error=tostring(err);log('BOOTSTRAP_DISABLED '..state.error)end
 end
 -- Menu values/translated callbacks keep updating even after a gameplay fault.
 local menu_ok,menu_err=pcall(menu_step)
 if not menu_ok and state.menu_error~=tostring(menu_err)then state.menu_error=tostring(menu_err);log('MENU_ERROR '..state.menu_error)end
 if solo and not state.bootstrap_fault then
  local ok,err=pcall(gameplay_step)
  if not ok then
   state.enhanced_fault=tostring(err);state.error=tostring(err);log('ENHANCED_PAUSED '..state.error)
   solo.pending=nil;solo.preparing=nil
   if dispatcher then dispatcher.pending=nil;dispatcher.queued=nil end
   if input_priority then pcall(input_priority.pulse,input_priority,nil,nil,keys,false);pcall(input_priority.take,input_priority,nil)end
   if probe then pcall(probe.close,probe,'runtime_error')end
   if trace then pcall(trace.stop,trace,'error')end
   state.effective_mode='normal';active_mode='normal';state.status='normal_after_enhanced_error'
  end
 end
 return unpack(values,1,values.n)
end
shutdown=function(...)
 if performance_blocker then pcall(performance_blocker.close,performance_blocker)end
 if input_priority then pcall(input_priority.close,input_priority)end
 if probe then pcall(probe.close,probe,'shutdown')end
 if trace then pcall(trace.stop,trace,'shutdown')end
 if logfile then log('shutdown');pcall(logfile.close,logfile);logfile=nil end
 if previous_shutdown then return previous_shutdown(...)end
end
