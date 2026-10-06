-- Experimental isolation: execute the accepted chassis loan without changing
-- any seat, role, weapon, pose, driver command, transform or physics state.
-- Native ownership handling itself may affect motion; that is the question.
return function(adapter,api,snapshot,trace,emit)
 local eligible,ticket,request=adapter.eligible,adapter.ticket,adapter.request
 local function allowed(c,source,owned,t,target)
  target=target or t and t.target
  if not c or not c.native or not c.sample or c.sample.player_count~=2 or
     c.native.vehicle~='m102' or source~=1 or target~=4 or not c.driver or c.driver.is_local then
   return false,'loan_only_requires_two_players_m102_friend_driver_front_to_gunner_key'
  end
  if owned and not t or t and (not t.loan_only or t.local_authority or t.fleet or
     t.driver_acquire or t.source~=1 or t.target~=4)then
   return false,'loan_only_requires_original_remote_driver'
  end
  return eligible(adapter,c,source,owned,t,target)
 end
 function adapter:eligible(c,source,owned,t,target)return allowed(c,source,owned,t,target)end
 function adapter:ticket(c,target)
  local ok,why=allowed(c,c.seat,c.owner.owner==c.owner.selfpeer,nil,target);assert(ok,why)
  local t=ticket(self,c,target)
  assert(not t.local_authority and not t.fleet and not t.driver_acquire,'loan_only_ticket_scope')
  t.loan_only=true
  return t
 end
 function adapter:request(c,t)
  local ok,why=allowed(c,t.source,false,t,t.target);assert(ok,why)
  return request(self,c,t)
 end
 function adapter:execute(c,t)
  assert(t.loan_only and not t.loan_only_read_started,'loan_only_already_checked')
  t.loan_only_read_started=true
  assert(not api.experiment_allowed or api.experiment_allowed(),'experiment_logging_unavailable')
  assert(trace.active,'trace_inactive');trace:health()
  assert(api.input_allowed(),'focus_or_input_blocked')
  local down=api.control_down or api.down
  for _,k in ipairs({1,2,4,5,6,32,65,68,69,81,83,87})do
   if down(k)then
    t.control_abort=true
    emit({event='integrated_control_abort',source=t.source,target=t.target,held_keys={k},mutation_started=false})
    error('release_movement_fire_action_inputs',0)
   end
  end
  local fresh=assert(self:capture(t));local ok,why=allowed(fresh,t.source,true,t,t.target);assert(ok,why)
  assert(snapshot.current(api,fresh.native),'loan_only_snapshot_changed')
  if self.motion then pcall(self.motion.boundary,self.motion,'ownership_loan_only_check',fresh,t)end
  -- No transaction preparation or native seat/weapon/pose/physics call, and
  -- no seat notifications. The existing probe returns the genuine loan next.
  t.loan_only_complete=true
  emit({event='ownership_loan_only_verified',seat=fresh.seat,requested_target=t.target,
   actual_owner_is_installer=true,seat_unchanged=true,seat_mutation=false,
   seat_notifications_sent=0,weapon_actions=0,pose_actions=0,physics_actions=0})
 end
 function adapter:confirmed(c,t,owned)
  return allowed(c,t.source,owned,t,t.target)
 end
 return adapter
end
