-- Real dispatcher/probe/adapter, simulated native-window consumption and RPC.
local prefix='work/seat_physics_layout_fix/'
local function load(name)return assert(loadfile(prefix..name..'.lua'))()end
local input=assert(loadfile('work/seat_switch/src/input.lua'))()
local config=assert(loadfile('work/seat_switch/src/config.lua'))()
local policy=assert(loadfile('work/seat_switch/src/policy.lua'))()
for _,borrowed in ipairs({false,true})do
 local function seat(n)return {collection=9,current=n,reserved=n,role=n==0 and 1 or n==4 and 2 or 3,target=-1,action=-1,transitioning=0,queued_exit=0}end
 local now,physical,consumed,edge=0,{},{},{}
 local api={now=function()return now end,down=function(k)return physical[k]end,focused=function()return true end,input_allowed=function()return true end,
  control_down=function(k)return physical[k]and not consumed[k]end}
 local avatar={id=7,unit=77,is_local=true,owned_local=true,vehicle_input=true,seat=seat(1)}
 local friend={id=8,unit=88,is_local=false,seat=borrowed and seat(0)or{collection=-1}}
 local c={identity='v',seat=1,avatar=avatar,destination='friend',sample={player_count=2,local_count=1,avatars={avatar,friend}},
  native={identity='av',vehicle='m102',transition=26,profile={roles={1,3,3,3,2}},player_count=2,peer_count=2,owned=not borrowed,avatar=7,avatar_unit=77,node=1,occupied={}},
  owner={owner=borrowed and'friend'or'self',selfpeer='self',coordinator='friend',members={self=true,friend=true},peer_count=2,vehicle={id=9,owned_local=not borrowed},avatars={[7]={owner='self'},[8]={owner='friend'}}}}
 local transfers,mutations,sends=0,0,0
 local function position(n)
  for i=0,4 do c.native.occupied[i]=false end
  if borrowed then c.native.occupied[0]=true end
  c.seat=n;c.native.node=n;c.native.occupied[n]=true;avatar.seat=seat(n)
  c.driver=borrowed and friend or n==0 and avatar or nil
 end
 position(1)
 local snapshot={current=function()return true end,predictions=function()return nil,nil end}
 local owner={summary=function()return {}end,send=function(_,o,from,to,hook)
  transfers=transfers+1;hook();c.owner.owner=to;c.owner.vehicle.owned_local=to=='self';c.native.owned=to=='self'
 end}
 local tx={prepare=function(_,s,target)return function()mutations=mutations+1;position(target)end end}
 local sender={prepare=function()return function()sends=sends+1 end end}
 local a=load('adapter').new(api,0,{},nil,owner,snapshot,tx,sender,{active=true,health=function()end},function()end,function()return ''end)
 a.capture=function()return c end
 local probe=load('probe').new(a,function()end,function()end,nil,true)
 local keys=config.parse('[m102]\ndriver=X\nfront_passenger=MOUSE2\nrear_left=Ctrl+Z\nrear_right=Ctrl+X\ngunner=Ctrl+MOUSE2')
 local gate={active=true,pulse=function()end,take=function()local e=edge;edge={};return e end}
 local d=load('dispatcher').new(api,keys,input,policy,snapshot,{},probe,function()end,gate)
 local function tick(dt)now=now+(dt or .016);d:update(c.native)end
 gate.active=false;gate.pending=true
 physical={[162]=true,[2]=true};edge[1026]=true
 tick();assert(not probe.pending and not d.queued and mutations==0 and transfers==0,'pending GUI install blocks new native/network requests')
 gate.active=true;gate.pending=false;physical={};edge={}
 tick();tick(.3)
 physical={[162]=true,[2]=true};consumed[2]=true;edge[1026]=true
 tick();assert(probe.pending and not d.queued,'submit during key-down, same dispatcher update')
 assert(transfers==(borrowed and 1 or 0))
 tick();assert(c.seat==4 and mutations==1 and sends==1,'held consumed right mouse must not defer mutation')
 for _=1,50 do tick()end
 assert(not probe.pending and mutations==1 and sends==1 and transfers==(borrowed and 2 or 0),'held key has no repeats; exact authority cleanup')
 physical={};consumed={};tick(.5)
 -- An unrelated held movement key still blocks all requests and mutations.
 physical={[162]=true,[2]=true,[87]=true};consumed[2]=true;edge[1026]=true
 -- Current gunner target is ignored as normal; instead request front passenger.
 physical[162]=nil;edge={[2]=true};tick()
 assert(d.queued and not probe.pending and mutations==1,'unrelated movement remains a control guard')
 physical[87]=nil;tick();assert(probe.pending);tick();assert(c.seat==1)
 for _=1,50 do tick()end
 assert(mutations==2 and sends==2 and not probe.pending)
end
print('PASS priority key-down dispatcher/adapter: immediate submit, held consumed mouse allowed through fresh preflight, no repeats, both authority paths, unrelated controls still block')
