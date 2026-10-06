-- Clear only steering input/history and native pivot mode on OWN driver exit.
-- No velocity write, periodic reset, borrowed authority, or teammate cleanup.
return function(api,game,p,compat,reader_factory,scope,emit)
 local ffi=assert(api.ffi);local reader
 local function get(a,n)local b=assert(api.read(a,n),'steer_reset_unreadable');assert(#b==n);return b end
 local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);assert(e);return a+c*256+d*65536+e*16777216 end
 local function ptr(a)return assert(api.pointer(get(a,8)),'steer_reset_pointer')end
 local function reference(name)
  local r=assert(p.spin.refs[name]);local at=game+assert(p.functions[r.record]).rva+r.offset
  local b=get(at,r.size);assert((b:sub(1,3):gsub('.',function(c)return string.format('%02x',c:byte())end))==r.opcode_hex,'steer_reset_reference')
  local d=u32(b,r.disp);if d>=2^31 then d=d-2^32 end;return at+r.size+d
 end
 local function observe(v)
  if not reader then reader=reader_factory(api,game,p,compat)end
  return reader:read_vehicle(v)
 end
 local function locate(s)
  local entity=get(s.collection_address,24)
  local v={name=s.vehicle,id=s.collection,unit=u32(entity,12),network_unit=s.collection_unit,resource=s.resource,owned_local=true}
  assert(u32(entity,8)==v.id and u32(entity,16)==v.network_unit,'steer_reset_vehicle_identity')
  local a=observe(v)
  assert(a.driver_backend_kind==1 and a.driver_in_owned_partition and a.vehicle_in_owned_partition and a.vehicle_live==1,'steer_reset_owned_default_backend_required')
  assert(math.abs(a.input_steer)<=2 and math.abs(a.replicated_steer)<=2,'steer_reset_input_range')
  local dm=ptr(reference('driver_manager'));local vm=ptr(reference('vehicle_manager'))
  local input=ptr(vm+0x60)+a.vehicle_component_index*16
  local replica_root=ptr(vm+0x78)+a.vehicle_component_index*0x58
  local replica=replica_root+0x34;local pivot=replica_root+0x50
  local command=ptr(dm+0x58)+a.driver_component_index*48
  local b=observe(v)
  assert(a.driver_component_index==b.driver_component_index and a.vehicle_component_index==b.vehicle_component_index
   and a.driver_backend_kind==b.driver_backend_kind,'steer_reset_component_changed')
  return {vehicle=v,identity=entity:sub(1,20),data=b,input=input,replica=replica,pivot=pivot,command=command,
   input_before=get(input,4),replica_before=get(replica,4),pivot_before=get(pivot,1)}
 end
 local self={}
 function self:prepare(s)
  local d=assert(scope.layout(s))
  assert(d.tank and s.node==0 and s.owned and not s.active and s.player_count>=1 and s.player_count<=4 and s.peer_count==s.player_count,'steer_reset_actual_owned_tank_driver_required')
  -- A seated, locally owned tank driver can already have an inactive backend
  -- during native inhibition. The exit call is idempotent; ownership/identity
  -- guards and the required post-exit inactive/neutral state remain mandatory.
  local before=locate(s)
  assert(before.data.driver_active==0 or before.data.driver_active==1,'steer_reset_invalid_driver_active')
  emit({event='tank_steer_reset_preflight',collection=s.collection,vehicle=s.vehicle,data=before.data,read_only=true})
  local used=false
  return function()
   assert(not used,'steer_reset_single_use');used=true
   local fresh=locate(s)
   assert(fresh.identity==before.identity and fresh.input==before.input and fresh.replica==before.replica and fresh.pivot==before.pivot and fresh.command==before.command,'steer_reset_storage_changed')
   assert(fresh.data.driver_active==0 and fresh.data.driver_command_steer==0,'steer_reset_native_exit_and_upstream_neutral_required')
   local zero=string.rep('\0',4)
   emit({event='tank_steer_reset_invoking',collection=s.collection,vehicle=s.vehicle,data=fresh.data,
    fields={'vehicle_input_steer','replicated_steer_history','native_pivot_mode'},physics_velocity_write=false})
   -- Existing api.replace is compare-before-write, not a cross-field atomic
   -- transaction. Refuse drift; any partial failure stops the experiment.
   -- The native tick can generate new steer/brake while +50 remains set,
   -- even with no driver command. Disable that latch before clearing steer.
   assert(api.replace(fresh.pivot,fresh.pivot_before,'\0'),'steer_reset_pivot_changed')
   if not api.replace(fresh.input,fresh.input_before,zero)then
    local restored=api.replace(fresh.pivot,'\0',fresh.pivot_before)
    emit({event='tank_steer_reset_partial_failure',pivot_restored=restored})
    error('steer_reset_input_changed')
   end
   if not api.replace(fresh.replica,fresh.replica_before,zero)then
    local restored=api.replace(fresh.input,zero,fresh.input_before)
    local pivot_restored=api.replace(fresh.pivot,'\0',fresh.pivot_before)
    emit({event='tank_steer_reset_partial_failure',input_restored=restored,pivot_restored=pivot_restored})
    error('steer_reset_history_changed')
   end
   local after=locate(s)
   assert(after.identity==fresh.identity and after.input==fresh.input and after.replica==fresh.replica and after.pivot==fresh.pivot
    and after.data.input_steer==0 and after.data.replicated_steer==0 and after.data.replicated_pivot_mode==0,'steer_reset_readback_failed')
   emit({event='tank_steer_reset_returned',collection=s.collection,vehicle=s.vehicle,data=after.data,
    physics_velocity_write=false,live_rotation_not_confirmed=true})
  end
 end
 return self
end
