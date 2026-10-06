local M={}
function M.new(adapter,emit,status)
 local self={count=0,phase='waiting'}
 local stable_key,stable_since,last_reason,pinned,observe_start,observed_at,last_summary
 local function event(name,data)data=data or {};data.event='sync_probe_'..name;emit(data)end
 local function phase(value)self.phase=value;status('sync_'..value)end
 local function wait(reason)
  stable_key=nil;stable_since=nil
  if last_reason~=reason then last_reason=reason;event('waiting',{reason=reason});status('sync_waiting '..reason)end
 end
 local function stop(reason)event('stopped',{reason=reason,count=self.count});phase('stopped')end
 function self:step(trigger,now,focused)
  if self.phase=='stopped'or self.phase=='finished_local_only'then return end
  local ok,c,why=pcall(adapter.capture,adapter)
  if not ok then why=tostring(c);c=nil end
  if not c then
   wait(why or 'capture_unavailable')
   if observe_start and now-observe_start>8 then stop('local_state_unconfirmed_after_operation')end
   return
  end
  local summary=c.summary
  if summary~=last_summary then last_summary=summary;event('state',{detail=summary})end
  if pinned and c.identity~=pinned then stop('vehicle_session_or_avatar_changed');return end
  local eligible,reason=adapter:eligible(c)
  if not eligible then
   if self.count>0 then stop(reason)else wait(reason)end
   if trigger then event('trigger_rejected',{reason=reason})end
   return
  end
  if self.phase=='observing'then
   local wanted=self.count==1 and 1 or 0
   if c.seat~=wanted then
    if now-observe_start>5 then stop('local_target_not_observed')end
    return
   end
   observed_at=observed_at or now
   if now-observed_at<0.5 then return end
   event('local_target_observed',{seat=wanted,remote_success_not_confirmed=true})
   if self.count==2 then phase('finished_local_only');return end
   phase('waiting_return');stable_key=nil;stable_since=nil
  end
  local expected=self.count==0 and 0 or 1
  if c.seat~=expected then
   if self.count>0 then stop('seat_changed_outside_probe')else wait('start_in_driver_seat')end
   return
  end
  if not focused then wait('focus_or_input_blocked');return end
  if stable_key~=c.identity then stable_key=c.identity;stable_since=now end
  if now-stable_since<3 or(observe_start and now-observe_start<10)then
   if trigger then event('trigger_rejected',{reason='settle_or_cooldown'})end
   return
  end
  local armed=self.count==0 and 'armed_to_gunner'or'armed_to_driver'
  if self.phase~=armed or last_reason then last_reason=nil;phase(armed);event('armed',{target=1-expected,trigger='Ctrl+Shift+Home'})end
  if not trigger then return end
  pinned=pinned or c.identity
  self.count=self.count+1;observe_start=now;observed_at=nil
  phase('executing');event('operation_attempt',{number=self.count,source=expected,target=1-expected})
  local done,err=pcall(adapter.execute,adapter,c,1-expected)
  if not done then stop('operation_failed '..tostring(err));return end
  phase('observing')
 end
 function self:close(reason)
  if self.count>0 and self.phase~='finished_local_only'and self.phase~='stopped'then stop(reason)end
 end
 return self
end
return M
