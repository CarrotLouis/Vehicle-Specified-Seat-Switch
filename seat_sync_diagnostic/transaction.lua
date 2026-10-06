-- Experimental, isolated adapter; gameplay0.2.4 remains unchanged.
return function(api,game,p,pose_factory,driver_factory,emit)
 local ffi=api.ffi
 local function bind(name,sig)
  local f=assert(p.functions[name]);assert(api.read(game+f.rva,#f.bytes)==f.bytes,'transaction_signature_'..name)
  return ffi.cast(sig,game+f.rva)
 end
 local reserve=bind('reserve','void (*)(void *,uint32_t,int32_t)')
 local release=bind('release','void (*)(void *,uint32_t,int32_t)')
 local clear=bind('clear_vehicle_weapon','void (*)(void *,uint32_t)')
 local restore_weapon=bind('restore_personal_weapon','void (*)(void *)')
 local refresh=bind('refresh_weapon_context','void (*)(void *)')
 local role=bind('set_role','void (*)(void *,uint32_t,uint32_t)')
 local seated=bind('restore_seated','void (*)(void *,void *,uint32_t,uint32_t,int32_t,bool)')
 local authority=bind('authority','void (*)(void *,uint32_t,int32_t,uint32_t)')
 local pose=pose_factory(api,p);local driver=driver_factory(api,game,p)
 local self={}
 function self:prepare(s,target)
  assert(s.vehicle=='bastion'and s.transition==43 and s.owned and s.player_count==2 and s.peer_count==2,'transaction_scope')
  assert((s.node==0 and target==1)or(s.node==1 and target==0),'transaction_direction')
  assert(not s.active and s.occupied[target]==false,'transaction_seat_busy')
  assert(pose.check(s),'transaction_pose_not_ready')
  local neutralize=s.node==0 and driver.prepare(s)or nil
  return function()
   local function stage(name)emit({event='sync_local_stage',stage=name,source=s.node,target=target})end
   if neutralize then stage('neutralize_driver');neutralize()end
   stage('reserve');reserve(s.collections,s.collection_index,target)
   stage('stop_vehicle_weapon');clear(s.avatar_address,0);clear(s.avatar_address,1)
   stage('restore_personal_context');restore_weapon(s.avatar_address);refresh(s.avatar_address)
   stage('release');release(s.collections,s.collection_index,s.node)
   stage('set_role');role(s.seaters,s.seater_index,s.profile.roles[target+1])
   stage('restore_seated');seated(s.seaters,nil,s.avatar,s.collection,target,false)
   stage('pose');local detail=pose.apply(s,target)
   stage('authority');authority(s.collections,s.collection_index,target,s.avatar)
   emit({event='sync_local_calls_returned',target=target,pose=detail})
  end
 end
 return self
end
