-- Five validated vehicle tables, two players. Only the installer's avatar changes.
-- or borrowed chassis with the remote driver retained. Only own avatar changes.
return function(api,game,p,pose_factory,personal_factory,emit,driver_factory,layout,tank_driver_factory)
 local function bind(name,sig)
  local f=assert(p.functions[name]);assert(api.read(game+f.rva,#f.bytes)==f.bytes,'integrated_signature_'..name)
  return api.ffi.cast(sig,game+f.rva)
 end
 local reserve=bind('reserve','void (*)(void *,uint32_t,int32_t)')
 local release=bind('release','void (*)(void *,uint32_t,int32_t)')
 local clear=bind('clear_vehicle_weapon','void (*)(void *,uint32_t)')
 local restore=bind('restore_personal_weapon','void (*)(void *)')
 local equip=bind('equip_current_personal_weapon','void (*)(void *)')
 local refresh=bind('refresh_weapon_context','void (*)(void *)')
 local role=bind('set_role','void (*)(void *,uint32_t,uint32_t)')
 local seated=bind('restore_seated','void (*)(void *,void *,uint32_t,uint32_t,int32_t,bool)')
 local authority=bind('authority','void (*)(void *,uint32_t,int32_t,uint32_t)')
 local action=bind('seat_action','float (*)(uint32_t,uint32_t,int32_t,int32_t)')
 local rotation=bind('avatar_rotation','void (*)(void *,uint32_t,bool)')
 local remove=layout and bind('remove_avatar_flag','void (*)(void *,uint32_t)')or nil
 local pose=pose_factory(api,p);local personal=personal_factory(api,game,p)
 return {prepare=function(_,s,target)
  local d=layout and layout(s)or not layout and s.vehicle=='m102'and s.transition==26 and {roles={1,3,3,3,2},frv=true,mount=4,prepare=4}
  assert(d and s.owned and s.player_count==2 and s.peer_count==2,'integrated_transaction_scope')
  assert(s.node>=0 and s.node<#d.roles and s.node%1==0 and target>=0 and target<#d.roles and target%1==0 and s.node~=target,'integrated_transaction_direction')
  assert(s.profile.roles[s.node+1]==d.roles[s.node+1]and s.profile.roles[target+1]==d.roles[target+1]and not s.active and s.occupied[target]==false,'integrated_transaction_seat')
  local personal_target=d.roles[target+1]==3 or d.frv and target==0
  if personal_target then assert(personal(s))end;assert(pose.check(s))
  local neutralize
  if s.node==0 then neutralize=assert(driver_factory,'driver_factory_required')(api,game,p,layout).prepare(s)end
  local leave_tank
  if d.tank and s.node==0 and tank_driver_factory then leave_tank=tank_driver_factory(api,game,p,layout,emit):prepare(s)end
  return function()
   local function stage(name)emit({event='integrated_local_stage',stage=name,source=s.node,target=target})end
   if neutralize then stage('neutralize_own_driver_commands');neutralize()end
   if leave_tank then stage('deactivate_own_tank_driver');leave_tank()end
   stage('reserve');reserve(s.collections,s.collection_index,target)
   stage('clear_own_weapon_channels');clear(s.avatar_address,0);clear(s.avatar_address,1)
   stage('refresh_own_weapon_context');restore(s.avatar_address);refresh(s.avatar_address)
   if d.smoke then stage('clear_old_driver_smoke_flag');remove(s.avatar_address,44)end
   if d.frv and s.node==d.mount then stage('restore_avatar_rotation');rotation(nil,s.avatar,true)end
   stage('release');release(s.collections,s.collection_index,s.node)
   stage('set_role');role(s.seaters,s.seater_index,s.profile.roles[target+1])
   if d.prepare and target==d.mount then stage('prepare_gunner_camera_body');action(s.transition,s.avatar,d.prepare,target)end
   stage('restore_seated');seated(s.seaters,nil,s.avatar,s.collection,target,false)
   if personal_target then stage('equip_personal_weapon');equip(s.avatar_address);restore(s.avatar_address)end
   stage('pose');local detail=pose.apply(s,target)
   stage('native_seat_authority');authority(s.collections,s.collection_index,target,s.avatar)
   emit({event='integrated_local_calls_returned',target=target,pose=detail})
  end
 end}
end
