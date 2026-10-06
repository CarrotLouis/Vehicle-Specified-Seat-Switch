-- Owner-side reservation / local-owner switch. No temporary chassis loan.
return function(scope,membership)
local M={};assert(scope and membership)
local function seated(a,v,node,role)
 local s=a and a.seat
 return s and s.collection==v.id and s.current==node and s.reserved==node and s.role==role
  and s.target==-1 and s.action==-1 and s.transitioning==0 and s.queued_exit==0
end
local function others(c)
 return assert(membership.capture(c)).occupants
end
function M.eligible(c,source,owned,t,target,granted)
 local s,o=c and c.native,c and c.owner
 if not s or not o then return false,'reservation_observation_unavailable'end
 local d=scope.layout(s)
 if not d or source~=s.node or target==nil or not scope.direction(s,target)then return false,'reservation_fleet_direction'end
 local members,member_error=membership.capture(c);if not members then return false,member_error end
 if not o.members[o.selfpeer]or not o.members[o.owner]or not o.members[o.coordinator]or not c.destination or not o.members[c.destination]or c.destination==o.selfpeer then return false,'reservation_members_changed'end
 if o.busy or s.owned~=(o.owner==o.selfpeer)or o.vehicle.owned_local~=s.owned or owned~=s.owned then return false,'reservation_authority_not_settled'end
 if not c.avatar or c.avatar.id~=s.avatar or c.avatar.unit~=s.avatar_unit or not c.avatar.is_local or not c.avatar.owned_local or not c.avatar.vehicle_input
  or not o.avatars[s.avatar]or o.avatars[s.avatar].owner~=o.selfpeer or not seated(c.avatar,o.vehicle,source,d.roles[source+1])or s.active then return false,'reservation_source_not_settled'end
 if source==0 and(not owned or not c.driver or c.driver.id~=s.avatar or not c.driver.is_local)then return false,'reservation_actual_local_driver_required'end
 if c.driver then
  local driver_owner=o.avatars[c.driver.id]
  if not seated(c.driver,o.vehicle,0,1)or not driver_owner or driver_owner.owner~=o.owner then return false,'reservation_driver_owner_changed'end
 end
 for _,a in ipairs(c.sample.avatars or{})do if not a.is_local and a.seat and a.seat.collection==o.vehicle.id then
  for _,field in ipairs({'current','target','reserved'})do if a.seat[field]==target then return false,'reservation_target_avatar_occupied'end end
 end end
 if not granted and s.occupied[target]~=false then return false,'reservation_target_occupied_or_reserved'end
 if t then
  if members.signature~=t.membership then return false,'reservation_membership_changed'end
  if c.identity~=t.identity or s.identity~=t.avatar_binding or o.vehicle.network_unit~=t.car_net or c.avatar.network_unit~=t.avatar_net
   or c.destination~=t.destination or o.coordinator~=t.coordinator or others(c)~=t.others then return false,'reservation_transaction_identity_changed'end
  if t.mode=='driver_acquire' then
   if o.owner==t.original then
    if o.serial~=t.serial or owned then return false,'reservation_original_driver_owner_changed'end
   elseif o.owner==t.selfpeer then
    if not owned or t.acquired_serial and o.serial~=t.acquired_serial then return false,'reservation_acquired_driver_owner_changed'end
   else return false,'reservation_unexpected_driver_owner'end
  elseif o.owner~=t.original or not t.allow_local_serial and o.serial~=t.serial then return false,'reservation_chassis_or_session_changed'end
  if t.driver_id and(c.driver==nil or c.driver.id~=t.driver_id or c.driver.unit~=t.driver_unit)then return false,'reservation_remote_driver_changed'end
 end
 return true
