-- Real input, dispatcher, probe and adapter; engine/RPC effects are simulated.
local prefix='work/seat_aboard_passenger_test/'
local function load(name)return assert(loadfile(prefix..name..'.lua'))()end
local input=assert(loadfile('work/seat_switch/src/input.lua'))()
local config=assert(loadfile('work/seat_switch/src/config.lua'))()
local policy=assert(loadfile('work/seat_switch/src/policy.lua'))()
for _,borrowed in ipairs({false,true})do
 local function seat(n)return {collection=9,current=n,reserved=n,role=n==0 and 1 or n==4 and 2 or 3,target=-1,action=-1,transitioning=0,queued_exit=0}end
 local now,down=0,{}
 local api={now=function()return now end,down=function(k)return down[k]end,focused=function()return true end,input_allowed=function()return true end}
 local av={id=7,unit=77,is_local=true,owned_local=true,vehicle_input=true,seat=seat(borrowed and 1 or 0)}
 local friend={id=8,unit=88,is_local=false,seat=borrowed and seat(0)or{collection=-1}}
 local c={identity='v',seat=av.seat.current,avatar=av,destination='friend',sample={player_count=2,local_count=1,avatars={av,friend}},
  native={identity='av',vehicle='m102',transition=26,profile={roles={1,3,3,3,2}},player_count=2,peer_count=2,owned=not borrowed,avatar=7,avatar_unit=77,node=av.seat.current,occupied={}},
  owner={owner=borrowed and'friend'or'self',selfpeer='self',coordinator='friend',members={self=true,friend=true},peer_count=2,vehicle={id=9,owned_local=not borrowed},avatars={[7]={owner='self'},[8]={owner='friend'}}}}
 local transfers,mutations,sends,natives=0,0,0,0
 local function position(n)
  for i=0,4 do c.native.occupied[i]=false end
  if borrowed then c.native.occupied[0]=true end
  c.seat=n;c.native.node=n;c.native.occupied[n]=true;av.seat=seat(n)
  c.driver=borrowed and friend or n==0 and av or nil
 end
 position(c.seat)
 local snapshot={current=function()return true end,predictions=function(s)
  if s.node==0 then return 1,nil elseif s.node==1 then return 0,nil elseif s.node==2 then return 3,nil elseif s.node==3 then return 2,nil end
 end}
 local owner={summary=function()return {}end,send=function(_,o,source,target,hook)
  transfers=transfers+1;hook();c.owner.owner=target;c.owner.vehicle.owned_local=target=='self';c.native.owned=target=='self'
 end}
 local tx={prepare=function(_,s,target)return function()mutations=mutations+1;position(target)end end}
 local sender={prepare=function(_,o,dest,s,target)return function()sends=sends+1 end end}
 local a=load('adapter').new(api,0,{},nil,owner,snapshot,tx,sender,{active=true,health=function()end},function()end,function()return ''end)
 a.capture=function()return c end
 local probe=load('probe').new(a,function()end,function()end,nil,true)
 local native={next=function()natives=natives+1;position(({[0]=1,[1]=0,[2]=3,[3]=2})[c.seat])end}
 local keys=config.parse('[m102]\ndriver=X\nfront_passenger=MOUSE2\nrear_left=Ctrl+Z\nrear_right=Ctrl+X\ngunner=Ctrl+MOUSE2')
 local d=load('dispatcher').new(api,keys,input,policy,snapshot,native,probe,function()end)
 local function tick(pressed,dt)down=pressed or{};now=now+(dt or .1);d:update(c.native)end
 local codes={[0]={88},[1]={2},[2]={162,90},[3]={162,88},[4]={162,2}}
 local route=borrowed and{2,3,4,2,1,4,1}or{4,1,2,0,3,1,0}
 for _,target in ipairs(route)do
  tick(nil,21);local key={};for _,code in ipairs(codes[target])do key[code]=true end
  tick(key);for _=1,60 do tick()end
  assert(c.seat==target and not probe.pending and not d.pending and probe.phase~='stopped','combined route failed target='..target..' seat='..c.seat..' phase='..probe.phase)
 end
 assert(mutations==6 and sends==6 and natives==1 and probe.count==6)
 assert(transfers==(borrowed and 12 or 0))
 -- Simultaneous distinct input edges must not enter either engine path.
 tick(nil,21);local before=mutations+natives;tick({[88]=true,[2]=true});tick();assert(mutations+natives==before)
 if borrowed then tick(nil,21);tick({[88]=true});tick();assert(c.seat==1 and transfers==12,'occupied driver key must never request authority')end
end
print('PASS combined real dispatcher/probe/adapter and actual local INI mapping: 7-step native/cross route in both contexts, exact cleanup, simultaneous input and occupied driver rejection; game/network simulated')
