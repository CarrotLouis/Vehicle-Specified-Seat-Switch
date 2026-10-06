local recorder=assert(loadfile('work/seat_network_diagnostic/recorder.lua'))()
local f=assert(io.open('work/seat_tank_pose_fix/entry.lua'));local source=f:read('*a');f:close()
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
 platform=function()return {now=function()return now end,pid=function()return 1 end,module=function()return 1 end,hash_module=function()return 'unknown'end,input_allowed=function()return false end}end,
 compat={start=function(_,_,_,_,mode)assert(mode=='enhanced');return {step=function()return {layout_schema='test',capabilities={enhanced=enhanced}}end}end},
 config={parse=function()return {},{}end},input={new=function()return {poll=function()return {}end}end},recorder=recorder,
 authority_observe={new=function()return {}end},sync_probe={new=function()return {step=function()end,close=function()end}end},
 transaction=function()return {}end,sender=function()return {}end,sync_adapter={new=function()return {}end},
 sampler={new=function()return {capture=function()return {avatars={},vehicles={},state=mission and 'mission'or'not_in_mission'}end}end},
 pages=function(a)return a end,routing={new=function()return {}end},
 transport=function()local t={active=false};function t:start()if fail_start then error('synthetic_install_failure')end;started=started+1;self.active=true end;function t:drain()end;function t:health()end;function t:stop()stopped=stopped+1;self.active=false end;return t end,
 update=function()original_calls=original_calls+1;return nil,'forwarded',nil,7 end,
 shutdown=function()return 'shutdown_forwarded'end,
 os={getenv=function()return nil end,date=function()return 'test'end}},{__index=_G})
local previous_update=env.update
local function tick(n)for _=1,n do now=now+.02;local a,b,c,d=env.update();assert(a==nil and b=='forwarded'and c==nil and d==7)end end
local function restart()
 VehicleSeatNetworkDiagnostic=nil;env.update=previous_update
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
-- Real entry/recorder path: a failed transport log write must keep pending cleanup alive.
enhanced=true
local pending={pending=false,cancelled=false,steps=0,close=function()end}
function pending:cancel()self.cancelled=true end
function pending:step()if self.pending then self.steps=self.steps+1 end end
env.sync_probe={new=function()return pending end}
local failing=false
env.transport=function(_,_,_,_,writer)
 local t={active=false}
 function t:start()self.active=true end
 function t:health()end
 function t:drain()if failing then writer:write({event='native_send_test'},now)end end
 function t:stop()self.active=false end
 return t
end
restart();tick(601);pending.pending=true
files[VehicleSeatNetworkDiagnostic.filename].write=function()error('synthetic_disk_failure')end
failing=true;tick(20)
assert(pending.cancelled and pending.steps>0 and VehicleSeatNetworkDiagnostic.status~='disabled')
assert(VehicleSeatNetworkDiagnostic.logging_failed)
pending.pending=false;tick(1);assert(VehicleSeatNetworkDiagnostic.status=='log_closed_experiment_disabled')
print('PASS transport log disk failure preserves pending cleanup; stops new work after return')
