-- Solo uses the same final seat/weapon/pose transaction, without notifications.
return function(api,game,p,normal,owned_transaction,pose_factory,scope)
 local ffi=api.ffi
 local function bind(name,signature)
  local f=assert(p.functions[name])
  assert(api.read(game+f.rva,#f.bytes)==f.bytes,'solo_interface_changed_'..name)
  return ffi.cast(signature,game+f.rva)
 end
 local busy=bind('ownership_busy','bool (*)(void *,uint32_t)')
 local active=bind('active_passenger','void (*)(void *,uint32_t,bool)')
 local pose=pose_factory(api,p)
 local self={next=normal.next,previous=normal.previous}
 function self.available(s)
  if not s or not s.owned or s.player_count~=1 or s.peer_count~=1 or not scope.layout(s) then
   return false,'solo_authority_or_membership_unavailable'
  end
  local systems=api.pointer(api.read(game+p.globals.entities,8))
  local engine=systems and api.pointer(api.read(systems+8,8))
  if not engine then return false,'missing_engine' end
  if s.collection_unit~=0x7fff and busy(engine,s.collection_unit) then return false,'vehicle_authority_changing' end
  local ok,why=pcall(pose.check,s)
  if not ok then return false,'solo_pose_unavailable '..tostring(why) end
  return true
 end
 function self.prepare(s)
  local ok,why=self.available(s);assert(ok,why)
  active(s.seaters,s.avatar,false)
 end
 function self.direct(s,target)
  local ok,why=self.available(s);assert(ok,why)
  assert(not s.active,'solo_passenger_still_active')
  -- All preparation is read-only. A rejected preflight is an ordinary refused
  -- request, not a reason to stop menus or every future seat operation.
  local ready,perform=pcall(owned_transaction.prepare,owned_transaction,s,target)
  if not ready then
   self.last_detail='direct_preflight_refused '..tostring(perform)
   return false,tostring(perform)
  end
  perform() -- Invocation errors may follow mutations and must stay fail-closed.
  self.last_detail='direct_complete; own_avatar_only; driver_exit_cleanup_if_required'
  return true
 end
 return self
end
