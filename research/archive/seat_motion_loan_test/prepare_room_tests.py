from pathlib import Path

R=Path(__file__).resolve().parent
base=(R/'test_observe.lua').read_text(encoding='utf-8')
base=base[:base.index('setup();local o=assert(observer:capture(s));')]
cases=r'''
local PEERS={LOCAL,FRIEND,peer(0x76543213,0xfedcba98),peer(0x76543214,0xfedcba98)}
for i,key in ipairs(PEERS)do reader.peers[key]='P'..i end
local fleet={vehicle,
 {id=722,unit=8391233,network_unit=4119,resource='fixture2',name='bastion',seat_count=4,owned_local=false},
 {id=723,unit=8391234,network_unit=4120,resource='fixture3',name='m104',seat_count=3,owned_local=false}}
local original_setup=setup
local function room_setup(count,host)
 original_setup()
 s.player_count=count;s.peer_count=count;s.vehicles=fleet;s.peers={};s.avatars={}
 local raw='';for i=1,count do raw=raw..PEERS[i];s.peers[i]='P'..i end
 put(S+0x162d8,le(count));put(S+0x162e0,raw)
 put(E+0x130,PEERS[host]);put(S+0xb3a8,PEERS[host])
 local owners,units={},{}
 for i,v in ipairs(fleet)do
  owners[v.network_unit]=PEERS[(i%count)+1];units[#units+1]=v.network_unit
 end
 for i=1,count do
  local a={id=i*11,unit=100+i,network_unit=4100+i,is_local=i==1,owned_local=i==1,
   vehicle_input=i~=count,seat={collection=i==1 and fleet[1].id or i==2 and fleet[2].id or 0,
   current=0,reserved=0,role=1,target=-1,action=-1,transitioning=0,queued_exit=0}}
  s.avatars[i]=a;owners[a.network_unit]=PEERS[i];units[#units+1]=a.network_unit
 end
 put(E+0x640,le(32)..le(32));put(E+0x648,ptr(ROWS)..ptr(0)..le(#units)..le(32))
 local free,links={},{ }
 for i=0,31 do free[i]=true;put(ROWS+i*0x248+0x240,le(0xfffffffe))end
 for _,unit in ipairs(units)do
  local h=mul(unit,0x5bd1e995);h=bit.bxor(h,bit.rshift(h,24));if h<0 then h=h+4294967296 end
  local index=mul(h,0x5bd1e995)%32
  if not free[index]then
   local tail=index;while links[tail]do tail=links[tail]end
   for k=0,31 do if free[k]then index=k;break end end
   links[tail]=index;put(ROWS+tail*0x248+0x240,le(index))
  end
  free[index]=nil;indices[unit]=index
  local at=ROWS+index*0x248
  put(at,le(unit));put(at+8,le(7)..le(unit));put(at+16,owners[unit])
  put(at+0x23a,'\1\0\0\0');put(at+0x240,le(0x7fffffff))
 end
 put(BUSY+0xb020,ptr(BHASH)..le(8)..le(0xffffffff)..le(1))
 for i=0,7 do put(BHASH+i*8,le(0xffffffff)..le(0xffffffff))end
 for i,v in ipairs(fleet)do
  put(BHASH+(v.network_unit%8)*8,le(v.network_unit)..le(i-1));put(BUSY+0x201c+i-1,'\0')
 end
 return owners
end
local cases=0
for count=1,4 do for host=1,count do
 local owners=room_setup(count,host)
 for _,v in ipairs(fleet)do
  local o=assert(observer:capture(s,v,'all'))
  assert(o.peer_count==count and o.coordinator==PEERS[host] and o.owner==owners[v.network_unit] and not o.busy)
  local actual=0;for raw in pairs(o.members)do actual=actual+1 end;assert(actual==count)
  for i,a in ipairs(s.avatars)do assert(o.avatars[a.id].owner==PEERS[i] and o.members[o.avatars[a.id].owner])end
  local summary=observer:summary(o);assert(summary.owner==reader.peers[owners[v.network_unit]])
  cases=cases+1
 end
end end
local owners=room_setup(4,4)
put(BUSY+0x201d,'\1');assert(observer:capture(s,fleet[2],'all').busy and not observer:capture(s,fleet[1],'all').busy)
-- Observed membership/owner changes must never turn into an authority request.
assert(#sends==0)
for _,change in ipairs({
 function()put(S+0x162e0,LOCAL..FRIEND..PEERS[3]..PEERS[3])end,
 function()put(S+0x162d8,le(5))end,
 function()put(S+0xb3a8,LOCAL)end,
 function()put(E+0x65c,le(0))end,
})do
 room_setup(4,4);change();assert(not pcall(observer.capture,observer,s,fleet[1],'all'))
end
assert(#sends==0)
print('PASS '..cases..' real ownership-reader fleet cases: 1/2/3/4 peers, every coordinator, three independent vehicles, all-avatar owners including another car/outside, per-vehicle busy, full-width peer IDs, 4 malformed-room guards; zero game calls/sends. Engine memory synthetic; code from immutable capture.')
'''
(R/'test_room_observe.lua').write_text(base+cases,encoding='utf-8')
print('Prepared real ownership-reader fleet fixture')
