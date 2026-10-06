local factory=assert(loadfile('work/seat_remote_animation_diagnostic/transaction.lua'))()
local names={'reserve','release','clear_vehicle_weapon','restore_personal_weapon','equip_current_personal_weapon','refresh_weapon_context','set_role','restore_seated','authority'}
local p={functions={}};local at={};local calls={}
for i,n in ipairs(names)do p.functions[n]={rva=i,bytes='x'};at[i]=n end
local api={read=function()return 'x'end,ffi={cast=function(sig,rva)return function(...)
 local n=at[rva];local args={...};calls[#calls+1]=n
 if n=='clear_vehicle_weapon'or n=='restore_personal_weapon'or n=='equip_current_personal_weapon'or n=='refresh_weapon_context'then assert(args[1]==700,'must affect only local avatar')end
 if n=='set_role'then assert(args[3]==3)end
 if n=='restore_seated'then assert(args[3]==7 and args[4]==9 and args[5]==2 and args[6]==false)end
end end}}
local pose=function()return {check=function()return true end,apply=function()calls[#calls+1]='pose';return 'pose'end}end
local personal=function()return function(s)assert(s.avatar==7);return true end end
local tx=factory(api,0,p,pose,personal,function()end)
local s={avatar=7,avatar_address=700,collection=9,vehicle='m102',transition=26,owned=true,player_count=2,peer_count=2,node=1,occupied={[2]=false},profile={roles={1,3,3,3,2}}}
local perform=tx:prepare(s,2);assert(#calls==0);perform()
assert(table.concat(calls,',')=='reserve,clear_vehicle_weapon,clear_vehicle_weapon,restore_personal_weapon,refresh_weapon_context,release,set_role,restore_seated,equip_current_personal_weapon,restore_personal_weapon,pose,authority')
for _,change in ipairs({function()s.node=0 end,function()s.owned=false end,function()s.active=true end})do
 s.node=1;s.owned=true;s.active=false;change();assert(not pcall(tx.prepare,tx,s,2))
end
print('PASS passenger transaction own-avatar-only calls, personal weapon rebind, final pose, no driver neutralization, scope refusal')
