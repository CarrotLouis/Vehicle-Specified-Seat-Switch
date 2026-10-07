-- Exact module prefixes and real input/controller/dispatcher; engine effects are explicit doubles.
local root='work/'
local function module(name)return assert(loadfile(root..'src/'..name..'.lua'))()end
local policy,input=module('policy'),module('input')
local runtime_policy=module('mode_policy')(policy,function()return VehicleSeatSwitch and VehicleSeatSwitch.effective_mode or 'normal'end)
local made_controllers={}
local config=module('config')
local profiles=module('profile').tables
local shared_snapshot={}
local options,bindings={},{}
ModOptionsMenu={api=1,version=3,register_option=function(id,spec)if options[id]==nil then options[id]=spec.default end;return true end,get=function(id)return options[id]end}
ModBindingsMenu={api=1,version=3,register_binding=function()return true end,is_down=function(id)return bindings[id]or false end}
local text=module('bingus_text');text.registry().steam_language='en'
local source_file=assert(io.open(root..'src/entry.lua','rb'));local source=source_file:read('*a');source_file:close()
local real_dispatcher=module('dispatcher')
local now,clock_frames=0,0
local enhanced,fail_compat,mission,count=false,false,false,1
local pressed={}
local reads,network_steps,solo_direct,native_calls,trace_starts,trace_stops,poll_count,original_calls=0,0,0,0,0,0,0,0
local gate_pulses=0;local inject_fault=false
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
local api={in_image=function()return false end,describe=function()return {}end,now=function()return now end,down=function(key)return pressed[key]or false end,
 focused=function()return true end,input_allowed=function()return true end,module=function()return 1 end,
 config_directory=function()return root..'tests/config_fixture'end,read=function()return nil end}
