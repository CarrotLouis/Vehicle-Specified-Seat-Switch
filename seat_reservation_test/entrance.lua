-- Native owner reservation uses a vehicle entrance, not a seating-node ID.
-- Discover the exact inverse only on a trigger: eight bounded interaction
-- records and five validated static preference rows. No cached guessed IDs.
return function(api,game,p,spec,compat,trace,emit)
 local ffi=require('ffi')
 local function code(name)
  local d=assert(spec.records[name]);local f=assert(p.functions[name]);local bytes=assert(api.read(game+f.rva,d.length))
  assert(compat.match(bytes,d.chunks),'reservation_code_'..name);return game+f.rva
 end
 local entry_node=ffi.cast('int32_t (*)(uint32_t,uint32_t,uint32_t)',code('reservation_entrance_node'))
 local resource=ffi.cast('void *(*)(void *)',code('reservation_interaction_resource'))
 local preferences=ffi.cast('void *(*)(uint32_t,uint32_t)',game+assert(p.functions.adjacency).rva)
 local function ints(bytes)local r=ffi.new('int32_t[2]');ffi.copy(r,bytes,8);return tonumber(r[0]),tonumber(r[1])end
 local function peer(key)local v=ffi.new('uint64_t[1]');ffi.copy(v,key,8);return v[0]end
 local function schema(name,hash,types,adapter)
  trace:health();assert(trace.active,'reservation_transport_inactive')
  local found;for _,m in ipairs(trace.registry or{})do if m.name==name then found=m;break end end
  assert(found and found.found and found.hash==hash and found.flags[1]==1 and found.flags[2]==1 and found.parameter_count==#types,'reservation_registry_'..name)
  for i,t in ipairs(types)do assert(found.type_indices[i]==t,'reservation_registry_type_'..name)end
  if adapter then
   local r=p.functions.route_dispatch.rva;local d=ffi.new('int32_t[1]');ffi.copy(d,assert(api.read(game+r+9,4)),4)
   local table_=game+r+13+tonumber(d[0]);local target=assert(api.pointer(api.read(table_+found.index*8,8)))
   assert(target==code(adapter),'reservation_accept_dispatch_changed')
  end
 end
 local self={}
 function self:find(s,target)
  assert(s.vehicle=='m102'and s.transition==26 and s.profile.row==8 and #s.profile.roles==5,'reservation_entrance_scope')
  code('reservation_entrance_node');code('reservation_interaction_resource');code('reservation_interaction_update')
  local record=resource(s.collection_address);assert(record~=nil,'reservation_interaction_resource_missing')
  record=ffi.cast('uint8_t *',record)
  local before=assert(api.read(record,0x450),'reservation_resource_unreadable')
  local table_before=assert(api.read(game+s.profile.rva+40,40),'reservation_preferences_unreadable')
  local candidates,details={},{}
  for entrance=0,7 do
   -- Native initialization bounds the interaction array to eight records;
   -- zero radius terminates it. The entry-node lookup stays within this block.
   local radius=ffi.new('float[1]');ffi.copy(radius,before:sub(entrance*0x88+13,entrance*0x88+16),4)
   local tag=ffi.new('uint32_t[1]');ffi.copy(tag,before:sub(entrance*0x88+21,entrance*0x88+24),4)
   if radius[0]==0 or tag[0]==0 then break end
   assert(radius[0]>0 and radius[0]<1000,'reservation_interaction_radius_changed')
   local node=tonumber(entry_node(26,s.collection,entrance))
   local first,terminator
   if node>=5 and node<=9 then
    local pointer=ffi.cast('uint8_t *',preferences(26,node))
    assert(pointer==game+s.profile.rva+node*8,'reservation_preference_pointer_changed')
    first,terminator=ints(assert(api.read(pointer,8)))
    assert(first>=0 and first<=4 and terminator==-1,'reservation_preference_layout_changed')
    if first==target then candidates[#candidates+1]=entrance end
   end
   details[#details+1]={entrance=entrance,hash=tonumber(tag[0]),node=node,first=first}
  end
  assert(api.read(record,0x450)==before and api.read(game+s.profile.rva+40,40)==table_before,'reservation_entrance_changed')
  emit({event='reservation_entrance_mapping',target=target,entries=details,matched=#candidates,read_only=true})
  assert(#candidates==1,'reservation_exact_entrance_unavailable')
  return candidates[1]
 end
 function self:prepare_request(c,target)
  schema('entry_request',0x3a44e090,{256,256,29});schema('accepted',0x2e986f01,{256,256,87},'reservation_accepted_adapter')
  schema('entry_denied',0xf2a7f3e4,{256,256})
  local s,o=c.native,c.owner;assert(o.owner==c.destination and o.owner~=o.selfpeer and not s.owned and not o.busy,'reservation_request_owner')
  local entrance=self:find(s,target)
  local send=ffi.cast('void (*)(uint64_t,uint32_t,uint32_t,uint32_t)',code('reservation_entry_send'))
  local used=false
  return function()assert(not used,'reservation_request_reused');used=true;trace:health();send(peer(o.owner),s.collection,s.avatar,entrance)end,entrance
 end
 function self:prepare_release(c,slot)
  schema('release_request',0xc698216f,{256,87})
  assert(slot>=1 and slot<=4 and slot%1==0,'reservation_release_scope')
  local send=ffi.cast('void (*)(uint64_t,uint32_t,int32_t)',code('reservation_release_send'))
  local used=false
  return function()assert(not used,'reservation_release_reused');used=true;trace:health();send(peer(c.owner.owner),c.native.collection,slot)end
 end
 return self
end
