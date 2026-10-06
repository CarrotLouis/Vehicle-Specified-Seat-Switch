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
 local remove_flag=bind('remove_avatar_flag','void (*)(void *,uint32_t)')
 local pose=pose_factory(api,p);local personal=personal_factory(api,game,p)
 return {prepare=function(_,s,target)
  assert(s.vehicle=='m102'and s.transition==26 and s.owned and s.player_count==2 and s.peer_count==2,'integrated_transaction_scope')
  assert((s.node==1 and target==4)or(s.node==4 and target==1),'integrated_transaction_direction')
  assert(s.profile.roles[s.node+1]==(s.node==4 and 2 or 3) and s.profile.roles[target+1]==(target==4 and 2 or 3) and not s.active and s.occupied[target]==false,'integrated_transaction_seat')
  if target==1 then assert(personal(s))end;assert(pose.check(s))
  return function()
   local function stage(name)emit({event='integrated_local_stage',stage=name,source=s.node,target=target})end
   stage('reserve');reserve(s.collections,s.collection_index,target)
   stage('clear_own_weapon_channels');clear(s.avatar_address,0);clear(s.avatar_address,1)
   stage('refresh_own_weapon_context');restore(s.avatar_address);refresh(s.avatar_address)
   if s.node==4 then
    -- Leaving a weapon seat must detach the avatar the way the engine does. Its own
    -- seat-change paths clear avatar flag bit 0x2c immediately before emitting the FRV
    -- entry event (0x1193dad / 0x1193f0b / 0x1194011: remove_avatar_flag(avatar,0x2c)
    -- then event 0xe8344235 or 0xd3a9222b). The experiment emitted the event but never
    -- cleared the bit, and the 0.8.1 live run showed the host still driving the turret
    -- from the guest's aim after the return. Production native.lua already clears
    -- bit 44 for maelstrom.
    stage('clear_weapon_attachment_flag');remove_flag(s.avatar_address,44)
    -- 0x6ba600 is a per-avatar boolean setter (hash lookup by avatar id, then
    -- record[value*0x90+0x71] = arg3), not a rotation restore. The engine writes a
    -- state-derived value, so leaving the gunner seat must write false. 0.8.0 wrote
    -- true, which left the avatar in the vehicle-attached facing state: facing frozen,
    -- only discrete snaps on large view movement, and local versus remote aim disagreeing.
    stage('restore_avatar_rotation');rotation(nil,s.avatar,false)
   end
   stage('release');release(s.collections,s.collection_index,s.node)
   stage('set_role');role(s.seaters,s.seater_index,s.profile.roles[target+1])
   if target==4 then stage('prepare_gunner_camera_body');action(s.transition,s.avatar,4,target)end
   stage('restore_seated');seated(s.seaters,nil,s.avatar,s.collection,target,false)
   -- The engine runs a per-destination-seat restore action when a seat change
   -- completes, and profile tables already record that action index per seat.
   -- Verified in the 25480438 image: the M102 action dispatcher's jump table maps
   -- index 1 to 0x1188026, which emits entry event 0x29e8fb0c (already in our
   -- entry_events) and performs an aim-channel reset (0x91e230), 0x11aae70,
   -- 0x91e350, 0x11a1fa0 and 0x11ac800 - none of which our own clear_vehicle_weapon
   -- calls cover. That is why the turret stayed bound to the guest after the return.
   local restore_action=s.profile.restore and s.profile.restore[target+1]
   if s.node==4 and restore_action and restore_action>0 then
    stage('restore_destination_action');action(s.transition,s.avatar,restore_action,target)
   end
   if target==1 then stage('equip_personal_weapon');equip(s.avatar_address);restore(s.avatar_address)end
   stage('pose');local detail=pose.apply(s,target)
   stage('native_seat_authority');authority(s.collections,s.collection_index,target,s.avatar)
   emit({event='integrated_local_calls_returned',target=target,pose=detail})
  end
 end}
end
