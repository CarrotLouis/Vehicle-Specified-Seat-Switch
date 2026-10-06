-- One poller owns native and network seat requests. No queued second switch.
local M={}
function M.new(api,keys,input,policy,snapshot,native,probe,emit)
 local self={poller=input.new(keys,api),pending=nil,queued=nil,cooldown=0,next_probe=0}
 local function event(reason,data)data=data or {};data.event='seat_input';data.reason=reason;emit(data)end
 local function quiet(binding)
  if binding and api.down(binding%256)then return false end
  for _,k in ipairs({1,2,4,5,6,32,65,68,69,81,83,87})do if api.down(k)then return false end end
  return true
 end
 function self:update(s,reason)
  local now=api.now();local focused=api.input_allowed()
  local enabled=not api.experiment_allowed or api.experiment_allowed()
  -- Keep polling even while blocked: held keys must never become deferred edges.
  local pressed=self.poller:poll(focused and enabled)
  local was_pending=probe.pending
  if now>=self.next_probe or probe.pending then
   self.next_probe=now+.1;probe:step(nil,now,focused and enabled)
  end
  if probe.phase=='stopped' then self.queued=nil;return 'network_stopped_restart_required'end
  if was_pending or probe.pending then self.queued=nil;return 'network_pending'end
  if self.pending then
   local p=self.pending
   if not s or s.identity~=p.identity then
    if now-p.started>6 then event('native_expired');self.pending=nil end
   elseif s.node==p.target then event('native_complete',{target=p.target});self.pending=nil
   elseif now-p.started>6 then event('native_expired');self.pending=nil end
   return 'native_pending'
  end
  if not focused or not enabled then self.queued=nil;return 'input_blocked'end
  if not s then self.queued=nil;return reason end
  local target,binding
  for i,name in ipairs(policy.seats[s.vehicle]or{})do
   local code=keys[s.vehicle][name]
   if pressed[code]then
    if target~=nil then self.queued=nil;event('multiple_seat_keys');return 'multiple_seat_keys'end
    target=i-1;binding=code
   end
  end
  if self.queued then
   local q=self.queued
   if target~=nil then self.queued=nil;event('cancelled_by_new_key');return 'cancelled_by_new_key'end
   if now-q.started>8 or s.identity~=q.identity or s.node~=q.source or s.occupied[q.target]~=false then
    self.queued=nil;event('release_wait_cancelled');return 'release_wait_cancelled'
   end
   if s.active or not quiet(q.binding)then return 'release_controls_before_switch'end
   if not probe.ready_at or now<probe.ready_at then return 'wait_network_settle'end
   self.queued=nil
   if not snapshot.current(api,s)then event('snapshot_changed');return 'snapshot_changed'end
   probe:step(q.target,now,true);return 'network_requested'
  end
  if target==nil then return 'ready'end
  if now<self.cooldown then event('input_cooldown');return 'input_cooldown'end
  self.cooldown=now+.35
  local seats=policy.seats[s.vehicle]
  local allowed,why=policy.check('enhanced',s.vehicle,seats[s.node+1],seats[target+1],s.occupied[target])
  if not allowed then event(why,{target=target});return why end
  if not snapshot.current(api,s)then event('snapshot_changed');return 'snapshot_changed'end
  local normal=policy.check('normal',s.vehicle,seats[s.node+1],seats[target+1],s.occupied[target])
  if normal then
   local n,p=snapshot.predictions(s)
   local op=n==target and 'next'or p==target and 'previous'or nil
   if not op then event('no_native_route');return 'no_native_route'end
   self.pending={identity=s.identity,target=target,started=now}
   event('native_request',{source=s.node,target=target,operation=op})
   native[op](s.seaters,s.avatar);return 'native_requested'
  end
  if s.vehicle~='m102'or s.player_count~=2 or s.peer_count~=2 then event('cross_scope_unavailable');return 'cross_scope_unavailable'end
  -- Mouse/letter bindings may also be fire or driving controls. Wait for their
  -- release before the authority request; never inject or consume game input.
  self.queued={identity=s.identity,source=s.node,target=target,binding=binding,started=now}
  event('waiting_key_release',{source=s.node,target=target})
  return 'release_controls_before_switch'
 end
 return self
end
return M
