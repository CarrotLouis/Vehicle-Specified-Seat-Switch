"""Replay exact deployment components + entry, with native backend doubles.

Use the real deployed Windows adapter rather than a fixture that invents ffi.
The previous package must reproduce the missing-ffi driver read failure.
Saved code/synthetic heaps are read only. No game hooks or live process access.
"""
from pathlib import Path
import json
import zipfile

R=Path(__file__).resolve().parent
W=R.parent
P=W.parent
source=(R/'bundled.lua').read_text(encoding='utf-8')
entry=(R/'entry.lua').read_text(encoding='utf-8')
assert source.endswith(entry)
prefix=source[:-len(entry)]
exports='\nreturn {platform=platform,physics_reader=physics_reader,driver_watch=driver_watch,recorder=recorder}\n'
(R/'components.lua').write_text(prefix+exports,encoding='utf-8')
with zipfile.ZipFile(P/'outputs/Vehicle-Seat-Driver-Observer-0.25.0.zip')as z:
    old=z.read('Source/driver_observer.lua').decode('utf-8')
old_entry=(W/'seat_driver_observer/entry.lua').read_text(encoding='utf-8')
assert old.endswith(old_entry)
(R/'previous_components.lua').write_text(old[:-len(old_entry)]+exports,encoding='utf-8')

# Keep the complete saved-native-code fixture, replacing ONLY its component
# loading and backend interceptions. Actual bundle exports supply the adapter,
# reader, watcher and recorder. Missing FFI is never filled by the fixture.
fixture=(W/'seat_pose_trace_test/test_physics_reader.lua').read_text(encoding='utf-8')
fixture=fixture[:fixture.index('\nlocal cases=0')]
fixture=fixture.replace("local maker=assert(loadfile('work/seat_pose_trace_test/physics_reader.lua'))()",'local maker=components.physics_reader')
fixture=fixture.replace("local api={module=function(n)return ffi.cast('uint8_t *',bases[n])end}",
    "local api=components.platform(function()return 'saved-capture'end)\n local adapter_ffi=api.ffi\n api.module=function(n)return ffi.cast('uint8_t *',bases[n])end")
fixture=fixture.replace('},{__index=ffi})\n api.ffi=proxy;',
    '},{__index=adapter_ffi})\n if adapter_ffi then api.ffi=proxy end;')
fixture=fixture.replace('function()return calls,writes end,function()torn=true end,function()nonfinite=true end,reader',
    'function()return calls,writes end,function()torn=true end,function()nonfinite=true end,reader,api,p,compat')
assert 'local adapter_ffi=api.ffi'in fixture and 'if adapter_ffi then api.ffi=proxy end'in fixture
fixture=fixture.replace('work/seat_pose_trace_test/motion_spec.lua','work/seat_driver_observer_fix/motion_spec.lua')

