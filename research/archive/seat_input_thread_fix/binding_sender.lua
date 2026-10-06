-- Only the installer's verified avatar, channel0, M102 gunner -> passenger seats 1..3.
-- New protocol path: explicit channel clear followed by the selected personal weapon bind.
-- No seat entry/exit requests. Successful calls are not remote acknowledgments.
return function(api,game,p,spec,compat,inspector,route,trace,personal_factory)
 local ffi=require('ffi')
 local descriptor=ffi.typeof('struct { uint32_t type; uint32_t size; const void *value; }[3]')
 local personal=personal_factory(api,game,p)
 local function code(name)
  local d=assert(spec.records[name]);local at=game+assert(p.functions[name]).rva
  local b=api.read(at,d.length);assert(b and compat.match(b,d.chunks),'binding_code_'..name);return at
 end
 local function schema()
  for _,n in ipairs({'binding_clear_avatar','binding_clear_adapter','binding_clear_dispatch','binding_bind_adapter','binding_bind_dispatch','binding_bind_send','binding_entity_lookup','trace_send'})do code(n)end
  local x=inspector:interface(route)
  assert(x.state=='observed' and x.clear_dispatch_matches and x.bind_dispatch_matches,'binding_dispatch_changed')
  for hash,types in pairs({[0x423a4034]={256,536},[0x2671dec5]={256,536,256}})do
   local row;for _,m in ipairs(x.messages or {})do if m.hash==hash then row=m end end
   assert(row and row.found and row.flags[1]==1 and row.flags[2]==1 and row.parameter_count==#types,'binding_schema')
   for i,t in ipairs(types)do assert(row.type_indices[i]==t,'binding_schema_type')end
  end
  return x
 end
 local function same(a,b)return a.id==b.id and a.unit==b.unit and a.network_unit==b.network_unit and a.flags==b.flags end
 return {prepare=function(_,s,dest,target)
  if target==4 or s.node~=4 then return {check=function()end,send=function()end}end
  assert(target>=0 and target<=3 and target%1==0 and s.node==4 and s.vehicle=='m102' and s.owned,'binding_switch_scope')
  local evidence=schema();local avatar=inspector:entity(s.avatar)
  assert(avatar.unit==s.avatar_unit and require('bit').band(avatar.flags,1)==1,'binding_avatar_not_local')
  local local_avatar={id=s.avatar,unit=s.avatar_unit,network_unit=avatar.network_unit,is_local=true}
  local before=inspector:capture(local_avatar)
  assert(before.stable and before.weapon_component_found and before.rotation_flag==0 and #before.slots==5,'binding_gunner_state')
  for i=2,5 do assert(before.slots[i].weapon==0,'binding_unexpected_extra_channel')end
  local gun=inspector:entity(before.slots[1].weapon)
  local ok,selected=personal(s);assert(ok and selected and selected~=gun.id,'binding_personal_selection')
  local weapon=inspector:entity(selected)
  local values=ffi.new('uint32_t[3]',{avatar.network_unit,0,weapon.network_unit});local args=descriptor()
  for i=0,2 do args[i].type=1;args[i].size=4;args[i].value=values+i end
  local invoke=ffi.cast('void (*)(uint32_t,uint64_t,const void *,uint32_t)',code('trace_send'))
  local used=false
  local function check()
   schema();assert(same(inspector:entity(s.avatar),avatar),'binding_avatar_changed')
   assert(same(inspector:entity(selected),weapon),'binding_personal_entity_changed')
   local ready,current=personal(s);assert(ready and current==selected,'binding_personal_selection_changed')
   local after=inspector:capture(local_avatar)
   assert(after.stable and after.rotation_flag==1 and #after.slots==5 and after.slots[1].weapon==selected,'binding_local_restore_incomplete')
   for i=2,5 do assert(after.slots[i].weapon==0,'binding_local_extra_channel')end
   return after
  end
  return {check=check,send=function(emit)
   assert(not used,'binding_pair_already_sent');trace:health();local after=check();used=true
   emit({event='sync_weapon_clear_invoking',avatar=s.avatar,network_unit=avatar.network_unit,channel=0,
    old_weapon=gun.id,selected_weapon=selected,before=before,after=after,interface=evidence,remote_success_not_confirmed=true})
   invoke(0x423a4034,dest,args,2)
   emit({event='sync_personal_bind_invoking',avatar=s.avatar,channel=0,weapon=selected,weapon_network_unit=weapon.network_unit,remote_success_not_confirmed=true})
   invoke(0x2671dec5,dest,args,3)
   assert(values[1]==0);emit({event='sync_weapon_pair_calls_returned',remote_success_not_confirmed=true})
  end}
 end}
end
