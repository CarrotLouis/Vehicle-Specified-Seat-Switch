local tag='VehicleSeatNetworkDiagnostic'
if rawget(_G,tag)then return end
local state={version='0.7.2',status='starting',read_only=true,native_hooks=false,data_hooks=false}
rawset(_G,tag,state)
local loader=rawget(_G,'CowboyBingusModLoader')
local previous,previous_shutdown=update,shutdown
local api,game,resolver,writer,statusfile,reader,inspector
local frames,next_sample,rounds,seated_rounds=0,0,0,0
local function status(value)
 if state.status==value then return end;state.status=value
 if statusfile then assert(statusfile:write(value..'\n'));statusfile:flush()end
end
local function init()
 assert(loader and loader.api==1 and loader.version>=16,'Bingus_Shared_Loader_v16_required')
 statusfile=assert(loader.open_log('VehicleSeatAnimationInterfaceDiagnostic.log'))
 api=pages(platform(module_hash));game=assert(api.module('game.dll'))
 resolver=compat.start(api,game,profile,compat_spec,'diagnostic',status)
end
local function step()
 frames=frames+1;if frames<180 then return end
 if not api then init()end
 if resolver then
  local p=resolver.step();if not p then return end;resolver=nil
  reader=sampler.new(api,game,p)
  local route=routing.new(api,game,p,{[0xbde53653]='animation_event'})
  inspector=animation_inspect.new(api,game,p,route)
  local now=api.now();state.filename='VehicleSeatAnimationInterface-'..os.date('%Y%m%d-%H%M%S')..'-'..api.pid()..'-'..math.floor(now*1000)..'.log'
  writer=recorder.new(assert(loader.open_log(state.filename)),now,1048576)
  writer:write({event='start',version=state.version,loader=loader.version,compatibility=p.compatibility,
   read_only=true,game_functions_called=false,data_hooks=false,network_messages_sent=false,seat_mutations=false},now)
  status('waiting_for_solo_M102 '..state.filename)
 end
 if not writer or writer.closed then return end
 local now=api.now();if now<next_sample then return end;next_sample=now+2
 rounds=rounds+1
 local ok,s,why=pcall(reader.capture,reader)
 if not ok or not s then
  seated_rounds=0;writer:write({event='read_gap',reason=ok and tostring(why)or tostring(s),round=rounds},now)
 else
  local avatar,n=nil,0
  for _,a in ipairs(s.avatars or {})do if a.is_local then avatar=a;n=n+1 end end
  if n~=1 then avatar=nil end
  local good,out=pcall(inspector.capture,inspector,avatar)
  if good then
   out.round=rounds;out.mission=s.state;out.seat=avatar and avatar.seat or nil;writer:write(out,now)
   local seated=false
   if s.state=='mission'and s.player_count==1 and s.peer_count==1 and avatar and avatar.seat then
    for _,v in ipairs(s.vehicles)do
     if v.name=='m102'and avatar.seat.collection==v.id and avatar.seat.current>=0 and avatar.seat.current<5 and avatar.seat.transitioning==0 then seated=true end
    end
   end
   if seated and not writer.closed then seated_rounds=seated_rounds+1 else seated_rounds=0 end
   if seated_rounds>=5 then writer:close(now,'five_seated_samples');status('complete '..state.filename)
   elseif seated then status('sampling_M102 '..seated_rounds..'/5 '..state.filename)end
  else seated_rounds=0;writer:write({event='interface_gap',reason=tostring(out),round=rounds},now)end
 end
 if rounds>=600 and not writer.closed then writer:close(now,'twenty_minute_limit');status('incomplete_time_limit '..state.filename)end
 if writer.closed and not state.status:match('^complete ')and not state.status:match('^incomplete_')then status('incomplete_log_closed '..state.filename)end
end
local function pack(...)return {n=select('#',...),...}end
if type(previous)~='function'then state.status='missing_update';return end
update=function(...)
 local values=pack(previous(...))
 if state.status~='disabled'and not state.status:match('^complete ')and not state.status:match('^incomplete_')then
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
 if statusfile then pcall(statusfile.close,statusfile)end
 if previous_shutdown then return previous_shutdown(...)end
end
