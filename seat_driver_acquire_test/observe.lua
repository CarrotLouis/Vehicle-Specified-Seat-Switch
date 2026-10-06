-- Bounded ownership observation. No engine query calls and no writes.
local ffi,bit=require('ffi'),require('bit')
local M={}
local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);assert(e,'short_authority_read');return a+c*256+d*65536+e*16777216 end
local function u16(b,o)local a,c=b:byte(o+1,o+2);return a+c*256 end
local function lowmul(a,b)return tonumber(ffi.cast('uint32_t',ffi.new('uint64_t',a)*ffi.new('uint64_t',b)))end
local function uint64(b)local v=ffi.new('uint64_t[1]');ffi.copy(v,b,8);return v[0]end
function M.new(api,game,p,spec,compat,reader,trace)
 local exe=assert(api.module('helldivers2.exe'),'authority_no_engine')
 local self={};local reads,guards
 local function location(address)
  if not api.describe then return {}end
  local d=api.describe(address)
  return {module=d.module,rva=d.rva,executable=d.executable,readable=d.readable}
 end
 local function get(a,n)
  reads=reads+1;assert(reads<=360,'authority_read_budget');local b=api.read(a,n)
  assert(b and #b==n,'authority_unreadable');return b
 end
 local function stable(a,n)local b=get(a,n);guards[#guards+1]={a,b};return b end
 local function pointer(a)return assert(api.pointer(stable(a,8)),'authority_invalid_pointer')end
 local function relative(base,rva,opcode)
  local b=get(base+rva,7);assert(b:sub(1,3)==opcode,'authority_reference_changed')
  local d=u32(b,3);if d>=2147483648 then d=d-4294967296 end
  return base+rva+7+d
 end
 local function verified(name)
  local d=assert(spec.records[name]);local base=d.module=='game'and game or exe
  local f=assert((d.module=='game'and p.functions or p.engine_functions)[name])
  assert(compat.match(get(base+f.rva,d.length),d.chunks),'authority_code_changed_'..name)
  return base+f.rva
 end
 local function check_code()
  for name in pairs(spec.records)do if name:sub(1,10)=='authority_'then verified(name)end end
  return verified('trace_send')
 end
 local function record(engine,unit,kind)
  assert(unit>0 and unit<0x7fff,'authority_invalid_network_unit')
  local evidence={kind=kind,network_unit=unit,nodes={}}
  self.evidence.lookups[#self.evidence.lookups+1]=evidence
  local first_guard=#guards+1
  -- The hash bucket region is followed by additional collision slots.
  -- Native insert/grow use +640 for total initialized rows, +65c only for DIV.
  local h=stable(engine+0x640,32);local rows=assert(api.pointer(h,8),'authority_entity_rows')
  local total,count,buckets=u32(h,0),u32(h,24),u32(h,28)
  evidence.count=count;evidence.total_slots=total;evidence.bucket_count=buckets
  assert(buckets>0 and buckets<=total and total<=262144 and count>0 and count<=total,'authority_entity_capacity')
  local a=lowmul(unit,0x5bd1e995);a=bit.bxor(a,bit.rshift(a,24));if a<0 then a=a+4294967296 end
  local index=lowmul(a,0x5bd1e995)%buckets;local seen={}
  evidence.bucket=index
  local function walk()
  for _=1,32 do
   evidence.current_index=index
   assert(index>=0 and index<total,'authority_entity_index_out_of_range')
   assert(not seen[index],'authority_entity_chain_cycle');seen[index]=true
   local at=rows+index*0x248;local b=stable(at,24);local next_=u32(stable(at+0x240,4),0)
   evidence.nodes[#evidence.nodes+1]={index=index,key=u32(b,0),next_index=next_}
   assert(next_~=0xfffffffe,'authority_entity_missing')
   -- table_insert returns row+8 (value payload), so payload+232 is row+23a.
   if u32(b,0)==unit then local tail=stable(at+0x23a,4);return {owner=b:sub(17,24),record_word0=u32(b,8),record_word1=u32(b,12),serial=u16(tail,0),flags={tail:byte(3,4)}}end
   assert(next_~=0x7fffffff,'authority_entity_missing');index=next_
  end
  error('authority_entity_chain_budget')
  end
  local ok,value=pcall(walk)
  -- Keep failed-read evidence distinguishable from a concurrent table update.
  local same=true
  for i=first_guard,#guards do local g=guards[i];if get(g[1],#g[2])~=g[2]then same=false end end
  evidence.unchanged_after_read=same
  if not same then error('authority_entity_table_changed_during_read')end
  if not ok then error(value,0)end
  evidence.found=true
  return value
 end
 local function busy(vehicle)
  self.evidence.stage='busy_lookup'
  local entities=pointer(game+p.globals.entities);local engine=pointer(entities+8)
  local h=stable(engine+0xb020,20);local cap,empty,mult=u32(h,8),u32(h,12),u32(h,16)
  local detail={key_kind='network_unit',key=vehicle.network_unit,capacity=cap,empty=empty,multiplier=mult,nodes={}}
  self.evidence.busy_lookup=detail
  assert(cap>0 and cap<=1048576 and bit.band(cap,cap-1)==0,'authority_busy_map')
  -- Native seat-switch caller loads entity record +10h (network_unit), not +Ch.
  local rows=assert(api.pointer(h),'authority_busy_rows');local start=lowmul(vehicle.network_unit,mult)
  for i=0,math.min(cap,64)-1 do
   local bucket=bit.band(start+i,cap-1)
   local b=stable(rows+bucket*8,8);local id,index=u32(b,0),u32(b,4)
   detail.nodes[#detail.nodes+1]={bucket=bucket,key=id,index=index}
   assert(id~=empty or id==vehicle.network_unit,'authority_busy_entity_missing')
   if id==vehicle.network_unit then
    assert(index<32768,'authority_busy_index');local value=stable(engine+0x201c+index,1):byte()
    detail.found=true;detail.value=value;return value~=0
   end
  end
  error('authority_busy_map_budget')
 end
 function self:capture(s,tracked,need_avatars)
  reads=0;guards={};self.evidence=nil
  if not s or s.state~='mission' then return nil,'not_in_mission'end
  local vehicle
  if tracked then
   for _,v in ipairs(s.vehicles)do if v.id==tracked.id and v.unit==tracked.unit and v.network_unit==tracked.network_unit and v.resource==tracked.resource then vehicle=v;break end end
  else
   for _,a in ipairs(s.avatars)do if a.is_local and a.seat then
    for _,v in ipairs(s.vehicles)do if v.id==a.seat.collection and v.name=='m102' then vehicle=v;break end end
   end end
  end
  if not vehicle then return nil,'vehicle_not_observed'end
  check_code()
  local session=pointer(game+p.globals.session);local engine=pointer(session+0xb390)
  local root=relative(game,p.functions.authority_apply.rva+0xd,'\72\139\5')
  local services=pointer(root);local entity_api=pointer(services+0x40)
  self.evidence={stage='entity_api',slots={}}
  for offset,name in pairs({[0x98]='api_exists',[0x138]='api_request',[0x140]='api_transfer',[0x160]='api_owner'})do
   local actual=pointer(entity_api+offset)
   self.evidence.slots[name]=location(actual)
   assert(actual==exe+p.engine_functions['authority_'..name].rva,'authority_api_slot_changed_'..name)
  end
  local vt=relative(exe,p.engine_functions.authority_constructor.rva+0x12,'\72\141\5')
  local actual_vt=pointer(engine);self.evidence.stage='concrete_session'
  self.evidence.expected_vtable=location(vt);self.evidence.actual_vtable=location(actual_vt)
  assert(actual_vt==vt,'authority_concrete_session_unrecognized')
  for offset,name in pairs({[0xf8]='exists',[0x110]='transfer',[0x128]='request',[0x178]='owner'})do
   assert(pointer(vt+offset)==exe+p.engine_functions['authority_'..name].rva,'authority_virtual_slot_changed')
  end
  assert(get(pointer(vt+0x68),5)=='\72\139\65\32\195','authority_local_peer_getter_changed')
  assert(get(pointer(vt+0x98),8)=='\72\139\129\48\1\0\0\195','authority_coordinator_getter_changed')
  local selfpeer=stable(engine+0x20,8);local coordinator=stable(engine+0x130,8)
  self.evidence.stage='peer_identity'
  assert(selfpeer~=string.rep('\0',8)and coordinator~=string.rep('\0',8),'authority_peer_not_ready')
  self.evidence.local_identity_matches=stable(session+0xb398,8)==selfpeer
  self.evidence.coordinator_matches=stable(session+0xb3a8,8)==coordinator
  assert(self.evidence.local_identity_matches,'authority_local_peer_disagrees')
  assert(self.evidence.coordinator_matches,'authority_coordinator_disagrees')
  local n=u32(stable(session+0x162d8,4),0);assert(n>=1 and n<=4,'authority_peer_count')
  local raw=stable(session+0x162e0,n*8);local members={}
  for i=0,n-1 do local key=raw:sub(i*8+1,i*8+8);assert(not members[key],'authority_duplicate_peer');members[key]=true end
  assert(members[selfpeer]and members[coordinator],'authority_peer_missing')
  local dispatch=relative(game,p.functions.route_dispatch.rva+6,'\76\141\5')
  local registration
  for _,r in ipairs(trace.registry or {})do if r.name=='authority_owned'then registration=r end end
  assert(registration and registration.hash==0xf8a9d630 and registration.flags[1]==1 and registration.flags[2]==1 and registration.parameter_count==2 and registration.type_indices[1]==107 and registration.type_indices[2]==91,'authority_registry_schema')
  assert(pointer(dispatch+registration.index*8)==game+p.functions.authority_adapter.rva,'authority_registered_handler_changed')
  self.evidence.stage='entity_ownership'
  self.evidence.lookups={}
  local owner=record(engine,vehicle.network_unit,'vehicle');local avatars={}
  if not tracked or need_avatars then
   for _,a in ipairs(s.avatars)do if a.seat and a.seat.collection==vehicle.id then avatars[a.id]=record(engine,a.network_unit,a.is_local and 'local_avatar'or'remote_avatar')end end
  end
  local epoch=stable(engine+0x60e4,4)
  local o={vehicle=vehicle,owner=owner.owner,record_word0=owner.record_word0,record_word1=owner.record_word1,serial=owner.serial,flags=owner.flags,
   selfpeer=selfpeer,coordinator=coordinator,members=members,peer_count=n,avatars=avatars,busy=busy(vehicle),
   context=tostring(session)..'/'..tostring(engine)..'/'..epoch..'/'..s.mission_value,
   session=session,engine=engine,mission=s.mission_value}
  for _,g in ipairs(guards)do assert(get(g[1],#g[2])==g[2],'authority_changed_during_read')end
  self.evidence.stage='ready'
  return o
 end
 function self:summary(o)
  local function alias(key)return reader.peers[key]or'not_in_session_labels'end
  return {owner=alias(o.owner),record_word0=o.record_word0,record_word1=o.record_word1,local_peer=alias(o.selfpeer),coordinator=alias(o.coordinator),
   serial=o.serial,flags=o.flags,busy=o.busy,network_unit=o.vehicle.network_unit,owned_local=o.vehicle.owned_local}
 end
 function self:send(o,destination,target,before_invoke,options)
  -- Preflight is repeated immediately before the only native call.
  local s,reason=reader:capture();assert(s,reason or 'authority_send_snapshot_unavailable')
  local requesting=destination~=o.selfpeer
  local fresh,why=self:capture(s,o.vehicle,requesting);assert(fresh,why or 'authority_send_observation_unavailable')
  assert(fresh.context==o.context and fresh.owner==o.owner and fresh.record_word0==o.record_word0 and fresh.record_word1==o.record_word1 and fresh.serial==o.serial and not fresh.busy,'authority_send_state_changed')
  assert(fresh.owner==destination,'authority_send_requires_current_owner_destination')
  assert(fresh.members[destination]and fresh.members[target],'authority_send_peer_left')
  if requesting then
   if options then assert(options.mode=='vacant_driver'and(options.source==2 or options.source==3)and target==o.selfpeer and options.avatar~=nil and options.avatar_unit~=nil and options.remote_id~=nil and options.remote_unit~=nil and type(options.validate)=='function','authority_driver_options_invalid')end
   assert(fresh.coordinator==o.coordinator,'authority_host_changed_before_request')
   assert(s.player_count==2 and s.local_count==1 and fresh.peer_count==2 and(fresh.coordinator==destination or fresh.coordinator==o.selfpeer),'authority_send_room_changed')
   local local_ok,driver_ok=false,false
   for _,a in ipairs(s.avatars)do local seat=a.seat;local peer=fresh.avatars[a.id]
    if seat and peer and seat.collection==o.vehicle.id and seat.target==-1 and seat.action==-1 and seat.transitioning==0 and seat.queued_exit==0 then
     if a.is_local and seat.current>=1 and seat.current<=4 and seat.current%1==0 and seat.reserved==seat.current and seat.role==(seat.current==4 and 2 or 3) and peer.owner==o.selfpeer then
      local_ok=not options or seat.current==options.source and a.id==options.avatar and a.unit==options.avatar_unit
     end
     if not a.is_local and peer.owner==destination then
      if options then driver_ok=seat.current==4 and seat.reserved==4 and seat.role==2 and a.id==options.remote_id and a.unit==options.remote_unit
      elseif seat.current==0 and seat.reserved==0 and seat.role==1 then driver_ok=true end
     end
    end
   end
   assert(local_ok and driver_ok,'authority_send_seats_changed')
  end
  reads=0;guards={};check_code()
  assert(o.members[destination]and o.members[target],'authority_send_peer_left')
  assert(pointer(game+p.globals.session)==o.session and pointer(o.session+0xb390)==o.engine,'authority_send_session_changed')
  assert(stable(o.engine+0x20,8)==o.selfpeer,'authority_send_identity_changed')
  for _,g in ipairs(guards)do assert(get(g[1],#g[2])==g[2],'authority_send_torn_read')end
  if options then assert(requesting,'authority_driver_options_on_return');options.validate()end
  if before_invoke then before_invoke()end
  ffi.cast('void (*)(uint64_t,uint32_t,uint64_t)',game+p.functions.authority_send.rva)(uint64(destination),o.vehicle.network_unit,uint64(target))
 end
 return self
end
return M
