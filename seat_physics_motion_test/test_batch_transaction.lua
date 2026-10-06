-- Actual transaction module and explicit recovered tables; native calls mocked.
local root='work/seat_physics_motion_test/'
local factory=assert(loadfile(root..'transaction.lua'))()
local layout=assert(loadfile(root..'adapter.lua'))().layout
local profiles=assert(loadfile('work/seat_switch/src/profile.lua'))().tables
local names={'reserve','release','clear_vehicle_weapon','restore_personal_weapon','equip_current_personal_weapon','refresh_weapon_context','set_role','restore_seated','authority','seat_action','avatar_rotation','remove_avatar_flag'}
local p={functions={}};local at={};local calls={};local v,source,target,d,smoke,checks;local cases=0
for i,name in ipairs(names)do p.functions[name]={rva=i,bytes='x'};at[i]=name end
local api={read=function()return 'x'end,ffi={cast=function(sig,rva)return function(...)
 local name,args=at[rva],{...};calls[#calls+1]=name
 if name=='clear_vehicle_weapon'or name=='restore_personal_weapon'or name=='equip_current_personal_weapon'or name=='refresh_weapon_context'or name=='remove_avatar_flag'then assert(args[1]==700)end
 if name=='clear_vehicle_weapon'then assert(args[2]==0 or args[2]==1)end
 if name=='set_role'then assert(args[3]==d.roles[target+1])end
 if name=='restore_seated'then assert(args[3]==7 and args[4]==9 and args[5]==target and args[6]==false);smoke=d.smoke and target==0 or false end
 if name=='seat_action'then assert(d.frv and target==d.mount and args[1]==d.transition and args[2]==7 and args[3]==d.prepare and args[4]==target)end
 if name=='avatar_rotation'then assert(d.frv and source==d.mount and args[1]==nil and args[2]==7 and args[3]==true)end
 if name=='remove_avatar_flag'then assert(d.smoke and args[2]==44);smoke=false end
 if name=='reserve'then assert(args[3]==target)end
 if name=='release'then assert(args[3]==source)end
 if name=='authority'then assert(args[3]==target and args[4]==7)end
end end}}
local pose=function()return {check=function()return true end,apply=function(_,t)assert(t==target);calls[#calls+1]='pose';return 'pose'end}end
local personal=function()return function(s)assert(s.avatar==7);checks=checks+1;return true end end
local driver=function(_,_,_,verify)return {prepare=function(s)assert(verify(s)and source==0);return function()calls[#calls+1]='neutralize_driver'end end}end
local tank_driver=function()return {prepare=function(_,s)assert(layout(s).tank and source==0);return function()calls[#calls+1]='deactivate_tank_driver'end end}end
local tx=factory(api,0,p,pose,personal,function()end,driver,layout,tank_driver)
for _,name in ipairs({'m102','m103','m104','bastion','maelstrom'})do
 v=name;local profile=profiles[v]
 for a=0,#profile.roles-1 do for b=0,#profile.roles-1 do if a~=b then
  source,target=a,b;local s={avatar=7,avatar_address=700,collection=9,vehicle=v,transition=profile.transition,profile=profile,
   owned=true,player_count=2,peer_count=2,node=source,occupied={[target]=false}}
  d=assert(layout(s));calls={};checks=0;smoke=d.smoke and source==0 or false
  local run=tx:prepare(s,target);assert(#calls==0);run()
  local sequence=','..table.concat(calls,',')..','
  local function has(name_)return sequence:find(','..name_..',',1,true)~=nil end
  assert((calls[1]=='neutralize_driver')==(source==0))
  assert(has('deactivate_tank_driver')==(d.tank and source==0 or false))
  if d.tank and source==0 then assert(calls[2]=='deactivate_tank_driver'and calls[3]=='reserve')end
  assert(has('avatar_rotation')==(d.frv and source==d.mount or false))
  assert(has('seat_action')==(d.prepare~=nil and target==d.mount))
  assert(has('remove_avatar_flag')==(d.smoke or false))
  local personal_target=d.roles[target+1]==3 or d.frv and target==0
  assert(has('equip_current_personal_weapon')==(personal_target or false)and checks==(personal_target and 1 or 0))
  assert(calls[#calls]=='authority'and smoke==(d.smoke and target==0 or false))
  cases=cases+1
  for _,change in ipairs({function()s.owned=false end,function()s.occupied[target]=true end,
   function()s.transition=99 end,function()s.active=true end,function()s.peer_count=3 end})do
   s.owned=true;s.occupied[target]=false;s.transition=profile.transition;s.active=false;s.peer_count=2;change();calls={}
   assert(not pcall(tx.prepare,tx,s,target)and #calls==0);cases=cases+1
  end
 end end end
end
print('PASS '..cases..' real batched transaction cases: all five vehicle pairs, exact native arguments/order, only own avatar, both channels, FRV preparation/rotation, tank personal-vs-mounted roles, Maelstrom smoke flag, driver neutralization, no mutation on guard failure')
