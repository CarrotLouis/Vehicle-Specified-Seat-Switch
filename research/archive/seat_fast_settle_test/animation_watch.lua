-- Read-only, bounded observation around the already-tested seat transaction.
-- No added RPC, engine setter, memory write or native hook.
return function(api,p,emit)
 local ffi=api.ffi;local exe=assert(api.module('helldivers2.exe'))
 local function bind(name,signature)
  local f=assert(p.engine_functions[name]);assert(api.read(exe+f.rva,#f.bytes)==f.bytes,'animation_watch_signature_'..name)
  return ffi.cast(signature,exe+f.rva)
 end
 local unit=bind('unit','void *(*)(uint32_t)')
 local get=bind('animation_get_states','void *(*)(int32_t *,uint32_t)')
 local watch={active=false,failed=false};local tracked,context,deadline,frames,last,heartbeat,operation
 local function read(a,n)local b=api.read(a,n);assert(b and #b==n,'animation_watch_unreadable');return b end
 local function ptr(a)return assert(api.pointer(read(a,8)),'animation_watch_pointer')end
 local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);assert(e);return a+c*256+d*65536+e*16777216 end
 local function finish(reason)
  watch.active=false;emit({event='animation_watch_end',operation=operation,reason=reason,samples=frames})
 end
 local function sample(label)
  if not watch.active then return end
  local now=api.now()
  if now>=deadline or frames>=6000 then finish(now>=deadline and 'ten_seconds' or 'sample_cap');return end
  frames=frames+1
  -- Do not retain a callable avatar handle through despawn, respawn or reuse.
  local identity=read(tracked.avatar_address+8,8)
  assert(u32(identity,0)==tracked.avatar and u32(identity,4)==tracked.avatar_unit,'animation_watch_avatar_changed')
  local object=unit(tracked.avatar_unit)
  assert(object~=nil and ffi.cast('uint8_t *',object)==context.object,'animation_watch_unit_changed')
  local layout=p.animation;local q=layout.queue
  assert(ptr(context.object+layout.component_offset)==context.machine,'animation_watch_machine_changed')
  assert(ptr(context.machine+0x28)==context.resource,'animation_watch_resource_changed')
  assert(ptr(context.object+q.world_offset)==context.world,'animation_watch_world_changed')
  local values=ffi.new('int32_t[33]');get(values,tracked.avatar_unit)
  assert(values[32]==layout.layers,'animation_watch_layer_count')
  local states={};for i=0,layout.layers-1 do states[#states+1]=tonumber(values[i])end
  local count=u32(read(context.world+q.count_offset,4),0)
  assert(count<=q.capacity,'animation_watch_queue_capacity')
  local events={};local truncated=count>512
  -- Never scan an unbounded world queue each frame. Report missing coverage.
  if not truncated and count>0 then
   local rows=read(context.world+q.records_offset,count*q.stride)
   for i=0,count-1 do local off=i*q.stride
    if u32(rows,off)==tracked.avatar_unit and u32(rows,off+0x50)==3 then
     events[#events+1]={slot=i,hash=u32(rows,off+4)}
    end
   end
  end
  local key=table.concat(states,',')..'/'..tostring(truncated)
  for _,e in ipairs(events)do key=key..'/'..e.slot..':'..e.hash end
  if key~=last or now>=heartbeat or label~='before_update' and label~='after_update' then
   emit({event='animation_watch_sample',operation=operation,phase=label,sample=frames,avatar=tracked.avatar,
    unit=tracked.avatar_unit,source=tracked.node,states=states,queue_count=count,queue_events=events,queue_truncated=truncated})
   last=key;heartbeat=now+.25
  end
 end
 function watch:sample(label)
  local ok,err=pcall(sample,label)
  if not ok then self.active=false;self.failed=true;emit({event='animation_watch_gap',phase=label,reason=tostring(err),operation=operation})end
 end
 function watch:arm(s)
  assert(not self.failed,'animation_watch_previously_failed')
  local c=assert(s.pose_context);local machine=ptr(c.object+p.animation.component_offset)
  tracked=s;context={object=c.object,world=c.world,machine=machine,resource=ptr(machine+0x28)}
  frames=0;last=nil;heartbeat=0;operation=(operation or 0)+1;deadline=api.now()+10;self.active=true
  self:sample('prepared');assert(not self.failed,'animation_watch_prepare_failed')
 end
 function watch:close()if self.active then finish('shutdown')end end
 return watch
end
