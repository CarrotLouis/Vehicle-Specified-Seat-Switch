-- Native tank driver-exit cleanup, without running its exit/entry animation.
-- Both tank action tables call this same routine with r8=false on driver exit.
return function(api,game,p,layout,emit)
 local ffi,bit=api.ffi,require('bit')
 local f=assert(p.functions.tank_driver_active,'Missing validated tank driver interface')
 assert(api.read(game+f.rva,#f.bytes)==f.bytes,'Tank driver interface changed')
 local native=ffi.cast('void (*)(void *,uint32_t,bool)',game+f.rva)
 local function read(a,n)local b=api.read(a,n);assert(b and #b==n,'Unreadable tank driver state');return b end
 local function ptr(a)return assert(api.pointer(read(a,8)),'Invalid tank driver pointer')end
 local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);assert(e);return a+c*256+d*65536+e*16777216 end
 local function locate(s)
  local manager=ptr(game+p.driver.global)
  local header=read(manager+0x38,20);local rows=assert(api.pointer(header))
  local cap,empty,mult=u32(header,8),u32(header,12),u32(header,16)
  assert(cap>0 and cap<=16384 and bit.band(cap,cap-1)==0,'Tank driver map changed')
  local start=((s.collection%cap)*(mult%cap))%cap;local index
  for i=0,math.min(cap,64)-1 do
   local row=read(rows+((start+i)%cap)*8,8)
   if u32(row,0)==s.collection then index=u32(row,4);break end
   if u32(row,0)==empty then break end
  end
  assert(index and index<4096 and index<u32(read(manager+0x24,4),0),'Tank driver component absent')
  local owner=ptr(ptr(manager+0x50)+index*8)
  assert(owner==s.collection_address,'Tank driver vehicle changed')
  local entity=read(owner,24)
  assert(u32(entity,8)==s.collection and u32(entity,16)==s.collection_unit and bit.band(entity:byte(21),1)~=0,'Tank driver authority/identity changed')
  local commands=ptr(manager+0x58)+index*48
  local runtime=ptr(manager+0x68)+index*0xd28
  local active=read(runtime+0xd18,1):byte();assert(active==0 or active==1,'Tank driver active flag changed')
  return {commands=commands,runtime=runtime,active=active,command_bytes=read(commands,48),tail=read(runtime+0xd08,32)}
 end
 local function hex(b)return (b:gsub('.',function(c)return string.format('%02x',c:byte())end))end
 return {prepare=function(_,s)
  local d=layout(s)
  assert(d and d.tank and s.node==0 and d.roles[1]==1 and s.owned and not s.active and s.player_count==2 and s.peer_count==2,'Tank driver exit scope')
  local before=locate(s);local used=false
  return function()
   assert(not used,'Tank driver exit already invoked')
   assert(api.read(game+f.rva,#f.bytes)==f.bytes,'Tank driver code changed before exit')
   local fresh=locate(s)
   assert(fresh.runtime==before.runtime and fresh.commands==before.commands and fresh.active==before.active,'Tank driver state changed before exit')
   -- Generic command neutralization deliberately precedes this routine.
   emit({event='tank_driver_exit_invoking',vehicle=s.vehicle,collection=s.collection,driver_active=fresh.active,
    driver_command_hex=hex(fresh.command_bytes),runtime_tail_hex=hex(fresh.tail),native_active=false})
   used=true;native(nil,s.collection,false)
   local after=locate(s);assert(after.runtime==before.runtime and after.active==0,'Tank driver exit readback failed')
   emit({event='tank_driver_exit_returned',vehicle=s.vehicle,collection=s.collection,driver_active=after.active,
    driver_command_hex=hex(after.command_bytes),runtime_tail_hex=hex(after.tail),live_motion_not_confirmed=true})
  end
 end}
end
