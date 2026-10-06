-- Discover actual linked weapons through two verified read-only helpers.
-- Lookup remains bounded: five joint tags and <=128 probed map rows on trigger.
return function(api,game,p,spec,compat,inspector,scope,emit)
 local ffi,bit=assert(api.ffi),require('bit')
 local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);assert(e);return a+c*256+d*65536+e*16777216 end
 local function code(name)
  local d,f=assert(spec.records[name]),assert(p.functions[name]);local b=assert(api.read(game+f.rva,d.length))
  assert(compat.match(b,d.chunks),'mounted_code_'..name);return game+f.rva
 end
 local tags=ffi.cast('void *(*)(uint32_t,uint32_t)',code('reservation_mounted_joint_tags'))
 local lookup=ffi.cast('void *(*)(void *,uint32_t *,uint32_t,uint32_t)',code('reservation_related_weapon_lookup'))
 code('reservation_related_weapon_resource')
 local function describe(s,target)
  local d=assert(scope.layout(s),'mounted_layout');assert(d.roles[target+1]==2,'mounted_target_role')
  code('reservation_mounted_joint_tags');code('reservation_related_weapon_lookup');code('reservation_related_weapon_resource')
  local guards={}
  local function read(a,n)local b=assert(api.read(a,n),'mounted_unreadable');assert(#b==n);guards[#guards+1]={a,b};return b end
  local function pointer(b)return assert(api.pointer(b),'mounted_pointer')end
  -- Prove this car is in the relation map before invoking the native helper.
  -- Its native loop could traverse the whole map for a missing key; refuse that.
  local ins=game+p.functions.reservation_related_weapon_lookup.rva+0x28
  local rip=read(ins,7);assert(rip:sub(1,3)=='\72\139\45','mounted_relation_reference')
  local disp=ffi.new('int32_t[1]');ffi.copy(disp,rip:sub(4),4)
  local root=ins+7+tonumber(disp[0]);local manager=pointer(read(root,8))
  local head=read(manager+0x20,20);local rows=pointer(head);local cap,empty,mult=u32(head,8),u32(head,12),u32(head,16)
  assert(cap>0 and cap<=262144 and bit.band(cap,cap-1)==0,'mounted_relation_capacity')
  local start=((s.collection%cap)*(mult%cap))%cap;local index
  for i=0,math.min(cap,128)-1 do local row=read(rows+((start+i)%cap)*8,8)
   local key=u32(row,0);if key==s.collection then index=u32(row,4);break end;if key==empty then break end
  end
  assert(index and index<262144,'mounted_relation_car_missing')
  local objects=pointer(read(manager+0x38,8));local car=pointer(read(objects+index*8,8))
  assert(car==s.collection_address,'mounted_relation_car_identity')
  local table_=ffi.cast('uint8_t *',tags(s.transition,target));assert(table_~=nil,'mounted_joint_table_missing')
  local raw=read(table_,20);local joints,ended={},false
  for i=0,4 do local tag=u32(raw,i*4);if tag==0 then ended=true;break end
   assert(tag~=4294967295,'mounted_wildcard_not_supported');joints[#joints+1]=tag
  end
  assert(ended and #joints>=1 and #joints<=4,'mounted_joint_bounds')
  local children,seen={},{}
  for _,tag in ipairs(joints)do
   -- Output storage belongs to this mod; the helper never edits the game.
   local id=ffi.new('uint32_t[1]');local out=lookup(nil,id,s.collection,tag)
   assert(out==ffi.cast('void *',id),'mounted_lookup_output_changed')
   local entity=inspector:entity(tonumber(id[0]))
   assert(entity.id~=s.collection and entity.id~=s.avatar and not seen[entity.id],'mounted_related_entity_invalid')
   seen[entity.id]=true;children[#children+1]={tag=tag,id=entity.id,unit=entity.unit,network_unit=entity.network_unit,owned=bit.band(entity.flags,1)~=0}
  end
  for _,g in ipairs(guards)do assert(api.read(g[1],#g[2])==g[2],'mounted_relation_changed')end
  return children
 end
 local self={}
 function self:prepare(c,target)
  local d=assert(scope.layout(c.native),'mounted_prepare_layout')
  if d.roles[target+1]~=2 then return nil end
  local children=describe(c.native,target)
  emit({event='reservation_mounted_preflight',target=target,children=children,read_only=true})
  return {target=target,children=children}
 end
 function self:ready(c,t)
  local actual=describe(c.native,t.target);assert(#actual==#t.children,'mounted_child_count_changed')
  for i,child in ipairs(actual)do local before=t.children[i]
   assert(child.tag==before.tag and child.id==before.id and child.unit==before.unit and child.network_unit==before.network_unit,'mounted_child_identity_changed')
   if not child.owned then return false,'linked_weapon_authority_not_received'end
  end
  return true
 end
 return self
end
