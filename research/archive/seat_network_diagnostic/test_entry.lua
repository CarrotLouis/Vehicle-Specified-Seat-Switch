local profile=assert(loadfile('work/seat_switch/src/profile.lua'))()
local recorder=assert(loadfile('work/seat_network_diagnostic/recorder.lua'))()
local raw=assert(io.open('work/seat_network_diagnostic/entry.lua','rb'));local source=raw:read('*a');raw:close()
local logs,files={},{}
local loader={api=1,version=16,open_log=function(name)
 logs[#logs+1]=name;local f={lines={},flush=function()return true end,close=function(self)self.closed=true;return true end}
 function f:write(text)assert(not self.closed);self.lines[#self.lines+1]=text;return self end
 files[name]=f;return f
end}
local now,read_calls=0,0
local api={now=function()return now end,pid=function()return 123 end,module=function(n)return n=='game.dll' and 100 or 200 end,
 hash_module=function(p)return p==100 and profile.game_sha256 or profile.exe_sha256 end,
 read=function(a)for _,p in pairs(profile.functions)do if a==100+p.rva then return p.bytes end end end,
 input_allowed=function()return true end}
local update_calls,shutdown_calls=0,0
local interfaces_ok=true
local original_update=function(a,b)update_calls=update_calls+1;assert(a==7 and b==9);return nil,'kept',nil,42 end
local original_shutdown=function(...)shutdown_calls=shutdown_calls+1;return ... end
local env=setmetatable({profile=profile,module_hash=function()end,platform=function()return api end,recorder=recorder,
 compat_spec={known_builds={}},compat={start=function()return {step=function()assert(interfaces_ok,'interface_not_compatible');return profile end}end},
 config={parse=function()return {m102={driver=112}},{ }end},input={new=function()return {poll=function()return {}end}end},
 sampler={new=function()return {capture=function()read_calls=read_calls+1;return {avatars={},vehicles={},state='not_in_mission'}end}end},
 update=original_update,shutdown=original_shutdown,os={getenv=function()return nil end,date=function()return '20260924-120000'end}}, {__index=_G})
CowboyBingusModLoader=loader
local fn=assert(loadstring(source));setfenv(fn,env);fn()
for i=1,181 do now=i/60;local a,b,c,d=env.update(7,9);assert(a==nil and b=='kept' and c==nil and d==42)end
assert(read_calls==2 and update_calls==181)
local tag=VehicleSeatNetworkDiagnostic;assert(tag.read_only and tag.status:find('recording'))
local previous=env.update;fn();assert(env.update==previous,'duplicate wrapper')
assert(env.shutdown('ok')=='ok' and shutdown_calls==1)
assert(files[tag.filename].closed and table.concat(files[tag.filename].lines):find('shutdown'))
-- New file hash is informational; incompatible interface evidence stops reads.
rawset(_G,'VehicleSeatNetworkDiagnostic',nil);api.hash_module=function()return 'new_build'end;interfaces_ok=false
env.update=original_update;env.shutdown=original_shutdown;env.sampler.new=function()error('should not collect')end
fn();for _=1,180 do env.update(7,9)end
assert(VehicleSeatNetworkDiagnostic.status=='disabled' and VehicleSeatNetworkDiagnostic.error:find('interface_not_compatible'))
rawset(_G,'VehicleSeatNetworkDiagnostic',nil)
print('PASS entry: callback coexistence/return forwarding, delayed startup, unique log, shutdown, duplicate guard and incompatible-layout refusal')
