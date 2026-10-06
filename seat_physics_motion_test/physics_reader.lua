-- Observe the SAME chassis actor selected by native game vehicle-speed code.
-- Only validated read APIs; no velocity setter, input reset or physics writes.
return function(api,game,p,compat)
 local ffi,bit=api.ffi,require('bit');local exe=assert(api.module('helldivers2.exe'))
 local spec=assert(p.motion);local reads,guards
 local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);assert(e,'motion_short_read');return a+c*256+d*65536+e*16777216 end
 local function get(a,n)reads=reads+1;assert(reads<=260,'motion_read_budget');local b=api.read(a,n);assert(b and #b==n,'motion_unreadable');return b end
 local function stable(a,n)local b=get(a,n);guards[#guards+1]={a,b};return b end
 local function ptr(a)return assert(api.pointer(stable(a,8)),'motion_invalid_pointer')end
 local function code(name)
  local d=assert(spec.records[name]);local base=d.module=='game'and game or exe
  local fs=d.module=='game'and p.functions or p.engine_functions
  local f=assert(fs[name]);assert(compat.match(get(base+f.rva,d.length),d.chunks),'motion_code_changed_'..name);return base+f.rva
 end
 local function reference(name)
  local r=assert(spec.refs[name]);local f=code(r.record);local b=get(f+r.offset,r.size)
  local prefix=(r.opcode_hex:gsub('..',function(x)return string.char(tonumber(x,16))end))
  assert(b:sub(1,3)==prefix,'motion_reference_changed')
  local n=u32(b,r.disp);if n>=2^31 then n=n-2^32 end
  return f+r.offset+r.size+n
 end
 local function unchanged()for _,g in ipairs(guards)do assert(get(g[1],#g[2])==g[2],'motion_identity_changed_during_read')end end
 local function lookup(h,key)
  local cap,empty,mult=u32(h,8),u32(h,12),u32(h,16)
  assert(cap>0 and cap<=1048576 and bit.band(cap,cap-1)==0,'motion_component_capacity')
  local rows=assert(api.pointer(h));local start=((key%cap)*(mult%cap))%cap
  for i=0,math.min(cap,64)-1 do
   local b=stable(rows+((start+i)%cap)*8,8);local id,index=u32(b,0),u32(b,4)
   if id==key then assert(index<262144,'motion_component_index');return index end
   if id==empty then break end
  end
  error('motion_body_component_missing',0)
 end
 local function hex(b)return (b:gsub('.',function(c)return string.format('%02x',c:byte())end))end
 local function engine_function(a)
  local rva=tonumber(a-exe);assert(rva>=0,'motion_virtual_outside_engine')
  local valid=false
  for _,r in ipairs(p.engine_ranges)do if r.execute and r.readable and rva>=r.rva and rva+32<=r.rva+r.size then valid=true;break end end
  assert(valid and get(a,32),'motion_virtual_not_executable');return rva
 end
 local function vec(a)
  local v={};for i=0,2 do local n=tonumber(a[i]);assert(n==n and math.abs(n)<=1000000,'motion_nonfinite_vector');v[i+1]=n end;return v
 end
 return {read_vehicle=function(_,v)
  reads=0;guards={}
  assert(v and v.name=='m102'and v.id>0 and v.unit>0 and v.unit<0x40000000,'motion_vehicle_scope')
  for name in pairs(spec.records)do code(name)end
  local manager=ptr(reference('component_manager'))
  -- Native callers pass game entity +8 (id), NOT engine unit or net unit.
  local index=lookup(stable(manager+0x40,20),v.id)
  local entity=ptr(ptr(manager+0x58)+index*8);local eb=stable(entity,24)
  assert(u32(eb,8)==v.id and u32(eb,12)==v.unit and u32(eb,16)==v.network_unit,'motion_entity_identity_mismatch')
  assert(hex(eb:sub(1,8):reverse())==v.resource,'motion_entity_resource_mismatch')
  local resource_key=eb:sub(1,8);local rm=ptr(reference('resource_manager'));local rows=ptr(rm+0xf12b80)
  local key=ffi.new('uint64_t[1]');ffi.copy(key,resource_key,8)
  local bucket=tonumber(key[0]%ffi.new('uint64_t',28));local profile
  for i=0,27 do
   local b=stable(rows+((bucket+i)%28)*16,12)
   if b:sub(1,8)==resource_key then local ri=u32(b,8);assert(ri<4096,'motion_resource_index');profile=rows+0x1c0+ri*0x1c8;break end
   if b:sub(1,8)==string.rep('\0',8)then break end
  end
  assert(profile,'motion_resource_profile_missing');local actor_name=u32(stable(profile+8,4),0)
  -- Reproduce the native unit component generation and actor-list checks.
  local units=ptr(reference('unit_components'));local ur=units+bit.band(v.unit,0x3fffff)*24
  local ub=stable(ur,24);local flags=u32(ub,4)
  assert(bit.band(flags,0x40000000)~=0 and bit.band(u32(ub,0),0x3fffffff)==v.unit,'motion_unit_generation_mismatch')
  local count=bit.band(flags,0x7f);assert(count>0 and count<=32,'motion_actor_count')
  local list=bit.band(flags,0x80000000)~=0 and ur+8 or assert(api.pointer(ub,8),'motion_actor_list_pointer')
  if bit.band(flags,0x80000000)~=0 then assert(count<=4,'motion_inline_actor_count')end
  local handles=stable(list,count*4);local pools=reference('actor_pools');local actor,ab,aid
  for i=0,count-1 do
   local handle=u32(handles,i*4)
   if handle~=0xffffffff then
    local world=bit.rshift(handle,30);local kind=bit.band(bit.rshift(handle,28),3)
    local pool=pools+(world*10+kind)*64;local pb=stable(pool,0x38)
    local slot=bit.band(handle,u32(pb,0x28));local cap=u32(pb,0x24);local packed=u32(pb,0x1c)
    assert(cap<=1048576,'motion_actor_pool_capacity')
    if slot<cap and bit.band(u32(pb,0x34),handle)~=0 then
     local stride=bit.band(packed,0xffff);local tag=bit.band(bit.rshift(packed,16),0xff);local off=bit.rshift(packed,24)
     assert(stride>=28 and stride<=1024 and tag+4<=stride and off+28<=stride,'motion_actor_pool_layout')
     local base=assert(api.pointer(pb));local at=base+slot*stride
     if u32(stable(at+tag,4),0)==handle then
      local rec=stable(at+off,28)
      if u32(rec,0xc)==v.unit and u32(rec,0x18)==actor_name then
       assert(not aid,'motion_duplicate_chassis_actor');actor=at+off;ab=rec;aid=handle
      end
     end
    end
   end
  end
  assert(aid,'motion_chassis_actor_missing')
  local lookup_api=ptr(reference('lookup_api'));assert(ptr(lookup_api+0x10)==code('motion_actor_lookup'),'motion_actor_api_changed')
  local velocity_api=ptr(reference('velocity_api'))
  assert(ptr(velocity_api+0xa8)==code('motion_actor_velocity'),'motion_velocity_api_changed')
  assert(ptr(velocity_api+0x50)==code('motion_actor_position'),'motion_position_api_changed')
  local world=bit.rshift(aid,30);local context=ptr(reference('physics_worlds')+world*0xb0)
  local vt=ptr(context);local methods={}
  for _,off in ipairs({0x70,0x88,0x98})do methods[tostring(off)]=engine_function(ptr(vt+off))end
  unchanged()
  local linear,angular,position=ffi.new('float[3]'),ffi.new('float[3]'),ffi.new('float[3]')
  local velocity=ffi.cast('void (*)(uint32_t,float *,float *)',code('motion_actor_velocity'))
  local locate=ffi.cast('void (*)(uint32_t,float *)',code('motion_actor_position'))
  velocity(aid,linear,angular);locate(aid,position)
  unchanged()
  local lv,av,pv=vec(linear),vec(angular),vec(position)
  local speed=math.sqrt(lv[1]^2+lv[2]^2+lv[3]^2)
  return {read_only=true,source='native_chassis_actor_velocity',collection=v.id,unit=v.unit,network_unit=v.network_unit,
   actor_handle=aid,actor_name_hash=actor_name,actor_flags=u32(ab,4),actor_aux=u32(ab,0x10),physics_body_id=u32(ab,0x14),world=world,
   body_identity_hex=hex(ab),component_index=index,body_api_methods=methods,linear_velocity=lv,angular_velocity=av,
   physical_position=pv,native_speed=speed,velocity_units='native_physics_units; not dashboard km/h',read_count=reads,
   remote_body_velocity_requires_position_comparison=not v.owned_local}
 end}
end
