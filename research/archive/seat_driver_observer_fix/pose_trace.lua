-- Passive driver derivative of 0.24.0; same original-forwarding native helper.
-- Two writable API slots; never edit physics arguments or suppress a call.
return function(api,game,p,compat,loader,helper,emit,test_library)
 local ffi,bit=require('ffi'),require('bit');local exe=assert(api.module('helldivers2.exe'))
 local spec=assert(p.pose_watch,'pose_watch_missing_contracts')
 for name,d in pairs(spec.records)do
  local base=d.module=='game'and game or exe;local fs=d.module=='game'and p.functions or p.engine_functions
  local f=assert(fs[name]);assert(compat.match(api.read(base+f.rva,d.length),d.chunks),'pose_watch_code_changed_'..name)
 end
 ffi.cdef[[
 typedef struct {void **slot;void *target;uint8_t head[32];} VSSM_Binding;
 typedef struct {void **slot;void *target;} VSSM_Guard;
 typedef struct {uint64_t sequence,tick,qpc,caller;uint32_t kind,thread,actor,valid,caller_module,epoch;float values[16];uint64_t reserved;} VSSM_Record;
 uint32_t VSSM_version(void);uint32_t VSSM_record_size(void);uint64_t VSSM_frequency(void);uint64_t VSSM_dropped(void);
 uint32_t VSSM_drain(VSSM_Record *,uint32_t);uint32_t VSSM_health(void);uint32_t VSSM_stop(void);uint32_t VSSM_disarm(void);
 int VSSM_start(const VSSM_Binding *,const VSSM_Guard *);int VSSM_arm(uint32_t,uint32_t,uint32_t);
 ]]
 local self={failed=false,epoch=0,until_at=0,seen=0,last_drop=0};local lib,buffer
 local function pointer(a)return assert(api.pointer(api.read(a,8)),'pose_watch_pointer')end
 local function reference()
  local r=assert(p.motion.refs.velocity_api);local f=assert(p.functions[r.record]);local at=game+f.rva+r.offset
  local b=assert(api.read(at,r.size));assert((b:sub(1,3):gsub('.',function(x)return string.format('%02x',x:byte())end))==r.opcode_hex,'pose_watch_reference')
  local n=0;for i=3,0,-1 do n=n*256+b:byte(r.disp+i+1)end;if n>=2^31 then n=n-2^32 end
  return at+r.size+n
 end
 local function fail(reason)
  self.failed=true;self.until_at=0;if lib then pcall(lib.VSSM_disarm)end
  emit({event='pose_call_gap',reason=tostring(reason),observation_only=true,original_calls_forwarded=true})
 end
 local function install()
  assert(not lib,'pose_watch_already_attempted')
  local global=reference();local actor_api=pointer(global)
  local bindings,guards=ffi.new('VSSM_Binding[2]'),ffi.new('VSSM_Guard[2]')
  local at={actor_api+0x70,actor_api+0xa0}
  local expected={exe+p.engine_functions.pose_actor_set.rva,exe+p.engine_functions.pose_velocity_set.rva}
  for i=1,2 do
   assert(api.in_image(exe,tonumber(at[i]-exe),8),'pose_watch_slot_outside_engine')
   assert(pointer(at[i])==expected[i],'pose_watch_api_target_changed')
   local page=api.describe(at[i]);assert(page.state==4096 and page.protection==4 and page.region_remaining>=8,'pose_watch_slot_not_plain_writable')
   bindings[i-1].slot=ffi.cast('void **',at[i]);bindings[i-1].target=ffi.cast('void *',expected[i])
   ffi.copy(bindings[i-1].head,assert(api.read(expected[i],32)),32)
  end
  local refs={global,actor_api+0xa8};local values={actor_api,exe+p.engine_functions.motion_actor_velocity.rva}
  for i=1,2 do
   assert(pointer(refs[i])==values[i],'pose_watch_api_root_changed')
   guards[i-1].slot=ffi.cast('void **',refs[i]);guards[i-1].target=ffi.cast('void *',values[i])
  end
  if test_library then lib=test_library else
   local bytes=helper.hex:gsub('..',function(x)return string.char(tonumber(x,16))end)
   assert(#bytes==helper.size and bytes:sub(1,2)=='MZ','pose_watch_helper_payload')
   local path=assert(loader.log_directory)..'/VSSMotionTrace-'..helper.sha256..'.dll'
   local f=io.open(path,'rb')
   if f then local old=f:read('*a');f:close();assert(old==bytes,'pose_watch_helper_file_mismatch')
   else local temp=path..'.tmp';f=assert(io.open(temp,'wb'));assert(f:write(bytes));assert(f:close());assert(os.rename(temp,path))end
   f=assert(io.open(path,'rb'));local actual=f:read('*a');f:close();assert(actual==bytes,'pose_watch_helper_verify')
   lib=ffi.load(path)
  end
  assert(lib.VSSM_version()==1 and lib.VSSM_record_size()==ffi.sizeof('VSSM_Record'),'pose_watch_ABI')
  buffer=ffi.new('VSSM_Record[256]')
  local code=tonumber(lib.VSSM_start(bindings,guards));assert(code==0,'pose_watch_install_failed_'..code)
  emit({event='pose_call_ready',helper_sha256=helper.sha256,frequency=tonumber(lib.VSSM_frequency()),
   strategy='two_writable_static_actor_api_slots; original_calls_forwarded',
   idle_path='helper_state_comparisons_only; no_C_FXSAVE_clock_or_game_memory_read',
   boundary='API_invocation_only; deferred_physical_callback_and_remote_process_not_captured'})
 end
 function self:arm_driver(v,s,a,physical)
  assert(not self.failed,'pose_watch_failed_restart_required')
  assert(v and v.name=='m102'and (v.resource=='cc21c7ffd3ebefb9'or v.resource=='e9cd1d0d118886af')and s and s.state=='mission'and
   s.player_count==2 and s.peer_count==2 and s.local_count==1 and a and a.is_local and a.owned_local and
   v.transition_type==26 and v.seat_count==5 and a.seat and a.seat.collection==v.id and
   a.seat.current==0 and a.seat.transitioning==0,
   'pose_watch_passive_driver_scope')
  assert(physical and physical.collection==v.id and physical.unit==v.unit and physical.actor_handle and physical.actor_handle~=0xffffffff,
   'pose_watch_chassis_identity')
  local ok,why=pcall(function()
   if not lib then install()end
   assert(lib.VSSM_health()==0,'pose_watch_bindings_changed')
   self.epoch=self.epoch+1
   assert(lib.VSSM_arm(physical.actor_handle,self.epoch,2000)==0,'pose_watch_arm_failed')
   self.until_at=api.now()+2
   self.needs_drain=true
   emit({event='pose_call_window',epoch=self.epoch,collection=v.id,unit=v.unit,actor_handle=physical.actor_handle,
    duration_ms=2000,observation_only=true})
  end)
  if not ok then fail(why);error(why,0)end
 end
 function self:disarm(reason)
  if not lib then return end
  lib.VSSM_disarm();self.until_at=0;self:update()
  emit({event='pose_call_disarmed',reason=reason,observation_only=true})
 end
 local function values(r,first,count)
  local out={};for i=first,first+count-1 do local n=tonumber(r.values[i]);assert(n==n and math.abs(n)<=1000000,'pose_watch_nonfinite_argument');out[#out+1]=n end;return out
 end
 function self:update()
  if not lib or self.failed or not self.needs_drain then return end
  local ok,why=pcall(function()
   if self.until_at>0 and api.now()>self.until_at then lib.VSSM_disarm();self.until_at=0 end
   if self.until_at==0 then return end
   assert(lib.VSSM_health()==0,'pose_watch_bindings_changed')
  end)
  if not ok then fail(why)end
  -- Always drain the last queued records, even after disarm/window expiry.
  local good,err=pcall(function()
   for _=1,8 do
    local n=tonumber(lib.VSSM_drain(buffer,256));assert(n>=0 and n<=256,'pose_watch_drain_count')
    for i=0,n-1 do
     local r=buffer[i];local kind,valid=tonumber(r.kind),tonumber(r.valid)
     local e={event='native_motion_api_call',kind=kind==0 and 'world_pose_request'or'velocity_request',
      sequence=tonumber(r.sequence),native_tick=tonumber(r.tick),qpc=tonumber(r.qpc),thread=tonumber(r.thread),
      epoch=tonumber(r.epoch),actor_handle=tonumber(r.actor),valid_mask=valid,
      caller_module=({'game.dll','helldivers2.exe'})[tonumber(r.caller_module)]or'unidentified',caller_rva=tonumber(r.caller),
      observation_only=true,original_call_forwarded=true,call_completion_not_observed=true}
     if kind==0 and bit.band(valid,1)~=0 then e.matrix=values(r,0,16)
     elseif kind==1 then
      if bit.band(valid,1)~=0 then e.linear_velocity=values(r,0,3)end
      if bit.band(valid,2)~=0 then e.angular_velocity=values(r,4,3)end
     end
     if e.caller_module=='game.dll'then
      local off=e.caller_rva-p.functions.pose_remote_tick.rva
      if off>=0 and off<spec.records.pose_remote_tick.length then
       e.native_path=off==0x487 and 'vehicle_remote_first_sample_pose'or'vehicle_remote_motion_update'
      end
     end
     emit(e);self.seen=self.seen+1
    end
    if n<256 then break end
   end
   local lost=tonumber(lib.VSSM_dropped());if lost~=self.last_drop then
    emit({event='pose_call_record_gap',dropped_total=lost});self.last_drop=lost
   end
  end)
  if not good then fail(err)end
  if self.until_at==0 then self.needs_drain=false end
 end
 function self:close(reason)
  if not lib then return end
  lib.VSSM_disarm();self.until_at=0;self:update()
  local code=tonumber(lib.VSSM_stop())
  emit({event='pose_call_stopped',reason=reason,restore_flags=code,events=self.seen,dropped_total=tonumber(lib.VSSM_dropped())})
  self.failed=true
 end
 return self
end
