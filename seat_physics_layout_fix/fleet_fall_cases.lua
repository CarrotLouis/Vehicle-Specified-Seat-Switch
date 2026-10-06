-- Appended to the extracted graph/recorded-pose fixture by prepare_fleet_tests.
-- All engine effects are mocked; this does not prove live animation delivery.
local fleet=assert(loadfile('work/seat_physics_layout_fix/fleet_policy.lua'))()
local peers={selfpeer,destination,'THIRD003','FOUR0004'}
local captures,replace_member=0,false
local function fleet_context(count,host)
 local row=context();row.sample.player_count=count;row.sample.peer_count=count;row.sample.avatars={row.avatar}
 row.owner.peer_count=count;row.owner.members={};row.owner.owner=destination;row.owner.coordinator=peers[host]
 row.owner.vehicle={id=9,unit=90,network_unit=900,owned_local=false}
 for i=1,count do
  row.owner.members[peers[i]]=true
  if i>1 then
   local a={id=699+i,unit=70+i,network_unit=700+i,is_local=false,owned_local=false,vehicle_input=false,
    seat={collection=0,current=0,reserved=0,role=0,target=-1,action=-1,transitioning=0,queued_exit=0}}
   row.sample.avatars[i]=a;row.owner.avatars[a.id]={owner=peers[i]}
  end
 end
 return row
end
local delivered={};local fleet_send={prepare_fall=function(_,snap,peer)
 assert(snap==s);local raw=ffi.string(ffi.new('uint64_t[1]',peer),8)
 assert(raw~=selfpeer and c.owner.members[raw])
 return {check=function()end,send=function()delivered[#delivered+1]=raw end}
end}
local fleet_adapter={capture=function()
 captures=captures+1
 if replace_member and captures==2 then
  c.owner.members[peers[3]]=nil;c.owner.members['NEWPEER3']=true;c.owner.avatars[702].owner='NEWPEER3'
 end
 return c
end}
local function new_fleet_helper()
 return assert(loadfile('work/seat_physics_layout_fix/fall_repair.lua'))()(api,profile,
  assert(loadfile('work/seat_physics_layout_fix/pose.lua'))(),fleet_adapter,fleet_send,snapshot,
  assert(loadfile('work/seat_physics_layout_fix/adapter.lua'))().layout,{health=function()end},function(e)events[#events+1]=e end,fleet)
end
api.experiment_allowed=function()return true end
local fleet_cases=0
for count=3,4 do for host=1,count do
 s.player_count=count;s.peer_count=count;c=fleet_context(count,host);captures=0;replace_member=false;delivered={}
 current[0]=122;current[13]=99;current[8]=238;local old=writes
 local helper=new_fleet_helper();helper:update(s)
 assert(writes==old+1 and current[8]==0 and current[0]==122 and current[13]==99 and #delivered==count-1)
 local seen={};for _,peer in ipairs(delivered)do assert(not seen[peer]);seen[peer]=true end
 helper:update(s);assert(writes==old+1 and #delivered==count-1);fleet_cases=fleet_cases+1
end end
for count=3,4 do
 s.player_count=count;s.peer_count=count;c=fleet_context(count,1);captures=0;replace_member=true;delivered={}
 current[8]=238;local old=writes;local helper=new_fleet_helper()
 assert(pcall(helper.update,helper,s)and writes==old and #delivered==0 and current[8]==238,
  'Member replacement must defer repair without disabling normal seat input')
 fleet_cases=fleet_cases+1
end
for count=3,4 do
 s.player_count=count;s.peer_count=count;c=fleet_context(count,1);captures=0;replace_member=false;delivered={}
 local waiting=c.sample.avatars[count];c.sample.avatars[count]=nil;current[8]=238
 local old=writes;local helper=new_fleet_helper();assert(pcall(helper.update,helper,s)and writes==old and #delivered==0)
 c.sample.avatars[count]=waiting;helper:update(s);assert(writes==old+1 and #delivered==count-1)
 fleet_cases=fleet_cases+1
end
print('PASS '..fleet_cases..' three/four-peer Bastion native-route repairs over extracted graph: all coordinators, layer8 only/once, all other peers, same-count roster and incomplete join defer before writes without disabling input, then resume. Effects mocked.')
