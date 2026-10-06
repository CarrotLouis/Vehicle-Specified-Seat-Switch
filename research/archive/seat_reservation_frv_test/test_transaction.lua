local factory=assert(loadfile('work/seat_reservation_frv_test/transaction.lua'))()
local scope=assert(loadfile('work/seat_reservation_frv_test/scope.lua'))()
local names={'clear_vehicle_weapon','restore_personal_weapon','equip_current_personal_weapon','refresh_weapon_context','set_role','restore_seated','seat_action','avatar_rotation'}
local p={functions={}};local at={};local calls={};local current,target
for i,name in ipairs(names)do p.functions[name]={rva=i,bytes='x'};at[i]=name end
local api={read=function()return 'x'end,ffi={cast=function(_,address)return function(...)
 local name=assert(at[address],'NO chassis reserve/release/authority binding');calls[#calls+1]=name;local args={...}
 if name=='set_role'then assert(args[1]==600 and args[2]==1 and args[3]==current.profile.roles[target+1])
 elseif name=='restore_seated'then assert(args[1]==600 and args[2]==nil and args[3]==7 and args[4]==9 and args[5]==target and args[6]==false)
 elseif name=='seat_action'then local d=scope.layout(current);assert(args[1]==current.transition and args[2]==7 and args[3]==d.prepare and args[4]==target)
 elseif name=='avatar_rotation'then assert(args[1]==nil and args[2]==7 and args[3]==true)
 else assert(args[1]==700,'only own avatar')end
 return 0
end end}}
local pose=function()return {check=function()return true end,apply=function(s,t)assert(s.avatar==7 and t==target);calls[#calls+1]='pose';return 'own_pose'end}end
local personal=function()return function(s)assert(s.avatar_address==700);return true end end
local tx=factory(api,0,p,pose,personal,function()end,scope);local cases=0
for _,name in ipairs({'m102','m103','m104'})do
 local roles=name=='m102'and {1,3,3,3,2}or name=='m103'and {1,3,3,3}or {1,3,2}
 for source=1,#roles-1 do for dest=1,#roles-1 do if source~=dest then
  current={avatar=7,avatar_address=700,collection=9,vehicle=name,transition=({m102=26,m103=27,m104=28})[name],owned=false,
   player_count=2,peer_count=2,node=source,active=false,profile={row=8,roles=roles},seaters=600,seater_index=1}
  target=dest;calls={};local valid=true;local grant={source=source,target=target,check=function()return valid end}
  assert(tx:preflight(current,target)and #calls==0);assert(not pcall(tx.prepare,tx,current,target,nil))
  local perform=tx:prepare(current,target,grant);assert(#calls==0);perform();assert(not pcall(perform))
  local sequence=table.concat(calls,',')
  assert(sequence:find('clear_vehicle_weapon,clear_vehicle_weapon,restore_personal_weapon,refresh_weapon_context',1,true)==1)
  assert(sequence:find('set_role',1,true)and sequence:find('restore_seated',1,true)and calls[#calls]=='pose')
  assert((sequence:find('seat_action',1,true)~=nil)==(roles[target+1]==2))
  assert((sequence:find('avatar_rotation',1,true)~=nil)==(roles[source+1]==2))
  assert((sequence:find('equip_current_personal_weapon',1,true)~=nil)==(roles[target+1]==3))
  calls={};perform=tx:prepare(current,target,grant);valid=false;assert(not pcall(perform)and #calls==0);cases=cases+1
 end end end
end
for _,change in ipairs({function(s)s.owned=true end,function(s)s.node=0 end,function(s)s.player_count=3 end,function(s)s.active=true end,function(s)s.vehicle='bastion'end})do
 current={avatar=7,avatar_address=700,collection=9,vehicle='m102',transition=26,owned=false,player_count=2,peer_count=2,node=1,active=false,profile={row=8,roles={1,3,3,3,2}},seaters=600,seater_index=1}
 calls={};change(current);assert(not pcall(tx.preflight,tx,current,2)and #calls==0)
end
print('PASS '..cases..' actual FRV transaction paths: own gunner camera/rotation/personal restoration, grant/single-use refusal, no chassis authority/mask mutation')
