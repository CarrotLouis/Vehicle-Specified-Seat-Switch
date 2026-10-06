local recorder=assert(loadfile('work/seat_network_diagnostic/recorder.lua'))()
local f=assert(io.open('work/seat_driver_observer/entry.lua'));local source=f:read('*a');f:close()
local now,original_calls,updates,closes=0,0,0,0
local bad_log,bad_data,fail_capture,fail_init,enhanced=false,false,false,false,true
local files={}
CowboyBingusModLoader={version=17,api=1,open_log=function(name)
 local file={text='',write=function(self,x)if bad_log or bad_data and name:find('VehicleSeatDriverObserver%-')then error('synthetic_disk_full')end;self.text=self.text..x;return self end,
  flush=function()return true end,close=function()return true end};files[name]=file;return file
end}
local env=setmetatable({profile={},compat_spec={},module_hash={},
 platform=function()return {module=function()return 0 end,now=function()return now end,pid=function()return 123 end,hash_module=function()return 'hash'end}end,
 pages=function(a)return a end,
 compat={start=function(_,_,_,_,mode)assert(mode=='enhanced');return {step=function()return {capabilities={enhanced=enhanced}}end}end},
 sampler={new=function()return {capture=function()if fail_capture then error('snapshot_fault')end;return {state='not_in_mission',avatars={},vehicles={}}end}end},
 physics_reader=function()if fail_init then error('reader_constructor_fault')end;return {}end,
 handoff_reader=function()return {}end,driver_context=function()return {}end,
 body_flags_reader=function()return {}end,motion_helper={},
 pose_trace=function()return {update=function()end,close=function()closes=closes+1 end}end,
 driver_watch=function()return {update=function()updates=updates+1 end,gap=function()updates=updates+1 end,close=function()closes=closes+1 end}end,
 recorder=recorder,os={date=function()return 'test'end},
 update=function()original_calls=original_calls+1;return nil,'original',nil,7 end,
 shutdown=function()return 'shutdown_original'end},{__index=_G})
local previous_update,previous_shutdown=env.update,env.shutdown
local function restart()
 VehicleSeatDriverObserver=nil;env.update=previous_update;env.shutdown=previous_shutdown
 local chunk=assert(loadstring(source));setfenv(chunk,env);chunk()
end
local function tick(n)for _=1,n do now=now+.01;local a,b,c,d=env.update();assert(a==nil and b=='original'and c==nil and d==7)end end
VehicleSeatNetworkDiagnostic=nil;VehicleSeatSwitch=nil;Hd2TankSeatSwitch=nil;Hd2TankSeatRoles=nil
restart();tick(300);assert(updates>0 and VehicleSeatDriverObserver.status:find('ready_passive'))
assert(files[VehicleSeatDriverObserver.filename].text:find('"ini_access":false'))
assert(env.shutdown()=='shutdown_original'and closes==2)
for _,tag in ipairs({'VehicleSeatNetworkDiagnostic','VehicleSeatSwitch','Hd2TankSeatSwitch','Hd2TankSeatRoles'})do
 _G[tag]={};restart();local before=updates;tick(190);assert(VehicleSeatDriverObserver.status=='disabled'and updates==before)
 _G[tag]=nil
end
enhanced=false;restart();tick(190);assert(VehicleSeatDriverObserver.error:find('interfaces_unavailable'));enhanced=true
fail_init=true;restart();tick(190);assert(VehicleSeatDriverObserver.error:find('reader_constructor_fault'));fail_init=false
restart();tick(190);fail_capture=true;local before=updates;tick(20);assert(updates>before and VehicleSeatDriverObserver.status~='disabled');fail_capture=false
bad_log=true;fail_capture=true;tick(10);assert(VehicleSeatDriverObserver.status=='disabled'and VehicleSeatDriverObserver.error:find('synthetic_disk_full'));bad_log=false;fail_capture=false
restart();tick(190);local before=closes;bad_data=true;fail_capture=true;tick(10)
assert(closes==before+2 and (VehicleSeatDriverObserver.status:find('log_closed')or VehicleSeatDriverObserver.status=='disabled'), 'data-log failure must close native observer even if status log works')
local closed_count=closes;tick(20);assert(closes==closed_count,'closed observer is stopped once')
bad_data=false;fail_capture=false
print('PASS passive entry: original update/shutdown returns, sampling clock, four conflict guards, compatibility/init failure, outer snapshot gap, log-write cleanup, no INI/config/input pipeline')
