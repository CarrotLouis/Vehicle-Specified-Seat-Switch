-- Real poller/gate/dispatcher/probe/adapter. Only the OS callback queue,
-- engine transaction and network delivery are simulated; no game is launched.
return function(version,source,host,borrowed,dir,remote_node,vehicle,module_overrides)
 local ffi=require('ffi');local prefix='work/'..version..'/'
 local function load(n)return assert(loadfile(prefix..(module_overrides and module_overrides[n]or n)..'.lua'))()end
 local input=assert(loadfile('work/seat_switch/src/input.lua'))()
 local config=assert(loadfile('work/seat_switch/src/config.lua'))()
 local policy=assert(loadfile('work/seat_switch/src/policy.lua'))()
 vehicle=vehicle or 'm102'
 local profile=assert(loadfile('work/seat_switch/src/profile.lua'))().tables[vehicle]
 local keys=config.parse('[m102]\ndriver=X\nfront_passenger=Z\nrear_left=Ctrl+Z\nrear_right=Ctrl+X\ngunner=Ctrl+MOUSE2\n'..
 '[m103]\ndriver=X\nfront_passenger=Z\nrear_left=Ctrl+Z\nrear_right=Ctrl+X\n'..
 '[m104]\ndriver=X\nfront_passenger=Z\nflamer=Ctrl+MOUSE2\n'..
 '[bastion]\ndriver=MOUSE4\ngunner=MOUSE5\npassenger_left=Z\npassenger_right=X\n'..
 '[maelstrom]\ndriver=MOUSE4\ngunner=MOUSE5\npassenger_left=Z\npassenger_right=X\n'..
 '[tanker]\ndriver=MOUSE4\ngunner=MOUSE5')
 local function seat(n)return {collection=9,current=n,reserved=n,role=profile.roles[n+1],transition_type=profile.transition,target=-1,action=-1,transitioning=0,queued_exit=0}end
 local f={now=10,physical={},suppressed={},queue={},events={},mutations=0,sends=0,transfers=0,focused=true,sequence=0,armed={}}
 local function emit(e)e.fixture_time=f.now;f.events[#f.events+1]=e end
 local api={now=function()return f.now end,down=function(k)return f.physical[k]end,
  focused=function()return f.focused end,input_allowed=function()return f.focused end}
 f.api=api
 local av={id=7,unit=77,network_unit=707,is_local=true,owned_local=true,vehicle_input=true,seat=seat(source)}
 local outside={collection=0,transition_type=0,role=0,entry_role=0,entrance=-1,current=0,reserved=0,target=-1,action=-1,transitioning=0,queued_exit=0}
 local friend={id=8,unit=88,network_unit=808,is_local=false,owned_local=false,vehicle_input=false,
  seat=remote_node=='outside'and outside or seat(borrowed and(remote_node or 0)or remote_node or 1)}
 local c={identity='vehicle',seat=source,avatar=av,destination='friend',sample={player_count=2,local_count=1,avatars={av,friend}},
  native={identity='avatar/vehicle',vehicle=vehicle,transition=profile.transition,profile=profile,player_count=2,peer_count=2,
   owned=not borrowed,avatar=7,avatar_unit=77,node=source,occupied={}},
  owner={owner=borrowed and 'friend'or 'self',selfpeer='self',coordinator=host,members={self=true,friend=true},peer_count=2,
   vehicle={id=9,name=vehicle,transition_type=profile.transition,seat_count=#profile.roles,owned_local=not borrowed},avatars={[7]={owner='self'},[8]={owner='friend'}}}}
 f.c=c;f.friend=friend;f.keys=keys[vehicle];f.policy=policy;f.native_calls=0
 local function position(n)
  c.seat=n;c.native.node=n;av.seat=seat(n)
  for i=0,#profile.roles-1 do c.native.occupied[i]=false end
  c.native.occupied[n]=true
  if friend.seat and friend.seat.collection==9 then c.native.occupied[friend.seat.current]=true end
  c.driver=friend.seat and friend.seat.collection==9 and friend.seat.current==0 and friend or n==0 and av or nil
 end
 f.position=position
 position(source)
 local snapshot={current=function(_,s)return f.snapshot_valid~=false and s.identity==c.native.identity and s.node==c.seat end,predictions=function(s)
  local targets={};local names=policy.seats[s.vehicle]
  for target=0,#names-1 do if policy.check('normal',s.vehicle,names[s.node+1],names[target+1],false)then targets[#targets+1]=target end end
  return targets[1],targets[2]
 end}
 local owner={summary=function()return {}end,send=function(_,o,from,to,hook,options)
  if options then options.validate()end
  f.transfers=f.transfers+1;hook()
  if f.defer_grant and to=='self'then return end
  c.owner.owner=to;c.owner.vehicle.owned_local=to=='self';c.native.owned=to=='self'
 end}
 local tx={prepare=function(_,s,target)return function()f.mutations=f.mutations+1;position(target)end end}
 local sender={prepare=function()return function()f.sends=f.sends+1 end end}
 f.tx=tx;f.sender=sender;f.owner_reader=owner;f.snapshot=snapshot
 local M=load('adapter')
 local a=M.new(api,0,{},nil,owner,snapshot,tx,sender,{active=true,health=function()end},emit,function()return ''end)
 a.capture=function()return c end;f.adapter=a
 local probe=load('probe').new(a,emit,function()end,nil,true);f.probe=probe
 local gate=load('input_gate')(api,{log_directory=dir},load('input_helper'),policy,snapshot,M.eligible,emit);f.gate=gate
 api.control_down=function(k)return gate:control_down(k)end
 local native={}
 for i,op in ipairs({'next','previous'})do native[op]=function()
  local a,b=snapshot.predictions(c.native);local target=i==1 and a or b
  assert(target and c.native.occupied[target]==false);f.native_calls=f.native_calls+1;position(target)
 end end
 local d=load('dispatcher').new(api,keys,input,policy,snapshot,native,probe,emit,gate);f.dispatcher=d
 local mock={VSSI_version=function()return 2 end,VSSI_record_size=function()return 40 end,
  VSSI_start=function()return 0 end,VSSI_status=function()return 0 end,VSSI_health=function()return 0 end,
  VSSI_stop=function()return 0 end,VSSI_dropped=function()return 0 end,
  VSSI_suppressed=function(k)return f.suppressed[k]and 1 or 0 end,
  VSSI_arm=function(items,n,source_,deadline,generation)
   f.armed={source=source_,generation=generation,items={}}
   for i=0,n-1 do f.armed.items[tonumber(items[i].target)]=tonumber(items[i].binding)end
   return 0
  end,
  VSSI_drain=function(b,max)
   assert(#f.queue<=max);local n=#f.queue
   for i,r in ipairs(f.queue)do for k,v in pairs(r)do b[i-1][k]=v end end
   f.queue={};return n
  end}
 function f:tick(dt)
  self.now=self.now+(dt or .016)
  local original=ffi.load
  ffi.load=function(name)if name=='user32'then return {GetForegroundWindow=function()return ffi.cast('void *',123)end}else return mock end end
  local ok,why=pcall(d.update,d,c.native)
  ffi.load=original;assert(ok,why);return why
 end
 function f:press(binding)
  self.physical[binding%256]=true
  self.physical[162]=math.floor(binding/1024)%4==1 or nil
 end
 function f:release()self.physical={};self.suppressed={}end
 function f:enqueue(binding,target,overrides)
  self.sequence=self.sequence+1
  local r={sequence=self.sequence,tick=math.floor((self.now+.016)*1000),generation=self.armed.generation,
   binding=binding,source=self.armed.source,target=target,message=binding%256==2 and 0x204 or 0x100}
  for k,v in pairs(overrides or{})do r[k]=v end
  self.queue[#self.queue+1]=r
  self.suppressed[binding%256]=self.physical[binding%256]or nil
 end
 function f:count(event,reason)
  local n=0;for _,e in ipairs(self.events)do if e.event==event and(not reason or e.reason==reason)then n=n+1 end end;return n
 end
 function f:finish()
  for _=1,65 do self:tick()end
  assert(not probe.pending and probe.phase~='stopped','operation must complete without a stopped probe')
 end
 f:tick();f:tick(.3)
 return f
end
