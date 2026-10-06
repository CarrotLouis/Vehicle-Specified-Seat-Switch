local recorder=assert(loadfile('work/seat_network_diagnostic/recorder.lua'))()
local f=assert(io.open('work/seat_protocol_diagnostic/entry.lua'));local source=f:read('*a');f:close()
local now,started,stopped,original_calls=0,0,0,0
local mission,fail_start=false,false
local files={}
CowboyBingusModLoader={version=16,api=1,open_log=function(name)
 local file={text='',write=function(self,x)self.text=self.text..x;return self end,flush=function()return true end,close=function()return true end};files[name]=file;return file
end}
VehicleSeatSwitch={version='0.2.4',status='starting'}
local env=setmetatable({profile={},compat_spec={known_builds={}},
 platform=function()return {now=function()return now end,pid=function()return 1 end,module=function()return 1 end,hash_module=function()return 'unknown'end}end,
 compat={start=function()return {step=function()return {layout_schema='test'}end}end},
 config={parse=function()return {},{}end},input={new=function()return {poll=function()return {}end}end},recorder=recorder,
 sampler={new=function()return {capture=function()return {avatars={},vehicles={},state=mission and 'mission' or 'not_in_mission'}end}end},
 protocol=function()local t={active=false};function t:start()if fail_start then error('synthetic_install_failure')end;started=started+1;self.active=true end;function t:drain()end;function t:stop()stopped=stopped+1;self.active=false end;return t end,
 update=function()original_calls=original_calls+1;return nil,'forwarded',nil,7 end,
 shutdown=function()return 'shutdown_forwarded'end,
 os={getenv=function()return nil end,date=function()return 'test'end}}, {__index=_G})
local function tick(n)for _=1,n do now=now+.02;local a,b,c,d=env.update();assert(a==nil and b=='forwarded' and c==nil and d==7)end end
local chunk=assert(loadstring(source));setfenv(chunk,env);chunk()
tick(650);assert(started==0,'must wait for gameplay initialization')
VehicleSeatSwitch.status='idle';mission=true;tick(10);assert(started==0,'must wait for ship')
mission=false;tick(1);assert(started==1 and VehicleSeatNetworkDiagnostic.protocol_ready)
tick(30);assert(started==1 and original_calls==691)
assert(env.shutdown()=='shutdown_forwarded' and stopped==1)
-- Install failure must stop diagnostics while preserving the previous callback.
VehicleSeatNetworkDiagnostic=nil;fail_start=true;chunk();tick(601)
assert(VehicleSeatNetworkDiagnostic.status=='disabled' and VehicleSeatNetworkDiagnostic.error:find('synthetic_install_failure'))
assert(started==1 and stopped==2)
print('PASS protocol entry: gameplay-init and ship gates, one install, callback forwarding, shutdown/installation-failure cleanup')
