-- Owner-side vacancy arbitration + own avatar notification, no chassis loan.
local M={}
local function seated(a,vehicle,node)
 local s=a and a.seat
 return s and s.collection==vehicle.id and s.current==node and s.reserved==node and s.role==(node==0 and 1 or 3)
  and s.target==-1 and s.action==-1 and s.transitioning==0 and s.queued_exit==0
end
function M.eligible(c,source,owned,ticket,target,granted)
 local s,o=c and c.native,c and c.owner
 if not s or not o then return false,'reservation_observation_unavailable'end
 if s.vehicle~='m102'or s.transition~=26 or source<1 or source>3 or source%1~=0 or target==nil or target<1 or target>3 or target%1~=0 or source==target then return false,'reservation_m102_passenger_scope'end
 if owned or s.owned or o.owner==o.selfpeer or o.vehicle.owned_local or o.busy or o.owner~=c.destination then return false,'reservation_remote_driver_authority_required'end
 if c.sample.player_count~=2 or c.sample.local_count~=1 or s.player_count~=2 or s.peer_count~=2 or o.peer_count~=2 then return false,'reservation_two_players_required'end
 if not o.members[o.selfpeer]or not o.members[o.owner]or not o.members[o.coordinator]then return false,'reservation_members_changed'end
 if not c.avatar or c.avatar.id~=s.avatar or c.avatar.unit~=s.avatar_unit or not c.avatar.is_local or not c.avatar.owned_local or not c.avatar.vehicle_input or
  not o.avatars[s.avatar]or o.avatars[s.avatar].owner~=o.selfpeer or not seated(c.avatar,o.vehicle,source)or s.node~=source or s.active then return false,'reservation_source_not_settled'end
 if not c.driver or c.driver.is_local or not seated(c.driver,o.vehicle,0)or not o.avatars[c.driver.id]or o.avatars[c.driver.id].owner~=o.owner then return false,'reservation_friend_must_remain_driver'end
 if s.profile.roles[source+1]~=3 or s.profile.roles[target+1]~=3 then return false,'reservation_roles_changed'end
 for _,a in ipairs(c.sample.avatars)do if not a.is_local and a.seat and a.seat.collection==o.vehicle.id then
  for _,field in ipairs({'current','target','reserved'})do if a.seat[field]==target then return false,'reservation_target_avatar_occupied'end end
 end end
 if not granted and s.occupied[target]~=false then return false,'reservation_target_occupied_or_reserved'end
 if ticket and(c.identity~=ticket.identity or s.identity~=ticket.avatar_binding or o.owner~=ticket.original or o.serial~=ticket.serial or
   c.driver.id~=ticket.driver_id or c.driver.unit~=ticket.driver_unit or c.avatar.network_unit~=ticket.avatar_net or o.vehicle.network_unit~=ticket.car_net)then return false,'reservation_transaction_identity_changed'end
 return true
