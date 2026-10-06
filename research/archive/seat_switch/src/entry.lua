-- Bundler supplies MODE, profile, policy, config, platform, snapshot, bind_native, Controller.
if rawget(_G,'VehicleSeatSwitch') then return end
local state={version='0.2.4',mode=MODE,status='starting'}
rawset(_G,'VehicleSeatSwitch',state)
local loader=rawget(_G,'CowboyBingusModLoader')
local logfile
local function log(line)
 print('[VehicleSeatSwitch] '..line)
 if logfile then logfile:write(os.date('%Y-%m-%d %H:%M:%S')..' '..line..'\n');logfile:flush() end
end
local previous,previous_shutdown=update,shutdown
local started,frames,api,game,controller=false,0
local resolver,resolved_profile
local unpack_values=unpack
local function pack(...)return {n=select('#',...),...} end
local function initialize()
 assert(loader and loader.api==1 and loader.version>=16,'Bingus Shared Loader v16 / API 1 required')
 logfile=assert(loader.open_log('VehicleSeatSwitch.log'),'Cannot create log')
 log('Vehicle Specified Seat Switch '..state.version..' mode='..MODE)
 log('loader_runtime='..tostring(loader.version)..' api='..tostring(loader.api)..' compatibility=interface_evidence')
 assert(profile.enabled,profile.reason or 'Native profile disabled')
 api=platform();game=assert(api.module('game.dll'),'Missing game module')
 assert(api.module('helldivers2.exe'),'Only supported in helldivers2.exe')
 local ok,digest=pcall(api.hash_module,game)
 log('game_sha256='..tostring(digest)..' known_build='..tostring(ok and compat_spec.known_builds[digest] or 'unknown'))
 resolver=compat.start(api,game,profile,compat_spec,MODE,log)
 state.status='checking_interfaces'
end
local function finish_initialize(p)
 resolved_profile=p
 local keys,issues,keypath,origin=config.load(api.config_directory(),loader.log_directory)
 state.config=keypath
 log('key_config '..origin..' path='..keypath)
 for _,issue in ipairs(issues) do log(issue) end
 local native=bind_native(api,game,p,bind_pose,log,bind_driver,MODE)
 controller=Controller.new(MODE,keys,api,native,log)
 state.status='ready';log('Ready; config='..keypath)
 -- Tiny static adjacency tables, never heap/module dumps.
 for name,t in pairs(p.tables) do
  local data=api.read(game+t.rva,t.size)
  local values={}
  if data then for offset=0,#data-4,4 do values[#values+1]=snapshot.i32(data,offset) end end
  log('seat_adjacency '..name..' '..table.concat(values,','))
 end
end
local last_status,last_snapshot,next_detail=nil,nil,0
local function step()
 frames=frames+1
 if frames<180 then return end
 if not started then started=true;initialize() end
 if resolver then
  local p,why=resolver.step()
  if not p then state.status=why or 'checking_interfaces';return end
  resolver=nil;finish_initialize(p)
 end
 if not controller then return end
 local ok,s,reason=pcall(snapshot.capture,api,game,resolved_profile)
 if not ok then
  reason='waiting_for_valid_state';state.last_snapshot_error=tostring(s);s=nil
  if api.now()>=next_detail then log('snapshot_wait '..state.last_snapshot_error);next_detail=api.now()+10 end
 end
 if s then
  local key=s.identity..s.node..tostring(s.owned)..s.mask..tostring(s.active)
  if key~=last_snapshot then
   log('snapshot vehicle='..s.vehicle..' resource='..s.resource..' transition='..s.transition..' node='..s.node..' mask='..s.mask..' owner='..tostring(s.owned)..' players='..s.player_count..' active='..tostring(s.active)..' provisional_identity='..tostring(s.provisional_identity or false))
   last_snapshot=key
  end
 end
 local status=controller:update(s,reason)
 state.status=status
 if status~=last_status then log('state='..tostring(status));last_status=status end
end
if type(previous)~='function' then state.status='missing_update';return end
update=function(...)
 local result=pack(previous(...))
 if state.status~='disabled_after_error' then
  local ok,err=pcall(step)
  if not ok then state.status='disabled_after_error';log('DISABLED '..tostring(err)) end
 end
 return unpack_values(result,1,result.n)
end
shutdown=function(...)
 if logfile then log('shutdown');logfile:close();logfile=nil end
 if previous_shutdown then return previous_shutdown(...) end
end