local env=setmetatable({
 MODE='full',i18n=module('i18n'),performance_data=module('performance_data'),performance_data_spec=module('performance_data_spec'),menu_integration=module('menu'),bingus_text=text,menu_locales=module('menu_locales'),input_source=module('input_source'),
 runtime_policy=runtime_policy,snapshot=snap,bind_native=function()return native end,seat_dispatcher=real_dispatcher,
 Controller=module('controller')(runtime_policy,snap,tracked_input),profile={},policy=policy,input=tracked_input,
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
   direct=function(s,target)if inject_fault then error('fixture_invocation_fault')end;assert(count==1);solo_direct=solo_direct+1;seat(target)end}
 end,
 input_gate=function()
  return {active=false,pulse=function()gate_pulses=gate_pulses+1 end,take=function()return {},{},{}end,
   filter=function()end,control_down=function(_,key)return api.down(key)end,close=function()end}
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
local original_new=env.Controller.new
env.Controller.new=function(...)local c=original_new(...);made_controllers[#made_controllers+1]=c;return c end
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
local prefix='vehicle_seat_tools.vss.'
local function option(id,value)options[prefix..id]=value;tick(3)end

enhanced=true;seat(1);restart();tick(610)
assert(VehicleSeatSwitch.effective_mode=='normal'and trace_starts==1 and VehicleSeatSwitch.transport_ready,tostring(VehicleSeatSwitch.error))
assert(VehicleSeatSwitch.input_strategy=='ini'and VehicleSeatSwitch.performance_block=='off')
mission=true;tick(6);tap(112);assert(shared_snapshot.node==0)
tap(116);assert(shared_snapshot.node==0 and solo_direct==0,'default Normal must not cross groups')
local controller=made_controllers[#made_controllers];assert(#made_controllers==1 and controller.mode=='enhanced')
local old_native=native_calls;local old_direct=solo_direct;local old_starts=trace_starts
option('mode',2);assert(#made_controllers==1 and made_controllers[1]==controller and native_calls==old_native and solo_direct==old_direct and trace_starts==old_starts,'variant change must not construct/call/install anything')
tap(116);assert(shared_snapshot.node==4 and solo_direct==1,'hot Enhanced solo route missing')
tap(113);assert(shared_snapshot.node==1)
count=3;tick(10);tap(116);assert(shared_snapshot.node==4 and network_steps>0,tostring(VehicleSeatSwitch.error))
tap(113);assert(shared_snapshot.node==1)
count=4;tick(10);tap(116);assert(shared_snapshot.node==4)
tap(113);assert(shared_snapshot.node==1)
count=1;tick(10);tap(116);assert(shared_snapshot.node==4 and solo_direct==3)
-- A held edge does not become a request on a member or settings transition.
pressed[116]=true;tick(1);local before=solo_direct;count=3;tick(10);count=1;tick(10)
assert(solo_direct==before);option('mode',1);option('mode',2);assert(solo_direct==before)
pressed[116]=nil;tick(20)
-- A strategy switch never edits INI or silently consumes its keys.
option('strategy',2);seat(1);tap(116);assert(shared_snapshot.node==1,'INI leaked into menu strategy')
bindings[prefix..'seat5']=true;tick(1);bindings[prefix..'seat5']=nil;tick(30)
assert(shared_snapshot.node==4,'native action route missing')
option('strategy',1);tap(113);assert(shared_snapshot.node==1)
-- Block unrelated config changes until a native request is observed complete.
local_calls=native_calls;pressed[112]=true;tick(1);assert(shared_snapshot.node==0)
options[prefix..'mode']=1;options[prefix..'strategy']=2;tick(1)
assert(VehicleSeatSwitch.settings_pending and VehicleSeatSwitch.effective_mode=='enhanced')
pressed[112]=nil;tick(3);assert(VehicleSeatSwitch.effective_mode=='normal'and VehicleSeatSwitch.input_strategy=='menu')
-- Normal restrictions hold in the resident multiplayer dispatcher too.
count=3;tick(10);local old_mutations=solo_direct
bindings[prefix..'seat2']=true;tick(1);bindings[prefix..'seat2']=nil;tick(30);assert(shared_snapshot.node==1)
before=network_steps;bindings[prefix..'seat5']=true;tick(1);bindings[prefix..'seat5']=nil;tick(30)
assert(shared_snapshot.node==1 and solo_direct==old_mutations)
mission=false;tick(5);local baseline=reads;tick(500)
assert(reads-baseline<=101,'idle snapshot polling exceeds ten Hz')
assert(env.shutdown()=='shutdown_forwarded'and trace_stops==1)
print('PASS default Normal/INI; resident Enhanced with Lua Normal restrictions; hot modes, independent sources, pending completion barrier, solo/3/4 routing, held edges, idle cadence and return/shutdown forwarding')

enhanced=false;count=2;mission=false;options[prefix..'mode']=2;options[prefix..'strategy']=1;restart();tick(610);mission=true;seat(1);tick(6)
tap(112);assert(shared_snapshot.node==0 and VehicleSeatSwitch.effective_mode=='normal')
env.shutdown();fail_compat=true;restart();tick(610)
assert(VehicleSeatSwitch.effective_mode=='normal'and not VehicleSeatSwitch.error)
fail_compat=false;env.shutdown()
VehicleSeatNetworkDiagnostic={};VehicleSeatSwitch=nil;env.update=previous;env.shutdown=previous_shutdown
local chunk=assert(loadstring(source));setfenv(chunk,env);chunk();tick(181)
assert(VehicleSeatSwitch.error and VehicleSeatSwitch.error:find('disable_old_seat_diagnostic'))
VehicleSeatNetworkDiagnostic=nil
print('PASS independent Normal fallback and old diagnostic conflict refusal')

local substitutions={'snapshot','bind_native','seat_dispatcher','Controller','platform','compat','normal_compat','config','input',
 'authority_observe','transaction','sender','sync_adapter','sampler','pages','routing','transport','input_gate',
 'animation_inspect','animation_sender','binding_inspect','binding_sender','reservation_tools','solo_native','runtime_policy'}
local f=assert(io.open(root..'build/bundled_full.lua','rb'));local bundle=f:read('*a');f:close()
assert(bundle:sub(-#source)==source)
local bridge='\n';for _,name in ipairs(substitutions)do bridge=bridge..name..'=__fixture.'..name..'\n'end
env.__fixture=env;enhanced=true;mission=false;count=1;options[prefix..'mode']=1
restart(bundle:sub(1,#bundle-#source)..bridge..source);tick(610)
assert(VehicleSeatSwitch.version=='0.4.3'and VehicleSeatSwitch.transport_ready,tostring(VehicleSeatSwitch.error))
assert(env.shutdown()=='shutdown_forwarded')
print('PASS exact unified archive prefix with real menu/input modules and declared engine doubles')

-- Reproduce a hard gameplay fault while preserving menu service and safe
-- native Normal actions. Mutation backend is an explicit error double here.
mission=false;count=1;options[prefix..'mode']=2;options[prefix..'strategy']=1
restart();tick(610);mission=true;seat(1);tick(6);inject_fault=true;tap(116);inject_fault=false
assert(VehicleSeatSwitch.enhanced_fault and VehicleSeatSwitch.effective_mode=='normal')
option('strategy',2);assert(VehicleSeatSwitch.input_strategy=='menu')
bindings[prefix..'seat1']=true;tick(1);bindings[prefix..'seat1']=nil;tick(30);assert(shared_snapshot.node==0)
option('strategy',1);assert(VehicleSeatSwitch.input_strategy=='ini');tap(113);assert(shared_snapshot.node==1)
assert(env.shutdown()=='shutdown_forwarded')
print('PASS hard gameplay error preserves menu/source updates and guarded Normal native controls; Enhanced remains fail-closed')

-- Required MOM can load later. Optional MBM must not enable an absent source,
-- even if its old saved selection is two.
local mom,mbm=ModOptionsMenu,ModBindingsMenu
ModOptionsMenu=nil;ModBindingsMenu=nil;options[prefix..'strategy']=2
mission=false;restart();tick(610);mission=true;seat(1);tick(6)
before=native_calls;tap(112)
assert(shared_snapshot.node==1 and native_calls==before and VehicleSeatSwitch.status=='required_ModOptionsMenu_missing')
ModOptionsMenu=mom;tick(6)
assert(VehicleSeatSwitch.input_strategy=='ini');tap(112);assert(shared_snapshot.node==0)
ModBindingsMenu=mbm;tick(6);assert(VehicleSeatSwitch.input_strategy=='menu')
env.shutdown()
print('PASS required MOM waits without input; absent optional MBM forces INI despite saved menu choice; delayed dependencies resume')
