local factory=assert(loadfile('work/seat_reservation_test/transaction.lua'))()
local names={'clear_vehicle_weapon','restore_personal_weapon','equip_current_personal_weapon','refresh_weapon_context','set_role','restore_seated'}
local profile={functions={}};local at={};local calls={};local target=2
for i,name in ipairs(names)do profile.functions[name]={rva=i,bytes='x'};at[i]=name end
local api={read=function()return 'x'end,ffi={cast=function(_,address)return function(...)
 local name=assert(at[address],'NO chassis reserve/release/authority binding permitted');local args={...};calls[#calls+1]=name
 if name=='set_role'then assert(args[1]==600 and args[2]==1 and args[3]==3)
 elseif name=='restore_seated'then assert(args[1]==600 and args[2]==nil and args[3]==7 and args[4]==9 and args[5]==target and args[6]==false)
 else assert(args[1]==700,'only own avatar')end
end end}}
local pose=function()return {check=function()return true end,apply=function(s,t)assert(s.avatar==7 and t==target);calls[#calls+1]='pose';return 'own_pose'end}end
local personal=function()return function(s)assert(s.avatar_address==700);return true end end
local tx=factory(api,0,profile,pose,personal,function()end)
local s={avatar=7,avatar_address=700,collection=9,vehicle='m102',transition=26,owned=false,player_count=2,peer_count=2,node=1,active=false,
 profile={roles={1,3,3,3,2}},seaters=600,seater_index=1}
local confirmed=true;local grant={source=1,target=2,check=function()return confirmed end}
assert(tx:preflight(s,2)and #calls==0)
assert(not pcall(tx.prepare,tx,s,2,nil)and #calls==0)
local run=tx:prepare(s,2,grant);assert(#calls==0);run()
assert(table.concat(calls,',')=='clear_vehicle_weapon,clear_vehicle_weapon,restore_personal_weapon,refresh_weapon_context,set_role,restore_seated,equip_current_personal_weapon,restore_personal_weapon,pose')
assert(not pcall(run),'never re-execute a partial mutation')
calls={};run=tx:prepare(s,2,grant);confirmed=false;assert(not pcall(run)and #calls==0);confirmed=true
for _,mutation in ipairs({function()s.owned=true end,function()s.node=0 end,function()s.node=4 end,function()s.player_count=3 end,function()s.active=true end,function()s.vehicle='m103'end})do
 s.owned=false;s.node=1;s.player_count=2;s.active=false;s.vehicle='m102';mutation();assert(not pcall(tx.preflight,tx,s,2)and #calls==0)
end
print('PASS own-avatar-only reserved transaction; authenticated grant, single invocation, remote chassis unchanged, excluded roles/models/fleets')
