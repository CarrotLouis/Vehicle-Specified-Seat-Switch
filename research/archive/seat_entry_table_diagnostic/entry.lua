local tag='VehicleSeatNetworkDiagnostic'
if rawget(_G,tag)then return end
local state={version='entry-tables-0.1.0',status='starting',passive=true,native_hooks=false,data_hooks=false}
rawset(_G,tag,state)
local previous,previous_shutdown=update,shutdown
local loader=rawget(_G,'CowboyBingusModLoader')
local frames,api,game,resolver,writer,statusfile=0
local function status(s)
 state.status=s
 if statusfile then statusfile:write(s..'\n');statusfile:flush()end
end
local function step()
 frames=frames+1
 if frames<180 or state.status=='entry_tables_complete' then return end
 if not api then
  assert(loader and loader.api==1 and loader.version>=16,'Bingus_Shared_Loader_v16_required')
  statusfile=assert(loader.open_log('VehicleSeatEntryTableDiagnostic.log'))
  api=platform(module_hash);game=assert(api.module('game.dll'),'missing_game_module')
  resolver=compat.start(api,game,tables.extend(profile),compat_spec,'diagnostic',status)
  status('checking_interfaces')
 end
 if resolver then
  local p,why=resolver.step();if not p then state.status=why or 'checking_interfaces';return end
  resolver=nil;state.profile=p
 end
 if frames<600 then status('waiting_for_capture');return end
 local now=api.now()
 local name='VehicleSeatEntryTables-'..os.date('%Y%m%d-%H%M%S')..'-'..api.pid()..'-'..math.floor(now*1000)..'.log'
 local file=assert(loader.open_log(name),'data_log_unavailable')
 state.filename=name;writer=recorder.new(file,now,65536)
 local ok,digest=pcall(api.hash_module,game)
 writer:write({event='start',version=state.version,game_sha256=ok and digest or 'unavailable',
  compatibility=state.profile.compatibility,read_only=true,requested_bytes=424},now)
 local result=tables.capture(api,game,state.profile)
 result.game_sha256=ok and digest or 'unavailable'
 writer:write(result,api.now());writer:close(api.now(),'complete')
 status('entry_tables_complete')
end
local function pack(...)return {n=select('#',...),...}end
if type(previous)~='function'then state.status='disabled';state.error='missing_update';return end
update=function(...)
 local values=pack(previous(...))
 if state.status~='disabled'then
  local ok,err=pcall(step)
  if not ok then
   state.error=tostring(err);state.status='disabled'
   if statusfile then pcall(function()statusfile:write('disabled '..state.error..'\n');statusfile:flush()end)end
   if writer then pcall(writer.close,writer,api.now(),'error')end
  end
 end
 return unpack(values,1,values.n)
end
shutdown=function(...)
 if writer then pcall(writer.close,writer,api.now(),'shutdown')end
 if statusfile then pcall(function()statusfile:close()end);statusfile=nil end
 if previous_shutdown then return previous_shutdown(...)end
end
