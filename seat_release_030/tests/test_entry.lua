-- Exact module prefixes and real input/controller/dispatcher; engine effects are explicit doubles.
local root='work/seat_release_030/'
local function module(name)return assert(loadfile(root..'src/'..name..'.lua'))()end
local policy,input=module('policy'),module('input')
local config=module('config')
local profiles=module('profile').tables
local shared_snapshot={}
local source_file=assert(io.open(root..'entry.lua','rb'));local source=source_file:read('*a');source_file:close()
local real_dispatcher=module('dispatcher')
local now,clock_frames=0,0
local enhanced,fail_compat,mission,count=false,false,false,1
local pressed={},nil
local reads,network_steps,solo_direct,native_calls,trace_starts,trace_stops,poll_count,original_calls=0,0,0,0,0,0,0,0
local gate_pulses=0
local function seat(node)
 local d=profiles.m102;local occupied={}
 for i=0,4 do occupied[i]=i==node end
 shared_snapshot={vehicle='m102',transition=26,profile=d,node=node,identity='actual_fixture_identity',
  player_count=count,peer_count=count,owned=true,active=false,mask=2^node,resource='fixture_resource',occupied=occupied,seaters=9,avatar=7}
end
local function native_target(target)native_calls=native_calls+1;seat(target)end
local snap={capture=function()reads=reads+1;if mission then shared_snapshot.player_count=count;shared_snapshot.peer_count=count;return shared_snapshot end end,
 current=function()return true end,predictions=function(s)
  if s.node==0 then return 1,-1 elseif s.node==1 then return -1,0 elseif s.node==2 then return 3,-1 elseif s.node==3 then return -1,2 else return -1,-1 end
 end}
local native={next=function()local n=snap.predictions(shared_snapshot);native_target(n)end,
 previous=function()local _,p=snap.predictions(shared_snapshot);native_target(p)end}
local actual_input=input.new
local tracked_input={new=function(keys,api)
 local p=actual_input(keys,api);local f=p.poll
 function p:poll(...)poll_count=poll_count+1;return f(self,...)end
 return p
end}
local closed=0
local log={write=function(self)return self end,flush=function()return true end,close=function()closed=closed+1 end}
CowboyBingusModLoader={version=17,api=1,log_directory=root..'tests',open_log=function()return log end}
local api={now=function()return now end,down=function(key)return pressed[key]or false end,
 focused=function()return true end,input_allowed=function()return true end,module=function()return 1 end,
 config_directory=function()return root..'tests/config_fixture'end,read=function()return nil end}
local env=setmetatable({
 MODE='enhanced',snapshot=snap,bind_native=function()return native end,seat_dispatcher=real_dispatcher,
 Controller=module('controller')(policy,snap,tracked_input),profile={},policy=policy,input=tracked_input,
 normal_compat_spec={},compat_spec={},module_hash=function()return 'unused'end,
 normal_compat={start=function()return {step=function()return {functions={},tables={},capabilities={normal=true,enhanced=false}}end}end},
 compat={start=function()return {step=function()if fail_compat then error('simulated_unknown_optional_interface')end;return {functions={},tables={},capabilities={normal=true,enhanced=enhanced}}end}end},
 config={load=function()return config.parse(config.template()),{},'fixture/VehicleSeatSwitch.ini','existing'end},
 platform=function()return api end,pages=function(a)return a end,
 sampler={new=function()return {capture=function()return {state=mission and 'mission'or'not_in_mission'}end}end},
 transport=function()
  local t={active=false}
  function t:start()trace_starts=trace_starts+1;self.active=true end
  function t:health()end
  function t:stop()trace_stops=trace_stops+1;self.active=false end
  return t
 end,
 authority_observe={new=function()return {}end},routing={new=function()return {}end},
 transaction=function()return {}end,sender=function()return {}end,
 animation_inspect={new=function()return {}end},animation_sender=function()return {}end,
 binding_inspect={new=function()return {}end},binding_sender=function()return {}end,
 sync_adapter={new=function()return {}end},
 solo_native=function()
  return {next=native.next,previous=native.previous,available=function()return true end,
   prepare=function()shared_snapshot.active=false end,
   direct=function(s,target)assert(count==1);solo_direct=solo_direct+1;seat(target)end}
 end,
 input_gate=function()
  return {active=false,pulse=function()gate_pulses=gate_pulses+1 end,take=function()return {},{},{}end,
   control_down=function(_,key)return api.down(key)end,close=function()end}
 end,
 update=function()original_calls=original_calls+1;return nil,'forwarded',nil,7 end,
 shutdown=function()return 'shutdown_forwarded'end,
},{__index=_G})
env.reservation_tools={scope=module('scope'),mounted_reader=function()return {}end,entrance=function()return {}end,
 steering_reset=function()return {}end,owned_transaction=function()return {}end,release_acquired=function()return {}end,
 probe={eligible=function()return true end,new=function()
  local p={pending=false,phase='waiting'}
  function p:step(target,time)
   network_steps=network_steps+1;self.ready_at=time;self.observed={native=shared_snapshot}
   if target~=nil then seat(target);return true end
  end
  function p:close()end
  return p
 end}}
local previous,previous_shutdown=env.update,env.shutdown
local function tick(n)
 for i=1,n do now=now+.02;clock_frames=clock_frames+1
  local a,b,c,d=env.update();assert(a==nil and b=='forwarded'and c==nil and d==7)
 end
