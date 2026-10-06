-- Bounded read-only observation of the existing driver component. No native
-- game calls, replacement/write functions or guesses about physical velocity.
return function(api,game,p,emit,spin)
 local ffi,bit=api.ffi,require('bit')
 local watched,until_at,last_sample,held_before=nil,0,-math.huge,false
 local function read(a,n)local b=api.read(a,n);assert(b and #b==n,'steering_watch_unreadable');return b end
 local function ptr(a)return assert(api.pointer(read(a,8)),'steering_watch_pointer')end
 local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);assert(e);return a+c*256+d*65536+e*16777216 end
 local function hex(b)return(b:gsub('.',function(c)return string.format('%02x',c:byte())end))end
 local function held()
  local r={};for _,k in ipairs({65,68,83,87})do if api.down(k)then r[#r+1]=k end end;return r
 end
 local function locate(v)
  for _,proof in ipairs(p.driver.proofs)do
   assert(read(game+proof.rva,#proof.bytes)==proof.bytes,'steering_watch_driver_proof')
  end
  local f=assert(p.functions.tank_driver_active)
  assert(read(game+f.rva,#f.bytes)==f.bytes,'steering_watch_tank_proof')
  local manager=ptr(game+p.driver.global)
  local header=read(manager+0x38,20);local rows=assert(api.pointer(header))
  local cap,empty,mult=u32(header,8),u32(header,12),u32(header,16)
  assert(cap>0 and cap<=16384 and bit.band(cap,cap-1)==0,'steering_watch_map')
  local start=((v.id%cap)*(mult%cap))%cap;local index
  for i=0,math.min(cap,64)-1 do
   local b=read(rows+((start+i)%cap)*8,8)
   if u32(b,0)==v.id then index=u32(b,4);break end
   if u32(b,0)==empty then break end
  end
  assert(index and index<4096 and index<u32(read(manager+0x24,4),0),'steering_watch_component')
  local owner=ptr(ptr(manager+0x50)+index*8);local entity=read(owner,24)
  assert(u32(entity,8)==v.id and u32(entity,12)==v.unit and u32(entity,16)==v.network_unit,
   'steering_watch_vehicle_identity')
  assert(hex(entity:sub(1,8):reverse())==v.resource and(bit.band(u32(entity,20),1)~=0)==v.owned_local,
   'steering_watch_resource_or_authority')
  local commands=ptr(manager+0x58)+index*48
  local runtime=ptr(manager+0x68)+index*0xd28
  local cb=read(commands,48);local tail=read(runtime+0xd08,32)
  local active=tail:byte(17);assert(active==0 or active==1,'steering_watch_active_flag')
  assert(read(owner,24)==entity and read(manager+0x38,20)==header and
   ptr(ptr(manager+0x50)+index*8)==owner and read(commands,48)==cb and read(runtime+0xd08,32)==tail,
   'steering_watch_changed_during_read')
  local values=ffi.new('float[12]');ffi.copy(values,cb,48);local floats={}
  -- Last word is a byte flag group; do not reinterpret it as a float.
  for i=0,10 do
   local x=tonumber(values[i]);assert(x==x and x~=math.huge and x~=-math.huge,'steering_watch_nonfinite')
   floats[#floats+1]=x
  end
  local data={driver_command_hex=hex(cb),command_floats_offset_00_to_28=floats,
   command_flags_offset_2c_to_2f={cb:byte(45,48)},driver_active=active,runtime_tail_hex=hex(tail)}
  -- Optional downstream telemetry must never disable the original watcher or
  -- prevent the caller from returning borrowed authority.
  -- FRV motion properties already provide its input/replica values at loan
  -- boundaries. Do not add this second reader to the idle FRV command ring.
  if spin and(v.name=='bastion'or v.name=='maelstrom')then
   local ok,result=pcall(spin.read_vehicle,spin,v)
   if ok then data.spin=result
   else data.spin_gap=tostring(result) end
  end
  return data
 end
 return {read_vehicle=function(_,v)return locate(v)end,update=function(_,sample)
  if not sample or sample.state~='mission'then watched=nil;held_before=false;return end
  local now=api.now();local own,own_vehicle
  for _,a in ipairs(sample.avatars)do if a.is_local then own=a end end
  if own and own.seat then for _,v in ipairs(sample.vehicles)do
   if v.id==own.seat.collection and(v.name=='bastion'or v.name=='maelstrom')then own_vehicle=v end
  end end
  local steering=own_vehicle and own.seat.current==0 and own.seat.role==1 and
    (api.down(65)or api.down(68))or false
  if steering and(not held_before or not watched or watched.id~=own_vehicle.id)then
   watched={id=own_vehicle.id,unit=own_vehicle.unit,network_unit=own_vehicle.network_unit,
    resource=own_vehicle.resource,mission=sample.mission_value}
   until_at=now+10;last_sample=-math.huge
   emit({event='steering_watch_started',collection=watched.id,vehicle=own_vehicle.name,
    duration_seconds=10,held_keys=held(),read_only=true})
  end
  held_before=steering
  if not watched or now>until_at then return end
  if sample.mission_value~=watched.mission then watched=nil;return end
  if now-last_sample<.09 then return end;last_sample=now
  local v
  for _,candidate in ipairs(sample.vehicles)do
   if candidate.id==watched.id and candidate.unit==watched.unit and candidate.network_unit==watched.network_unit and
     candidate.resource==watched.resource then v=candidate;break end
  end
  if not v then watched=nil;emit({event='steering_watch_ended',reason='tracked_vehicle_missing',read_only=true});return end
  local ok,data=pcall(locate,v)
  if not ok then
   watched=nil;emit({event='steering_watch_gap',collection=v.id,reason=tostring(data),read_only=true});return
  end
  data.event='steering_watch_sample';data.read_only=true;data.collection=v.id;data.vehicle=v.name
  data.players=sample.player_count;data.peer_count=sample.peer_count;data.owned_local=v.owned_local
  data.held_keys=held();data.local_avatar=own and own.id;data.local_seat=own and own.seat
  data.occupants={}
  for _,a in ipairs(sample.avatars)do if a.seat and a.seat.collection==v.id then
   data.occupants[#data.occupants+1]={id=a.id,unit=a.unit,network_unit=a.network_unit,is_local=a.is_local,
    vehicle_input=a.vehicle_input,seat=a.seat}
  end end
  emit(data)
 end}
end
