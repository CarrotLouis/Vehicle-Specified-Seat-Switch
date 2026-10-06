-- M102 passenger1 <-> gunner4. The friend remains the driver.
return function(api,game,p,pose_factory,personal_factory,emit)
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
 local pose=pose_factory(api,p);local personal=personal_factory(api,game,p)
 return {prepare=function(_,s,target)
  assert(s.vehicle=='m102'and s.transition==26 and s.owned and s.player_count==2 and s.peer_count==2,'integrated_transaction_scope')
  assert((s.node>=1 and s.node<=3 and s.node%1==0 and target==4)or(s.node==4 and target>=1 and target<=3 and target%1==0),'integrated_transaction_direction')
  assert(s.profile.roles[s.node+1]==(s.node==4 and 2 or 3) and s.profile.roles[target+1]==(target==4 and 2 or 3) and not s.active and s.occupied[target]==false,'integrated_transaction_seat')
  if target~=4 then assert(personal(s))end;assert(pose.check(s))
  return function()
   local function stage(name)emit({event='integrated_local_stage',stage=name,source=s.node,target=target})end
   stage('reserve');reserve(s.collections,s.collection_index,target)
   stage('clear_own_weapon_channels');clear(s.avatar_address,0);clear(s.avatar_address,1)
   stage('refresh_own_weapon_context');restore(s.avatar_address);refresh(s.avatar_address)
   if s.node==4 then stage('restore_avatar_rotation');rotation(nil,s.avatar,true)end
   stage('release');release(s.collections,s.collection_index,s.node)
   stage('set_role');role(s.seaters,s.seater_index,s.profile.roles[target+1])
   if target==4 then stage('prepare_gunner_camera_body');action(s.transition,s.avatar,4,target)end
   stage('restore_seated');seated(s.seaters,nil,s.avatar,s.collection,target,false)
   if target~=4 then stage('equip_personal_weapon');equip(s.avatar_address);restore(s.avatar_address)end
   stage('pose');local detail=pose.apply(s,target)
   stage('native_seat_authority');authority(s.collections,s.collection_index,target,s.avatar)
   emit({event='integrated_local_calls_returned',target=target,pose=detail})
  end
 end}
end
