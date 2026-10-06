-- Observe this car's existing driver commands across a switch. They are INPUT
-- values, not a speed measurement. No game calls, writes or velocity guesses.
return function(api,reader,driver_reader,emit)
 local ring,key,last_node,last_operation,until_at,sequence=nil,nil,nil,0,0,0
 local function alias(peer)return reader.peers[peer]or'unlabelled_peer'end
 local function end_window(reason)
  if until_at>0 then emit({event='motion_watch_ended',reason=reason,read_only=true,sequence=sequence})end
  ring=nil;key=nil;last_node=nil;until_at=0
 end
 return {boundary=function(_,stage,c,t)
  -- Capture short ownership loans at the actual transaction boundaries,
  -- rather than relying solely on the 100ms background sample. Only reads.
  local v,driver=c.owner and c.owner.vehicle,c.driver
  if not v or not driver or driver.is_local then return end
  local ok,data=pcall(driver_reader.read_vehicle,driver_reader,v)
  if not ok then emit({event='motion_boundary_gap',stage=stage,collection=v.id,reason=tostring(data),read_only=true});return end
  data.event='motion_boundary';data.stage=stage;data.read_only=true;data.driver_commands_not_velocity=true
  data.collection=v.id;data.vehicle=v.name;data.source=t.source;data.target=t.target
  data.operation_identity_hex=(t.identity:gsub('.',function(x)return string.format('%02x',x:byte())end))
  data.t_sample_ms=math.floor(api.now()*1000+.5)
  data.driver={id=driver.id,unit=driver.unit,network_unit=driver.network_unit,seat=driver.seat}
  data.snapshot_local_seat=c.avatar and c.avatar.seat;data.snapshot_owner=alias(c.owner.owner)
  data.snapshot_owned_local=v.owned_local;data.owner_serial=c.owner.serial
  emit(data)
 end,update=function(_,sample,probe)
  if not sample or sample.state~='mission'then end_window('not_in_mission');return end
  local own,driver,v
  for _,a in ipairs(sample.avatars)do if a.is_local then own=a;break end end
  if own and own.seat then for _,x in ipairs(sample.vehicles)do if x.id==own.seat.collection then v=x;break end end end
  if not v then end_window('own_vehicle_missing');return end
  for _,a in ipairs(sample.avatars)do if not a.is_local and a.seat and a.seat.collection==v.id and
    a.seat.current==0 and a.seat.reserved==0 and a.seat.role==1 and a.seat.target==-1 and
    a.seat.action==-1 and a.seat.transitioning==0 and a.seat.queued_exit==0 then driver=a;break end end
  if not driver then end_window('remote_driver_missing');return end
  local id=tostring(v.id)..'/'..tostring(v.unit)..'/'..tostring(v.network_unit)..'/'..v.resource..'/'..sample.mission_value
  if key~=id then end_window('car_identity_changed');key=id;ring={} end
  local now=api.now();local ok,data=pcall(driver_reader.read_vehicle,driver_reader,v)
  if not ok then
   if until_at>0 then emit({event='motion_watch_gap',collection=v.id,reason=tostring(data),read_only=true,sequence=sequence})end
   return -- A telemetry gap never changes seat/input eligibility.
  end
  data.t_sample_ms=math.floor(now*1000+.5);data.collection=v.id;data.vehicle=v.name
  data.owned_local=v.owned_local;data.driver={id=driver.id,unit=driver.unit,network_unit=driver.network_unit,seat=driver.seat}
  data.local_seat=own.seat;data.players=sample.player_count;data.peer_count=sample.peer_count
  data.operation=probe.count;data.phase=probe.phase;data.pending=probe.pending
  local c=probe.observed
  if c and c.owner.vehicle.id==v.id and c.owner.vehicle.unit==v.unit then
   data.last_probe_owner={owner=alias(c.owner.owner),self=alias(c.owner.selfpeer),coordinator=alias(c.owner.coordinator),
    serial=c.owner.serial,busy=c.owner.busy,sample_ms=probe.observed_at and math.floor(probe.observed_at*1000+.5)}
  end
  local new_operation=probe.count~=last_operation
  local new_seat=last_node~=nil and own.seat.current~=last_node
  if new_operation or new_seat then
   sequence=sequence+1;until_at=now+2
   emit({event='motion_watch_started',sequence=sequence,collection=v.id,vehicle=v.name,operation=probe.count,
    trigger=new_operation and'cross_request'or'native_or_untracked_seat_change',pre_samples=ring,
    duration_seconds=2,driver_commands_not_velocity=true,read_only=true})
  end
  last_operation=probe.count;last_node=own.seat.current
  if until_at>0 and now<=until_at then
   data.event='motion_watch_sample';data.sequence=sequence;data.read_only=true;emit(data)
  elseif until_at>0 then
   emit({event='motion_watch_ended',sequence=sequence,reason='window_complete',read_only=true});until_at=0
  end
  ring[#ring+1]=data;if #ring>5 then table.remove(ring,1)end
 end}
end
