-- Read-only observation of ONE unmodded teammate on the SAME Maelstrom.
-- No setters, authority requests, messages, hooks or full-process scans.
return function(api,p,pose,binding,emit)
 local ffi=api.ffi;local watch={};local tracked,previous,car_previous,local_previous,deadline,next_at,last,heartbeat,frames,context
 local failed_key;local get_states,read_pose;local last_poll=0
 local function read(a,n)local b=api.read(a,n);assert(b and #b==n,'remote_pose_unreadable');return b end
 local function ptr(a)return assert(api.pointer(read(a,8)),'remote_pose_pointer')end
 local function load_get()
  if get_states then return end
  local f=assert(p.engine_functions.animation_get_states)
  local exe=assert(api.module('helldivers2.exe'))
  assert(read(exe+f.rva,#f.bytes)==f.bytes,'remote_pose_get_states_changed')
  get_states=ffi.cast('void *(*)(int32_t *,uint32_t)',exe+f.rva)
 end
 local function key(a)
  local s=a.seat or{}
  return table.concat({a.id,a.unit,a.network_unit,s.collection or 0,s.current or -1,s.role or 0},':')
 end
 local function finish(reason)
  if tracked then emit({event='remote_pose_watch_end',avatar=tracked.id,reason=reason,samples=frames,read_only=true})end
  tracked=nil;context=nil
 end
 local function capture(a,vehicle)
  load_get()
  local binding_row=binding:observe_remote(a)
  assert(binding_row.stable,'remote_pose_binding_unstable')
  local identity=binding:entity(a.id)
  assert(identity.unit==a.unit and identity.network_unit==a.network_unit,'remote_pose_identity_changed_before_get')
  -- Existing pose.check only validates the current unit, component/resource,
  -- final-state identities and bounded world queue. It never changes states.
  if not context then
   local s={avatar=a.id,avatar_unit=a.unit,vehicle='maelstrom',transition=44,
    node=a.seat.current,profile={row=12,roles={1,2,3,3}}}
   read_pose=read_pose or pose(api,p)
   assert(read_pose.check(s),'remote_pose_avatar_invalid')
   local c=assert(s.pose_context);local machine=ptr(c.object+p.animation.component_offset)
   context={object=c.object,machine=machine,resource=ptr(machine+0x28),vtable=read(c.object,8)}
  end
  local c=context;local machine,resource=c.machine,c.resource
  assert(read(c.object,8)==c.vtable and ptr(c.object+p.animation.component_offset)==machine
   and ptr(machine+0x28)==resource,'remote_pose_component_changed_before_get')
  local values=ffi.new('int32_t[33]');get_states(values,a.unit)
  assert(values[32]==p.animation.layers,'remote_pose_layers_changed')
  local states={};for i=0,p.animation.layers-1 do states[#states+1]=tonumber(values[i])end
  local fresh=binding:entity(a.id)
  assert(fresh.unit==a.unit and fresh.network_unit==a.network_unit
   and ptr(c.object+p.animation.component_offset)==machine and ptr(machine+0x28)==resource,'remote_pose_identity_changed')
  return {avatar=a.id,unit=a.unit,network_unit=a.network_unit,seat=a.seat,
   vehicle_owned_local=vehicle.owned_local,collection=vehicle.id,states=states,
   rotation_flag=binding_row.rotation_flag,rotation_component_found=binding_row.rotation_component_found,
   slots=binding_row.slots,input_flags_low=a.input_flags_low,input_flags_high=a.input_flags_high,
   read_only=true,remote_avatar_modified=false}
 end
 function watch:update(sample)
  local now=api.now();if now<last_poll+.095 then return end;last_poll=now
  local local_avatar,friend,vehicle
  if sample and type(sample.avatars)=='table'and #sample.avatars==2 then
   for _,a in ipairs(sample.avatars)do if a.is_local then local_avatar=a else friend=a end end
   if local_avatar and friend then
    local own_seat=local_avatar.seat or{}
    for _,v in ipairs(sample.vehicles or{})do if v.id==own_seat.collection and v.name=='maelstrom'then vehicle=v;break end end
   end
  end
  if not vehicle or not friend then finish('context_left');previous=nil;car_previous=nil;local_previous=nil;failed_key=nil;return end
  local current=key(friend);local car_key=table.concat({vehicle.id,vehicle.unit,vehicle.network_unit,tostring(vehicle.owned_local)},':')
  local local_key=key(local_avatar)
  if current~=previous or car_key~=car_previous or local_key~=local_previous then
   emit({event='remote_pose_transition',avatar=friend.id,unit=friend.unit,network_unit=friend.network_unit,
    previous=previous,current=current,collection=vehicle.id,owned_local=vehicle.owned_local,seat=friend.seat,
    installer_avatar=local_avatar.id,installer_seat=local_avatar.seat,read_only=true})
   previous=current;car_previous=car_key;local_previous=local_key
   if failed_key~=current then
    tracked={id=friend.id,unit=friend.unit,network_unit=friend.network_unit};deadline=now+12;next_at=now;frames=0;last=nil;heartbeat=0;context=nil
   end
  end
  if not tracked then return end
  if now>=deadline or frames>=125 then finish('window_complete');return end
  if now<next_at then return end;next_at=now+.1
  if friend.id~=tracked.id or friend.unit~=tracked.unit or friend.network_unit~=tracked.network_unit then finish('avatar_changed');return end
  -- No engine accessor for an outside/unfinished seat; await vanilla entry.
  local seat=friend.seat or{}
  if seat.collection~=vehicle.id or (seat.current~=0 and seat.current~=1 and seat.current~=2 and seat.current~=3)
   or seat.transitioning~=0 or seat.role==0 then return end
  local ok,data=pcall(capture,friend,vehicle)
  if not ok then failed_key=current;finish('read_gap');emit({event='remote_pose_watch_gap',reason=tostring(data),read_only=true});return end
  frames=frames+1
  local fingerprint=table.concat(data.states,',')..'/'..tostring(data.rotation_flag)..'/'..tostring(seat.active_passenger)
  for _,s in ipairs(data.slots)do fingerprint=fingerprint..'/'..s.channel..':'..s.weapon..':'..s.secondary end
  if fingerprint~=last or now>=heartbeat then
   emit({event='remote_pose_watch_sample',data=data,sample=frames,read_only=true})
   last=fingerprint;heartbeat=now+.5
  end
 end
 function watch:close()finish('shutdown')end
 return watch
end
