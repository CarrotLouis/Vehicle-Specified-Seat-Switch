-- One pending transfer at a time; late grants are returned without switching.
local M={}
function M.new(adapter,emit,status)
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
 function self:cancel(reason)
  if ticket and self.pending and not ticket.cancel_reason then ticket.cancel_reason=reason;event('cancelled',{reason=reason,mutation_started=ticket.mutation_started or false})end
 end
 function self:step(trigger,now,focused)
  if self.phase=='stopped'or self.phase=='finished'then return end
  local ok,c,why=pcall(adapter.capture,adapter,self.pending and ticket or nil)
  if not ok then why=tostring(c);c=nil end
  if not c then
   stable_since=nil;stable_key=nil;note(why or 'observation_unavailable')
   if self.pending and now-requested>5 then self:cancel('observation_timeout; monitoring_late_grant_without_switch')end
   return
  end
  if c.summary~=last_summary then last_summary=c.summary;event('state',{detail=c.summary})end
  if self.pending then
   if not adapter:context(c,ticket)then stop('session_peer_or_vehicle_changed; return_not_confirmed');return end
   local o=c.owner
   if not ticket.acquired then
    if o.owner==ticket.selfpeer and o.vehicle.owned_local and not o.busy then
     ticket.acquired=true;event('acquired',{source=ticket.source,target=ticket.target})
     if now-requested>5 then self:cancel('late_grant')end
     local allowed,reason=adapter:eligible(c,ticket.source,true,ticket)
     if not allowed then self:cancel(reason)end
     if not focused then self:cancel('focus_or_input_blocked')end
     if not ticket.cancel_reason then
      -- Consumed before invocation; never rerun a partially completed mutation.
      ticket.switch_attempted=true;event('switch_attempt',{source=ticket.source,target=ticket.target})
      local done,err=pcall(adapter.execute,adapter,c,ticket)
      if not done then self:cancel('switch_failed '..tostring(err))end
     end
     phase('awaiting_return')
     -- Do not use the pre-mutation ownership snapshot for returning authority.
     return
    end
    if o.owner~=ticket.original and o.owner~=ticket.selfpeer then stop('unexpected_owner_before_grant');return end
    if now-requested>5 then self:cancel('grant_timeout; keep_monitoring_late_grant');phase('late_grant_watch')end
    return
   end
   if o.owner==ticket.original and not o.vehicle.owned_local and not o.busy then
    return_stable=return_stable or now
    if now-return_stable<0.5 then return end
    ticket.return_confirmed=true
    event('ownership_return_confirmed',{cancelled=ticket.cancel_reason~=nil,return_invoked=ticket.return_invoked or false})
    self.pending=false
    if ticket.cancel_reason then phase('stopped');event('aborted_and_returned',{reason=ticket.cancel_reason,mutation_started=ticket.mutation_started or false});return end
    local good,reason=adapter:eligible(c,ticket.target,false,ticket)
    if not good or not ticket.sync_returned then stop('returned_but_seat_unconfirmed '..tostring(reason));return end
    event('operation_complete',{number=self.count,seat=ticket.target,remote_visual_confirmation_required=true})
    cooldown=now+10;stable_key=nil;stable_since=nil;last_reason=nil
    if self.count==2 then phase('finished')else phase('waiting_second_trigger')end
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
  local source=self.count==0 and 1 or 4
  if self.count>0 and ticket and c.identity~=ticket.identity then stop('session_or_vehicle_changed_between_operations');return end
  local ready,reason=adapter:eligible(c,source,false,self.count>0 and ticket or nil)
  if not ready or not focused then stable_since=nil;stable_key=nil;note(not ready and reason or 'focus_or_input_blocked');return end
  if stable_key~=c.identity then stable_key=c.identity;stable_since=now end
  if now-stable_since<3 or now<cooldown then if trigger then event('trigger_rejected',{reason='settle_or_cooldown'})end;return end
  local armed=self.count==0 and 'armed_to_gunner'or'armed_to_front_passenger'
  if self.phase~=armed or last_reason then last_reason=nil;phase(armed);event('armed',{source=source,target=5-source})end
  if not trigger then return end
  ticket=adapter:ticket(c);self.count=self.count+1;self.pending=true;requested=now;return_at=nil;return_stable=nil;last_return_try=-math.huge
  phase('awaiting_acquire');event('request_attempt',{number=self.count,source=source,target=5-source})
  local sent,err=pcall(adapter.request,adapter,c,ticket)
  if not sent then
   self:cancel('request_failed '..tostring(err))
   if not ticket.request_invoked then stop('request_refused_before_invocation')else phase('late_grant_watch')end
  end
 end
 function self:close(reason)
  if self.pending then event('incomplete',{reason=reason,phase=self.phase,ownership_return_confirmed=false})end
 end
 return self
end
return M
