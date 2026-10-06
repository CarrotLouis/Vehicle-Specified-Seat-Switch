-- Short windows of real chassis-actor motion across the accepted loan only.
return function(api,reader,physics,legacy,emit,handoff,pose_calls,body_flags)
 local ring,key,last_operation,until_at,last=nil,nil,0,0,nil
 local gap_key,gap_at,ready_key=nil,-math.huge,nil
 local function capture(v,stage,c,t)
  local ok,data=pcall(physics.read_vehicle,physics,v)
  if not ok then
   local why=tostring(data);local now=api.now()
   local signature=tostring(v.id)..'/'..tostring(v.unit)..'/'..stage..'/'..why
   -- Keep exact boundary failures. Repeated background failures carry the
   -- same bounded layout evidence at most once per second.
   if stage~='background' or signature~=gap_key or now-gap_at>=1 then
    gap_key=signature;gap_at=now
    emit({event='physics_motion_gap',stage=stage,collection=v.id,reason=why,
     read_only=true,layout=physics.last_read})
   end
   return nil,tostring(data)
  end
  local now=api.now();data.t_sample_ms=math.floor(now*1000+.5);data.event='physics_motion_sample';data.stage=stage
  -- Property/schema reads occur at explicit handoff boundaries and only in the
  -- short post-trigger window. They add no background whole-memory sweep.
  if handoff and c and (stage~='background' or until_at>0 and now<=until_at)then
   local property_start=api.now()
   local good,property=pcall(handoff.read_vehicle,handoff,v,c.owner)
   if good then
    property.read_start_ms=math.floor(property_start*1000+.5)
    property.read_end_ms=math.floor(api.now()*1000+.5)
    property.time_resolution_caution='Uses existing game diagnostic clock; not a sub-millisecond performance benchmark.'
    data.handoff_properties=property
   else emit({event='handoff_property_gap',stage=stage,collection=v.id,
    reason=tostring(property),read_only=true,layout=handoff.last_read})end
  end
  if body_flags and (stage~='background' or until_at>0 and now<=until_at)then
   local good,value=pcall(body_flags.read,body_flags,data)
   if good then data.body_flags=value
   else emit({event='body_flags_gap',stage=stage,collection=v.id,reason=tostring(value),read_only=true})end
  end
  if c then
   data.owner=reader.peers[c.owner.owner]or'unlabelled_peer';data.owner_serial=c.owner.serial
   data.installer_is_host=c.owner.selfpeer==c.owner.coordinator;data.actual_seat=c.seat
  end
  if t then data.operation_identity_hex=(t.identity:gsub('.',function(x)return string.format('%02x',x:byte())end));data.requested_target=t.target end
  local id=tostring(v.id)..'/'..tostring(v.unit)..'/'..v.resource..'/'..tostring(data.actor_handle)
  if ready_key~=id then
   ready_key=id;emit({event='physics_motion_ready',collection=v.id,unit=v.unit,
    actor_handle=data.actor_handle,actor_count=data.actor_count,actor_storage=data.actor_storage,read_only=true})
  end
  if last and last.id==id then
   local dt=now-last.now
   if dt>=.001 and dt<=1 then
    local speed=0
    for i=1,3 do local d=data.physical_position[i]-last.position[i];speed=speed+d*d end
    data.position_delta_native_per_second=math.sqrt(speed)/dt;data.position_delta_seconds=dt
   end
  end
  last={id=id,now=now,position=data.physical_position}
  return data
 end
 local self={}
 function self:before_request(c,t)
  local data,why=capture(c.owner.vehicle,'request_preflight',c,t)
  assert(data,'physical_observation_required_before_loan '..tostring(why));emit(data)
  assert(pose_calls,'pose_call_observer_required_before_loan')
  pose_calls:arm(c.owner.vehicle,c,t,data)
 end
 function self:boundary(stage,c,t)
  if legacy then pcall(legacy.boundary,legacy,stage,c,t)end
  local v=c.owner and c.owner.vehicle;if not v or v.name~='m102' then return end
  local data=capture(v,stage,c,t);if data then emit(data)end
 end
 function self:update(sample,probe)
  if legacy then legacy:update(sample,probe)end
  if not sample or sample.state~='mission'or sample.player_count~=2 or sample.peer_count~=2 then ring=nil;key=nil;last=nil;until_at=0;ready_key=nil;return end
  local a,v
  for _,x in ipairs(sample.avatars)do if x.is_local then a=x;break end end
  if a and a.seat and a.seat.current==1 then
   for _,x in ipairs(sample.vehicles)do if x.id==a.seat.collection and x.name=='m102'then v=x;break end end
  end
  if not v then ring=nil;key=nil;last=nil;until_at=0;ready_key=nil;return end
  local id=tostring(v.id)..'/'..tostring(v.unit)..'/'..v.resource..'/'..tostring(sample.mission_value)
  if id~=key then ring={};key=id;last=nil;until_at=0 end
  local c=probe.observed
  if not c or c.owner.vehicle.id~=v.id or c.owner.vehicle.unit~=v.unit then c=nil end
  local data=capture(v,'background',c)
  if not data then return end
  if probe.count~=last_operation then
   last_operation=probe.count;until_at=api.now()+2
   emit({event='physics_motion_window',operation=probe.count,collection=v.id,pre_samples=ring,read_only=true})
  end
  if until_at>0 and api.now()<=until_at then data.operation=probe.count;data.phase=probe.phase;emit(data)end
  ring[#ring+1]=data;if #ring>10 then table.remove(ring,1)end
 end
 return self
end
