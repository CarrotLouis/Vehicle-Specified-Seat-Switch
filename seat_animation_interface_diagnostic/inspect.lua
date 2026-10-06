-- Read-only preflight for an existing animation-event RPC. Never invokes it.
local M={};local bit=require('bit')
local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);assert(e);return a+c*256+d*65536+e*16777216 end
function M.new(api,game,p,route)
 local function relative(name,off,opcode)
  local at=p.functions[name].rva+off;local b=assert(api.read(game+at,7))
  assert(b:sub(1,3)==opcode,'animation_reference_changed')
  local d=u32(b,3);if d>=2147483648 then d=d-4294967296 end
  local rva=at+7+d;assert(api.in_image(game,rva,8),'animation_global_outside_image');return rva
 end
 local dictionary=relative('anim_event_index',4,'\76\139\21')
 assert(dictionary==relative('anim_event_adapter',0x1f,'\72\139\5'),'animation_dictionary_references_disagree')
 local systems=relative('anim_event_receive',0xd,'\76\139\37')
 local dispatch=relative('route_dispatch',6,'\76\141\5')
 local self={}
 function self:capture(avatar)
  local guards={};local reads=0
  local function read(a,n)
   reads=reads+1;assert(reads<=4096,'animation_inspect_read_budget')
   local b=api.read(a,n);assert(b and #b==n,'animation_inspect_unreadable')
   guards[#guards+1]={a,b};return b
  end
  local function ptr(a)return assert(api.pointer(read(a,8)),'animation_inspect_pointer')end
  local function map(header,key)
   local cap,empty,mult=u32(header,8),u32(header,12),u32(header,16)
   if cap==0 then return nil,'empty_map' end
   assert(cap<=262144 and bit.band(cap,cap-1)==0,'animation_map_capacity')
   -- Power-of-two reduction keeps the product exact under Lua doubles.
   local rows=assert(api.pointer(header));local start=((key%cap)*(mult%cap))%cap
   for i=0,math.min(cap,128)-1 do
    local b=read(rows+((start+i)%cap)*8,8);local k=u32(b,0)
    if k==key then local index=u32(b,4);return index~=4294967295 and index or nil,'matched' end
    if k==empty then return nil,'not_found' end
   end
   return nil,'probe_budget'
  end
  local out={event='animation_interface',dictionary_root_rva=dictionary,systems_root_rva=systems,
   avatar=avatar and {id=avatar.id,unit=avatar.unit,network_unit=avatar.network_unit}or nil}
  local routed=route:capture();out.routing=routed
  assert(routed.state=='observed','animation_registry_unstable')
  for _,item in ipairs(routed.messages)do if item.hash==0xbde53653 and item.found then
   out.dispatch_matches=ptr(game+dispatch+item.index*8)==game+p.functions.anim_event_adapter.rva
  end end
  local dict=ptr(game+dictionary);local header=read(dict+8,20)
  local count=u32(read(dict+0x28,4),0);assert(count<=262144,'animation_event_count')
  local values=count>0 and ptr(dict+0x20)or nil;out.event_count=count;out.events={}
  for _,item in ipairs({{'action_end',0xdab88e64},{'frv_enter_front_right',0xb32ac618},
                        {'frv_enter_back_left',0x929e2ba1},{'frv_switch',0xd429c3f4}})do
   local index,why=map(header,item[2]);local row={name=item[1],hash=item[2],lookup=why,found=index~=nil}
   if index then
    assert(index<count,'animation_event_index_out_of_bounds');row.index=index
    row.roundtrip=u32(read(values+index*4,4),0)==item[2]
   end
   out.events[#out.events+1]=row
  end
  local root=ptr(game+systems);local count=u32(read(root+0x3e70,4),0)
  assert(count<=16,'animation_system_count');out.system_count=count;out.animators={}
  local list=count>0 and read(root+0x3e78,count*16)or ''
  for i=0,count-1 do
   local row=list:sub(i*16+1,i*16+16)
   if u32(row,8)==7 then
    local manager=assert(api.pointer(row));local entry={slot=i,kind=7}
    if avatar then
     local header=read(manager+0x48,20);local index,why=map(header,avatar.id)
     entry.avatar_found=index~=nil;entry.lookup=why
     if index then
      assert(index<262144,'animation_entity_index_out_of_bounds')
      local ep=ptr(ptr(manager+0x60)+index*8);local entity=read(ep,24)
      entry.entity_matches=u32(entity,8)==avatar.id and u32(entity,12)==avatar.unit
      entry.network_matches=u32(entity,16)==avatar.network_unit
      entry.entity_flags=u32(entity,20)
     end
    end
    out.animators[#out.animators+1]=entry
   end
  end
  for _,g in ipairs(guards)do assert(api.read(g[1],#g[2])==g[2],'animation_inspect_changed_during_read')end
  out.stable=true;out.reads=reads;return out
 end
 return self
end
return M
