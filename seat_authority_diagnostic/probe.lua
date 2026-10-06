-- Single ownership round trip. Never writes seats or local ownership flags.
local M={}
function M.new(observer,emit,status)
 local self={used=false,phase='idle',tracked=nil};local stable_key,stable_since,last_reason,last_observation
 local requested_at,return_at,return_stable,context,original,localpeer
 local function event(name,data)
  data=data or {};data.event='authority_probe_'..name;emit(data)
 end
 local function phase(value)self.phase=value;status('probe_'..value)end
 local function note(reason)
  if reason~=last_reason then last_reason=reason;event('waiting',{reason=reason});status('probe_waiting '..reason)end
 end
 local function seated(a,vehicle,seat,role)
  local s=a and a.seat
  return s and s.collection==vehicle.id and s.current==seat and s.reserved==seat and s.role==role
   and s.target==-1 and s.action==-1 and s.transitioning==0 and s.queued_exit==0
 end
 local function eligibility(s,o)
  if s.local_count~=1 or s.player_count~=2 or o.peer_count~=2 then return nil,'exactly_two_players_required'end
  if o.selfpeer==o.coordinator then return nil,'friend_must_host'end
  if o.vehicle.name~='m102' or o.vehicle.seat_count~=5 then return nil,'m102_required'end
  if o.owner~=o.coordinator or o.owner==o.selfpeer or not o.members[o.owner]then return nil,'friend_not_vehicle_owner'end
  if o.busy or o.vehicle.owned_local then return nil,'ownership_not_stable'end
  local local_avatar,driver
  for _,a in ipairs(s.avatars)do
   if a.is_local then local_avatar=a
   elseif seated(a,o.vehicle,0,1)then driver=a end
  end
  if not seated(local_avatar,o.vehicle,1,3)or not local_avatar.vehicle_input then return nil,'sit_still_in_front_passenger'end
  if not driver then return nil,'friend_must_remain_driver'end
  local a,b=o.avatars[local_avatar.id],o.avatars[driver.id]
  if not a or not b or a.owner~=o.selfpeer or b.owner~=o.owner then return nil,'avatar_peer_identity_not_confirmed'end
  if o.vehicle.free_mask%4~=0 then return nil,'driver_passenger_claims_not_confirmed'end
  return o.context..'/'..o.vehicle.id..'/'..o.vehicle.unit..'/'..o.vehicle.network_unit..'/'..o.serial..'/'..local_avatar.id..'/'..driver.id
 end
 function self:step(s,o,why,pressed,now)
  if self.phase=='complete'or self.phase=='ended'or self.phase=='send_failed'then return end
  if o then
   local summary=observer:summary(o)
   local key=summary.owner..'/'..tostring(summary.busy)..'/'..summary.serial..'/'..tostring(summary.owned_local)
   if key~=last_observation then last_observation=key;event('ownership',summary)end
  end
  if self.used then
   if s and s.state~='mission'then event('incomplete',{reason='mission_ended',previous=self.phase});phase('ended');return end
   if not o then note(why or 'observation_unavailable');return end
   if o.context~=context then event('incomplete',{reason='session_or_mission_changed',previous=self.phase});phase('ended');return end
   if not o.members[original]or o.selfpeer~=localpeer then event('incomplete',{reason='original_peer_left_or_identity_changed',previous=self.phase});phase('ended');return end
   if not return_at then
    if o.owner==localpeer and not o.busy and o.vehicle.owned_local then
     event('acquired',observer:summary(o))
     -- Consume the return attempt before invocation. No retry if a call throws.
     return_at=now;phase('awaiting_return');event('return_sent',observer:summary(o))
     local ok,err=pcall(observer.send,observer,o,localpeer,original)
     if not ok then event('send_failed',{stage='return',reason=tostring(err)});phase('send_failed')end
    elseif now-requested_at>=5 and self.phase=='awaiting_acquire'then
     event('request_timeout',{reason='still_monitoring_for_late_grant; no_retry'});phase('late_grant_watch')
    end
   else
    if o.owner==original and not o.busy and not o.vehicle.owned_local then
     return_stable=return_stable or now
     if now-return_stable>=0.5 then event('complete',observer:summary(o));phase('complete')end
    else return_stable=nil end
    if self.phase=='awaiting_return'and now-return_at>=5 then
     event('return_timeout',{reason='return_not_confirmed; no_retry'});phase('return_not_confirmed')
    end
   end
   return
  end
  if not o then stable_key=nil;stable_since=nil;if self.phase=='armed'then phase('idle')end;note(why or 'observation_unavailable');return end
  local key,reason=eligibility(s,o)
  if not key then stable_key=nil;stable_since=nil;if self.phase=='armed'then phase('idle')end;note(reason);if pressed then event('trigger_rejected',{reason=reason})end;return end
  if stable_key~=key then stable_key=key;stable_since=now;if self.phase=='armed'then phase('idle')end end
  if now-stable_since<3 then note('wait_three_seconds_seated');if pressed then event('trigger_rejected',{reason='wait_three_seconds_seated'})end;return end
  if self.phase~='armed'then phase('armed');event('armed',{trigger='Ctrl+Shift+Home',scope='one_roundtrip_per_process; no_seat_switch'})end
  last_reason=nil
  if not pressed then return end
  self.used=true;self.tracked={id=o.vehicle.id,unit=o.vehicle.unit,network_unit=o.vehicle.network_unit,resource=o.vehicle.resource}
  context=o.context;original=o.owner;localpeer=o.selfpeer;requested_at=now
  phase('awaiting_acquire');event('request_sent',observer:summary(o))
  local ok,err=pcall(observer.send,observer,o,original,localpeer)
  if not ok then event('send_failed',{stage='acquire',reason=tostring(err)});phase('send_failed')end
 end
 function self:close(reason)
  if self.used and self.phase~='complete'and self.phase~='ended'then event('incomplete',{reason=reason,previous=self.phase})end
 end
 return self
end
return M
