-- Select only the two vehicle pose layers. All other layers are preserved.
-- IDs/hashes come from this build's avatar state machine, not guessed names.
return function(api,profile)
 local ffi=api.ffi
 local exe=assert(api.module('helldivers2.exe'),'Missing engine module')
 local function bind(name,ctype)
  local p=assert(profile.engine_functions[name])
  assert(api.read(exe+p.rva,#p.bytes)==p.bytes,'Engine signature mismatch: '..name)
  return ffi.cast(ctype,exe+p.rva)
 end
 local unit=bind('unit','void *(*)(uint32_t)')
 local set_states=bind('animation_set_states','void (*)(uint32_t,const int32_t *)')
 local get_states=bind('animation_get_states','void *(*)(int32_t *,uint32_t)')
 local getter=profile.engine_functions.animation_component
 if not profile.animation.runtime_vtable then
  assert(api.read(exe+getter.rva,#getter.bytes)==getter.bytes,'Animation component signature mismatch')
 end
 local enqueue=profile.engine_functions.animation_event_enqueue
 assert(api.read(exe+enqueue.rva,#enqueue.bytes)==enqueue.bytes,'Animation queue signature mismatch')
 local layout=profile.animation
 local targets={m102={'front_left','front_right','back_left','back_right','frv_gunner'},
  m103={'front_left','front_right','back_left','back_right'},
  m104={'front_left','front_right','frv_gunner'},
  bastion={'tank_top','tank_gunner','tank_top','tank_top'},
  maelstrom={'tank_top','tank_gunner','tank_top','tank_top'}}
 local p={}
 local function read(address,n)
  local b=api.read(address,n);assert(b and #b==n,'Unreadable animation state');return b
 end
 local function ptr(address)return assert(api.pointer(read(address,8)),'Invalid animation pointer') end
 local function u32(b,o)
  local a,c,d,e=b:byte(o+1,o+4);assert(e);return a+c*256+d*65536+e*16777216
 end
 local function offset(n)assert(n>=0 and n<0x2000000,'Animation offset exceeds bound');return n end
 function p.check(s)
  assert(targets[s.vehicle],'No direct pose profile')
  local object=unit(s.avatar_unit);assert(object~=nil,'Avatar engine unit expired')
  object=ffi.cast('uint8_t *',object)
  local vtable=ptr(object)
  if layout.runtime_vtable then
   local function in_image(p,n,kind)
    local rva=tonumber(p-exe)
    for _,range in ipairs(profile.engine_ranges)do
     if rva>=range.rva and rva+n<=range.rva+range.size and range[kind] then return true end
    end
    return false
   end
   assert(in_image(vtable,0x1b8,'readable'),'Avatar vtable outside engine')
   local accessor=ptr(vtable+0x1b0)
   assert(in_image(accessor,#layout.getter_bytes,'execute') and read(accessor,#layout.getter_bytes)==layout.getter_bytes,'Animation accessor layout changed')
  else
   assert(vtable==exe+layout.unit_vtable,'Unsupported avatar unit class')
   assert(ptr(vtable+0x1b0)==exe+getter.rva,'Animation component accessor changed')
  end
  -- This getter is exactly mov rax,[rcx+178h];ret. Read it without an indirect call.
  local machine=ptr(object+layout.component_offset)
  local resource=ptr(machine+0x28);local header=read(resource,60)
  assert(u32(header,4)==layout.layers,'Avatar animation layer count changed')
  local groups=resource+offset(u32(header,8))
  local group_table=read(groups,4+layout.layers*4)
  assert(u32(group_table,0)==layout.layers,'Invalid animation group table')
  -- Validate bounds and every target state name before the first gameplay change.
  for _,pair in pairs(layout.states) do for _,state in ipairs(pair) do
   local layer=groups+offset(u32(group_table,4+state.layer*4))
   local row=read(layer,12+state.count*4)
   assert(u32(row,8)==state.count,'Avatar animation state count changed')
   local address=layer+offset(u32(row,12+state.index*4))
   assert(read(address,8)==state.hash,'Avatar animation state identity changed')
  end end
  if s.vehicle=='bastion' and layout.bastion_fall then
   for _,state in ipairs(layout.bastion_fall.states)do
    local layer=groups+offset(u32(group_table,4+state.layer*4))
    local row=read(layer,12+state.count*4)
    assert(u32(row,8)==state.count,'Bastion overlay state count changed')
    assert(read(layer+offset(u32(row,12+state.index*4)),8)==state.hash,'Bastion fall-state identity changed')
   end
  end
  local q=layout.queue;local world=ptr(object+q.world_offset)
  local count=u32(read(world+q.count_offset,4),0)
  assert(count<q.capacity-128,'Animation command queue near capacity')
  s.pose_context={object=object,world=world,start=count}
  return true
 end
 -- Clear only the observed Fall/Fall_Aim overlay. Never reset a seated/lean,
 -- reload, recoil or other action layer, and never enqueue an entry/exit clip.
 function p.fall_present(s)
  if s.vehicle~='bastion' or not layout.bastion_fall or s.transition~=43 or
     not s.profile or s.profile.roles[s.node+1]~=3 then return false end
  -- Validate the current engine unit/component/resource before any state
  -- getter call. An expired avatar handle must not reach an engine accessor.
  assert(p.check(s))
  local values=ffi.new('int32_t[33]');get_states(values,s.avatar_unit)
  assert(values[32]==layout.layers,'Bastion overlay layer count changed')
  return (values[8]==237 or values[8]==238)and
   (values[0]==123 and values[13]==102 or values[0]==122 and values[13]==99)
 end
 function p.clear_fall(s)
  if not p.fall_present(s)then return false end
  assert(p.check(s));local before=ffi.new('int32_t[33]');get_states(before,s.avatar_unit)
  assert(before[32]==layout.layers and (before[8]==237 or before[8]==238),'Bastion overlay changed before reset')
  -- These two layers have other outgoing transitions for the chosen native
  -- event. Captured seated values have no such transition; require them.
  assert(before[7]==3 and before[17]==18,'Bastion overlay auxiliary pose changed')
  local values=ffi.new('int32_t[33]');for i=0,31 do values[i]=-1 end
  values[8]=0;values[32]=9
  set_states(s.avatar_unit,values)
  local after=ffi.new('int32_t[33]');get_states(after,s.avatar_unit)
  assert(after[32]==layout.layers and after[8]==0,'Bastion overlay reset failed')
  for i=0,layout.layers-1 do if i~=8 then assert(before[i]==after[i],'Bastion overlay reset changed another layer')end end
  return true,tonumber(before[8])
 end
 function p.apply(s,target)
  local name=assert(targets[s.vehicle][target+1],'No target pose')
  local context=assert(s.pose_context,'Pose was not validated')
  local q=layout.queue
  assert(ptr(context.object+q.world_offset)==context.world,'Animation world changed')
  local finish=u32(read(context.world+q.count_offset,4),0)
  assert(finish>=context.start and finish<=context.start+128,'Animation command batch changed')
  local skipped=0
  for i=context.start,finish-1 do
   local address=context.world+q.records_offset+i*q.stride
   local row=read(address,q.stride)
   -- Only this avatar's NEW entry events from this synchronous switch batch.
   -- Keep all earlier commands, other units, non-entry events, and queue counts.
   if u32(row,0)==s.avatar_unit and u32(row,0x50)==3 and q.entry_events[u32(row,4)] then
    assert(read(address,q.stride)==row and api.replace(address+4,row:sub(5,8),q.end_event),'Entry event changed')
    skipped=skipped+1
   end
  end
  -- Unit.animation_event queues commands. Setting a pose alone is insufficient:
  -- the queued entry clip would otherwise overwrite it at the next world update.
  -- Its normal completion event has no outgoing link on any selected final pose.
  local values=ffi.new('int32_t[33]')
  for i=0,31 do values[i]=-1 end -- engine leaves these layers untouched
  for _,state in ipairs(layout.states[name]) do values[state.layer]=state.index end
  values[32]=14 -- highest selected layer is 13; no other layer is reset
  set_states(s.avatar_unit,values)
  local actual=ffi.new('int32_t[33]');get_states(actual,s.avatar_unit)
  assert(actual[32]==layout.layers,'Animation layer count changed during switch')
  for _,state in ipairs(layout.states[name]) do
   assert(actual[state.layer]==state.index,'Engine did not apply the requested seat pose')
  end
  -- Use the target role for the overlay check, not the pre-switch driver role.
  local target_s=setmetatable({node=target},{__index=s})
  local cleared,old=p.clear_fall(target_s)
  return 'pose_layers='..tonumber(actual[0])..','..tonumber(actual[13])..' entry_action_skipped=true entry_events_replaced='..skipped..
   ' bastion_fall_cleared='..tostring(cleared)..' old_overlay='..tostring(old)
 end
 return p
end
