local tag='VehicleSeatNetworkDiagnostic'
if rawget(_G,tag) then return end
local state={version='0.1.2',status='starting',read_only=true}
rawset(_G,tag,state)
local loader=rawget(_G,'CowboyBingusModLoader')
local previous,previous_shutdown=update,shutdown
local frames,started=0,false
local api,game,reader,writer,statusfile,poller,keys
local resolver,resolved_profile,game_digest
local next_sample,next_fault=0,0
local function status(value)
 state.status=value
 if statusfile then pcall(function()statusfile:write(value..'\n');statusfile:flush()end) end
end
local function init()
 assert(loader and loader.api==1 and loader.version>=16,'Bingus Shared Loader v16 required')
 statusfile=assert(loader.open_log('VehicleSeatNetworkDiagnostic.log'),'status_log_unavailable')
 api=platform(module_hash)
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
 local now=api.now()
 local filename='VehicleSeatNetwork-'..os.date('%Y%m%d-%H%M%S')..'-'..api.pid()..'-'..math.floor(now*1000)..'.log'
 local log=assert(loader.open_log(filename),'data_log_unavailable')
 state.filename=filename
 writer=recorder.new(log,now)
 writer:write({event='start',version=state.version,build=compat_spec.known_builds[game_digest] or 'unknown',loader=loader.version,
  sampling='state_changes_and_2s_heartbeat; polls_at_most_every_16ms',keys=origin,key_issues=#issues,
  peer_aliases='opaque_session_labels; not_host_or_owner_mapping',network_packets_captured=false,
  game_sha256=game_digest,compatibility=p.compatibility,schema=p.layout_schema},now)
 reader=sampler.new(api,game,p)
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
 if not writer or writer.closed then return end
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
  if state.status~='recording '..state.filename then status('recording '..state.filename) end
 elseif now>=next_fault then
  writer:write({event='read_gap',reason=why or 'no_snapshot'},now);next_fault=now+2
  status('waiting '..(why or 'no_snapshot'))
 end
 if writer.closed then status('size_limit_reached; restart game for another log') end
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
   if statusfile then pcall(function()statusfile:write(state.error..'\n');statusfile:flush()end) end
   if writer then pcall(writer.close,writer,api.now(),'error') end
  end
 end
 return unpack_values(values,1,values.n)
end
shutdown=function(...)
 if writer then pcall(writer.close,writer,api.now(),'shutdown') end
 if statusfile then pcall(function()statusfile:close()end);statusfile=nil end
 if previous_shutdown then return previous_shutdown(...) end
end
