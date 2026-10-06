-- Read-only inspection of the two independently evidenced network API slots.
-- No hook, native game call, pointer replacement, protection change or packet capture.
local M={}
local offsets={0x5b,0xa9,0x158,0x21c,0x25a}
local function signed32(b)
 local a,c,d,e=b:byte(4,7);assert(e,'short_reference')
 local v=a+c*256+d*65536+e*16777216
 return v>=2147483648 and v-4294967296 or v
end
function M.locate(api,game,p)
 local entry=assert(p.functions.trace_send,'missing_verified_sender').rva
 local root
 for _,offset in ipairs(offsets)do
  local b=assert(api.read(game+entry+offset,7),'reference_unreadable')
  assert(b:sub(1,3)=='\72\139\5','reference_instruction_changed')
  local rva=entry+offset+7+signed32(b)
  assert(not root or root==rva,'inconsistent_network_api_reference');root=rva
 end
 assert(api.in_image(game,root,8),'network_api_global_outside_image')
 return root
end
function M.new(api,game,p)
 local root=M.locate(api,game,p)
 local function pointer(address)
  local b=api.read(address,8)
  return b and api.pointer(b),b
 end
 local self={}
 function self:capture()
  local out={event='interface_snapshot',root_rva=root,reference_count=#offsets,
   boundary='pointer_and_page_metadata_only; no_protocol_events',slots={}}
  out.global=api.describe(game+root)
  local services,root_bytes=pointer(game+root)
  if not services then out.state='services_unavailable';return out end
  out.services=api.describe(services)
  out.network_pointer_slot=api.describe(services+0x38)
  local network,network_bytes=pointer(services+0x38)
  if not network then out.state='network_api_unavailable';return out end
  out.network_api=api.describe(network)
  local slot_bytes={}
  for _,s in ipairs({{name='send_one',offset=0x38},{name='send_many',offset=0x40}})do
   local target,b=pointer(network+s.offset);slot_bytes[s.offset]=b
   local row={name=s.name,offset=s.offset,storage=api.describe(network+s.offset)}
   if target then
    row.target=api.describe(target)
    -- Code only, bounded to the current executable region; never dump heap data.
    if row.target.executable and row.target.readable and row.target.state==0x1000 then
     local n=math.min(64,row.target.region_remaining or 0)
     if n>0 then local head=api.read(target,n)
      if head then row.head_hex=(head:gsub('.',function(c)return string.format('%02x',c:byte())end))end
     end
    end
   else row.unavailable=true end
   out.slots[#out.slots+1]=row
  end
  -- Dynamic tables can be replaced. A mixed snapshot is evidence of no stable chain.
  local stable=api.read(game+root,8)==root_bytes and api.read(services+0x38,8)==network_bytes
  for _,s in ipairs(out.slots)do stable=stable and slot_bytes[s.offset]~=nil and api.read(network+s.offset,8)==slot_bytes[s.offset]end
  if not stable then out.state='changed_during_read';out.slots={};return out end
  out.state='observed';return out
 end
 return self
end
return M
