-- Appended to the actual captured-code ownership fixture. No live process.
local R='work/seat_multi_vehicle_fix/'
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