base="local components=assert(loadfile('work/seat_driver_observer_fix/components.lua'))()\n"+fixture
tests=r'''
local read,put,f,counts,_,_,physical,api,profile,compat=fixture(2,false,41,false)
assert(api.ffi and api.ffi.new and api.ffi.copy and api.ffi.cast,'exact deployed adapter must supply FFI')
local first=read();assert(first.actor_count==41 and first.native_speed==5)
-- An end-to-end entry/driver run with the actual adapter and physical reader.
-- Only snapshot, context/property lookup and native-hook backend are doubles.
local now,arms,stops,events,files=0,0,0,{},{}
local owner,serial='DRIVER',1
local v=f.v;v.owned_local=true;v.transition_type=26;v.seat_count=5
local a={id=33,unit=44,is_local=true,owned_local=true,seat={collection=v.id,current=0,transitioning=0}}
local sample={state='mission',mission_value=1,player_count=2,peer_count=2,local_count=1,avatars={a},vehicles={v}}
api.now=function()return now end;api.pid=function()return 77 end;api.hash_module=function()return 'saved-capture'end
profile.capabilities={enhanced=true}
CowboyBingusModLoader={api=1,version=17,open_log=function(name)
 local file={text='',write=function(self,s)self.text=self.text..s;return self end,flush=function()return true end,close=function()return true end}
 files[name]=file;return file
end}
VehicleSeatDriverObserver=nil;VehicleSeatNetworkDiagnostic=nil;VehicleSeatSwitch=nil;Hd2TankSeatSwitch=nil;Hd2TankSeatRoles=nil
local path='work/seat_driver_observer_fix/entry.lua';local h=assert(io.open(path));local entry=h:read('*a');h:close()
local env=setmetatable({platform=function()return api end,pages=function(x)return x end,profile={},compat_spec={},module_hash={},
 compat={start=function()return {step=function()return profile end}end},
 sampler={new=function()return {capture=function()return sample end}end},recorder=components.recorder,
 physics_reader=function()return physical end,
 handoff_reader=function()return {read_vehicle=function()return {engine_owner_hex=owner,engine_serial=serial}end}end,
 driver_context=function()return {read=function()return {local_peer_hex='DRIVER',selfpeer='D',coordinator='D',coordinator_hex='DRIVER',read_count=23}end}end,
 body_flags_reader=function()return nil end,motion_helper={},
 pose_trace=function()return {update=function()end,arm_driver=function(_,vehicle,s,avatar,p)
  assert(vehicle.id==v.id and avatar.seat.current==0 and p.actor_handle==f.aid);arms=arms+1
 end,disarm=function()stops=stops+1 end,close=function()stops=stops+1 end}end,
 driver_watch=components.driver_watch,
 os={date=function()return 'replay'end},
 update=function()return nil,'forwarded',nil,7 end,shutdown=function()return 'shutdown_forwarded'end}, {__index=_G})
local chunk=assert(loadstring(entry));setfenv(chunk,env);chunk()
local function tick(n)for i=1,n do now=now+.02;local a,b,c,d=env.update();assert(a==nil and b=='forwarded'and c==nil and d==7)end end
tick(210);assert(arms>=1 and VehicleSeatDriverObserver.status~='disabled',VehicleSeatDriverObserver.error)
owner='INSTALLER';serial=2;v.owned_local=false;tick(4)
owner='DRIVER';serial=3;v.owned_local=true;tick(4)
local text=files[VehicleSeatDriverObserver.filename].text
assert(text:find('driver_watch_started')and text:find('driver_physics_sample')and text:find('driver_authority_observed_change'))
assert(not text:find('driver_watch_gap')and not text:find('read_gap'))
local calls,writes=counts();assert(calls>2 and writes==0)
a.seat.current=1;tick(4);local paused=calls;tick(30);calls,writes=counts();assert(calls==paused and writes==0)
assert(env.shutdown()=='shutdown_forwarded'and stops>=2)
print('PASS exact deployed components plus entry: real read-only adapter FFI, saved-code/41-actor physical reads, driver entry/loan/return/leave, telemetry present, original tuple/shutdown, zero writes; native outputs/context/property/hook backend mocked')
'''
(R/'test_bundle_driver.lua').write_text(base+tests,encoding='utf-8')
negative="local components=assert(loadfile('work/seat_driver_observer_fix/previous_components.lua'))()\n"+fixture+r'''
local read,_,_,counts,_,_,reader,api=fixture(2,false,41,false)
assert(api.ffi==nil,'prior adapter should reproduce the captured missing FFI')
local ok,why=pcall(read)
assert(not ok and tostring(why):find("upvalue 'ffi'"),tostring(why))
local calls,writes=counts();assert(calls==0 and writes==0)
print('PASS negative control: exact 0.25.0 deployment reproduces missing-ffi first-driver failure before native getters/hooks; no fabricated zero speed')
'''
(R/'test_previous_bundle_failure.lua').write_text(negative,encoding='utf-8')
print('PASS exact final/old deployment replay generated; old failure required as negative control')
