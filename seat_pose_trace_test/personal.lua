return function(api,game,profile)
 local ffi=api.ffi
 local function personal_ready(s)
  local function get(a,n)local b=api.read(a,n);assert(b and #b==n,'Unreadable personal inventory');return b end
  local function ptr(b)local p=api.pointer(b);assert(p,'Invalid personal inventory pointer');return p end
  local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);return a+c*256+d*65536+e*16777216 end
  local inv=ptr(get(game+profile.globals.inventory,8))
  local h=get(inv+0x28,20);local cap,empty,mult=u32(h,8),u32(h,12),u32(h,16)
  local bit=require('bit')
  assert(cap>0 and cap<=4096 and bit.band(cap,cap-1)==0,'Invalid inventory map')
  local rows=ptr(h)
  local start=tonumber(ffi.cast('uint32_t',ffi.new('uint64_t',s.avatar)*ffi.new('uint64_t',mult)))
  local index
  for j=0,math.min(cap,64)-1 do
   local row=get(rows+8*bit.band(start+j,cap-1),8)
   if u32(row,0)==s.avatar then index=u32(row,4);break end
   if u32(row,0)==empty then break end
  end
  assert(index and index<1024,'Missing personal inventory')
  local owner=ptr(get(ptr(get(inv+0x40,8))+index*8,8))
  assert(owner==s.avatar_address,'Personal inventory identity mismatch')
  local data=get(ptr(get(inv+0x50,8))+index*48,48)
  local slot=u32(data,0x1c);assert(slot<=6,'Invalid personal weapon selection')
  -- Native completion preserves slots 1..4 and falls back to 1 otherwise.
  local offset=({[1]=0,[2]=4,[3]=8,[4]=16})[slot] or 0
  local weapon=u32(data,offset)
  assert(weapon~=0 and weapon~=0xffffffff,'Missing selected personal weapon')
  return true,weapon
 end
 return personal_ready
end
