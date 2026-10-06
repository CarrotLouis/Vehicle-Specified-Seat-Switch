-- Neutralize persistent driver commands, not physical vehicle velocity.
return function(api,game,profile,vehicle_layout)
 local ffi,bit=api.ffi,require('bit')
 local layout=assert(profile.driver,'Missing validated driver layout')
 for _,p in ipairs(layout.proofs) do
  assert(api.read(game+p.rva,#p.bytes)==p.bytes,'Driver input signature mismatch')
 end
 local function read(a,n)local b=api.read(a,n);assert(b and #b==n,'Unreadable driver state');return b end
 local function ptr(b)local p=api.pointer(b);assert(p,'Invalid driver pointer');return p end
 local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);return a+c*256+d*65536+e*16777216 end
 local function locate(s)
  local manager=ptr(read(game+layout.global,8))
  local h=read(manager+0x38,20);local cap,empty,mult=u32(h,8),u32(h,12),u32(h,16)
  assert(cap>0 and cap<=16384 and bit.band(cap,cap-1)==0,'Invalid driver map')
  local rows=ptr(h)
  local start=tonumber(ffi.cast('uint32_t',ffi.new('uint64_t',s.collection)*ffi.new('uint64_t',mult)))
  local index
  for j=0,math.min(cap,64)-1 do
   local row=read(rows+8*bit.band(start+j,cap-1),8)
   if u32(row,0)==s.collection then index=u32(row,4);break end
   if u32(row,0)==empty then break end
  end
  assert(index and index<u32(read(manager+0x24,4),0) and index<4096,'Missing driver component')
  local owner=ptr(read(ptr(read(manager+0x50,8))+index*8,8))
  assert(owner==s.collection_address,'Driver vehicle identity mismatch')
  local entity=read(owner,24)
  assert(u32(entity,8)==s.collection and bit.band(entity:byte(21),1)~=0,'Driver vehicle authority changed')
  return ptr(read(manager+0x58,8))+index*48+0x18
 end
 return {prepare=function(s)
  assert(s.owned and (vehicle_layout and vehicle_layout(s)or not vehicle_layout and s.vehicle=='m102')and s.player_count>=1 and s.player_count<=4 and s.peer_count==s.player_count and s.node==0 and s.profile.roles[s.node+1]==1,'Driver reset requires validated local multiplayer driver')
  local address=locate(s);local before=read(address,24)
  -- +18/+1c/+20 throttle/brake/steer; +24/+28 retained directional
  -- commands are independently written even in the native inhibited branch.
  -- Preserve +2c/+2d mode flags; release the two remaining held buttons.
  local after=string.rep('\0',20)..before:sub(21,22)..'\0\0'
  return function()
   assert(locate(s)==address,'Driver component moved')
   assert(api.replace(address,before,after),'Driver commands changed before neutralization')
   assert(read(address,24)==after,'Driver neutralization readback failed')
  end
 end}
end
