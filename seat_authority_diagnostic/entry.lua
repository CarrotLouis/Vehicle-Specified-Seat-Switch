local tag='VehicleSeatNetworkDiagnostic'

if rawget(_G,tag) then return end

local state={version='0.5.3',status='starting',passive=false,native_hooks=false,data_hooks=true}

rawset(_G,tag,state)

local loader=rawget(_G,'CowboyBingusModLoader')

local previous,previous_shutdown=update,shutdown

local frames,started=0,false

local api,game,reader,writer,statusfile,poller,keys

local resolver,resolved_profile,game_digest

local trace,trace_started=false,false

local probe,authority_reader,probe_poller,probe_conflict,last_preflight
local next_sample,next_fault=0,0

local function status(value)

 state.status=value

 if statusfile then pcall(function()statusfile:write(value..'\n');statusfile:flush()end) end

end

local function init()

 assert(loader and loader.api==1 and loader.version>=16,'Bingus Shared Loader v16 required')

 statusfile=assert(loader.open_log('VehicleSeatAuthorityDiagnostic.log'),'status_log_unavailable')

 api=pages(platform(module_hash))

 game=assert(api.module('game.dll'),'missing_game_module')

 local ok,value=pcall(api.hash_module,game);game_digest=ok and value or 'unavailable'

 resolver=compat.start(api,game,profile,compat_spec,'diagnostic',status)

 status('checking_interfaces')

end

