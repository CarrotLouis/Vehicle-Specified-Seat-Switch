-- Read-only weapon-slot observer. No FFI call into game code and no network sends.
local M={};local bit=require('bit')
local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);assert(e,'short_binding_read');return a+c*256+d*65536+e*16777216 end
function M.new(api,game,p)
 local function relative(name,off,opcode)
  local at=p.functions[name].rva+off;local b=assert(api.read(game+at,7))
  assert(b:sub(1,3)==opcode,'binding_reference_changed')
  local d=u32(b,3);if d>=2147483648 then d=d-4294967296 end
  local rva=at+7+d;assert(api.in_image(game,rva,8),'binding_root_outside_image');return rva
 end
 local weapons=relative('binding_clear_avatar',0x1d,'\72\139\53')
 local rotation=relative('avatar_rotation',0xc,'\76\139\21')
 local dispatch=relative('route_dispatch',6,'\76\141\5')
 local self={}
 function self:interface(route)
  local out=route:capture();out.clear_dispatch_matches=false;out.bind_dispatch_matches=false
  for _,row in ipairs(out.messages or {})do
   if row.hash==0x423a4034 and row.found then
    local b=api.read(game+dispatch+row.index*8,8)
    out.clear_dispatch_matches=b~=nil and api.pointer(b)==game+p.functions.binding_clear_adapter.rva
   end
   if row.hash==0x2671dec5 and row.found then
    local b=api.read(game+dispatch+row.index*8,8)
    out.bind_dispatch_matches=b~=nil and api.pointer(b)==game+p.functions.binding_bind_adapter.rva
   end
  end
  out.weapon_root_rva=weapons;out.rotation_root_rva=rotation;return out
 end
 function self:entity(id)
  assert(id~=0 and id~=0xffffffff,'binding_invalid_entity')
  local root=relative('binding_entity_lookup',0x10,'\76\139\21')
  assert(root==p.globals.entities,'binding_entity_root_disagrees')
  local guards={}
  local function read(a,n)local b=api.read(a,n);assert(b and #b==n,'binding_entity_unreadable');guards[#guards+1]={a,b};return b end
  local e=assert(api.pointer(read(game+root,8)))
  local h=read(e+0xf1aeb0,20);local cap,empty,mult=u32(h,8),u32(h,12),u32(h,16)
  assert(cap>0 and cap<=1048576 and bit.band(cap,cap-1)==0,'binding_entity_capacity')
  local rows=assert(api.pointer(h));local start=((id%cap)*(mult%cap))%cap;local idx
  for i=0,math.min(cap,128)-1 do local b=read(rows+((start+i)%cap)*8,8)
   if u32(b,0)==id then idx=u32(b,4);break end
   if u32(b,0)==empty then break end
  end
  assert(idx and idx<262144,'binding_entity_missing')
  local b=read(e+p.layout.entity_records+idx*24,24)
  assert(u32(b,8)==id,'binding_entity_id_mismatch')
  local out={id=id,unit=u32(b,12),network_unit=u32(b,16),flags=u32(b,20)}
  assert(out.unit~=0 and out.network_unit~=0 and out.network_unit~=0x7fff and out.network_unit~=0xffffffff,'binding_entity_invalid_network_ref')
  for _,g in ipairs(guards)do assert(api.read(g[1],#g[2])==g[2],'binding_entity_changed')end
  return out
 end
 function self:capture(avatar)
  local guards={};local reads=0
  local function read(a,n)
   reads=reads+1;assert(reads<=320,'binding_read_budget')
   local b=api.read(a,n);assert(b and #b==n,'binding_unreadable')
   guards[#guards+1]={a,b};return b
  end
  local function ptr(a)return assert(api.pointer(read(a,8)),'binding_pointer')end
  local function lookup(manager,id)
   local h=read(manager+0x30,20);local cap,empty,mult=u32(h,8),u32(h,12),u32(h,16)
   assert(cap>0 and cap<=262144 and bit.band(cap,cap-1)==0,'binding_capacity')
   local rows=assert(api.pointer(h));local start=((id%cap)*(mult%cap))%cap
   for i=0,math.min(cap,128)-1 do
    local b=read(rows+((start+i)%cap)*8,8);local key=u32(b,0)
    if key==id then local idx=u32(b,4);assert(idx<262144,'binding_index');return idx end
    if key==empty then return nil end
   end
   error('binding_probe_budget')
  end
  assert(avatar.is_local,'binding_local_avatar_only')
  local out={avatar=avatar.id,unit=avatar.unit,network_unit=avatar.network_unit,seat=avatar.seat,slots={}}
  local manager=ptr(game+weapons);local index=lookup(manager,avatar.id)
  out.weapon_component_found=index~=nil
  if index then
   local count=u32(read(manager+0x20,4),0);assert(count<=262144 and index<count,'binding_active_count')
   local entity=read(ptr(ptr(manager+0x48)+index*8),24)
   assert(u32(entity,8)==avatar.id and u32(entity,12)==avatar.unit and u32(entity,16)==avatar.network_unit,'binding_identity_changed')
   local slots=ptr(manager+0x60)+index*0x1d0
   for channel=0,4 do
    local b=read(slots+channel*0x50,8)
    out.slots[#out.slots+1]={channel=channel,weapon=u32(b,0),secondary=u32(b,4)}
   end
  end
  local rm=ptr(game+rotation);local ri=lookup(rm,avatar.id)
  out.rotation_component_found=ri~=nil
  if ri then out.rotation_flag=read(ptr(rm+0x58)+ri*0x90+0x71,1):byte()end
  for _,g in ipairs(guards)do assert(api.read(g[1],#g[2])==g[2],'binding_changed_during_read')end
  out.stable=true;out.reads=reads;return out
 end
 return self
end
return M
