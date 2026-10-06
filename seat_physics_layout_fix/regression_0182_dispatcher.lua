-- One poller owns native and network seat requests. No queued second switch.
local M={}
function M.new(api,keys,input,policy,snapshot,native,probe,emit,gate)
 local self={poller=input.new(keys,api),pending=nil,queued=nil,cooldown=0,next_probe=0}
 local function event(reason,data)data=data or {};data.event='seat_input';data.reason=reason;emit(data)end
 local function quiet(binding)
  local down=api.control_down or api.down
  if binding and down(binding%256)then return false end
  for _,k in ipairs({1,2,4,5,6,32,65,68,69,81,83,87})do if down(k)then return false end end
  return true
 end
 local function submit(q,now)
  -- A fresh capture may reject a known same-seat passenger retraction. Keep
  -- this one request briefly; all mutation guards remain strict and fresh.
  local accepted,why,retryable,context=probe:step(q.target,now,true,q.deferred)
  if accepted~=false then self.queued=nil;return 'network_requested'end
  if retryable then
   q.defer_started=q.defer_started or now;q.deferred=context;self.queued=q
   if now-q.defer_started<=1 then
    if q.defer_reason~=why then q.defer_reason=why;event('waiting_friend_retract',{source=q.source,target=q.target})end
    return 'waiting_friend_retract'
   end
  end
  self.queued=nil;event('network_trigger_refused',{source=q.source,target=q.target,detail=why})
  return 'network_trigger_refused'
 end
 function self:update(s,reason)
  local now=api.now();local focused=api.input_allowed()
  local enabled=not api.experiment_allowed or api.experiment_allowed()
  -- Keep polling even while blocked: held keys must never become deferred edges.
  local pressed=self.poller:poll(focused and enabled)
  local physical={};for code in pairs(pressed)do physical[code]=true end
  local consumed,records,discarded={},{},{}
  local was_pending=probe.pending
  if now>=self.next_probe or probe.pending then
   self.next_probe=now+.1;probe:step(nil,now,focused and enabled)
  end
  if gate then
   gate:pulse(s,probe.observed,keys,enabled and probe.phase~='stopped')
   consumed,records,discarded=gate:take(s);records=records or{};discarded=discarded or{}
   if gate.filter then gate:filter(pressed,consumed)end
   if gate.failed or gate.pending then enabled=false end
   if focused and enabled then for code in pairs(consumed)do pressed[code]=true end end
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
  -- A validated request may outlive the brief same-seat lean animation raised
  -- by its mouse binding. Only wait here; no engine/RPC call uses stale state.
  local vehicle=s and s.vehicle or self.queued and self.queued.vehicle
  local target,binding
  for i,name in ipairs(policy.seats[vehicle]or{})do
   local code=keys[vehicle][name]
   if pressed[code]then
    if target~=nil then self.queued=nil;event('multiple_seat_keys');return 'multiple_seat_keys'end
    target=i-1;binding=code
   end
  end
  local q=self.queued
  if q and q.physical_pending and discarded[q.binding]then
   self.queued=nil;event('discarded_queued_press',{source=q.source,target=q.target});return 'discarded_queued_press'
  end
  if q and target~=nil and s then
   local r=records[binding]
   -- Physical polling can see the down edge one or two frames before the
   -- GUI thread publishes its consumed intent. They are the same request,
   -- not a new key: require a single fresh native record and no new poll edge.
   local same_press=q.physical_pending and not physical[binding]and binding==q.binding and target==q.target
     and s.identity==q.identity and s.node==q.source and now-q.started>=0 and now-q.started<=.25
     and r and r.count==1 and r.source==q.source and r.target==q.target and r.generation==q.generation
   if same_press then
    q.physical_pending=false;event('matched_native_press',{source=q.source,target=q.target,sequence=r.sequence,delay_ms=math.floor((now-q.started)*1000+.5)})
    target=nil;binding=nil
   end
  end
  if not s then
   local q=self.queued
   if q then
    if target~=nil then self.queued=nil;event('cancelled_by_new_key');return 'cancelled_by_new_key'end
    local lean_gap=(q.vehicle=='m102'or q.vehicle=='m103'or q.vehicle=='m104'or q.vehicle=='bastion'or q.vehicle=='maelstrom')and
      policy.seats[q.vehicle]and q.source>=1 and q.source<=3 and
      (reason=='transition_in_progress'or reason=='transition_pending')
    if lean_gap and now-q.started<=8 then
     if q.snapshot_wait~=reason then q.snapshot_wait=reason;event('waiting_lean_transition',{source=q.source,target=q.target,snapshot_reason=reason})end
     return 'waiting_lean_transition'
    end
    self.queued=nil;event('release_wait_cancelled',{snapshot_reason=reason or'unavailable'})
   end
   return reason
  end
  if self.queued then
   local q=self.queued
   if target~=nil then self.queued=nil;event('cancelled_by_new_key');return 'cancelled_by_new_key'end
   if now-q.started>8 or s.identity~=q.identity or s.node~=q.source or s.occupied[q.target]~=false then
    self.queued=nil;event('release_wait_cancelled');return 'release_wait_cancelled'
   end
   if q.defer_started and now-q.defer_started>1 then
    self.queued=nil;event('friend_retract_wait_expired',{source=q.source,target=q.target});return 'friend_retract_wait_expired'
   end
   if q.snapshot_wait then q.snapshot_wait=nil;event('lean_transition_finished',{source=q.source,target=q.target})end
   if s.active or not quiet(q.binding)then return 'release_controls_before_switch'end
   if not probe.ready_at or now<probe.ready_at then return 'wait_network_settle'end
   if not snapshot.current(api,s)then self.queued=nil;event('snapshot_changed');return 'snapshot_changed'end
   return submit(q,now)
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
  if (s.vehicle~='m102'and s.vehicle~='m103'and s.vehicle~='m104'and s.vehicle~='bastion'and s.vehicle~='maelstrom')or s.player_count~=2 or s.peer_count~=2 then event('cross_scope_unavailable');return 'cross_scope_unavailable'end
  local request={identity=s.identity,vehicle=s.vehicle,source=s.node,target=target,binding=binding,started=now,
   physical_pending=not consumed[binding],generation=gate and gate.generation}
  -- A consumed primary is absent from gameplay controls even while physically
  -- held. Submit in this update if all fresh guards and other controls permit.
  if gate and gate.active and not gate.failed and not s.active and quiet(binding) and probe.ready_at and now>=probe.ready_at then
   event('priority_request',{source=s.node,target=target})
   return submit(request,now)
  end
  -- Unconsumed input keeps the bounded release/lean fallback.
  self.queued=request
  event('waiting_key_release',{source=s.node,target=target})
  return 'release_controls_before_switch'
 end
 return self
end
return M