end
local function restart(code)
 VehicleSeatSwitch=nil;VehicleSeatNetworkDiagnostic=nil
 env.update=previous;env.shutdown=previous_shutdown
 local chunk=assert(loadstring(code or source));setfenv(chunk,env);chunk()
end
local function tap(key)
 pressed[key]=true;tick(1);pressed[key]=nil;tick(30)
end
enhanced=true;seat(1);restart();tick(610)
assert(VehicleSeatSwitch.effective_mode=='enhanced'and trace_starts==1 and VehicleSeatSwitch.transport_ready,tostring(VehicleSeatSwitch.error)..' status='..tostring(VehicleSeatSwitch.status)..' trace='..trace_starts)
mission=true;tick(6);tap(116);assert(solo_direct==1 and shared_snapshot.node==4,'solo cross route missing')
tap(113);assert(solo_direct==2 and shared_snapshot.node==1)
count=3;tick(10);tap(116);assert(shared_snapshot.node==4 and network_steps>0,tostring(VehicleSeatSwitch.error)..' status='..tostring(VehicleSeatSwitch.status)..' node='..shared_snapshot.node)
tap(113);assert(shared_snapshot.node==1)
count=4;tick(10);tap(116);assert(shared_snapshot.node==4)
tap(113);assert(shared_snapshot.node==1)
count=1;tick(10);tap(116);assert(shared_snapshot.node==4 and solo_direct==3)
-- Held input crossing a membership boundary must not become an extra request.
pressed[116]=true;tick(1);local before=solo_direct;count=3;tick(10);count=1;tick(10)
assert(solo_direct==before);pressed[116]=nil;tick(20)
-- New packaging has no background physics/private-pose observers or recorder.
mission=false;tick(5);local baseline=reads;tick(500)
assert(reads-baseline<=101,'idle snapshot polling exceeds ten Hz')
assert(poll_count<=clock_frames+20,'more than one poller ran during ordinary updates')
assert(env.shutdown()=='shutdown_forwarded'and trace_stops==1)
print('PASS single key poller, solo/three/four/solo routing, held-edge transition suppression, bounded idle snapshot cadence, original return/shutdown forwarding')

enhanced=false;count=2;mission=false;restart();tick(610);mission=true;seat(1);tick(6)
tap(112);assert(shared_snapshot.node==0 and VehicleSeatSwitch.effective_mode=='normal')
env.shutdown()
fail_compat=true;restart();tick(610)
assert(VehicleSeatSwitch.effective_mode=='normal'and not VehicleSeatSwitch.error,'optional interface failure must preserve native Normal')
fail_compat=false;env.shutdown()
VehicleSeatNetworkDiagnostic={};VehicleSeatSwitch=nil;env.update=previous;env.shutdown=previous_shutdown
local chunk=assert(loadstring(source));setfenv(chunk,env);chunk();tick(181)
assert(VehicleSeatSwitch.error:find('disable_old_seat_diagnostic'))
VehicleSeatNetworkDiagnostic=nil
print('PASS optional Enhanced/core-network failure preserves independently validated Normal; conflicting old diagnostics refused')

-- Execute the exact archive-bound static prefix and supply only declared backend doubles at the entry boundary.
local substitutions={'snapshot','bind_native','seat_dispatcher','Controller','platform','compat','normal_compat','config','input',
 'authority_observe','transaction','sender','sync_adapter','sampler','pages','routing','transport','input_gate',
 'animation_inspect','animation_sender','binding_inspect','binding_sender','reservation_tools','solo_native'}
local f=assert(io.open(root..'bundled_enhanced.lua','rb'));local bundle=f:read('*a');f:close()
assert(bundle:sub(-#source)==source)
local bridge='\n';for _,name in ipairs(substitutions)do bridge=bridge..name..'=__fixture.'..name..'\n'end
env.__fixture=env;enhanced=true;mission=false;count=1
restart(bundle:sub(1,#bundle-#source)..bridge..source);tick(610)
assert(VehicleSeatSwitch.version=='0.3.0'and VehicleSeatSwitch.transport_ready)
assert(env.shutdown()=='shutdown_forwarded')
print('PASS exact Enhanced bundle prefix composition and module/spec wiring')

local f=assert(io.open(root..'src/normal_entry.lua','rb'));local normal_source=f:read('*a');f:close()
f=assert(io.open(root..'bundled_normal.lua','rb'));bundle=f:read('*a');f:close()
assert(bundle:sub(-#normal_source)==normal_source)
bridge='\n';for _,name in ipairs({'snapshot','bind_native','Controller','platform','compat','config','input'})do bridge=bridge..name..'=__fixture.'..name..'\n'end
env.MODE='normal';env.compat=env.normal_compat;enhanced=false;count=4;mission=true;seat(1)
restart(bundle:sub(1,#bundle-#normal_source)..bridge..normal_source);tick(190)
tap(112);assert(shared_snapshot.node==0 and VehicleSeatSwitch.mode=='normal')
tap(116);assert(shared_snapshot.node==0,'Normal must retain original cross-region restrictions')
assert(env.shutdown()=='shutdown_forwarded')
print('PASS exact Normal bundle preserves native group restrictions without multiplayer hooks')
