-- Ten-Hz short windows of ONE validated chassis, reads only. No API hooks,
-- body flags, ownership edits, velocity/pose writes or idle physics polling.
return function(api,reader,physics,handoff,emit,scope)
 local until_at,last_operation,next_at=0,0,0
 local self={}
 local function read(stage,c,t)
  -- The reused body reader is live-validated only for M102. Other FRVs retain
  -- seat/protocol logs without futile body polls or misleading zero samples.
  if not c or not c.owner or not c.native or c.native.vehicle~='m102'or not scope.layout(c.native)or c.sample.player_count~=2 then return end
  local v=c.owner.vehicle;local ok,data=pcall(physics.read_vehicle,physics,v)
  if not ok then emit({event='reservation_physics_gap',stage=stage,reason=tostring(data),read_only=true});return end
  local property_ok,property=pcall(handoff.read_vehicle,handoff,v,c.owner)
  if property_ok then data.handoff_properties=property else emit({event='reservation_property_gap',stage=stage,reason=tostring(property),read_only=true})end
  data.event='reservation_physics_sample';data.stage=stage;data.owner=reader.peers[c.owner.owner]or'unlabelled_peer';data.owner_serial=c.owner.serial
  data.actual_seat=c.seat;data.collection=v.id;data.collection_unit=v.network_unit;data.operation=last_operation
  data.installer_is_host=c.owner.coordinator==c.owner.selfpeer;data.physics_writes_enabled=false
  if t then data.source=t.source;data.target=t.target end
  emit(data)
 end
 function self:boundary(stage,c,t)
  until_at=api.now()+3;read(stage,c,t)
 end
 function self:update(_,probe)
  if probe.count==0 and until_at==0 then return end
  if probe.count~=last_operation then last_operation=probe.count;until_at=api.now()+3 end
  local now=api.now()
  if now>until_at or now<next_at then return end
  next_at=now+.1;read('short_window',probe.observed)
 end
 return self
end