end
function M.new(adapter,api,snapshot,trace,entrance,transaction,sender,emit,status)
 local self={count=0,phase='waiting',pending=false};local ticket,cooldown=nil,0
 local function event(name,e)e=e or{};e.event='reservation_'..name;emit(e)end
 local function phase(name)self.phase=name;status(name)end
 local function boundary(stage,c,t)if adapter.motion then adapter.motion:boundary(stage,c,t)end end
 local function stop(reason)phase('stopped');event('stopped',{reason=reason,gate_retained= ticket and ticket.cookie~=nil or false,full_exit_required=true})end
 local function healthy()assert(trace.active,'reservation_trace_inactive');trace:health();assert(api.input_allowed(),'reservation_input_blocked');assert(not api.experiment_allowed or api.experiment_allowed(),'reservation_log_unavailable')end
 local function quiet()
  healthy();local down=api.control_down or api.down
  for _,key in ipairs({1,2,4,5,6,32,65,68,69,81,83,87})do assert(not down(key),'reservation_movement_fire_action_held')end
 end
 local function assert_grant(t)
  trace:health();local ack=trace:gate_peek(t.cookie)
  assert(ack.status==2 and ack.guard_lost==0 and ack.peer_key==t.original and ack.car==t.car_net and ack.avatar==t.avatar_net and
   ack.source==t.source and ack.target==t.target and ack.chosen==t.target,'reservation_authenticated_grant_changed')
  local fresh=assert(adapter:capture(t));local source=fresh.seat
  assert(source==t.source or source==t.target,'reservation_own_seat_changed')
  local other=source==t.source and t.target or t.source
  local good,why=M.eligible(fresh,source,false,t,other,true);assert(good,why)
  assert(snapshot.current(api,fresh.native),'reservation_fresh_snapshot_changed');return true
 end
 function self:cancel(reason)
  if ticket and self.pending then ticket.cancel_reason=ticket.cancel_reason or reason;event('cancelled',{reason=reason})end
 end
 function self:close(reason)if self.pending then self:cancel(reason);stop(reason)end end
 function self:step(trigger,now,focused,expected)
  if self.phase=='stopped'then return false,'reservation_stopped'end
  local c,why=adapter:capture(ticket);self.observed=c;self.observed_at=now
  if not c then self.ready_at=nil;if self.pending then stop(why or 'reservation_capture_lost')end;if trigger~=nil then return false,why end;return end
  if not self.pending then
   self.ready_at=math.max(now,cooldown)
   if trigger==nil then return end
   if not focused or now<cooldown then return false,'reservation_focus_or_cooldown'end
   local good,reason=M.eligible(c,c.seat,c.owner.owner==c.owner.selfpeer,nil,trigger)
   if not good then return false,reason end
   if expected and (expected.identity~=c.identity or expected.source~=c.seat)then return false,'reservation_expected_context_changed'end
   quiet();assert(snapshot.current(api,c.native),'reservation_initial_snapshot_changed')
   local send,entry_id=entrance:prepare_request(c,trigger)
   -- Prepare every local avatar/notification dependency BEFORE any native
   -- request. Use a preflight object that can only check the unchanged context;
   -- it is never passed to the committing transaction or sender.
   assert(transaction:preflight(c.native,trigger));assert(sender:preflight(c.owner,c.destination,c.native,trigger))
   local fresh=assert(adapter:capture());good,reason=M.eligible(fresh,c.seat,false,nil,trigger);assert(good,reason)
   assert(fresh.identity==c.identity and fresh.native.identity==c.native.identity and fresh.owner.serial==c.owner.serial and snapshot.current(api,c.native),'reservation_request_context_changed')
   ticket={identity=c.identity,avatar_binding=c.native.identity,source=c.seat,target=trigger,serial=c.owner.serial,
    original=c.owner.owner,selfpeer=c.owner.selfpeer,destination=c.destination,driver_id=c.driver.id,driver_unit=c.driver.unit,
    car_net=c.owner.vehicle.network_unit,avatar_net=c.avatar.network_unit,vehicle=c.owner.vehicle,requested_at=now,entrance=entry_id}
   ticket.cookie=trace:gate_arm(ticket.original,ticket.car_net,ticket.avatar_net,ticket.source,ticket.target)
   self.pending=true;self.count=self.count+1;phase('awaiting_owner_reservation')
   event('request',{operation=self.count,source=ticket.source,target=ticket.target,entrance=entry_id,cookie=ticket.cookie,chassis_authority_requested=false})
   boundary('before_owner_reservation',fresh,ticket)
   -- Logging or a motion read can fail after arming the exact reply gate.
   -- Recheck before sending; the error handler keeps that gate until exit.
   quiet();assert(snapshot.current(api,fresh.native),'reservation_request_snapshot_changed')
   local final=assert(adapter:capture(ticket));good,reason=M.eligible(final,ticket.source,false,ticket,ticket.target);assert(good,reason)
   send();return true
  end
  local t=ticket;local ack=trace:gate_peek(t.cookie)
  if ack.guard_lost~=0 then stop('reservation_session_guard_lost');return end
  if c.identity~=t.identity or c.owner.owner~=t.original or c.owner.serial~=t.serial or c.owner.vehicle.owned_local or c.native and c.native.owned then stop('reservation_chassis_or_session_changed');return end
  if ack.status==1 then
   if now-t.requested_at>5 and not t.cancel_reason then self:cancel('owner_reply_timeout; late_reply_monitored')end
   return
  end
  if ack.status==3 then trace:gate_finish(t.cookie);self.pending=false;cooldown=now+.35;ticket=nil;phase('waiting');event('owner_denied');return end
  if ack.status~=2 then stop('reservation_conflicting_owner_reply');return end
  if not t.accepted_logged then t.accepted_logged=true;event('owner_accepted',{cookie=t.cookie,target=t.target,chosen=ack.chosen,reply_tick=ack.tick});boundary('owner_reservation_received',c,t)end
  if ack.chosen~=t.target or t.cancel_reason then
   -- No local seat change on cancellation or owner-selected fallback. This
   -- first prototype retains the gate and stops for exact-protocol review;
   -- it never frees an alternative or an unexpected driving reservation.
   if ack.chosen<1 or ack.chosen>4 or ack.chosen==t.source then stop('reservation_alternative_unsafe_to_release');return end
   stop('reservation_fallback_requires_read_only_review; no_arbitrary_release');return
  end
  local grant={source=t.source,target=t.target,check=function()return assert_grant(t)end}
  if not t.executed then
   -- The native property may be delivered after the reliable ACK. Wait for
   -- its actual mask before moving own avatar into target; otherwise the
   -- snapshot reader correctly refuses an unreserved current seat.
   if require('bit').band(c.native.mask,2^t.target)~=0 then
    if not t.mask_wait_logged then t.mask_wait_logged=true;event('waiting_owner_reservation_mask',{target=t.target})end
    if now-t.requested_at>5 then stop('reservation_grant_mask_not_received')end
    return
   end
   if not focused then self:cancel('focus_lost_before_commit');stop('reservation_cancelled_after_grant');return end
   quiet();assert_grant(t)
   local perform=transaction:prepare(c.native,t.target,grant)
   local notify=sender:prepare(c.owner,c.destination,c.native,t.target,grant)
   local release=entrance:prepare_release(c,t.source)
   quiet();assert_grant(t)
   t.executed=true;phase('committing_own_avatar');boundary('before_own_avatar_change',c,t)
   perform();assert_grant(t);notify(emit);t.sync_returned=true
   local after=assert(adapter:capture(t));assert(after.native and after.seat==t.target and not after.native.active and snapshot.current(api,after.native),'reservation_target_not_settled')
   assert_grant(t);boundary('before_original_slot_release',after,t);release();t.released_source=true;t.release_at=now
   phase('awaiting_owner_mask');return
  end
  assert_grant(t)
  if c.seat~=t.target then stop('reservation_target_changed_after_commit');return end
  if c.native.occupied[t.source]==false and c.native.occupied[t.target]==true then
   boundary('owner_mask_confirmed',c,t);trace:gate_finish(t.cookie);self.pending=false;ticket=nil;cooldown=now+.35;phase('waiting')
   event('operation_complete',{operation=self.count,source=t.source,target=t.target,authority_serial=c.owner.serial,chassis_authority_unchanged=true,old_slot_released=true});return
  end
  if now-t.release_at>5 then stop('reservation_original_slot_release_not_confirmed')end
 end
 return self
end
return M
