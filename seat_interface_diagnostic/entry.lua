local tag='VehicleSeatNetworkDiagnostic'
if rawget(_G,tag)then return end
local state={version='0.3.1',status='starting',read_only=true,native_hooks=false}
rawset(_G,tag,state)
local loader=rawget(_G,'CowboyBingusModLoader')
local previous,previous_shutdown=update,shutdown
local frames,rounds,next_sample=0,0,0
local api,game,resolver,writer,statusfile,reader,route_reader
local function status(value)
 if state.status==value then return end
 state.status=value
 if statusfile then pcall(function()statusfile:write(value..'\n');statusfile:flush()end)end
end
local function init()
 assert(loader and loader.api==1 and loader.version>=16,'Bingus Shared Loader v16 required')
 statusfile=assert(loader.open_log('VehicleSeatInterfaceDiagnostic.log'),'status_log_unavailable')
 api=pages(platform(module_hash));game=assert(api.module('game.dll'),'missing_game_module')
 resolver=compat.start(api,game,profile,compat_spec,'diagnostic',status)
 status('checking_interfaces')
end
local function step()
 frames=frames+1;if frames<180 then return end
 if not api then init()end
 if resolver then
  local p,why=resolver.step();if not p then state.status=why or 'checking_interfaces';return end
  resolver=nil;reader=observer.new(api,game,p);route_reader=routing.new(api,game,p,messages)
  local now=api.now()
  state.filename='VehicleSeatInterface-'..os.date('%Y%m%d-%H%M%S')..'-'..api.pid()..'-'..math.floor(now*1000)..'.log'
  writer=recorder.new(assert(loader.open_log(state.filename),'data_log_unavailable'),now,262144)
  writer:write({event='start',version=state.version,loader=loader.version,compatibility=p.compatibility,
   read_only=true,native_hooks=false,network_packets_captured=false,seat_mutations=false},now)
  status('reading_interfaces '..state.filename)
 end
 if not writer or writer.closed then return end
 local now=api.now();if now<next_sample then return end;next_sample=now+2
 local ok,s=pcall(reader.capture,reader)
 rounds=rounds+1
 if ok then s.round=rounds;writer:write(s,now)
 else writer:write({event='read_gap',round=rounds,reason=tostring(s)},now)end
 local routed,result=pcall(route_reader.capture,route_reader)
 if routed then writer:write({event='routing_snapshot',round=rounds,data=result},now)
 else writer:write({event='routing_gap',round=rounds,reason=tostring(result)},now)end
 if rounds>=10 then writer:close(now,'snapshot_limit');status('complete '..state.filename)
 elseif writer.closed then status('size_limit_reached')end
end
local function pack(...)return {n=select('#',...),...}end
if type(previous)~='function' then status('missing_update');return end
update=function(...)
 local values=pack(previous(...))
 if state.status~='disabled' and not state.status:match('^complete ')then
  local ok,err=pcall(step)
  if not ok then
   state.error=tostring(err);status('disabled')
   if statusfile then pcall(function()statusfile:write(state.error..'\n');statusfile:flush()end)end
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
