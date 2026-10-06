local M={}
local function seated(a,v,node,role)
 local s=a and a.seat
 return s and s.collection==v.id and s.current==node and s.reserved==node and s.role==role
  and s.target==-1 and s.action==-1 and s.transitioning==0 and s.queued_exit==0
end
function M.eligible(c,source,owned,ticket,target,confirmation)
 local s,o=c.native,c.owner
 if not s then return false,c.native_reason or 'local_seat_unavailable'end
 if s.vehicle~='m102'or s.transition~=26 or #s.profile.roles~=5 then return false,'M102_only'end
 local expected=owned and o.selfpeer or c.destination
 if o.owner~=expected or s.owned~=owned or o.vehicle.owned_local~=owned or o.busy then return false,'ownership_not_ready'end
 if c.sample.player_count~=2 or c.sample.local_count~=1 or s.player_count~=2 or s.peer_count~=2 or o.peer_count~=2 then return false,'two_players_required'end
 if not c.destination or c.destination==o.selfpeer or not o.members[c.destination]or not o.members[o.coordinator]or(o.coordinator~=o.selfpeer and o.coordinator~=c.destination)then return false,'two_peer_host_identity_required'end
 if not c.avatar or not c.avatar.is_local or not c.avatar.owned_local or not o.avatars[s.avatar]or o.avatars[s.avatar].owner~=o.selfpeer then return false,'avatar_owner_unconfirmed'end
 if s.node~=source or source<0 or source>4 or source%1~=0 or(s.active and(not confirmation or s.profile.roles[source+1]~=3))or not c.avatar.vehicle_input or not seated(c.avatar,o.vehicle,source,s.profile.roles[source+1])then return false,'sit_still_in_expected_seat'end
 local borrowed=ticket and not ticket.local_authority or not ticket and not owned
 local retracting=false
 if borrowed then
  if source==0 or target==0 or ticket and(ticket.source==0 or ticket.target==0)then return false,'borrowed_driver_target_not_enabled'end
  if not c.driver or c.driver.is_local or not seated(c.driver,o.vehicle,0,1)or not o.avatars[c.driver.id]or o.avatars[c.driver.id].owner~=c.destination then return false,'friend_must_remain_driver'end
  if ticket and(c.driver.id~=ticket.driver_id or c.driver.unit~=ticket.driver_unit)then return false,'remote_driver_changed'end
 else
  local remote_count,remote=0,nil
  for _,a in ipairs(c.sample.avatars)do if not a.is_local then
   remote_count=remote_count+1;remote=a
  end end
  if remote_count~=1 then return false,'one_remote_avatar_required'end
  local aboard=remote.seat and remote.seat.collection==o.vehicle.id or false
  local remote_node
  if aboard then
   remote_node=remote.seat.current
   -- Never mutate while the friend is transitioning. Recognize only the
   -- captured same-seat retraction as a bounded, retryable input refusal.
   local rs=remote.seat
   local same_seat_retraction=remote_node~=4 and rs.collection==o.vehicle.id and rs.reserved==remote_node and rs.role==3
     and rs.target==remote_node and rs.action==20 and rs.transitioning==1 and rs.queued_exit==0
   local remote_role=remote_node==4 and 2 or 3
   if type(remote_node)~='number'or remote_node<1 or remote_node>4 or remote_node%1~=0 or
      (not seated(remote,o.vehicle,remote_node,remote_role)and not same_seat_retraction)or remote_node==source or s.occupied[remote_node]~=true then
    return false,'friend_must_remain_seated_passenger_or_gunner'
   end
   -- Remote gunner must stay in its verified mounted seat. This extension
   -- never assigns/clears its role, weapon, rotation or chassis ownership.
   retracting=same_seat_retraction
   if not o.avatars[remote.id]or o.avatars[remote.id].owner~=c.destination then return false,'friend_occupant_owner_unconfirmed'end
  end
  if ticket and ticket.local_authority and ticket.remote_id and
     (remote.id~=ticket.remote_id or remote.unit~=ticket.remote_unit or aboard~=ticket.remote_aboard or
      aboard and remote_node~=ticket.remote_node)then return false,'friend_passenger_context_changed'end
  if source==0 then
   if not c.driver or not c.driver.is_local or c.driver.id~=s.avatar or c.driver.unit~=s.avatar_unit then return false,'local_driver_identity_changed'end
  elseif c.driver then return false,'driver_seat_must_remain_empty'end
 end
 local destination=target or(ticket and(source==ticket.source and ticket.target or ticket.source))
 if not destination or destination<0 or destination>4 or destination%1~=0 or destination==source then return false,'invalid_experiment_target'end
 if s.occupied[destination]~=false then return false,'target_occupied_or_reserved'end
 if ticket and(c.identity~=ticket.identity or s.identity~=ticket.avatar_binding or c.destination~=ticket.destination or o.coordinator~=ticket.coordinator)then return false,'operation_identity_changed'end
 if retracting then return false,'friend_passenger_retracting',true end
 return true
