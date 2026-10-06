-- ABI recovered from Steam build 25327279. This is an in-game TEST adapter.
-- Native code has no recoverable Lua exception boundary; profile and identity
-- checks must complete before calling it. No arbitrary address is accepted.
return function(api,game,profile)
 local ffi=api.ffi
 local n={}
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
  return true
 end
 function n.prepare(s)active_passenger(s.seaters,s.avatar,false) end
 function n.direct(s,target)
  assert(type(target)=='number' and target%1==0 and target>=0 and target<#s.profile.roles and target~=s.node and s.occupied[target]==false,'Invalid direct target')
  assert(s.owned and not s.active,'Direct operation requires local vehicle authority')
  assert(profile.direct_solo_only and s.player_count==1 and s.peer_count<=1,'Multiplayer direct restore not validated')
  -- These routines update the replicated seat mask and linked interactables.
  -- They are only called on the owning peer after fresh occupancy checks.
  reserve(s.collections,s.collection_index,target)
  release(s.collections,s.collection_index,s.node)
  set_role(s.seaters,s.seater_index,s.profile.roles[target+1])
  restore_seated(s.seaters,nil,s.avatar,s.collection,target,false)
  authority(s.collections,s.collection_index,target,s.avatar)
  -- Kept for protocol research only. A late-join snapshot alone does not update
  -- remote role/input state. Never send this incomplete sequence in the test.
 end
 return n
end
