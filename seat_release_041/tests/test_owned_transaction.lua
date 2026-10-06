-- Real owner-local transaction and actual native-call FFI signatures.
-- Driver, native exit and steering backend are explicit effect doubles.
local ffi=require('ffi');local scope=assert(loadfile('work/seat_release_041/src/scope.lua'))()
local base=assert(loadfile('work/seat_release_041/src/owned_base.lua'))()
local wrapper=assert(loadfile('work/seat_release_041/src/owned_transaction.lua'))()
local profiles=assert(loadfile('work/seat_release_041/src/profile.lua'))().tables
local p={functions={}};local code={};local callbacks={};local calls={};local source,target,d
local manager,avatar=ffi.cast('void *',0x420000),ffi.cast('void *',0x430000)
local sigs={reserve='void (*)(void *,uint32_t,int32_t)',release='void (*)(void *,uint32_t,int32_t)',
 clear_vehicle_weapon='void (*)(void *,uint32_t)',restore_personal_weapon='void (*)(void *)',
 equip_current_personal_weapon='void (*)(void *)',refresh_weapon_context='void (*)(void *)',
 set_role='void (*)(void *,uint32_t,uint32_t)',restore_seated='void (*)(void *,void *,uint32_t,uint32_t,int32_t,bool)',
 authority='void (*)(void *,uint32_t,int32_t,uint32_t)',seat_action='float (*)(uint32_t,uint32_t,int32_t,int32_t)',
 avatar_rotation='void (*)(void *,uint32_t,bool)',remove_avatar_flag='void (*)(void *,uint32_t)'}
for name,sig in pairs(sigs)do
 local cb=ffi.cast(sig,function(...)
  local a={...};calls[#calls+1]=name
  if name=='reserve'or name=='release'then assert(a[1]==manager and a[2]==12 and a[3]==(name=='reserve'and target or source))
  elseif name=='clear_vehicle_weapon'then assert(a[1]==avatar and(a[2]==0 or a[2]==1))
  elseif name=='restore_personal_weapon'or name=='equip_current_personal_weapon'or name=='refresh_weapon_context'then assert(a[1]==avatar)
  elseif name=='set_role'then assert(a[1]==manager and a[2]==47 and a[3]==d.roles[target+1])
  elseif name=='restore_seated'then assert(a[1]==manager and a[2]==nil and a[3]==7 and a[4]==9 and a[5]==target and a[6]==false)
  elseif name=='authority'then assert(a[1]==manager and a[2]==12 and a[3]==target and a[4]==7)
  elseif name=='seat_action'then assert(d.prepare and target==d.mount and a[1]==d.transition and a[2]==7 and a[3]==d.prepare and a[4]==target);return 0
  elseif name=='avatar_rotation'then assert(d.frv and source==d.mount and a[1]==nil and a[2]==7 and a[3]==true)
  elseif name=='remove_avatar_flag'then assert(d.smoke and a[1]==avatar and a[2]==44)end
 end)
 callbacks[#callbacks+1]=cb;local at=tonumber(ffi.cast('uintptr_t',cb));p.functions[name]={rva=at,bytes='x'};code[at]='x'
end
local api={ffi=ffi,read=function(at,n)return code[tonumber(ffi.cast('uintptr_t',at))]end}
local active,neutralized
local driver=function()return {prepare=function(s)assert(s.node==0);return function()calls[#calls+1]='neutralize';neutralized=true end end}end
local tank=function()return {prepare=function(_,s)assert(d.tank and s.node==0);return function()assert(neutralized);active=false;calls[#calls+1]='native_exit'end end}end
local steering={prepare=function(_,s)assert(d.tank and s.node==0);return function()assert(not active and neutralized);calls[#calls+1]='steering_reset'end end}
local pose=function()return {check=function()return true end,apply=function(_,t)assert(t==target);calls[#calls+1]='pose';return {}end}end
local personal=function()return function(s)assert(s.avatar_address==avatar);return true end end
local tx=wrapper(api,ffi.cast('uint8_t *',0),p,base,pose,personal,function()end,driver,scope,tank,steering)
local count=0
for room_count=1,4 do for _,name in ipairs({'m102','m103','m104','bastion','maelstrom'})do
 local profile=profiles[name]
 for from=0,#profile.roles-1 do for to=0,#profile.roles-1 do if from~=to then
  source,target=from,to;local s={vehicle=name,transition=profile.transition,profile=profile,node=source,
   owned=true,player_count=room_count,peer_count=room_count,active=false,occupied={},collections=manager,collection_index=12,
   seaters=manager,seater_index=47,avatar=7,avatar_address=avatar,collection=9}
  for n=0,#profile.roles-1 do s.occupied[n]=n==source end
  d=assert(scope.layout(s));active=true;neutralized=false;calls={};local perform=tx:prepare(s,target);assert(#calls==0);perform()
  assert(not pcall(perform),'owner transaction reusable');assert(calls[#calls]=='authority')
  local joined=','..table.concat(calls,',')..','
  if source==0 then assert(calls[1]=='neutralize')end
  if d.tank and source==0 then assert(joined:find(',neutralize,native_exit,steering_reset,reserve,',1,true)==1,'tank cleanup must precede reservation')
  else assert(not joined:find(',native_exit,',1,true)and not joined:find(',steering_reset,',1,true))end
  count=count+1
 end end end
end end
for _,cb in ipairs(callbacks)do cb:free()end
print('PASS '..count..' actual owner transaction FFI cases; generic neutralization -> native tank exit -> steering reset -> reserve; exact own avatar/slot/role, no entry animation, single-use')
