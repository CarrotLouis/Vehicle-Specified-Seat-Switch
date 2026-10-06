local factory=assert(loadfile('work/seat_weapon_sync_diagnostic/transaction.lua'))()
local names={'reserve','release','clear_vehicle_weapon','restore_personal_weapon','equip_current_personal_weapon','refresh_weapon_context','set_role','restore_seated','authority','seat_action','avatar_rotation','remove_avatar_flag'}
local p={functions={}};local at={};local calls={};local target,source,personal_ok,checks
for i,n in ipairs(names)do p.functions[n]={rva=i,bytes='x'};at[i]=n end
local api={read=function()return 'x'end,ffi={cast=function(sig,rva)return function(...)
 local n=at[rva];local a={...};calls[#calls+1]=n
 if n=='clear_vehicle_weapon'or n=='restore_personal_weapon'or n=='equip_current_personal_weapon'or n=='refresh_weapon_context'then assert(a[1]==700,'must affect only local avatar')end
 if n=='set_role'then assert(a[3]==(target==4 and 2 or 3))end
 if n=='restore_seated'then assert(a[3]==7 and a[4]==9 and a[5]==target and a[6]==false)end
 if n=='seat_action'then
  if target==4 then assert(a[1]==26 and a[2]==7 and a[3]==4 and a[4]==4,'gunner prep action')
  else assert(source==4 and a[1]==26 and a[2]==7 and a[3]==1 and a[4]==1,'destination restore action') end
 end
 -- 0x6ba600 writes arg3 into the per-avatar vehicle-attachment flag; detaching from
 -- the gunner seat must clear it. 0.8.1 corrected the inverted value.
 if n=='avatar_rotation'then assert(source==4 and a[1]==nil and a[2]==7 and a[3]==false)end
 -- The engine clears avatar flag bit 0x2c (44) before emitting the FRV entry event.
 if n=='remove_avatar_flag'then assert(source==4 and a[1]==700 and a[2]==44)end
 if n=='reserve'then assert(a[3]==target)end
 if n=='release'then assert(a[3]==source)end
 if n=='authority'then assert(a[3]==target and a[4]==7)end
end end}}
local pose=function()return {check=function()return true end,apply=function(_,t)assert(t==target);calls[#calls+1]='pose';return 'pose'end}end
local personal=function()return function(s)assert(s.avatar==7);checks=checks+1;return personal_ok end end
local tx=factory(api,0,p,pose,personal,function()end)
local s={avatar=7,avatar_address=700,collection=9,vehicle='m102',transition=26,owned=true,player_count=2,peer_count=2,node=1,occupied={[1]=false,[4]=false},profile={roles={1,3,3,3,2},restore={0,1,2,3,5}}}
source=1;target=4;checks=0;personal_ok=true
local perform=tx:prepare(s,target);assert(#calls==0 and checks==0);perform()
assert(table.concat(calls,',')=='reserve,clear_vehicle_weapon,clear_vehicle_weapon,restore_personal_weapon,refresh_weapon_context,release,set_role,seat_action,restore_seated,pose,authority')
source=4;target=1;s.node=4;calls={};perform=tx:prepare(s,target);assert(#calls==0 and checks==1);perform()
assert(table.concat(calls,',')=='reserve,clear_vehicle_weapon,clear_vehicle_weapon,restore_personal_weapon,refresh_weapon_context,remove_avatar_flag,avatar_rotation,release,set_role,restore_seated,seat_action,equip_current_personal_weapon,restore_personal_weapon,pose,authority')
calls={};personal_ok=false;assert(not pcall(tx.prepare,tx,s,1)and #calls==0)
personal_ok=true
for _,change in ipairs({function()s.node=0 end,function()s.owned=false end,function()s.active=true end,function()s.occupied[4]=true end,function()s.player_count=3 end})do
 s.node=1;s.owned=true;s.active=false;s.occupied[4]=false;s.player_count=2;change();assert(not pcall(tx.prepare,tx,s,4))
end
assert(#calls==0)
print('PASS passenger/gunner camera/body prep, both weapon channels, engine detach flag bit 44 cleared before the entry event, attachment boolean false, engine destination restore action on the return, personal rebind, local avatar only, untouched driver, preflight refusal')