local function finish_init(p)

 resolved_profile=p

 local text,origin=nil,'defaults'

 local base=os.getenv('APPDATA')

 local f=base and io.open(base..'/Arrowhead/Helldivers2/VehicleSeatSwitch.ini','rb')

 if f then text=f:read(131073);f:close();assert(text and #text<=131072,'config_too_large');origin='existing_ini' end

 local issues;keys,issues=config.parse(text)

 poller=input.new(keys,api)

 probe_poller=input.new({probe={trigger=1316}},api)

 for _,map in pairs(keys)do for _,binding in pairs(map)do if binding==1316 then probe_conflict=true end end end

 local now=api.now()

 local filename='VehicleSeatAuthority-'..os.date('%Y%m%d-%H%M%S')..'-'..api.pid()..'-'..math.floor(now*1000)..'.log'

 local log=assert(loader.open_log(filename),'data_log_unavailable')

 state.filename=filename

 writer=recorder.new(log,now)

 writer:write({event='start',version=state.version,build=compat_spec.known_builds[game_digest] or 'unknown',loader=loader.version,

  sampling='state_changes_and_2s_heartbeat; polls_at_most_every_16ms',keys=origin,key_issues=#issues,

  peer_aliases='opaque_session_labels; not_host_or_owner_mapping',network_packets_captured=false,

  native_call_trace_requested=true,local_identity='entity_handle_map',

  game_sha256=game_digest,compatibility=p.compatibility,schema=p.layout_schema},now)

 reader=sampler.new(api,game,p)

 trace=transport(api,game,p,loader,writer,reader,observer,routing.new(api,game,p,messages),messages,helper)

 authority_reader=authority_observe.new(api,game,p,compat_spec,compat,reader,trace)

 probe=authority_probe.new(authority_reader,function(e)

  if not writer.closed then writer:write(e,api.now());writer.file:flush()end

 end,function(label)state.probe_status=label;status(label..' '..state.filename)end)



 status('recording '..filename)

end

local function step()

 frames=frames+1

 if frames<180 then return end

 if not started then started=true;init() end

 if resolver then

  local p,why=resolver.step();if not p then state.status=why or 'checking_interfaces';return end

  resolver=nil;finish_init(p)

 end

 if not writer then return end

 if writer.closed and not (probe and probe.used and probe.phase~='complete'and probe.phase~='ended'and probe.phase~='send_failed')then if trace and trace.active then trace:stop('log_closed') end;return end

 -- Gameplay must finish all byte checks/binding before the observer installs.

 if trace and not trace_started and frames>=600 then

  local gameplay=rawget(_G,'VehicleSeatSwitch')

  if not gameplay then status('waiting_for_gameplay_0.2.4');return end

  assert(gameplay.version=='0.2.4','gameplay_version_0.2.4_required_for_initialization_order')

  assert(gameplay.status~='disabled_after_error','gameplay_disabled_before_protocol')

  if gameplay.status=='starting' or gameplay.status=='checking_interfaces' then status('waiting_for_gameplay_initialization');return end

  -- Install on the ship after gameplay initialization; no claim that all threads are idle.

  local ok,initial=pcall(reader.capture,reader)

  if not ok or not initial or initial.state~='not_in_mission' then status('waiting_for_ship_before_protocol');return end

  assert(gameplay.mode=='normal','active_probe_requires_gameplay_normal')

  trace_started=true;trace:start();state.transport_ready=true

  status('transport_ready '..state.filename)

 end

 if trace and trace.active then trace:health();trace:drain() end

 local now=api.now();if now<next_sample then return end;next_sample=now+0.016

 local ok,s,why=pcall(reader.capture,reader)

 if not ok then why='read_failed '..tostring(s);s=nil end

 local vehicle,local_avatar

 if s then

  for _,a in ipairs(s.avatars) do if a.is_local then

   local_avatar=a

   if a.seat then for _,v in ipairs(s.vehicles) do if v.id==a.seat.collection then vehicle=v.name;break end end end

   break

  end end

 end

 local focused=vehicle~=nil and local_avatar and local_avatar.vehicle_input and api.input_allowed()

 local pressed=poller:poll(focused and true or false)

 if s then

  writer:sample(s,now,frames)

  if vehicle then for name,binding in pairs(keys[vehicle]) do

   if binding~=0 and pressed[binding] then writer:write({event='configured_seat_key',vehicle=vehicle,seat=name},now) end

  end end

  local label=(state.probe_status or (state.transport_ready and 'transport_ready ' or 'waiting_for_transport ' ))..' '..state.filename

  if state.status~=label then status(label) end

 elseif now>=next_fault then

  writer:write({event='read_gap',reason=why or 'no_snapshot'},now);next_fault=now+2

  status('waiting '..(why or 'no_snapshot'))

 end

 

 if trace and trace.active then

  local trigger=probe_poller:poll(focused and not probe_conflict and not writer.closed and true or false)[1316]

  local o,reason

  if s then

   local ok,value,why=pcall(authority_reader.capture,authority_reader,s,probe.tracked)

   if ok then o,reason=value,why else reason=tostring(value)end
   if authority_reader.evidence then
    local encoded=recorder.encode(authority_reader.evidence)
    if encoded~=last_preflight then
     last_preflight=encoded;writer:write({event='authority_interface_preflight',data=authority_reader.evidence},now)
    end
   end
  else reason='snapshot_unavailable'end

  if probe_conflict and not probe.used then reason='Ctrl_Shift_Home_conflicts_with_seat_binding';o=nil end

  probe:step(s,o,reason,trigger,now)

 end

 if writer.closed then status('size_limit_reached; pending_return_monitor='..tostring(probe and probe.used))end



end

local function pack(...)return {n=select('#',...),...}end

local unpack_values=unpack

if type(previous)~='function' then status('missing_update');return end

update=function(...)

 local values=pack(previous(...))

 if state.status~='disabled' then

  local ok,err=pcall(step)

  if not ok then

   state.error=tostring(err);status('disabled')

   if probe then pcall(probe.close,probe,'diagnostic_error')end

   if trace then pcall(trace.stop,trace,'error') end

   if statusfile then pcall(function()statusfile:write(state.error..'\n');statusfile:flush()end) end

   if writer then pcall(writer.close,writer,api.now(),'error') end

  end

 end

 return unpack_values(values,1,values.n)

end

shutdown=function(...)

 if probe then pcall(probe.close,probe,'shutdown')end

 if trace then pcall(trace.stop,trace,'shutdown') end

 if writer then pcall(writer.close,writer,api.now(),'shutdown') end

 if statusfile then pcall(function()statusfile:close()end);statusfile=nil end

 if previous_shutdown then return previous_shutdown(...) end

end