end
function M.new(adapter,api,snapshot,trace,entrance,transaction,sender,emit,status)
 local self={count=0,phase='waiting',pending=false};local ticket,cooldown=nil,0
 local function event(name,e)e=e or{};e.event='reservation_'..name;emit(e)end
 local function phase(name)self.phase=name;status(name)end
 local function boundary(stage,c,t)if adapter.motion then adapter.motion:boundary(stage,c,t)end end
 local function stop(reason)phase('stopped');event('stopped',{reason=reason,gate_retained=ticket and ticket.cookie~=nil or false,full_exit_required=true})end
 local function quiet(s)
  assert(trace.active,'reservation_trace_inactive');trace:health();assert(api.input_allowed(),'reservation_input_blocked')
  assert(not api.experiment_allowed or api.experiment_allowed(),'reservation_log_unavailable')
  local d=s and scope.layout(s);local steer=d and d.tank and s.node==0 and s.owned
  local down=api.control_down or api.down
  for _,key in ipairs({1,2,4,5,6,32,65,68,69,81,83,87})do assert(steer and(key==65 or key==68)or not down(key),'reservation_movement_fire_action_held')end
 end
 local function check(t)
  trace:health()
  local ack=t.cookie and trace:gate_peek(t.cookie)
  if ack then assert(ack.status==2 and ack.guard_lost==0 and ack.peer_key==t.original and ack.car==t.car_net and ack.avatar==t.avatar_net
   and ack.source==t.source and ack.target==t.target and ack.chosen==t.target,'reservation_authenticated_grant_changed')end
  local fresh=assert(adapter:capture(t));local source=fresh.seat
  assert(source==t.source or source==t.target,'reservation_own_seat_changed')
  local other=source==t.source and t.target or t.source
  local good,why=M.eligible(fresh,source,fresh.native and fresh.native.owned,t,other,true);assert(good,why)
  if t.mounted then assert(adapter.mounted:ready(fresh,t.mounted),'reservation_mounted_grant_changed')end
  assert(snapshot.current(api,fresh.native),'reservation_fresh_snapshot_changed');return fresh
 end
 function self:cancel(reason)if ticket and self.pending then ticket.cancel_reason=ticket.cancel_reason or reason;event('cancelled',{reason=reason})end end
 function self:close(reason)if self.pending then self:cancel(reason);stop(reason)end end
 function self:step(trigger,now,focused,expected)
  if self.phase=='stopped'then return false,'reservation_stopped'end
  local c,why=adapter:capture(ticket);self.observed=c;self.observed_at=now
  if not c then self.ready_at=nil;if self.pending then stop(why or 'reservation_capture_lost')end;if trigger~=nil then return false,why end;return end
  if not self.pending then
   self.ready_at=math.max(now,cooldown)
   if trigger==nil then return end
   if not focused or now<cooldown then return false,'reservation_focus_or_cooldown'end
   local good,reason=M.eligible(c,c.seat,c.native and c.native.owned,nil,trigger);if not good then return false,reason end
   if expected and(expected.identity~=c.identity or expected.source~=c.seat)then return false,'reservation_expected_context_changed'end
   quiet(c.native);assert(snapshot.current(api,c.native),'reservation_initial_snapshot_changed')
   local own=c.owner.owner==c.owner.selfpeer
   local mode=own and 'local_owner'or trigger==0 and 'driver_acquire'or 'remote_reservation'
   local perform,notify,request,entry_id,mounted
   if own then
    perform=assert(adapter.owned_transaction,'reservation_owned_transaction_missing'):prepare(c.native,trigger)
    notify=sender:prepare_all(c.owner,assert(membership.capture(c)).destinations,c.native,trigger)
   else
    request,entry_id=entrance:prepare_request(c,trigger)
    assert(transaction:preflight(c.native,trigger));assert(sender:preflight_all(c.owner,assert(membership.capture(c)).destinations,c.native,trigger))
    mounted=assert(adapter.mounted):prepare(c,trigger)
   end
   local fresh=assert(adapter:capture());good,reason=M.eligible(fresh,c.seat,own,nil,trigger);assert(good,reason)
   assert(fresh.identity==c.identity and fresh.native.identity==c.native.identity and fresh.owner.serial==c.owner.serial and snapshot.current(api,c.native),'reservation_request_context_changed')
   ticket={identity=c.identity,avatar_binding=c.native.identity,source=c.seat,target=trigger,serial=c.owner.serial,original=c.owner.owner,
    selfpeer=c.owner.selfpeer,destination=c.destination,coordinator=c.owner.coordinator,others=others(c),mode=mode,
    driver_id=not own and trigger~=0 and c.driver and c.driver.id,driver_unit=c.driver and c.driver.unit,
    car_net=c.owner.vehicle.network_unit,avatar_net=c.avatar.network_unit,avatar_id=c.avatar.id,avatar_unit=c.avatar.unit,
    vehicle=c.owner.vehicle,requested_at=now,entrance=entry_id,mounted=mounted,
    membership=assert(membership.capture(c)).signature,peer_count=c.sample.player_count}
   self.pending=true;self.count=self.count+1
   if own then
    phase('committing_local_owner');event('local_owner_request',{operation=self.count,source=ticket.source,target=ticket.target,chassis_loan=false})
    boundary('before_local_owner_change',fresh,ticket);quiet(fresh.native);check(ticket)
    perform();ticket.allow_local_serial=true
    local after=check(ticket);ticket.serial=after.owner.serial;ticket.allow_local_serial=false
    notify(emit);after=check(ticket)
    assert(after.seat==ticket.target and after.native.occupied[ticket.source]==false and after.native.occupied[ticket.target]==true,'reservation_owned_mask_not_settled')
    boundary('after_local_owner_change',after,ticket)
    event('local_owner_complete',{operation=self.count,source=ticket.source,target=ticket.target,authority_serial=after.owner.serial,remote_success_not_confirmed=true})
    self.pending=false;ticket=nil;cooldown=now+.35;phase('waiting');return true
   end
   ticket.cookie=trace:gate_arm(ticket.original,ticket.car_net,ticket.avatar_net,ticket.source,ticket.target)
   phase('awaiting_owner_reservation');event('request',{operation=self.count,source=ticket.source,target=ticket.target,entrance=entry_id,cookie=ticket.cookie,
    driver_acquisition=mode=='driver_acquire',chassis_authority_requested=mode=='driver_acquire',chassis_loan=false})
   boundary('before_owner_reservation',fresh,ticket);quiet(fresh.native);assert(snapshot.current(api,fresh.native),'reservation_request_snapshot_changed')
   local final=assert(adapter:capture(ticket));good,reason=M.eligible(final,ticket.source,false,ticket,ticket.target);assert(good,reason)
   request();return true
  end
  local t=ticket;local members=membership.capture(c)
  if not members or members.signature~=t.membership then stop('reservation_membership_changed');return end
  local ack=trace:gate_peek(t.cookie)
  if ack.guard_lost~=0 then stop('reservation_session_guard_lost');return end
  if c.identity~=t.identity then stop('reservation_context_changed');return end
  if t.mode~='driver_acquire'and(c.owner.owner~=t.original or c.owner.serial~=t.serial or c.owner.vehicle.owned_local)then stop('reservation_chassis_or_session_changed');return end
  if t.mode=='driver_acquire'then
   if c.owner.owner~=t.original and c.owner.owner~=t.selfpeer then stop('reservation_unexpected_driver_owner');return end
   if c.owner.owner==t.original and c.owner.serial~=t.serial then stop('reservation_original_driver_owner_changed');return end
   if c.owner.owner==t.selfpeer then
    t.acquired_serial=t.acquired_serial or c.owner.serial
    if c.owner.serial~=t.acquired_serial then stop('reservation_acquired_driver_serial_changed');return end
   end
  end
  if ack.status==1 then if now-t.requested_at>5 and not t.cancel_reason then self:cancel('owner_reply_timeout; late_reply_monitored')end;return end
  if ack.status==3 then trace:gate_finish(t.cookie);self.pending=false;cooldown=now+.35;ticket=nil;phase('waiting');event('owner_denied');return end
  if ack.status~=2 then stop('reservation_conflicting_owner_reply');return end
  if not t.accepted_logged then t.accepted_logged=true;event('owner_accepted',{cookie=t.cookie,target=t.target,chosen=ack.chosen,reply_tick=ack.tick})end
  if ack.chosen~=t.target or t.cancel_reason then stop('reservation_fallback_requires_read_only_review; no_arbitrary_release');return end
  if not c.native then
   if t.mode=='driver_acquire'and c.avatar and c.avatar.id==t.avatar_id and c.avatar.unit==t.avatar_unit and c.avatar.network_unit==t.avatar_net
    and c.avatar.seat and c.avatar.seat.collection==t.vehicle.id and c.avatar.seat.current==t.source and others(c)==t.others then
    if now-t.requested_at>5 then stop('reservation_driver_snapshot_timeout')end;return
   end
   stop('reservation_native_snapshot_lost');return
  end
  if not t.executed then
   if require('bit').band(c.native.mask,2^t.target)~=0 then
    if not t.mask_wait_logged then t.mask_wait_logged=true;event('waiting_owner_reservation_mask',{target=t.target})end
    if now-t.requested_at>5 then stop('reservation_grant_mask_not_received')end;return
   end
   if t.mode=='driver_acquire'and(c.owner.owner~=t.selfpeer or not c.native.owned or not c.owner.vehicle.owned_local or c.owner.busy)then
    if not t.driver_wait_logged then t.driver_wait_logged=true;event('waiting_driver_authority',{target=t.target})end
    if now-t.requested_at>5 then stop('reservation_driver_authority_timeout')end;return
   end
   if t.mounted then local ready,reason=adapter.mounted:ready(c,t.mounted)
    if not ready then if not t.mounted_wait_logged then t.mounted_wait_logged=true;event('waiting_mounted_authority',{target=t.target,reason=reason})end
     if now-t.requested_at>5 then stop('reservation_mounted_authority_timeout')end;return end
   end
   if not focused then self:cancel('focus_lost_before_commit');stop('reservation_cancelled_after_grant');return end
   quiet(c.native);check(t)
   local grant={source=t.source,target=t.target,check=function()return check(t)~=nil end}
   local perform=transaction:prepare(c.native,t.target,grant)
   local notify=sender:prepare_all(c.owner,assert(membership.capture(c)).destinations,c.native,t.target,grant)
   local release
   if t.mode=='driver_acquire'then release=assert(adapter.release_acquired):prepare(c.native,t.source,grant)
   else release=entrance:prepare_release(c,t.source)end
   quiet(c.native);check(t);t.executed=true;phase('committing_own_avatar');boundary('before_own_avatar_change',c,t)
   perform();check(t);notify(emit);t.sync_returned=true
   local after=check(t);assert(after.seat==t.target,'reservation_target_not_settled')
   boundary('before_original_slot_release',after,t);release();t.release_at=now;phase('awaiting_owner_mask');return
  end
  local after=check(t)
  if after.seat~=t.target then stop('reservation_target_changed_after_commit');return end
  if after.native.occupied[t.source]==false and after.native.occupied[t.target]==true then
   boundary('owner_mask_confirmed',after,t);trace:gate_finish(t.cookie);self.pending=false;ticket=nil;cooldown=now+.35;phase('waiting')
   event('operation_complete',{operation=self.count,source=t.source,target=t.target,authority_serial=after.owner.serial,
    chassis_authority_unchanged=t.mode~='driver_acquire',driver_acquired=t.mode=='driver_acquire',old_slot_released=true});return
  end
  if now-t.release_at>5 then stop('reservation_original_slot_release_not_confirmed')end
 end
 return self
end
return M
end
