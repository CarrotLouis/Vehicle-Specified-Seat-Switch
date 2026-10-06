-- Actual preserved module sections, read-only mock address space. No live game.
local profile=assert(loadfile('work/seat_switch/src/profile.lua'))()
local spec=assert(loadfile('work/seat_protocol_diagnostic/compat_spec.lua'))()
local points=assert(loadfile('work/seat_protocol_diagnostic/trace_points.lua'))()
for _,point in ipairs(points)do profile.functions['trace_'..point.name]={rva=point.rva}end
profile,spec=assert(loadfile('work/seat_interface_diagnostic/routing_spec.lua'))()(profile,spec)
profile,spec=assert(loadfile('work/seat_authority_diagnostic/authority_spec.lua'))()(profile,spec)
local compat=assert(loadfile('work/seat_switch/src/compat.lua'))()
local ffi=require('ffi')
local root=assert(os.getenv('VSS_CAPTURE'),'VSS_CAPTURE required')
local f=assert(io.open(root..'/capture.txt','rb'));local report=f:read('*a');f:close()
local modules={};local bases={['game.dll']=0x10000000,['helldivers2.exe']=0x20000000}
local function file(name)local h=assert(io.open(root..'/'..name,'rb'));local b=h:read('*a');h:close();return b end
for name,base in pairs(bases)do
 local rows={{a=base,b=file(name..'.headers.bin')}}
 for fn,hex in report:gmatch('([^%s]+%.%d+_([%da-f]+)%.bin) name=')do
  if fn:sub(1,#name)==name then rows[#rows+1]={a=base+tonumber(hex,16),b=file(fn)}end
 end
 modules[name]=rows
end
local patches={}
local function rawread(a,n)
 for _,rows in pairs(modules)do for _,r in ipairs(rows)do if a>=r.a and a+n<=r.a+#r.b then return r.b:sub(a-r.a+1,a-r.a+n)end end end
end
local api={module=function(name)return bases[name]end}
function api.read(a,n)
 local b=rawread(a,n);if not b then return nil end
 for _,p in ipairs(patches)do
  local lo,hi=math.max(a,p.a),math.min(a+n,p.a+#p.b)
  if lo<hi then b=b:sub(1,lo-a)..p.b:sub(lo-p.a+1,hi-p.a)..b:sub(hi-a+1)end
 end
 return b
end
local function run(mode,s)
 local task=compat.start(api,bases['game.dll'],profile,s or spec,mode)
 for i=1,30000 do local p=task.step();if p then return p,i end end
 error('resolver never finished')
end

-- Appended to the immutable capture fixture by build.py. Actual game functions
-- are never executed: the single FFI send signature is replaced in this fixture.
local p=run('diagnostic');local game,exe=bases['game.dll'],bases['helldivers2.exe']
local bit=require('bit');local extra={};local regions={};local rawapi=api.read
local pointers=os.getenv('VSS_TEST_POINTERS')=='1'
local function number(a)return type(a)=='cdata'and tonumber(ffi.cast('uintptr_t',a))or a end
if pointers then
 game,exe=ffi.cast('uint8_t *',game),ffi.cast('uint8_t *',exe)
 local original_module=api.module;api.module=function(name)return ffi.cast('uint8_t *',original_module(name))end
end
local function put(a,b)extra[#extra+1]={a=number(a),b=b}end
local function le(n)local v=ffi.new('uint32_t[1]',n);return ffi.string(v,4)end
local function ptr(n)local v=ffi.new('uint64_t[1]',number(n));return ffi.string(v,8)end
local function peer(lo,hi)local v=ffi.new('uint32_t[2]',{lo,hi});return ffi.string(v,8)end
function api.read(a,n)
 a=number(a)
 local b=rawapi(a,n)
 if not b then for _,r in ipairs(regions)do if a>=number(r[1])and a+n<=number(r[1])+r[2]then b=string.rep('\0',n);break end end end
 if not b then return nil end
 for _,r in ipairs(extra)do
  local lo,hi=math.max(a,r.a),math.min(a+n,r.a+#r.b)
  if lo<hi then b=b:sub(1,lo-a)..r.b:sub(lo-r.a+1,hi-r.a)..b:sub(hi-a+1)end
 end
 return b
end
function api.pointer(b,o)
 o=o or 0;if not b or #b<o+8 then return nil end
 local v=ffi.new('uint64_t[1]');ffi.copy(v,b:sub(o+1,o+8),8);local n=tonumber(v[0]);return n>=65536 and n<2^47 and (pointers and ffi.cast('uint8_t *',v[0])or n)or nil
end
local function displacement(a)
 local v=ffi.new('int32_t[1]');ffi.copy(v,assert(api.read(a+3,4)),4);return a+7+tonumber(v[0])
end
local S,E,SERVICES,API,ROWS,ENTITIES,BUSY,BHASH=0x50010000,0x50040000,0x50050000,0x50051000,0x50060000,0x50070000,0x50080000,0x50090000
regions={{0x50000000,0x100000},{game+p.globals.session,8},{game+p.globals.entities,8}}
local root=displacement(game+p.functions.authority_apply.rva+0xd);regions[#regions+1]={root,8}
local vt=displacement(exe+p.engine_functions.authority_constructor.rva+0x12)
local dispatch=displacement(game+p.functions.route_dispatch.rva+6)
local LOCAL=peer(0x76543211,0xfedcba98);local FRIEND=peer(0x76543212,0xfedcba98)
local vehicle={id=721,unit=8391232,network_unit=4118,resource='fixture',name='m102',seat_count=5,owned_local=false}
local s={state='mission',mission_value=99,player_count=2,local_count=1,vehicles={vehicle},avatars={
 {id=11,is_local=true,network_unit=4107,seat={collection=721,current=1,reserved=1,role=3,target=-1,action=-1,transitioning=0,queued_exit=0}},
 {id=22,is_local=false,network_unit=274,seat={collection=721,current=0,reserved=0,role=1,target=-1,action=-1,transitioning=0,queued_exit=0}}}}
local reader={peers={[LOCAL]='P1',[FRIEND]='P2'},capture=function()return s end}
local trace={registry={{name='authority_owned',hash=0xf8a9d630,flags={1,1},parameter_count=2,type_indices={107,91},index=575}}}
local function mul(a,b)return tonumber(ffi.cast('uint32_t',ffi.new('uint64_t',a)*ffi.new('uint64_t',b)))end
local indices={}
local function setup()
 extra={};indices={}
 put(game+p.globals.session,ptr(S));put(S+0xb390,ptr(E));put(root,ptr(SERVICES));put(SERVICES+0x40,ptr(API))
 for off,name in pairs({[0x98]='api_exists',[0x138]='api_request',[0x140]='api_transfer',[0x160]='api_owner'})do put(API+off,ptr(exe+p.engine_functions['authority_'..name].rva))end
 put(E,ptr(vt))
 for off,name in pairs({[0xf8]='exists',[0x110]='transfer',[0x128]='request',[0x178]='owner'})do put(vt+off,ptr(exe+p.engine_functions['authority_'..name].rva))end
 -- These leaf getters are not individually scanned. Their table relationships
 -- and exact bytes are checked by the production observer.
 put(vt+0x68,ptr(exe+0x292bd0));put(vt+0x98,ptr(exe+0x292cc0))
 put(E+0x20,LOCAL);put(E+0x130,FRIEND);put(S+0xb398,LOCAL);put(S+0xb3a8,FRIEND)
 put(S+0x162d8,le(2));put(S+0x162e0,LOCAL..FRIEND);put(E+0x60e4,le(42))
 put(dispatch+575*8,ptr(game+p.functions.authority_adapter.rva))
 put(E+0x640,le(8)..le(8));put(E+0x648,ptr(ROWS)..ptr(0)..le(3)..le(8))
 local free={};for i=0,7 do free[i]=true;put(ROWS+i*0x248+0x240,le(0xfffffffe))end
 local unitpeers={[vehicle.network_unit]=FRIEND,[s.avatars[1].network_unit]=LOCAL,[s.avatars[2].network_unit]=FRIEND}
 for _,unit in ipairs({vehicle.network_unit,s.avatars[1].network_unit,s.avatars[2].network_unit})do
  local a=mul(unit,0x5bd1e995);a=bit.bxor(a,bit.rshift(a,24));if a<0 then a=a+4294967296 end
  local i=mul(a,0x5bd1e995)%8
  if not free[i]then local j=i;while indices['next'..j]do j=indices['next'..j]end
   for k=0,7 do if free[k]then i=k;break end end
   put(ROWS+j*0x248+0x240,le(i));indices['next'..j]=i
  end
  free[i]=nil;indices[unit]=i;local at=ROWS+i*0x248
  put(at,le(unit));put(at+8,le(7)..le(unit));put(at+16,unitpeers[unit]);put(at+0x23a,'\1\0\0\0');put(at+0x240,le(0x7fffffff))
 end
 put(game+p.globals.entities,ptr(ENTITIES));put(ENTITIES+8,ptr(BUSY))
 put(BUSY+0xb020,ptr(BHASH)..le(2)..le(0xffffffff)..le(1))
 put(BHASH,le(0xffffffff)..le(0xffffffff)..le(0xffffffff)..le(0xffffffff))
 put(BHASH+(vehicle.network_unit%2)*8,le(vehicle.network_unit)..le(0));put(BUSY+0x201c,'\0')
end
local sends={};local proxy=setmetatable({}, {__index=ffi})
proxy.cast=function(signature,address)
 if signature=='void (*)(uint64_t,uint32_t,uint64_t)'then
  assert(address==game+p.functions.authority_send.rva)
  return function(dest,unit,target)
   local d,t=ffi.new('uint64_t[1]',dest),ffi.new('uint64_t[1]',target)
   sends[#sends+1]={ffi.string(d,8),unit,ffi.string(t,8)}
  end
 end
 return ffi.cast(signature,address)
end
local fn=assert(loadfile('work/seat_multi_peer_diagnostic/observe.lua'))
setfenv(fn,setmetatable({require=function(name)return name=='ffi'and proxy or require(name)end},{__index=_G}))
local observer=fn().new(api,game,p,spec,compat,reader,trace)
-- Appended to the actual captured-code ownership fixture. No live process.
local R='work/seat_multi_peer_diagnostic/'
local oldfn=assert(loadfile(R..'regression_0180_observe.lua'))
setfenv(oldfn,setmetatable({require=function(name)return name=='ffi'and proxy or require(name)end},{__index=_G}))
local old_observer=oldfn().new(api,game,p,spec,compat,reader,trace)
local replay=assert(loadfile(R..'selection_replay.lua'))()
local replay_cases,counts=0,{}
for _,row in ipairs(replay)do for _,host in ipairs({LOCAL,FRIEND})do
 s=row.sample;vehicle=nil
 for _,v in ipairs(s.vehicles)do if v.id==s.avatars[1].seat.collection then vehicle=v;break end end
 assert(vehicle and vehicle.name==row.name)
 setup();put(E+0x130,host);put(S+0xb3a8,host)
 local old,reason=old_observer:capture(s,nil,'all')
 assert(not old and reason=='vehicle_not_observed','0.18.0 must reproduce the recorded early refusal')
 local current=assert(observer:capture(s,nil,'all'),row.name..'/'..row.t)
 assert(current.vehicle==vehicle and current.vehicle.id==s.avatars[1].seat.collection)
 assert(current.avatars[s.avatars[1].id].owner==LOCAL and current.avatars[s.avatars[2].id].owner==FRIEND)
 assert(current.owner==FRIEND and current.coordinator==host and not current.busy)
 counts[row.name]=(counts[row.name]or 0)+1;replay_cases=replay_cases+1
end end
assert(replay_cases==512 and counts.m103==104 and counts.m104==102 and counts.bastion==188 and counts.maelstrom==118)
print('PASS '..replay_cases..' untracked observer live-state replays: all 256 recorded new-model states, both coordinators, actual vehicle/avatar/unit/collection identities; old 0.18.0 reproduces refusal')

local adapter_module=assert(loadfile(R..'adapter.lua'))()
local input=assert(loadfile('work/seat_switch/src/input.lua'))()
local config=assert(loadfile('work/seat_switch/src/config.lua'))()
local policy=assert(loadfile('work/seat_switch/src/policy.lua'))()
local recorder=assert(loadfile('work/seat_network_diagnostic/recorder.lua'))()
local keys=config.parse(nil)
local dir=assert(os.getenv('VSS_INPUT_SELECTION_DIR'),'isolated input fixture directory required')
local normal_calls,mutations=0,0
local function denied()error('this fixture must stop after the real authority request')end
trace.active=true;trace.health=function()end
local chain_cases=0
for _,name in ipairs({'m102','m103','m104','bastion','maelstrom'})do for _,host in ipairs({LOCAL,FRIEND})do
 local layout=p.tables[name];local seats=policy.seats[name]
 for source=1,#layout.roles-1 do for target=0,#layout.roles-1 do
  if source~=target and not policy.check('normal',name,seats[source+1],seats[target+1],false)then
   for _,kind in ipairs({'driver','outside','seated'})do
    local remote
    if kind=='driver'then remote=0
    elseif kind=='seated'then for node=1,#layout.roles-1 do if node~=source and node~=target then remote=node;break end end end
    if(kind~='driver'or target~=0)and(kind~='seated'or remote~=nil)then
     vehicle={id=721,unit=8391232,network_unit=4118,resource='fixture',name=name,transition_type=layout.transition,seat_count=#layout.roles,owned_local=false}
     local function seat(node)return {collection=721,current=node,reserved=node,role=layout.roles[node+1],transition_type=layout.transition,target=-1,action=-1,transitioning=0,queued_exit=0}end
     s={state='mission',mission_value=99,player_count=2,local_count=1,avatars={
      {id=11,unit=1111,network_unit=4107,is_local=true,owned_local=true,vehicle_input=true,seat=seat(source)},
      {id=22,unit=2222,network_unit=274,is_local=false,owned_local=false,vehicle_input=false,
       seat=kind=='outside'and {collection=0,transition_type=0,role=0,entry_role=0,entrance=-1,current=0,reserved=0,target=-1,action=-1,transitioning=0,queued_exit=0}or seat(remote)}},
      vehicles={{id=999,unit=99999,network_unit=4999,name='m102',resource='distractor',owned_local=false},vehicle}}
     setup();put(E+0x130,host);put(S+0xb3a8,host)
     local native={identity=name..'/'..source,vehicle=name,transition=layout.transition,profile=layout,player_count=2,peer_count=2,
      owned=false,avatar=11,avatar_unit=1111,node=source,occupied={},collection=721,collection_unit=4118,resource='fixture'}
     for node=0,#layout.roles-1 do native.occupied[node]=node==source or node==remote end
     assert(native.occupied[target]==false)
     local snapshot={capture=function()return native end,current=function()return true end,
      predictions=function()local targets={};for node=0,#layout.roles-1 do
       if policy.check('normal',name,seats[source+1],seats[node+1],false)then targets[#targets+1]=node end
      end;return targets[1],targets[2]end}
     local events={};local function emit(e)events[#events+1]=e end
     local now,physical,suppressed,armed,queue=10,{},{},{},{}
     api.now=function()return now end;api.input_allowed=function()return true end;api.focused=api.input_allowed
     api.down=function(k)return physical[k]end;api.experiment_allowed=function()return true end
     local transaction={prepare=function()mutations=mutations+1;denied()end}
     local sender={prepare=denied}
     local adapter=adapter_module.new(api,game,p,reader,observer,snapshot,transaction,sender,trace,emit,recorder.encode)
     -- No replacement of adapter.capture or owner_reader.capture: this is the
     -- previously missed untracked path, then fresh tracked preflight and F8.
     local probe=assert(loadfile(R..'probe.lua'))().new(adapter,emit,function()end,nil,true)
     local gate=assert(loadfile(R..'input_gate.lua'))()(api,{log_directory=dir},assert(loadfile(R..'input_helper.lua'))(),policy,snapshot,adapter_module.eligible,emit)
     api.control_down=function(k)return gate:control_down(k)end
     local dispatcher=assert(loadfile(R..'dispatcher.lua'))().new(api,keys,input,policy,snapshot,
      {next=function()normal_calls=normal_calls+1;denied()end,previous=function()normal_calls=normal_calls+1;denied()end},probe,emit,gate)
     local mock={VSSI_version=function()return 2 end,VSSI_record_size=function()return 40 end,VSSI_start=function()return 0 end,
      VSSI_status=function()return 0 end,VSSI_health=function()return 0 end,VSSI_stop=function()return 0 end,VSSI_dropped=function()return 0 end,
      VSSI_suppressed=function(k)return suppressed[k]and 1 or 0 end,
      VSSI_arm=function(items,n,source_,deadline,generation)
       armed={source=source_,generation=generation,items={}}
       for i=0,n-1 do armed.items[tonumber(items[i].target)]=tonumber(items[i].binding)end;return 0
      end,VSSI_drain=function(buffer,cap)
       assert(#queue<=cap);local n=#queue
       for i,row in ipairs(queue)do for k,v in pairs(row)do buffer[i-1][k]=v end end;queue={};return n
      end}
     local function tick(dt)
      now=now+(dt or .016);local original=ffi.load
      ffi.load=function(lib)return lib=='user32'and {GetForegroundWindow=function()return ffi.cast('void *',123)end}or mock end
      local ok,reason=pcall(dispatcher.update,dispatcher,native);ffi.load=original;assert(ok,reason);return reason
     end
     tick();tick(.3)
     local binding=keys[name][seats[target+1]]
     assert(probe.observed and probe.observed.owner.vehicle==vehicle and probe.observed.native==native)
     assert(armed.items[target]==binding,'cross binding must be armed by a real untracked context')
     local before=#sends
     physical[binding%256]=true;suppressed[binding%256]=true
     queue={{sequence=1,tick=math.floor((now+.016)*1000),generation=armed.generation,binding=binding,source=source,target=target,message=0x100}}
     assert(tick()=='network_requested'and probe.pending and #sends==before+1)
     assert(sends[#sends][1]==FRIEND and sends[#sends][2]==4118 and sends[#sends][3]==LOCAL)
     assert(not dispatcher.queued and probe.observed.native==native and s.avatars[1].seat.current==source)
     local consumed,requested=0,0
     for _,e in ipairs(events)do
      if e.event=='input_priority_consumed'then consumed=consumed+1 end
      if e.event=='integrated_request_attempt'then requested=requested+1 end
     end
     assert(consumed==1 and requested==1,'one key must cause one native authority request')
     native.occupied[target]=true;gate:pulse(native,probe.observed,keys,true)
     assert(armed.items[target]==nil,'occupied target must not be armed')
     native.occupied[target]=false;native.transition=99;gate:pulse(native,probe.observed,keys,true)
     assert(armed.items[target]==nil,'unverified layout must not be armed')
     native.transition=layout.transition;gate:close();chain_cases=chain_cases+1
    end
   end
  end
 end end
end end
assert(chain_cases>100 and normal_calls==0 and mutations==0)
print('PASS '..chain_cases..' real untracked observer-adapter-probe-keygate-dispatcher-FFI request cases: five models/all allowed cross routes/both hosts/driver-foot-seated owner; exact-once input, no writes, occupied/layout refusals')

local scope_cases=0
for _,change in ipairs({
 function()s.state='not_in_mission'end,
 function()s.avatars[1].seat=nil end,
 function()s.avatars[1].is_local=false end,
 function()s.avatars[1].seat.collection=998 end,
 function()vehicle.name='tanker'end,
 function()vehicle.name='unknown_vehicle'end,
})do
 local saved_state,saved_local,saved_seat,saved_name=s.state,s.avatars[1].is_local,s.avatars[1].seat,vehicle.name
 local saved_collection=saved_seat.collection;change()
 assert(observer:capture(s,nil,'all')==nil)
 s.state=saved_state;s.avatars[1].is_local=saved_local;s.avatars[1].seat=saved_seat;saved_seat.collection=saved_collection;vehicle.name=saved_name
 scope_cases=scope_cases+1
end
print('PASS '..scope_cases..' untracked selection scope refusals: ship/missing seat/remote-only/other collection/tanker/unknown model; distracting M102 never selected')
