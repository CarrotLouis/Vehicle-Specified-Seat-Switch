-- Bounded reads of known layout; deliberately retains unstable/transition states.
-- No remote peer is inferred from local ownership flags or array position.
local bit,ffi=require('bit'),require('ffi')
local M={}
local function u32(b,o)
 local a,c,d,e=b:byte(o+1,o+4);assert(e,'short_integer')
 return a+c*256+d*65536+e*16777216
end
local function i32(b,o)local n=u32(b,o);return n>=2147483648 and n-4294967296 or n end
local function hash(b)return b:reverse():gsub('.',function(c)return string.format('%02x',c:byte())end)end
local vehicles={cc21c7ffd3ebefb9='m102',e9cd1d0d118886af='m102',['9b2140378640432e']='m103',
 ['2d85bfe3d8717fe5']='m104',['16474112801385b6']='bastion',b0c9faf4af8903f9='maelstrom',['423ff97d57ab04f5']='tanker'}
local function entity(b)
 return {resource=hash(b:sub(1,8)),id=u32(b,8),unit=u32(b,12),network_unit=u32(b,16),flags=u32(b,20),owned_local=bit.band(u32(b,20),1)~=0}
end
function M.new(api,game,profile)
 local self={peers={},peer_serial=0,watched={},mission_token=nil}
 local reads,guards
 local function get(p,n)
  reads=reads+1;assert(reads<=512,'read_budget')
  local b=api.read(p,n);assert(b and #b==n,'unreadable_state');return b
 end
 local function ptr(b,o)local p=api.pointer(b,o);assert(p,'invalid_pointer');return p end
 local function stable(p,n)local b=get(p,n);guards[#guards+1]={p,b};return b end
 local function global(rva)return ptr(stable(game+rva,8))end
 local function lookup(header,id,maxcap)
  local cap,empty,mult=u32(header,8),u32(header,12),u32(header,16)
  if cap==0 then return nil end
  assert(cap<=(maxcap or 4096) and bit.band(cap,cap-1)==0,'invalid_map')
  local rows=ptr(header)
  local start=tonumber(ffi.cast('uint32_t',ffi.new('uint64_t',id)*ffi.new('uint64_t',mult)))
  for j=0,math.min(cap,64)-1 do
   local r=get(rows+8*bit.band(start+j,cap-1),8)
   if u32(r,0)==id then local index=u32(r,4);return index~=0xffffffff and index or nil end
   if u32(r,0)==empty then return nil end
  end
 end
 local function manager(address)
  local b=stable(address+8,12)
  local total,active,owned=u32(b,0),u32(b,4),u32(b,8)
  assert(total<=256 and active<=total and owned<=active,'invalid_manager_counts')
  return {address=address,total=total,active=active,owned=owned,
   map=stable(address+0x20,20),records=stable(address+0x38,8),states=stable(address+0x48,8)}
 end
 local function counts(m)return {total=m.total,active=m.active,owned=m.owned}end
 local function seater(b)
  return {collection=u32(b,0),transition_type=u32(b,4),role=u32(b,8),entry_role=u32(b,12),
   entrance=i32(b,16),current=i32(b,20),target=i32(b,24),reserved=i32(b,28),action=i32(b,32),
   deadline_low=u32(b,40),deadline_high=u32(b,44),transitioning=b:byte(49),active_passenger=b:byte(50),
   instant=b:byte(51),queued_exit=b:byte(52)}
 end
 function self:capture()
  reads=0;guards={}
  local result={avatars={},vehicles={},peers={}}
  local session=global(profile.globals.session)
  local pn=u32(stable(session+0x162d8,4),0);assert(pn<=4,'invalid_peer_count')
  result.peer_count=pn
  if pn>0 then
   local peers=stable(session+0x162e0,pn*8)
   for i=0,pn-1 do
    local raw=peers:sub(i*8+1,i*8+8)
    if not self.peers[raw] then self.peer_serial=self.peer_serial+1;self.peers[raw]='P'..self.peer_serial end
    result.peers[#result.peers+1]=self.peers[raw]
   end
  end
  local mission=stable(global(profile.globals.mission),0x44)
  result.mission_value=u32(mission,8);result.mission_phase=u32(mission,64)
  local pm=global(profile.globals.player)
  local pc=stable(pm+0x84,8);result.player_count=u32(pc,0);result.local_count=u32(pc,4)
  assert(result.player_count<=4 and result.local_count<=4,'invalid_player_counts')
  if result.mission_value==0 or result.mission_phase<1 or result.mission_phase>7 then
   self.watched={};self.mission_token=nil;result.state='not_in_mission'
  else
   if self.mission_token~=result.mission_value then self.watched={};self.mission_token=result.mission_value end
   result.state='mission';local locals={}
   if result.local_count>0 then
    local b=stable(pm+0x3a8,result.local_count*20)
    -- Player records contain an entity-map handle, not the unit field at +12.
    -- Resolve it exactly as gameplay snapshot.capture does. Equal-looking
    -- synthetic handles previously concealed this mismatch in real sessions.
    local entities=global(profile.globals.entities)
    local map=stable(entities+profile.layout.entity_unit_map,20)
    for i=0,result.local_count-1 do
     local handle=u32(b,i*20)
     if handle~=0x7fff then
      local index=lookup(map,handle,1048576)
      if index then
       assert(index<262144,'invalid_local_entity_index')
       local raw=stable(entities+profile.layout.entity_records+index*24,24)
       local resolved=entity(raw)
       if resolved.resource=='4d1c334d294dfa97' and resolved.owned_local then
        locals[resolved.id]=raw
       end
      end
     end
    end
   end
   local am=global(profile.globals.avatar)
   local an=u32(stable(am+0x6c,4),0);assert(an<=8,'invalid_avatar_count')
   local sm=manager(global(profile.globals.seater))
   local cm=manager(global(profile.globals.collection))
   local masks=stable(cm.address+0x50,8)
   result.seater_counts=counts(sm);result.collection_counts=counts(cm)
   local ids={}
   for i=0,an-1 do
    local ap=ptr(stable(am+0x110+i*8,8))
    local b=stable(ap,24);local avatar=entity(b)
    assert(avatar.resource=='4d1c334d294dfa97','avatar_identity_changed')
    avatar.is_local=locals[avatar.id]==b
    local flags=get(am+0x53e888+i*0x1238,8)
    avatar.input_flags_low=u32(flags,0);avatar.input_flags_high=u32(flags,4)
    avatar.vehicle_input=bit.band(avatar.input_flags_high,0x40000)~=0
    local si=lookup(sm.map,avatar.id)
    if si and si<sm.active then
     local ep=ptr(stable(ptr(sm.records)+si*8,8))
     assert(stable(ep,24)==b,'seater_identity_changed')
     avatar.seat=seater(stable(ptr(sm.states)+si*64,64))
     local cid=avatar.seat.collection
     if cid~=0 and cid~=0xffffffff then ids[cid]=true end
    end
    result.avatars[#result.avatars+1]=avatar
   end
   local previous_count=0
   for id in pairs(self.watched) do previous_count=previous_count+1;if previous_count<=8 then ids[id]=true end end
   local next_watch={}
   for id in pairs(ids) do
    local ci=lookup(cm.map,id)
    if ci and ci<cm.active then
     local ep=ptr(stable(ptr(cm.records)+ci*8,8));local vehicle=entity(stable(ep,24))
     assert(vehicle.id==id,'collection_identity_changed')
     vehicle.name=vehicles[vehicle.resource]
     if vehicle.name then
      local b=stable(ptr(cm.states)+ci*100,100)
      vehicle.transition_type=u32(b,0)
      local expected=assert(profile.tables[vehicle.name],'unknown_profile')
      assert(vehicle.transition_type==expected.transition,'vehicle_profile_changed')
      local mask=stable(ptr(masks)+ci*12,12)
      vehicle.free_mask=u32(mask,0);vehicle.sync_word1=u32(mask,4);vehicle.sync_word2=u32(mask,8)
      vehicle.seat_count=#expected.roles
      result.vehicles[#result.vehicles+1]=vehicle;next_watch[id]=true
     end
    end
   end
   self.watched=next_watch
   table.sort(result.avatars,function(a,b)return a.id<b.id end)
   table.sort(result.vehicles,function(a,b)return a.id<b.id end)
  end
  -- Reject torn observations instead of assigning a peer/seat based on mixed data.
  for _,g in ipairs(guards) do if get(g[1],#g[2])~=g[2] then return nil,'state_changed_during_read' end end
  return result
 end
 return self
end
return M
