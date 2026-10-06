-- One pending transfer at a time; late grants are returned without switching.
local M={}
function M.new(adapter,emit,status,route,dynamic)
 route=route or {1,4,1}
 assert(#route>=3 and #route<=7 and (route[1]==0 or route[1]==1),'invalid_experiment_route')
 for i=1,#route-1 do local a,b=route[i],route[i+1];assert(a>=0 and a<=4 and a%1==0 and b>=0 and b<=4 and b%1==0 and a~=b and(a==4 or b==4 or a==0 or b==0),'invalid_experiment_pair')end
 local settle=dynamic and .2 or 3
 local self={count=0,phase='waiting',pending=false}
 local ticket,requested,return_at,stable_since,stable_key,last_reason,return_stable,last_return_try,last_summary,cooldown= nil,nil,nil,nil,nil,nil,nil,-math.huge,nil,0
 local function event(name,data)data=data or {};data.event='integrated_'..name;emit(data)end
 local function phase(name)self.phase=name;status('integrated_'..name)end
 local function note(reason)
  if reason~=last_reason then last_reason=reason;event('waiting',{reason=reason});status('integrated_waiting '..reason)end
 end
 local function stop(reason)
  event('stopped',{reason=reason,ownership_return_confirmed=ticket and ticket.return_confirmed or false});self.pending=false;phase('stopped')
 end
 local function executed(t)
  return t.loan_only and t.loan_only_complete or not t.loan_only and t.sync_returned
 end
 local function complete(now)
  self.pending=false
  event(ticket.loan_only and 'loan_operation_complete'or'operation_complete',{number=self.count,seat=ticket.loan_only and ticket.source or ticket.target,requested_target=ticket.target,seat_mutation=not ticket.loan_only,seat_notifications_sent=ticket.loan_only and 0 or nil,authority_path=ticket.local_authority and 'already_local'or ticket.driver_acquire and'acquired_retained'or'borrowed_returned',remote_visual_confirmation_required=true})
  cooldown=now+(dynamic and .35 or 10);stable_key=nil;stable_since=nil;last_reason=nil
  if not dynamic and self.count==#route-1 then phase('finished')else phase('waiting_second_trigger')end
 end
 local function confirmation(c,owned,now)
  local good,reason
  if adapter.confirmed then good,reason=adapter:confirmed(c,ticket,owned)
  else good,reason=adapter:eligible(c,ticket.target,owned,ticket)end
  if good then return true end
  local transient=reason=='transition_in_progress'or reason=='transition_pending'
  ticket.confirm_started=ticket.confirm_started or now
  if transient and now-ticket.confirm_started<=5 then
   if ticket.local_authority then return_stable=nil end
   if ticket.confirm_reason~=reason then ticket.confirm_reason=reason;event('waiting_target_pose',{reason=reason,target=ticket.target})end
   return nil,reason
  end
  return false,reason
 end
 local function recover_control_abort(c,owned,now,reason)
  if not dynamic or not ticket.control_abort or ticket.mutation_started or executed(ticket)
   or type(adapter.resume_after_control_abort)~='function'then return false end
  local ok,ready=pcall(adapter.resume_after_control_abort,adapter,c,ticket,owned)
  if not ok or not ready then return false end
  self.pending=false;self.ready_at=nil;stable_key=nil;stable_since=nil;return_stable=nil;last_reason=nil
  cooldown=now+.35;phase('waiting_second_trigger')
  event('input_abort_recovered',{source=ticket.source,target=ticket.target,reason=reason,
   local_authority=owned,ownership_return_confirmed=ticket.return_confirmed or false,fresh_press_required=true})
  return true
 end
 function self:cancel(reason)
  if ticket and self.pending and not ticket.cancel_reason then ticket.cancel_reason=reason;event('cancelled',{reason=reason,mutation_started=ticket.mutation_started or false})end
 end
 function self:step(trigger,now,focused,expected)
  if self.phase=='stopped'or self.phase=='finished'then return false,'experiment_not_running'end
  local ok,c,why=pcall(adapter.capture,adapter,self.pending and ticket or nil)
  if not ok then why=tostring(c);c=nil end
  self.observed=c;self.observed_at=now
  if not c then
   stable_since=nil;stable_key=nil;self.ready_at=nil;note(why or 'observation_unavailable')
   if self.pending and now-requested>5 then self:cancel('observation_timeout; monitoring_late_grant_without_switch')end
   if trigger~=nil then return false,why or 'observation_unavailable' end
   return
  end
  if c.summary~=last_summary then last_summary=c.summary;event('state',{detail=c.summary})end
  if self.pending then
   if not adapter:context(c,ticket)then stop('session_peer_or_vehicle_changed; return_not_confirmed');return end
   local o=c.owner
   if ticket.local_authority then
    -- This operation never borrowed authority. Never enter grant/return recovery.
    if ticket.cancel_reason then stop('local_operation_cancelled '..ticket.cancel_reason);return end
    if o.owner~=ticket.selfpeer or not o.vehicle.owned_local or o.busy then stop('local_authority_changed');return end
    if not ticket.switch_attempted then
     local good,reason=adapter:eligible(c,ticket.source,true,ticket)
     if not good or not focused then stop(not focused and 'focus_or_input_blocked'or reason);return end
     ticket.switch_attempted=true;event('switch_attempt',{source=ticket.source,target=ticket.target,authority_path='already_local'})
     local done,err=pcall(adapter.execute,adapter,c,ticket)
     if not done then
      if not recover_control_abort(c,true,now,tostring(err))then stop('local_switch_failed '..tostring(err))end
      return
     end
     phase('awaiting_local_confirmation');return
    end
    local good,reason=confirmation(c,true,now)
    if good==nil then return end
    if not good or not executed(ticket) then stop('local_seat_unconfirmed '..tostring(reason));return end
    return_stable=return_stable or now
    if now-return_stable<0.5 then return end
    event('local_authority_preserved',{source=ticket.source,target=ticket.target})
    complete(now);return
   end
   if not ticket.acquired then
    if o.owner==ticket.selfpeer and o.vehicle.owned_local and not o.busy then
     ticket.acquired=true;event('acquired',{source=ticket.source,target=ticket.target})
     if now-requested>5 then self:cancel('late_grant')end
     local allowed,reason=adapter:eligible(c,ticket.source,true,ticket)
     if not allowed then self:cancel(reason)end
     if not focused then self:cancel('focus_or_input_blocked')end
     if not ticket.cancel_reason then
      -- Consumed before invocation; never rerun a partially completed mutation.
      ticket.switch_attempted=true;event(ticket.loan_only and 'loan_check_attempt'or'switch_attempt',{source=ticket.source,target=ticket.target})
      local done,err=pcall(adapter.execute,adapter,c,ticket)
      if not done then self:cancel('switch_failed '..tostring(err))end
     end
     phase(ticket.driver_acquire and executed(ticket) and not ticket.cancel_reason and 'awaiting_driver_confirmation'or'awaiting_return')
     -- Do not use the pre-mutation ownership snapshot for returning authority.
     return
    end
    if o.owner~=ticket.original and o.owner~=ticket.selfpeer then stop('unexpected_owner_before_grant');return end
    if now-requested>5 then self:cancel('grant_timeout; keep_monitoring_late_grant');phase('late_grant_watch')end
    return
   end
   if ticket.driver_acquire and executed(ticket) and not ticket.cancel_reason then
    if o.owner~=ticket.selfpeer or not o.vehicle.owned_local or o.busy then stop('driver_authority_lost');return end
    local good,reason=confirmation(c,true,now)
    if good==nil then return end
    if not good then self:cancel('driver_seat_unconfirmed '..tostring(reason));return_stable=nil;return end
    return_stable=return_stable or now
    if now-return_stable<0.5 then return end
    event('driver_authority_retained',{source=ticket.source,target=ticket.target})
    complete(now);return
   end
   if o.owner==ticket.original and not o.vehicle.owned_local and not o.busy then
    return_stable=return_stable or now
    if now-return_stable<0.5 then return end
    if not ticket.return_confirmed then
     ticket.return_confirmed=true
     event('ownership_return_confirmed',{cancelled=ticket.cancel_reason~=nil,return_invoked=ticket.return_invoked or false})
    end
    if ticket.cancel_reason then
     event('aborted_and_returned',{reason=ticket.cancel_reason,mutation_started=ticket.mutation_started or false})
     if not recover_control_abort(c,false,now,ticket.cancel_reason)then self.pending=false;phase('stopped')end
     return
    end
    local good,reason=confirmation(c,false,now)
    if good==nil then return end
    if not good or not executed(ticket) then stop('returned_but_seat_unconfirmed '..tostring(reason));return end
    complete(now)
    return
   end
   return_stable=nil
   if o.owner~=ticket.selfpeer and o.owner~=ticket.original then stop('unexpected_owner_after_grant');return end
   if ticket.return_invoked then
    if return_at and now-return_at>5 then note('return_not_confirmed; no_resend; keep_monitoring')end
    return
   end
   if o.busy then note('waiting_busy_clear_before_return');return end
   if now-last_return_try<0.1 then return end;last_return_try=now
   local sent,err=pcall(adapter.return_owned,adapter,c,ticket)
   if ticket.return_invoked then return_at=now;event('return_invoked',{call_returned=sent})end
   if not sent then note('return_preflight_or_call_failed '..tostring(err))end
   return
  end
  local source,target
  if dynamic then
   source=c.seat;target=type(trigger)=='number'and trigger or nil
   local key=c.identity..'/'..tostring(source)..'/'..tostring(c.owner.owner)
   if not focused or not c.native or c.native.active or c.owner.busy then
    stable_since=nil;stable_key=nil;self.ready_at=nil
    if target~=nil then return false,not focused and 'input_blocked'or 'state_not_ready'end
    return
   end
   if stable_key~=key then stable_key=key;stable_since=now end
   self.ready_at=math.max(stable_since+settle,cooldown)
   if target==nil then return end
   if now-stable_since<settle or now<cooldown then event('trigger_rejected',{reason='settle_or_cooldown',target=target});return false,'settle_or_cooldown'end
   if target<0 or target>4 or target%1~=0 or source==target then event('trigger_rejected',{reason='invalid_target',target=target});return false,'invalid_target'end
   local locally_owned=c.owner.owner==c.owner.selfpeer
   if expected and(expected.source~=source or expected.target~=target or expected.local_authority~=locally_owned or not adapter:context(c,expected))then
    event('trigger_rejected',{reason='deferred_context_changed',target=target});return false,'deferred_context_changed'
   end
   local ready,reason,retryable=adapter:eligible(c,source,locally_owned,expected,target)
   if not ready then
    event('trigger_rejected',{reason=reason,target=target,retryable=retryable or false})
    return false,reason,retryable,retryable and(expected or adapter:ticket(c,target))or nil
   end
  else
  source,target=route[self.count+1],route[self.count+2]
  if self.count>0 and ticket and c.identity~=ticket.identity then stop('session_or_vehicle_changed_between_operations');return end
  local locally_owned=c.owner.owner==c.owner.selfpeer
  local ready,reason=adapter:eligible(c,source,locally_owned,self.count>0 and ticket or nil,target)
  if not ready or not focused then stable_since=nil;stable_key=nil;note(not ready and reason or 'focus_or_input_blocked');return end
  if stable_key~=c.identity then stable_key=c.identity;stable_since=now end
  if now-stable_since<3 or now<cooldown then if trigger then event('trigger_rejected',{reason='settle_or_cooldown'})end;return end
  local armed='armed_step_'..(self.count+1)..'_to_seat_'..target
  if self.phase~=armed or last_reason then last_reason=nil;phase(armed);event('armed',{source=source,target=target})end
  if not trigger then return end
  end
  ticket=adapter:ticket(c,target);assert(ticket.source==source and ticket.target==target,'ticket_route_disagrees');self.count=self.count+1;self.pending=true;requested=now;return_at=nil;return_stable=nil;last_return_try=-math.huge
  if ticket.local_authority then
   phase('awaiting_local_switch');event('local_authority_selected',{number=self.count,source=source,target=target});return true
  end
  phase('awaiting_acquire');event('request_attempt',{number=self.count,source=source,target=target})
  local sent,err=pcall(adapter.request,adapter,c,ticket)
  if not sent then
   self:cancel('request_failed '..tostring(err))
   if not ticket.request_invoked then
    if not recover_control_abort(c,false,now,ticket.cancel_reason)then stop('request_refused_before_invocation')end
   else phase('late_grant_watch')end
  end
  return true
 end
 function self:close(reason)
  if self.pending then event('incomplete',{reason=reason,phase=self.phase,ownership_return_confirmed=false})end
 end
 return self
end
return M
