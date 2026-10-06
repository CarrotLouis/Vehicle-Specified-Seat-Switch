local recorder=assert(loadfile('work/seat_network_diagnostic/recorder.lua'))()
local f=assert(io.open('work/seat_reservation_fleet_test/entry.lua','rb'));local source=f:read('*a');f:close()
local ffi=require('ffi')
local real_platform=assert(loadfile('work/seat_pose_trace_test/platform.lua'))()
local scope=assert(loadfile('work/seat_reservation_fleet_test/scope.lua'))()
local real_probe=assert(loadfile('work/seat_reservation_fleet_test/probe.lua'))()(scope)
local now,started,stopped,original_calls=0,0,0,0
local mission,fail_start,enhanced=false,false,true
local files={}
CowboyBingusModLoader={version=16,api=1,open_log=function(name)
 local file={text='',write=function(self,x)self.text=self.text..x;return self end,flush=function()return true end,close=function()return true end};files[name]=file;return file
end}
VehicleSeatSwitch=nil
local env=setmetatable({snapshot={capture=function()return nil end},bind_native=function()return {}end,seat_dispatcher={new=function(_,_,_,_,_,_,probe)return {update=function()probe:step()end}end},profile={},compat_spec={known_builds={}},
 binding_inspect={new=function()return {}end},binding_sender=function()return {}end,
 input_gate=function()return {pulse=function()end,take=function()return {}end,control_down=function()return false end,close=function()end}end,input_helper={},
 animation_inspect={new=function()return {}end},animation_sender=function()return {}end,
 animation_watch=function()return {sample=function()end,arm=function()end,close=function()end}end,
 fall_repair=function()return {update=function()end,needs_check=function()return false end}end,tank_driver=function()return {}end,
 room_watch=function()return {update=function()end}end,steering_watch=function()return {update=function()end}end,
 ownership_loan_only=function(a)return a end,
 motion_watch=function()return {update=function()end}end,fleet_policy={},
 physics_reader=function()return {}end,handoff_reader=function()return {}end,spin_reader=function()return {}end,physics_watch=function()return {update=function()end}end,
 pose_trace=function()return {update=function()end,close=function()end}end,motion_helper={},body_flags_reader=function()return {}end,
 platform=function()local a=real_platform(function()return 'unknown'end);assert(a.ffi==ffi and type(a.read)=='function'and type(a.replace)=='function');a.now=function()return now end;a.pid=function()return 1 end;a.module=function()return 1 end;a.input_allowed=function()return false end;return a end,
 compat={start=function(_,_,_,_,mode)assert(mode=='enhanced');return {step=function()return {layout_schema='test',capabilities={enhanced=enhanced}}end}end},
 config={parse=function()return {},{}end},input={new=function()return {poll=function()return {}end}end},recorder=recorder,
 authority_observe={new=function()return {}end},sync_probe={new=function()return {step=function()end,close=function()end}end},
 transaction=function()return {}end,sender=function()return {}end,sync_adapter={new=function()return {capture=function()return nil,'not_in_mission'end}end},
 sampler={new=function()return {capture=function()return {avatars={},vehicles={},state=mission and 'mission'or'not_in_mission'}end}end},
 pages=function(a)return a end,routing={new=function()return {}end},
 transport=function()local t={active=false};function t:start()if fail_start then error('synthetic_install_failure')end;started=started+1;self.active=true end;function t:drain()end;function t:health()end;function t:stop()stopped=stopped+1;self.active=false end;return t end,
 update=function()original_calls=original_calls+1;return nil,'forwarded',nil,7 end,
 shutdown=function()return 'shutdown_forwarded'end,
 os={getenv=function()return nil end,date=function()return 'test'end}},{__index=_G})
env.reservation_tools={probe=real_probe,scope=scope,mounted_reader=function(a)assert(a.ffi==ffi);return {}end,entrance=function(a)assert(a.ffi==ffi);return {}end,motion_watch=function()return {update=function()end}end,
 owned_transaction=function(a)assert(a.ffi==ffi);return {}end,release_acquired=function(a)assert(a.ffi==ffi);return {}end,
 steering_reset=assert(loadfile('work/seat_reservation_fleet_test/steering_reset.lua'))(),spin_reader=function()error('must not poll idle')end}
local previous_update=env.update
local previous_shutdown=env.shutdown

env.motion_tools={pose_trace=env.pose_trace,body_flags_reader=env.body_flags_reader,helper={},
 physics_reader=env.physics_reader,handoff_reader=env.handoff_reader,physics_watch=env.physics_watch}
local function tick(n)for _=1,n do now=now+.02;local a,b,c,d=env.update();assert(a==nil and b=='forwarded'and c==nil and d==7)end end
local function restart()
 VehicleSeatNetworkDiagnostic=nil;env.update=previous_update;env.shutdown=previous_shutdown
 local chunk=assert(loadstring(source));setfenv(chunk,env);chunk()
end
mission=true;restart();tick(650);assert(started==0)
mission=false;tick(1);assert(started==1 and VehicleSeatNetworkDiagnostic.transport_ready)
tick(30);assert(started==1 and original_calls==681)
assert(env.shutdown()=='shutdown_forwarded'and stopped==1)
fail_start=true;restart();tick(601)
assert(VehicleSeatNetworkDiagnostic.status=='disabled'and VehicleSeatNetworkDiagnostic.error:find('synthetic_install_failure'))
assert(started==1);fail_start=false
VehicleSeatSwitch={};restart();tick(601)
assert(VehicleSeatNetworkDiagnostic.status=='disabled'and VehicleSeatNetworkDiagnostic.error:find('disable_gameplay_companion'));assert(started==1)
VehicleSeatSwitch=nil;Hd2TankSeatSwitch={};restart();tick(601)
assert(VehicleSeatNetworkDiagnostic.error:find('disable_TankSeatKit'));assert(started==1);Hd2TankSeatSwitch=nil
enhanced=false;restart();tick(601)
assert(VehicleSeatNetworkDiagnostic.error:find('interfaces_unavailable'));assert(started==1)
print('PASS entry ship/init/Normal/interface/conflicting-mod gates, callback returns, cleanup')

-- Run the EXACT shipped module prefix, then substitute only external backends
-- at the entry boundary. This exercises actual grouping/local names/wiring.
enhanced=true
local f=assert(io.open('work/seat_reservation_fleet_test/bundled.lua','rb'));local bundle=f:read('*a');f:close()
assert(bundle:sub(-#source)==source,'entry must be exact bundle suffix')
local substitutions={'snapshot','bind_native','seat_dispatcher','platform','compat','config','input','authority_observe','transaction','sender','sync_adapter','sampler','pages','routing','transport','input_gate','animation_watch','animation_inspect','animation_sender','binding_inspect','binding_sender','motion_tools','reservation_tools'}
local bridge='\n'
for _,name in ipairs(substitutions)do bridge=bridge..name..'=__fixture.'..name..'\n'end
env.__fixture=env
source=bundle:sub(1,#bundle-#source)..bridge..source
restart();tick(601);assert(VehicleSeatNetworkDiagnostic.transport_ready and VehicleSeatNetworkDiagnostic.version=='0.28.0')
assert(env.shutdown()=='shutdown_forwarded')
print('PASS exact shipped bundle prefix/new factory grouping, real platform.ffi and real probe constructor; ship lifecycle and original returns')
