-- Only bounded reads of the current M102, its schema and handoff properties.
-- Does not call game code, change state, restore speed or emit network traffic.
return function(api,game,p,compat)
 local ffi,bit=api.ffi,require('bit')
 local exe=assert(api.module('helldivers2.exe'))
 local self={};local guards,reads;local schema_cache;local code_verified=false
 local target={
  [0x791943f0]={name='motion_peer',kind=9,size=8,offset=0},
  [0x91f98cec]={name='motion_time',kind=2,size=4,offset=8},
  [0x7615f45d]={name='linear_velocity',kind=3,size=12,offset=0xc},
  [0xeeb1225e]={name='position',kind=3,size=12,offset=0x18},
  [0xcca43d10]={name='rotation',kind=4,size=16,offset=0x24},
  [0x5a8871e3]={name='steering',kind=2,size=4,offset=0x34},
 }
 local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);assert(e,'handoff_short_read');return a+c*256+d*65536+e*16777216 end
 local function hex(b)return(b:gsub('.',function(x)return string.format('%02x',x:byte())end))end
 local function get(a,n)
  reads=reads+1;self.last_read.read_count=reads
  assert(reads<=2048 and n>0 and n<=65536,'handoff_read_budget')
  local b=api.read(a,n);assert(b and #b==n,'handoff_unreadable');return b
 end
 local function stable(a,n)local b=get(a,n);guards[#guards+1]={a,b};return b end
 local function pointer(a)return assert(api.pointer(stable(a,8)),'handoff_invalid_pointer')end
 local function optional_pointer(a)
  local b=stable(a,8);if b==string.rep('\0',8)then return nil end
  return assert(api.pointer(b),'handoff_invalid_optional_pointer')
 end
 local function match(name)
  local d=assert(p.handoff.records[name]);local base=d.module=='game'and game or exe
  local f=(d.module=='game'and p.functions or p.engine_functions)[name]
  assert(f and compat.match(get(base+f.rva,d.length),d.chunks),'handoff_code_changed_'..name)
  return base+f.rva
 end
 local function component_reference()
  local r=p.handoff.refs.component_manager
  local a=match(r.record)+r.offset;local b=get(a,r.size)
  assert(hex(b:sub(1,3))==r.opcode_hex,'handoff_manager_reference_changed')
  local d=u32(b,r.disp);if d>=2^31 then d=d-2^32 end
  return a+r.size+d
 end
 local function lowmul(a,b)return tonumber(ffi.cast('uint32_t',ffi.new('uint64_t',a)*ffi.new('uint64_t',b)))end
 local function entity_index(manager,key)
  local h=stable(manager+0x40,20);local rows=assert(api.pointer(h),'handoff_entity_rows')
  local cap,empty,mult=u32(h,8),u32(h,12),u32(h,16)
  assert(cap>0 and cap<=1048576 and bit.band(cap,cap-1)==0,'handoff_entity_capacity')
  local start=lowmul(key,mult)
  for i=0,math.min(cap,64)-1 do
   local at=rows+bit.band(start+i,cap-1)*8;local b=stable(at,8)
   if u32(b,0)==key then
    local n=u32(b,4);assert(n<65536,'handoff_component_index');return n
   end
   assert(u32(b,0)~=empty,'handoff_component_missing')
  end
  error('handoff_component_chain_budget')
 end
 local function engine_record(engine,unit)
  local h=stable(engine+0x640,32);local rows=assert(api.pointer(h,8),'handoff_network_rows')
  local total,count,buckets=u32(h,0),u32(h,24),u32(h,28)
  assert(buckets>0 and buckets<=total and total<=262144 and count>0 and count<=total,'handoff_network_capacity')
  local a=lowmul(unit,0x5bd1e995);a=bit.bxor(a,bit.rshift(a,24));if a<0 then a=a+2^32 end
  local index=lowmul(a,0x5bd1e995)%buckets;local seen={}
  for _=1,32 do
   assert(index<total and not seen[index],'handoff_network_chain');seen[index]=true
   local at=rows+index*0x248;local b=stable(at,40);local next_=u32(stable(at+0x240,4),0)
   assert(next_~=0xfffffffe,'handoff_network_missing')
   if u32(b,0)==unit then
    local tail=stable(at+0x23a,4)
    self.last_read.network_record_hex=hex(b)
    return {at=at,payload=at+8,kind=u32(b,12),owner=b:sub(17,24),
     raw=assert(api.pointer(b,32),'handoff_raw_property_pointer'),serial=tail:byte(1)+tail:byte(2)*256}
   end
   assert(next_~=0x7fffffff,'handoff_network_missing');index=next_
  end
  error('handoff_network_chain_budget')
 end
 local primitive={[0]=4,[1]=4,[2]=4,[3]=12,[4]=16,[5]=0,[6]=4,[7]=8,[8]=8,[9]=8,[11]=12,[12]=8}
 local function schema(manager,kind,context)
  assert(kind<4096,'handoff_type_index_budget')
  local types=pointer(manager+0x78);local global=pointer(manager+0x18)
  local descriptor=types+kind*80;local db=stable(descriptor,80)
  local count=u32(db,0x18);assert(count>0 and count<=512,'handoff_property_count')
  self.last_read.descriptor_hex=hex(db);self.last_read.property_count=count
  self.last_read.property_type_index=kind
  local indices=assert(api.pointer(db,0x20),'handoff_property_indices')
  local hashes=assert(api.pointer(db,0x38),'handoff_property_hashes')
  local ib,hb=stable(indices,count*4),stable(hashes,count*4)
  local key=context..'/'..tostring(manager)..'/'..kind..'/'..tostring(descriptor)
  local previous=schema_cache
  if previous and previous.key==key and previous.db==db and previous.ib==ib and previous.hb==hb then
   for _,r in ipairs(previous.type_records)do
    assert(stable(r.address,24)==r.bytes,'handoff_cached_type_changed')
   end
   self.last_read.schema_cache_hit=true;return previous
  end
  local type_records,type_seen={},{}
  local function type_record(index)
   assert(index<16384,'handoff_property_type_budget')
   if not type_seen[index]then
    local address=global+index*24;local bytes=stable(address,24)
    type_seen[index]=bytes;type_records[#type_records+1]={address=address,bytes=bytes}
   end
   return type_seen[index]
  end
  local function size(index,depth,path)
   assert(depth<=8 and not path[index],'handoff_nested_type_cycle_or_depth')
   local b=type_record(index);local k=b:byte(13)
   if primitive[k]then return primitive[k]end
   assert(k==10,'handoff_unknown_property_kind')
   path[index]=true;local child,n=u32(b,0x10),u32(b,0x14)
   assert(n<=4096,'handoff_array_count_budget')
   local length=4+size(child,depth+1,path)*n;path[index]=nil
   assert(length<=65536,'handoff_array_size_budget');return length
  end
  local out={key=key,db=db,ib=ib,hb=hb,descriptor=descriptor,manager=manager,count=count,fields={},type_records=type_records}
  local offset,found=0,0
  for i=0,count-1 do
   local ti,hash=u32(ib,i*4),u32(hb,i*4);local b=type_record(ti);local length=size(ti,0,{})
   if target[hash]then
    local expected=target[hash]
    assert(not out.fields[expected.name],'handoff_duplicate_motion_property')
    assert(b:byte(13)==expected.kind and length==expected.size,'handoff_motion_property_schema_changed')
    out.fields[expected.name]={index=i,hash=hash,kind=expected.kind,size=length,offset=offset,component_offset=expected.offset,interpolated=b:byte(15)~=0}
    found=found+1
   end
   offset=offset+length;assert(offset<=65536,'handoff_property_buffer_budget')
  end
  assert(found==6,'handoff_motion_properties_missing');out.total_bytes=offset;schema_cache=out
  self.last_read.schema_cache_hit=false;return out
 end
 local function decode(bytes,field)
  local out={hex=hex(bytes)}
  if field.kind==9 then return out end
  local n=field.size/4;local value=ffi.new('float[?]',n);ffi.copy(value,bytes,#bytes)
  out.values={}
  for i=0,n-1 do local x=tonumber(value[i]);assert(x==x and math.abs(x)<1e12,'handoff_nonfinite_property');out.values[#out.values+1]=x end
  return out
 end
 function self:read_vehicle(v,o)
  reads=0;guards={};self.last_read={stage='start',read_only=true}
  assert(v and v.name=='m102'and v.id>0 and v.unit>0 and v.network_unit>0 and v.network_unit<0x7fff,'handoff_vehicle_scope')
  assert(o and o.vehicle.id==v.id and o.vehicle.unit==v.unit and o.vehicle.network_unit==v.network_unit and o.vehicle.resource==v.resource,'handoff_observation_identity')
  -- These layout/serialization witnesses are read-only contracts. Check the
  -- full set once after startup compatibility, retain the exact component
  -- getter check on each read, and revalidate all mutable identities/schema.
  -- No repeated long code reads, native calls or memory search while sampling.
  if not code_verified then for name in pairs(p.handoff.records)do match(name)end;code_verified=true end
  local session=pointer(game+p.globals.session);assert(session==o.session,'handoff_session_changed')
  local engine=pointer(session+0xb390);assert(engine==o.engine,'handoff_engine_changed')
  assert(stable(engine+0x20,8)==o.selfpeer and stable(engine+0x130,8)==o.coordinator,'handoff_peer_context_changed')
  local manager=pointer(component_reference());local index=entity_index(manager,v.id)
  local count=u32(stable(manager+0x30,8),0);assert(index<count and count<=65536,'handoff_component_count')
  local entity=pointer(pointer(manager+0x58)+index*8);local eb=stable(entity,24)
  assert(u32(eb,8)==v.id and u32(eb,12)==v.unit and u32(eb,16)==v.network_unit,'handoff_vehicle_entity_changed')
  assert(hex(eb:sub(1,8):reverse())==v.resource,'handoff_vehicle_resource_changed')
  local network=pointer(manager+0x78)+index*0x58
  local state=get(network,0x58)
  local input=get(pointer(manager+0x60)+index*16,16)
  local runtime=pointer(manager+0x70)+index*0x670
  local clock=get(runtime+0x3c,0x10);local mode=get(runtime+0x614,0x10)
  self.last_read.stage='network_properties'
  local record=engine_record(engine,v.network_unit);local sm=pointer(engine+0x18)
  local desc=schema(sm,record.kind,o.context)
  local cached=optional_pointer(record.payload+0x228)
  self.last_read.interpolation_cache_present=cached~=nil
  local cache_values,cache_offsets
  if cached then
   self.last_read.cache_header_hex=hex(get(cached,0x30))
   assert(pointer(cached)==sm and pointer(cached+8)==desc.descriptor,'handoff_interpolation_schema_mismatch')
   cache_values=pointer(cached+0x18);cache_offsets=pointer(cached+0x28)
  end
  local out={read_only=true,collection=v.id,unit=v.unit,network_unit=v.network_unit,
   entity_identity_hex=hex(eb),engine_owner_hex=hex(record.owner),engine_serial=record.serial,
   property_type_index=record.kind,property_count=desc.count,property_buffer_bytes=desc.total_bytes,
   interpolation_cache_present=cached~=nil,component_index=index,component_clock_hex=hex(clock),
   full_contract_witnesses_checked_once=true,component_getter_revalidated=true,
   component_mode_hex=hex(mode),component_input_hex=hex(input),component_input=decode(input:sub(1,12),{kind=3,size=12}),
   component_input_flag=input:byte(13),component_state_hex=hex(state),properties={},read_count=0,
   caution='Replica velocity contains vx/vy/0; compare native body velocity and position. These are polling observations, not packet capture.'}
  for name,f in pairs(desc.fields)do
   local row={index=f.index,hash=f.hash,kind=f.kind,offset=f.offset,interpolated=f.interpolated,
    component=decode(state:sub(f.component_offset+1,f.component_offset+f.size),f),
    raw_engine=decode(get(record.raw+f.offset,f.size),f),serializer_source='raw_engine'}
   if f.interpolated and cached then
    assert(f.kind<=4,'handoff_interpolation_kind')
    local cb=stable(cache_offsets+f.index*12,12);local offset=u32(cb,4)
    assert(offset<=65536,'handoff_interpolation_offset_budget')
    row.cache_offset=offset;row.cached=decode(get(cache_values+offset+8,f.size),f)
    row.serializer_source='interpolation_cache'
   end
   out.properties[name]=row
  end
  for _,g in ipairs(guards)do assert(get(g[1],#g[2])==g[2],'handoff_identity_or_schema_changed_during_read')end
  out.read_count=reads;out.schema_cache_hit=self.last_read.schema_cache_hit;self.last_read.stage='ready'
  return out
 end
 return self
end