end
function M.new(api,game,p,reader,owner_reader,snapshot,transaction,sender,trace,emit,encode)
 local self={}
 function self:capture(ticket)
  local sample,why=reader:capture();if not sample or sample.state~='mission'then return nil,why or 'not_in_mission'end
  local o,reason=owner_reader:capture(sample,ticket and ticket.vehicle,true);if not o then return nil,reason end
  local a,driver,dest,n=nil,nil,nil,0
  for _,x in ipairs(sample.avatars)do
   if x.is_local then a=x end
   if seated(x,o.vehicle,0,1)then driver=x end
  end
  for peer in pairs(o.members)do if peer~=o.selfpeer then dest=peer;n=n+1 end end
  if n~=1 then dest=nil end
  local ok,s,err=pcall(snapshot.capture,api,game,p)
  if not ok then err=tostring(s);s=nil end
  if s and (not a or a.id~=s.avatar or a.unit~=s.avatar_unit or s.collection~=o.vehicle.id or s.collection_unit~=o.vehicle.network_unit or s.resource~=o.vehicle.resource)then s=nil;err='local_tracked_identity_disagrees'end
  local c={sample=sample,owner=o,native=s,native_reason=err,avatar=a,driver=driver,destination=dest,seat=s and s.node}
  -- Additional peers cancel switching but must not prevent return to the original owner.
  c.identity=o.context..'/'..o.vehicle.id..'/'..o.vehicle.unit..'/'..o.vehicle.network_unit..'/'..o.vehicle.resource..o.selfpeer
  local occupants={}
  for _,x in ipairs(sample.avatars)do if not x.is_local then
   occupants[#occupants+1]={id=x.id,unit=x.unit,collection=x.seat and x.seat.collection,node=x.seat and x.seat.current,role=x.seat and x.seat.role}
  end end
  c.summary=encode({seat=c.seat,ownership=owner_reader:summary(o),local_ready=s~=nil,remote_occupants=occupants})
  return c
 end
 function self:eligible(c,source,owned,ticket,target)return M.eligible(c,source,owned,ticket,target)end
 -- Confirm completed target identity/ownership while allowing a settled lean.
 -- New mutations still use eligible(), which requires the weapon lowered.
 function self:confirmed(c,t,owned)return M.eligible(c,t.target,owned,t,nil,true)end
 function self:ticket(c,target)
  local t={identity=c.identity,vehicle=c.owner.vehicle,selfpeer=c.owner.selfpeer,original=c.owner.owner,
   destination=c.destination,coordinator=c.owner.coordinator,local_authority=c.owner.owner==c.owner.selfpeer,
   source=c.seat,target=assert(target),avatar_binding=c.native.identity,driver_id=c.driver and c.driver.id,driver_unit=c.driver and c.driver.unit}
  if t.local_authority then for _,a in ipairs(c.sample.avatars)do if not a.is_local then
   t.remote_id=a.id;t.remote_unit=a.unit;t.remote_aboard=a.seat and a.seat.collection==c.owner.vehicle.id or false
   if t.remote_aboard then t.remote_node=a.seat.current end
  end end end
  return t
 end
 function self:context(c,t)
  return c.identity==t.identity and c.owner.selfpeer==t.selfpeer and c.owner.members[t.original]and c.owner.members[t.destination]
 end
 local function quiet()
  assert(api.input_allowed(),'focus_or_input_blocked')
  local down=api.control_down or api.down
  for _,k in ipairs({1,2,4,5,6,32,65,68,69,81,83,87})do assert(not down(k),'release_movement_fire_action_inputs')end
 end
 function self:request(c,t)
  assert(not t.local_authority and t.original==t.destination,'request_requires_borrowed_authority')
  assert(not api.experiment_allowed or api.experiment_allowed(),'experiment_logging_unavailable')
  assert(trace.active,'trace_inactive');trace:health();quiet()
  local fresh=assert(self:capture(t));local ok,why=M.eligible(fresh,t.source,false,t);assert(ok,why)
  owner_reader:send(fresh.owner,t.original,t.selfpeer,function()t.request_invoked=true end)
 end
 function self:execute(c,t)
  assert(not api.experiment_allowed or api.experiment_allowed(),'experiment_logging_unavailable')
  trace:health();quiet()
  local fresh=assert(self:capture(t));local ok,why=M.eligible(fresh,t.source,true,t);assert(ok,why)
  local perform=transaction:prepare(fresh.native,t.target)
  local send=sender:prepare(fresh.owner,t.destination,fresh.native,t.target)
  local final=assert(self:capture(t));ok,why=M.eligible(final,t.source,true,t);assert(ok,why)
  assert(final.owner.serial==fresh.owner.serial and snapshot.current(api,fresh.native),'state_changed_before_mutation')
  emit({event='integrated_preflight_passed',source=t.source,target=t.target,ownership=owner_reader:summary(final.owner)})
  t.mutation_started=true;perform()
  local after=assert(self:capture(t));ok,why=M.eligible(after,t.target,true,t);assert(ok,why)
  assert(snapshot.current(api,after.native),'state_changed_before_sync')
  send(emit);t.sync_returned=true
 end
 function self:return_owned(c,t)
  assert(not t.local_authority and t.original==t.destination,'no_borrowed_authority_to_return')
  assert(not t.return_invoked,'return_already_invoked')
  assert(trace.active,'trace_inactive');trace:health()
  local fresh=assert(self:capture(t));assert(self:context(fresh,t),'return_context_changed')
  local o=fresh.owner
  assert(o.owner==t.selfpeer and o.vehicle.owned_local and not o.busy,'return_owner_not_ready')
  -- Recovery may run after local exit/read failure; never require a local seat.
  -- Do not give the chassis away underneath a new/different driver.
  if fresh.driver then
   assert(not fresh.driver.is_local and fresh.driver.id==t.driver_id and fresh.driver.unit==t.driver_unit,'return_driver_changed')
   assert(o.avatars[fresh.driver.id]and o.avatars[fresh.driver.id].owner==t.original,'return_driver_owner_changed')
  end
  owner_reader:send(o,t.selfpeer,t.original,function()t.return_invoked=true end)
 end
 return self
end
return M
