-- Read-only, bounded observation of driver backend and exported vehicle input.
-- No game calls, writes, network sends, background scans or physics changes.
return function(api,game,p,compat)
 local ffi,bit=api.ffi,require('bit')
 local spec=assert(p.spin,'spin_missing_spec')
 local guards,reads;local self={}
 local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);assert(e,'spin_short_read');return a+c*256+d*65536+e*16777216 end
 local function hex(b)return(b:gsub('.',function(c)return string.format('%02x',c:byte())end))end
 local function get(a,n)
  reads=reads+1;assert(reads<=256 and n>0 and n<=65536,'spin_read_budget')
  local b=api.read(a,n);assert(b and #b==n,'spin_unreadable');return b
 end
 local function stable(a,n)local b=get(a,n);guards[#guards+1]={a,b};return b end
 local function pointer(a)return assert(api.pointer(stable(a,8)),'spin_pointer')end
 -- The cached compatibility resolver has already located these functions.
 -- Verify full masked bodies once; per-sample checks only read three native
 -- references plus the current object's bounded maps and fields.
 for name,d in pairs(spec.records)do
  local f=assert(p.functions[name],'spin_missing_function')
  local body=api.read(game+f.rva,d.length)
  assert(body and #body==d.length and compat.match(body,d.chunks),'spin_code_changed_'..name)
 end
 local active=assert(p.functions.tank_driver_active,'spin_missing_driver_active')
 assert(api.read(game+active.rva,#active.bytes)==active.bytes,'spin_active_code_changed')
 local function reference(name)
  local r=assert(spec.refs[name]);local f=assert(p.functions[r.record]);local at=game+f.rva+r.offset
  local b=stable(at,r.size);assert(hex(b:sub(1,3))==r.opcode_hex,'spin_reference_opcode')
  local displacement=u32(b,r.disp);if displacement>=2^31 then displacement=displacement-2^32 end
  return at+r.size+displacement
 end
 local function lowmul(a,b)return tonumber(ffi.cast('uint32_t',ffi.new('uint64_t',a)*ffi.new('uint64_t',b)))end
 local function index(manager,key,offset,count)
  local h=stable(manager+offset,20);local rows=assert(api.pointer(h),'spin_rows')
  local cap,empty,mult=u32(h,8),u32(h,12),u32(h,16)
  assert(cap>0 and cap<=16384 and bit.band(cap,cap-1)==0,'spin_map_capacity')
  local start=lowmul(key,mult)
  for i=0,math.min(cap,64)-1 do
   local b=stable(rows+bit.band(start+i,cap-1)*8,8)
   if u32(b,0)==key then local n=u32(b,4);assert(n<count and n<4096,'spin_component_index');return n end
   assert(u32(b,0)~=empty,'spin_component_missing')
  end
  error('spin_chain_budget')
 end
 local function identity(manager,offset,n,v)
  local entity=pointer(pointer(manager+offset)+n*8);local b=stable(entity,24)
  assert(u32(b,8)==v.id and u32(b,12)==v.unit and u32(b,16)==v.network_unit,'spin_entity_identity')
  assert(hex(b:sub(1,8):reverse())==v.resource and(bit.band(u32(b,20),1)~=0)==v.owned_local,'spin_entity_resource_or_authority')
  return entity
 end
 local function floats(b)
  local n=#b/4;local data=ffi.new('float[?]',n);ffi.copy(data,b,#b);local out={}
  for i=0,n-1 do local x=tonumber(data[i]);assert(x==x and x~=math.huge and x~=-math.huge,'spin_nonfinite');out[#out+1]=x end
  return out
 end
 function self:read_vehicle(v)
  reads=0;guards={}
  assert(v and(v.name=='m102'or v.name=='m103'or v.name=='m104'or v.name=='bastion'or v.name=='maelstrom')and
   v.id>0 and v.id<0xffffffff and v.unit>0 and v.network_unit>0 and type(v.resource)=='string'and #v.resource==16 and
   type(v.owned_local)=='boolean','spin_vehicle_scope')
  local driver_global=reference('driver_manager');assert(driver_global==game+p.driver.global,'spin_driver_reference_disagrees')
  local vehicle_global=reference('vehicle_manager');assert(vehicle_global==reference('vehicle_input_manager'),'spin_vehicle_references_disagree')
  local dm,vm=pointer(driver_global),pointer(vehicle_global)
  local driver_counts=stable(dm+0x24,12);local total,enabled,owned=u32(driver_counts,0),u32(driver_counts,4),u32(driver_counts,8)
  assert(total>0 and total<=4096 and enabled<=total and owned<=total,'spin_driver_count')
  local di=index(dm,v.id,0x38,total);local de=identity(dm,0x50,di,v)
  local vehicle_counts=stable(vm+0x30,8);local count,vehicle_owned=u32(vehicle_counts,0),u32(vehicle_counts,4)
  assert(count>0 and count<=4096 and vehicle_owned<=count,'spin_vehicle_count')
  local vi=index(vm,v.id,0x40,count);local ve=identity(vm,0x58,vi,v)
  assert(de==ve,'spin_component_owner_disagrees')
  local backend=stable(pointer(dm+0x60)+di*8,8)
  local current_kind=u32(backend,4);assert(current_kind<=3,'spin_backend_kind')
  local commands=get(pointer(dm+0x58)+di*48,48)
  local driver_active=get(pointer(dm+0x68)+di*0xd28+0xd18,1):byte(1)
  assert(driver_active==0 or driver_active==1,'spin_driver_active')
  local input=get(pointer(vm+0x60)+vi*16,16)
  local replica=get(pointer(vm+0x78)+vi*0x58+0x34,12)
  local live=get(pointer(vm+0x78)+vi*0x58+0x4f,1):byte(1)
  assert(live==0 or live==1,'spin_vehicle_live_flag')
  local cv,iv,rv=floats(commands:sub(1,44)),floats(input:sub(1,12)),floats(replica)
  for _,g in ipairs(guards)do assert(get(g[1],#g[2])==g[2],'spin_identity_changed_during_read')end
  return {read_only=true,driver_component_index=di,driver_total=total,driver_owned_count=owned,
   driver_in_owned_partition=di<owned,driver_backend_hex=hex(backend),driver_backend_word_00=u32(backend,0),driver_backend_kind=current_kind,
   driver_active=driver_active,driver_command_hex=hex(commands),driver_command_steer=cv[9],driver_command_throttle=cv[7],driver_command_brake=cv[8],
   driver_command_flags_offset_2c_to_2f={commands:byte(45,48)},vehicle_component_index=vi,
   vehicle_in_owned_partition=vi<vehicle_owned,vehicle_live=live,input_hex=hex(input),input_steer=iv[1],input_throttle=iv[2],input_brake=iv[3],
   input_flags_offset_0c_to_0f={input:byte(13,16)},replicated_controls_hex=hex(replica),replicated_steer=rv[1],replicated_throttle=rv[2],replicated_brake=rv[3],
   read_count=reads,caution='Bounded polling samples, not atomic physics or network capture; controls are not vehicle velocity.'}
 end
 return self
end
