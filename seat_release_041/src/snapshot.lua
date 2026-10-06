local ffi,bit=require('ffi'),require('bit')
local M={}
local function u32(b,o)
 local a,b1,c,d=b:byte(o+1,o+4);assert(d,'Short integer read');return a+b1*256+c*65536+d*16777216
end
local function i32(b,o)local v=u32(b,o);return v>=2147483648 and v-4294967296 or v end
local function hash(s)return s:gsub('..',function(p)return string.char(tonumber(p,16)) end):reverse() end
M.u32=u32;M.i32=i32
local AVATAR=hash('4d1c334d294dfa97')
M.vehicles={
 [hash('cc21c7ffd3ebefb9')]='m102',
 [hash('e9cd1d0d118886af')]='m102',
 [hash('9b2140378640432e')]='m103',
 [hash('2d85bfe3d8717fe5')]='m104',
 [hash('16474112801385b6')]='bastion',
 [hash('b0c9faf4af8903f9')]='maelstrom',
 [hash('423ff97d57ab04f5')]='tanker',
}
function M.current(api,s)
 for _,g in ipairs(s.guards) do if api.read(g.address,#g.bytes)~=g.bytes then return false end end
 return true
end
function M.capture(api,game,build)
 assert(build and (build.layout_schema=='seat-layout-v1' or build.source_build==25327279),'Missing validated seat layout')
 local s={guards={},reads=0}
 local function get(address,size)
  s.reads=s.reads+1;assert(s.reads<=300,'Read limit')
  local data=api.read(address,size);assert(data and #data==size,'Unreadable state')
  s.guards[#s.guards+1]={address=address,bytes=data};return data
 end
 local function ptr(data,offset)local p=api.pointer(data,offset);assert(p,'Invalid pointer');return p end
 local function global(rva)return ptr(get(game+rva,8))end
 local function lookup(header,key,maxcap)
  local cap,empty,mult=u32(header,8),u32(header,12),u32(header,16)
  if cap==0 then return nil end
  assert(cap<=maxcap and bit.band(cap,cap-1)==0,'Invalid map size')
  local data=ptr(header)
  local start=tonumber(ffi.cast('uint32_t',ffi.new('uint64_t',key)*ffi.new('uint64_t',mult)))
  for j=0,math.min(64,cap)-1 do
   local row=get(data+8*bit.band(start+j,cap-1),8)
   if u32(row,0)==key then local n=u32(row,4);return n~=0xffffffff and n or nil end
   if u32(row,0)==empty then return nil end
  end
  return nil
 end
 local mission=get(global(build.globals.mission),0x44)
 if u32(mission,8)==0 or u32(mission,0x40)<1 or u32(mission,0x40)>7 then return nil,'not_in_mission' end
 local pm=global(build.globals.player);local counts=get(pm+0x84,8)
 assert(u32(counts,0)<=4 and u32(counts,4)<=4,'Unsupported player count')
 if u32(counts,0)==0 or u32(counts,4)==0 then return nil,'no_player' end
 s.player_count=u32(counts,0)
 s.peer_count=u32(get(global(build.globals.session)+0x162d8,4),0)
 assert(s.peer_count<=4,'Unsupported peer count')
 local player=get(ptr(get(pm+0xe8,8)),24)
 if bit.band(player:byte(21),1)==0 then return nil,'no_local_player' end
 local unit=u32(get(pm+0x3a8,4),0)
 if unit==0x7fff then return nil,'no_avatar' end
 local entities=global(build.globals.entities)
 local ei=lookup(get(entities+build.layout.entity_unit_map,20),unit,1048576)
 if not ei then return nil,'no_avatar' end
 assert(ei<262144,'Entity index exceeds bound')
 s.avatar_address=entities+build.layout.entity_records+ei*24
 local avatar=get(s.avatar_address,24)
 if avatar:sub(1,8)~=AVATAR or bit.band(avatar:byte(21),1)==0 then return nil,'not_local_avatar' end
 s.avatar=u32(avatar,8);s.avatar_unit=u32(avatar,12)
 local avatars=global(build.globals.avatar);local ai=lookup(get(avatars+0xf8,20),s.avatar,64)
 if not ai then return nil,'no_avatar_component' end
 local acount=u32(get(avatars+0x6c,4),0)
 assert(acount<=8 and ai<acount,'Avatar index exceeds bound')
 if get(ptr(get(avatars+0x110+ai*8,8)),24)~=avatar then return nil,'avatar_mismatch' end
 -- Read the same permission bit tested by native vehicle input at a7d450.
 local vehicle_input=u32(get(avatars+0x53e88c+ai*0x1238,4),0)
 if bit.band(vehicle_input,0x40000)==0 then return nil,'native_vehicle_input_inactive' end
 s.seaters=global(build.globals.seater)
 local sh=get(s.seaters,0x50);local count=u32(sh,0xc)
 assert(count<=u32(sh,8) and u32(sh,8)<=256,'Invalid seater count')
 local si=lookup(sh:sub(0x21,0x34),s.avatar,1024)
 if not si or si>=count then return nil,'not_seated' end
 s.seater_index=si
 if get(ptr(get(ptr(sh,0x38)+si*8,8)),24)~=avatar then return nil,'seater_mismatch' end
 local states=get(ptr(sh,0x48),count*64)
 s.seater=ptr(sh,0x48)+si*64
 local current=states:sub(si*64+1,(si+1)*64)
 s.seater_bytes=current;s.collection=u32(current,0)
 if s.collection==0 or s.collection==0xffffffff then return nil,'not_seated' end
 s.node=i32(current,0x1c);s.active=current:byte(0x32)==1
 if current:byte(0x31)~=0 or i32(current,0x14)~=s.node or s.node<0 then return nil,'transition_in_progress' end
 if i32(current,0x18)~=-1 or i32(current,0x20)~=-1 then return nil,'transition_pending' end
 s.collections=global(build.globals.collection)
 local ch=get(s.collections,0x58)
 local cc=u32(ch,0xc);assert(cc<=u32(ch,8) and u32(ch,8)<=256,'Invalid collection count')
 local ci=lookup(ch:sub(0x21,0x34),s.collection,1024)
 if not ci or ci>=cc then return nil,'no_vehicle_component' end
 s.collection_index=ci
 s.collection_address=ptr(get(ptr(ch,0x38)+ci*8,8))
 local vehicle=get(s.collection_address,24)
 assert(u32(vehicle,8)==s.collection,'Vehicle identity mismatch')
 local cs=get(ptr(ch,0x48)+ci*100,100)
 s.resource=vehicle:sub(1,8):reverse():gsub('.',function(c)return string.format('%02x',c:byte()) end)
 s.vehicle=M.vehicles[vehicle:sub(1,8)]
 if not s.vehicle then return nil,'unsupported_vehicle resource='..s.resource..' transition='..u32(cs,0) end
 s.profile=assert(build.tables[s.vehicle],'Missing vehicle table')
 s.owned=bit.band(vehicle:byte(21),1)~=0
 s.collection_unit=u32(vehicle,0x10)
 if u32(cs,0)~=s.profile.transition or u32(current,4)~=s.profile.transition then return nil,'transition_profile_mismatch' end
 s.transition=s.profile.transition
 if s.node>=#s.profile.roles or u32(current,8)~=s.profile.roles[s.node+1] then return nil,'seat_role_mismatch' end
 s.mask=u32(get(ptr(ch,0x50)+ci*12,12),0)
 if bit.band(s.mask,bit.lshift(1,s.node))~=0 then return nil,'current_seat_not_reserved' end
 s.occupied={}
 for node=0,#s.profile.roles-1 do s.occupied[node]=bit.band(s.mask,bit.lshift(1,node))==0 end
 for i=0,count-1 do
  local offset=i*64
  if i~=si and u32(states,offset)==s.collection then
   for _,field in ipairs({0x14,0x18,0x1c}) do
    local node=i32(states,offset+field)
    if node>=0 and node<#s.profile.roles then s.occupied[node]=true end
   end
  end
 end
 s.graph={}
 local graph=get(game+s.profile.rva,s.profile.row*#s.profile.roles)
 for node=0,#s.profile.roles-1 do
  local row,terminated={},false
  for j=0,s.profile.row/4-1 do
   local target=i32(graph,node*s.profile.row+j*4)
   if target==-1 then terminated=true;break end
   assert(target>=0 and target<#s.profile.roles,'Unsupported seat adjacency')
   row[#row+1]=target
  end
  assert(terminated,'Unterminated seat adjacency');s.graph[node]=row
 end
 s.identity=avatar:sub(1,20)..vehicle:sub(1,20)
 return s
end
-- The native next/previous helpers walk these lists and the free-seat mask.
function M.predictions(s)
 local function free(node)return bit.band(s.mask,bit.lshift(1,node))~=0 end
 local node,nextseat=s.node,nil;local visited={}
 for _=1,32 do
  if visited[node] then break end;visited[node]=true
  local row=s.graph[node];if not row or not row[1] then break end
  for _,target in ipairs(row) do if free(target) then nextseat=target;break end end
  if nextseat then break end
  node=row[1];if node==s.node then break end
 end
 node=s.node;local previous,done=nil,false;visited={}
 for _=1,32 do
  if visited[node] then break end;visited[node]=true
  local row=s.graph[node];if not row or not row[1] then break end
  local found
  for _,target in ipairs(row) do
   if free(target) then previous=target;found=target;break end
   if target==s.node then done=true;break end
  end
  if done then break end
  node=found or row[1]
 end
 return nextseat,done and previous or nil
end
return M
