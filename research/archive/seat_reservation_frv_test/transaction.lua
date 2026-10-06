-- An authenticated owner grant already holds target. Mutate only the
-- installer's avatar. Never reserve/release the nonowned collection locally.
return function(api,game,p,pose_factory,personal_factory,emit,scope)
 local function bind(name,sig)
  local f=assert(p.functions[name]);assert(api.read(game+f.rva,#f.bytes)==f.bytes,'reserved_transaction_signature_'..name)
  return api.ffi.cast(sig,game+f.rva)
 end
 local clear=bind('clear_vehicle_weapon','void (*)(void *,uint32_t)')
 local restore=bind('restore_personal_weapon','void (*)(void *)')
 local equip=bind('equip_current_personal_weapon','void (*)(void *)')
 local refresh=bind('refresh_weapon_context','void (*)(void *)')
 local role=bind('set_role','void (*)(void *,uint32_t,uint32_t)')
 local seated=bind('restore_seated','void (*)(void *,void *,uint32_t,uint32_t,int32_t,bool)')
 local action=bind('seat_action','float (*)(uint32_t,uint32_t,int32_t,int32_t)')
 local rotation=bind('avatar_rotation','void (*)(void *,uint32_t,bool)')
 local pose=pose_factory(api,p);local personal=personal_factory(api,game,p)
 local function preflight(s,target)
  assert(scope.layout(s)and not s.owned and s.player_count==2 and s.peer_count==2,'reserved_transaction_scope')
  assert(scope.direction(s,target)and not s.active,'reserved_transaction_direction')
  if s.profile.roles[target+1]==3 then assert(personal(s))end;assert(pose.check(s))
  return true
 end
 return {preflight=function(_,s,target)return preflight(s,target)end,prepare=function(_,s,target,grant)
  preflight(s,target)
  assert(grant and grant.target==target and grant.source==s.node and grant:check(),'reserved_transaction_real_grant_required')
  local used=false
  return function()
   assert(not used and grant:check(),'reserved_transaction_grant_changed');used=true
   local function stage(name)emit({event='reserved_local_stage',stage=name,source=s.node,target=target})end
   stage('clear_own_weapon_channels');clear(s.avatar_address,0);clear(s.avatar_address,1)
   stage('refresh_own_weapon_context');restore(s.avatar_address);refresh(s.avatar_address)
   local d=assert(scope.layout(s));local personal_target=d.roles[target+1]==3
   if d.mount and s.node==d.mount then stage('restore_own_avatar_rotation');rotation(nil,s.avatar,true)end
   stage('set_own_seat_role');role(s.seaters,s.seater_index,d.roles[target+1])
   if d.prepare and target==d.mount then stage('prepare_own_mounted_camera_body');action(s.transition,s.avatar,d.prepare,target)end
   stage('restore_own_seated');seated(s.seaters,nil,s.avatar,s.collection,target,false)
   if personal_target then stage('equip_own_personal_weapon');equip(s.avatar_address);restore(s.avatar_address)end
   stage('apply_own_seated_pose');local detail=pose.apply(s,target)
   emit({event='reserved_local_calls_returned',target=target,pose=detail,chassis_authority_transfer=false})
  end
 end}
end
