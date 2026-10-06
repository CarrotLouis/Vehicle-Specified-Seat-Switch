local tag='VehicleSeatNetworkDiagnostic'
if rawget(_G,tag)then return end
local state={version='0.10.0',status='starting',passive=true,native_hooks=false,data_hooks=false}
rawset(_G,tag,state)
local loader=rawget(_G,'CowboyBingusModLoader')
local previous,previous_shutdown=update,shutdown
local api,game,resolver,reader,writer,inspector,route,statusfile
local frames,next_sample,next_interface,last=0,0,0,nil
local function status(s)state.status=s;if statusfile then assert(statusfile:write(s..'\n'));statusfile:flush()end end
local function emit(e)assert(writer:write(e,api.now()));writer.file:flush()end
local function step()
 frames=frames+1;if frames<180 then return end
 if not api then
  assert(loader and loader.api==1 and loader.version>=16,'Loader_v16_required')
  statusfile=assert(loader.open_log('VehicleSeatBindingDiagnostic.log'))
  api=pages(platform(module_hash));game=assert(api.module('game.dll'))
  resolver=compat.start(api,game,profile,compat_spec,'enhanced',status)
 end
 if resolver then
  local p=resolver.step();if not p then return end;resolver=nil
  assert(p.capabilities and p.capabilities.enhanced,'binding_interfaces_unavailable')
  local now=api.now();state.filename='VehicleSeatBinding-'..os.date('%Y%m%d-%H%M%S')..'-'..api.pid()..'.log'
  writer=recorder.new(assert(loader.open_log(state.filename)),now)
  emit({event='start',version=state.version,loader=loader.version,compatibility=p.compatibility,passive=true,network_sends=false,game_calls=false})
  reader=sampler.new(api,game,p);inspector=binding_inspect.new(api,game,p)
  route=routing.new(api,game,p,{[0x423a4034]='weapon_channel_clear',[0x2671dec5]='weapon_channel_bind'})
  status('ready_read_only '..state.filename)
 end
 local now=api.now();if now<next_sample then return end;next_sample=now+.25
 if now>=next_interface then
  next_interface=now+15;local ok,x=pcall(inspector.interface,inspector,route)
  emit({event='binding_interface',ok=ok,data=ok and x or nil,reason=not ok and tostring(x)or nil})
 end
 local ok,s,why=pcall(reader.capture,reader)
 if not ok or not s then emit({event='binding_read_gap',reason=ok and why or tostring(s)});return end
 writer:sample(s,now,frames)
 local any=false
 for _,a in ipairs(s.avatars or {})do if a.is_local then
  any=true;local good,data=pcall(inspector.capture,inspector,a)
  local e={event='binding_sample',ok=good,data=good and data or nil,reason=not good and tostring(data)or nil}
  local encoded=recorder.encode(e)
  if encoded~=last then last=encoded;emit(e)end
 end end
 if not any then last=nil end
end
local function pack(...)return {n=select('#',...),...}end
if type(previous)~='function'then state.status='missing_update';return end
update=function(...)
 local values=pack(previous(...))
 if state.status~='disabled'then local ok,err=pcall(step);if not ok then
  state.error=tostring(err);pcall(status,'disabled '..state.error);state.status='disabled'
  if writer then pcall(writer.close,writer,api and api.now()or 0,'error')end
 end end
 return unpack(values,1,values.n)
end
shutdown=function(...)
 if writer then pcall(writer.close,writer,api.now(),'shutdown')end
 if statusfile then pcall(statusfile.close,statusfile)end
 if previous_shutdown then return previous_shutdown(...)end
end
