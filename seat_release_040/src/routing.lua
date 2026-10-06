-- Bounded read-only receive callback and seat-message registry inspection.
local M={}
local function u32(b,o)
 local a,c,d,e=b:byte(o+1,o+4);assert(e,'short_routing_read');return a+c*256+d*65536+e*16777216
end
local function relative(api,base,rva,opcode)
 local b=assert(api.read(base+rva,7),'routing_reference_unreadable')
 assert(b:sub(1,3)==opcode,'routing_reference_changed')
 local d=u32(b,3);if d>=2147483648 then d=d-4294967296 end
 return rva+7+d
end
function M.new(api,game,p,messages)
 local exe=assert(api.module('helldivers2.exe'),'missing_engine_module')
 local send=assert(p.engine_functions.route_send_many).rva
 local decode=assert(p.engine_functions.route_decode).rva
 local root=relative(api,exe,send+0x2d,'\72\139\61')
 assert(root==relative(api,exe,decode+0x2a,'\72\139\53'),'inconsistent_registry_root')
 assert(api.in_image(exe,root,8),'registry_root_outside_image')
 local setup=assert(p.functions.route_setup).rva
 assert(relative(api,game,setup+0x14,'\72\139\53')==p.globals.session,'callback_session_reference_changed')
 local dispatcher=relative(api,game,setup+0x13c,'\72\141\5')
 assert(dispatcher==p.functions.route_dispatch.rva,'callback_dispatch_relationship_changed')
 local function pointer(a)
  local b=api.read(a,8);return b and api.pointer(b),b
 end
 local function scalar(a)
  local b=api.read(a,4);return b and u32(b,0),b
 end
 local self={}
 function self:capture()
  local out={registry_root_rva=root,callback_offset=0xb3f8,expected_dispatch_rva=dispatcher,messages={}}
  local session,sb=pointer(game+p.globals.session)
  if session then
   local at=session+0xb3f8;local target,tb=pointer(at)
   local row={storage=api.describe(at),matches_dispatch=target~=nil and target==game+dispatcher or false}
   if target then row.target=api.describe(target)end
   row.stable=tb~=nil and api.read(game+p.globals.session,8)==sb and api.read(at,8)==tb
   out.callback=row
  else out.callback={unavailable=true}end
  local network,nb=pointer(exe+root)
  if not network then out.state='network_state_unavailable';return out end
  local registry,rb=pointer(network)
  if not registry then out.state='registry_unavailable';return out end
  local count,cb=scalar(registry+0x88);local rows,pb=pointer(registry+0x90)
  out.registry_count=count
  if not count or count<1 or count>8192 or not rows then out.state='invalid_registry_layout';return out end
  local ordering={};local observed={};local type_reads={};local reads=0
  local function row_at(i)
   reads=reads+1;assert(reads<=240,'registry_read_budget')
   local b=assert(api.read(rows+i*0x68,0x68),'registry_row_unreadable');local hash=u32(b,0)
   for j,value in pairs(ordering)do assert((i>=j or hash<value)and(i<=j or hash>value),'registry_order_changed')end
   assert(not observed[i]or observed[i]==b,'registry_changed_during_read')
   ordering[i]=hash;observed[i]=b;return hash,b
  end
  for hash,name in pairs(messages)do
   local lo,hi=0,count-1;local item={name=name,hash=hash,found=false}
   while lo<=hi do
    local mid=math.floor((lo+hi)/2);local value,b=row_at(mid)
    if value==hash then
     item.found=true;item.index=mid;item.flags={b:byte(5),b:byte(6)}
     item.parameter_count=u32(b,0x50)
     -- These are registry type indices, not decoded gameplay argument values.
     if item.parameter_count<=8 then
      item.type_indices={};local types=api.pointer(b,0x58)
      if item.parameter_count>0 and types then
       local values=api.read(types,item.parameter_count*4)
       if values then type_reads[#type_reads+1]={address=types,bytes=values};for i=0,item.parameter_count-1 do item.type_indices[#item.type_indices+1]=u32(values,i*4)end
       else item.types_unavailable=true end
      elseif item.parameter_count>0 then item.types_unavailable=true end
     else item.types_skipped=true end
     break
    elseif value<hash then lo=mid+1 else hi=mid-1 end
   end
   out.messages[#out.messages+1]=item
  end
  table.sort(out.messages,function(a,b)return a.hash<b.hash end)
  local stable=api.read(exe+root,8)==nb and api.read(network,8)==rb and api.read(registry+0x88,4)==cb and api.read(registry+0x90,8)==pb
  for i,b in pairs(observed)do stable=stable and api.read(rows+i*0x68,0x68)==b end
  for _,t in ipairs(type_reads)do stable=stable and api.read(t.address,#t.bytes)==t.bytes end
  if not stable then out.messages={};out.state='registry_changed_during_read'
  else out.state='observed' end
  return out
 end
 return self
end
return M
