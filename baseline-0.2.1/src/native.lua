-- ABI recovered from Steam build 25327279. This is an in-game TEST adapter.
-- Native code has no recoverable Lua exception boundary; profile and identity
-- checks must complete before calling it. No arbitrary address is accepted.
return function(api,game,profile,pose_factory,trace)
 local ffi=api.ffi
 local n={}
 local transaction=0
 local function mark(stage)
  if trace then pcall(trace,'direct_stage id='..transaction..' stage='..stage) end
 end
 local function bind(name,ctype)
  local p=assert(profile.functions[name],name)
  assert(api.read(game+p.rva,#p.bytes)==p.bytes,'Native signature mismatch: '..name)
  return ffi.cast(ctype,game+p.rva)
 end
 n.next=bind('next','void (*)(void *,uint32_t)')
 n.previous=bind('previous','void (*)(void *,uint32_t)')
 local reserve=bind('reserve','void (*)(void *,uint32_t,int32_t)')
 local release=bind('release','void (*)(void *,uint32_t,int32_t)')
 local authority=bind('authority','void (*)(void *,uint32_t,int32_t,uint32_t)')
 local set_role=bind('set_role','void (*)(void *,uint32_t,uint32_t)')
 local restore_seated=bind('restore_seated','void (*)(void *,void *,uint32_t,uint32_t,int32_t,bool)')
 local ownership_busy=bind('ownership_busy','bool (*)(void *,uint32_t)')
 local active_passenger=bind('active_passenger','void (*)(void *,uint32_t,bool)')
 local clear_weapon=bind('clear_vehicle_weapon','void (*)(void *,uint32_t)')
 local restore_personal=bind('restore_personal_weapon','void (*)(void *)')
 local refresh_weapon=bind('refresh_weapon_context','void (*)(void *)')
 local remove_flag=bind('remove_avatar_flag','void (*)(void *,uint32_t)')
 local action=bind('seat_action','float (*)(uint32_t,uint32_t,int32_t,int32_t)')
 local rotation=bind('avatar_rotation','void (*)(void *,uint32_t,bool)')
 local pose
 local function pose_ready(s)
  if not pose then pose=assert(pose_factory,'Missing pose adapter')(api,profile) end
  return pose.check(s)
 end
 function n.available(s)
  if not s.owned then return false,'vehicle_owned_by_other_peer' end
  -- The first gameplay test must establish local pose/control correctness before
  -- enabling the unverified multiplayer restore protocol. Native group switches
  -- still use the game's normal owner arbitration in either package variant.
  if not profile.direct_solo_only or s.player_count~=1 or s.peer_count>1 then return false,'direct_multiplayer_not_validated' end
  local systems=api.pointer(api.read(game+profile.globals.entities,8))
  if not systems then return false,'missing_engine' end
  -- The native request checks the entity system -> +8 before ownership handoff.
  local engine=api.pointer(api.read(systems+8,8))
  if not engine then return false,'missing_engine' end
  if s.collection_unit~=0x7fff and ownership_busy(engine,s.collection_unit) then
   return false,'vehicle_authority_changing'
  end
  local ok,why=pcall(pose_ready,s)
  if not ok then return false,'direct_pose_unavailable '..tostring(why) end
  return true
 end
 function n.prepare(s)active_passenger(s.seaters,s.avatar,false) end
 function n.direct(s,target)
  assert(type(target)=='number' and target%1==0 and target>=0 and target<#s.profile.roles and target~=s.node and s.occupied[target]==false,'Invalid direct target')
  assert(s.owned and not s.active,'Direct operation requires local vehicle authority')
  assert(profile.direct_solo_only and s.player_count==1 and s.peer_count<=1,'Multiplayer direct restore not validated')
  assert(pose_ready(s))
  -- These routines update the replicated seat mask and linked interactables.
  -- They are only called on the owning peer after fresh occupancy checks.
  transaction=transaction+1
  mark('reserve_target')
  reserve(s.collections,s.collection_index,target)
  -- The original switch/exit paths stop a mounted weapon before unbinding it.
  -- Both channels matter: tanks use channel 1 for the coaxial gun, and the
  -- Maelstrom driver uses channel 0 for the smoke launcher.
  mark('stop_old_weapon_0')
  clear_weapon(s.avatar_address,0)
  mark('stop_old_weapon_1')
  clear_weapon(s.avatar_address,1)
  mark('restore_personal_weapon')
  restore_personal(s.avatar_address)
  mark('refresh_weapon_context')
  refresh_weapon(s.avatar_address)
  mark('clear_old_seat_flags')
  if s.vehicle=='maelstrom' then remove_flag(s.avatar_address,44) end
  if (s.vehicle=='m102' or s.vehicle=='m104') and s.profile.roles[s.node+1]==2 then
   rotation(nil,s.avatar,true)
  end
  mark('release_old_seat')
  release(s.collections,s.collection_index,s.node)
  mark('set_new_role')
  set_role(s.seaters,s.seater_index,s.profile.roles[target+1])
  -- FRV late-join restore only runs the final gun attachment action. Its
  -- preceding action configures the gunner camera, holster and body modes.
  mark('prepare_target')
  if s.profile.roles[target+1]==2 then
   if s.vehicle=='m102' then action(s.transition,s.avatar,4,target)
   elseif s.vehicle=='m104' then action(s.transition,s.avatar,2,target) end
  end
  mark('restore_target')
  restore_seated(s.seaters,nil,s.avatar,s.collection,target,false)
  -- Same callback, before another rendered/simulation frame: replace the entry
  -- clip with its final seated state; never run an exit action or clear collection.
  mark('apply_final_pose')
  n.last_detail=pose.apply(s,target)..' old_weapon_channels_cleared=0,1'
  mark('transfer_authority')
  authority(s.collections,s.collection_index,target,s.avatar)
  mark('complete')
  -- Kept for protocol research only. A late-join snapshot alone does not update
  -- remote role/input state. Never send this incomplete sequence in the test.
 end
 return n
end
