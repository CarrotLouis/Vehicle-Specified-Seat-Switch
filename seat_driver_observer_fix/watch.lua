-- Automatic passive capture of one locally occupied M102 driver seat.
-- At most 20 Hz for 120 seconds; no physical/property reads outside this scope.
return function(api,physics,handoff,context,body_flags,calls,emit)
 local self={};local identity,started,next_arm,last_owner,last_position,last_time
 local until_at=0;local segment=0;local failed=false
 local function select_driver(s)
  if not s or s.state~='mission'or s.player_count~=2 or s.peer_count~=2 or s.local_count~=1 then return end
  local a;for _,x in ipairs(s.avatars)do if x.is_local then if a then return end;a=x end end
  if not a or not a.owned_local or not a.seat or a.seat.current~=0 or a.seat.transitioning~=0 then return end
  for _,v in ipairs(s.vehicles)do
   if v.id==a.seat.collection and v.name=='m102'and
   (v.resource=='cc21c7ffd3ebefb9'or v.resource=='e9cd1d0d118886af')and
   v.transition_type==26 and v.seat_count==5 then return v,a end
  end
 end
 local function disarm(reason)
  if identity then
   calls:disarm(reason);emit({event='driver_watch_ended',reason=reason,segment=segment,read_only=true})
  end
  identity=nil;until_at=0;last_owner=nil;last_position=nil;last_time=nil
 end
 function self:update(s)
  if failed then return end
  local v,a=select_driver(s)
  if not v then disarm('driver_or_two_player_scope_left');return end
  local key=tostring(s.mission_value)..'/'..v.id..'/'..v.unit..'/'..v.network_unit..'/'..v.resource..'/'..a.id..'/'..a.unit
  local now=api.now()
  if identity and identity~=key then disarm('driver_vehicle_identity_changed')end
  if identity==key and now>until_at then
   if not self.expired then
    calls:disarm('capture_120s_expired');self.expired=true
    emit({event='driver_watch_expired',segment=segment,read_only=true})
   end
   return
  end
  local ok,why=pcall(function()
   local physical=physics:read_vehicle(v)
   local o=context:read(s,v)
   local h=handoff:read_vehicle(v,o)
   if not identity then
    segment=segment+1;identity=key;started=now;until_at=now+120;next_arm=0;self.expired=false
    emit({event='driver_watch_started',segment=segment,collection=v.id,unit=v.unit,
     network_unit=v.network_unit,actor_handle=physical.actor_handle,max_duration_seconds=120,
     local_peer_hex=o.local_peer_hex,coordinator_hex=o.coordinator_hex,
     driver_is_host=o.selfpeer==o.coordinator,read_only=true})
   end
   -- Renewal leaves a 500 ms grace period. No custom key or borrowed authority.
   if now>=next_arm then
    calls:arm_driver(v,s,a,physical);next_arm=now+1.5
   end
   local owner_key=h.engine_owner_hex..'/'..h.engine_serial
   local change=last_owner and owner_key~=last_owner
   if change then
    emit({event='driver_authority_observed_change',segment=segment,
     from=last_owner,to=owner_key,owned_by_driver=h.engine_owner_hex==o.local_peer_hex,
     polling_only=true,may_miss_shorter_than_50ms=true})
   end
   physical.event='driver_physics_sample';physical.segment=segment
   physical.t_sample_ms=math.floor(api.now()*1000+.5);physical.actual_seat=a.seat.current
   physical.driver_is_host=o.selfpeer==o.coordinator;physical.owner_hex=h.engine_owner_hex
   physical.owner_serial=h.engine_serial;physical.driver_peer_hex=o.local_peer_hex
   physical.driver_owns_chassis=h.engine_owner_hex==o.local_peer_hex
   physical.collection_owned_local=v.owned_local;physical.handoff_properties=h
   physical.context_read_count=o.read_count;physical.observation_only=true
   if body_flags then
    local good,value=pcall(body_flags.read,body_flags,physical)
    if good then physical.body_flags=value
    else emit({event='body_flags_gap',reason=tostring(value),read_only=true,segment=segment})end
   end
   if last_position and now>last_time then
    local ds=0;for i=1,3 do ds=ds+(physical.physical_position[i]-last_position[i])^2 end
    physical.position_delta_native_per_second=math.sqrt(ds)/(now-last_time)
   end
   last_owner=owner_key;last_position=physical.physical_position;last_time=now
   emit(physical)
  end)
  if not ok then
   pcall(disarm,'read_or_observer_gap');failed=true
   emit({event='driver_watch_gap',reason=tostring(why),read_only=true,restart_required=true})
  end
 end
 function self:gap(reason)
  if failed then return end
  -- A failed outer snapshot must immediately end the old actor's capture.
  local ok,why=pcall(disarm,reason)
  if not ok then failed=true;emit({event='driver_watch_gap',reason=tostring(why),read_only=true})end
 end
 function self:close(reason)pcall(disarm,reason);failed=true end
 return self
end
