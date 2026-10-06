local ffi,bit=require('ffi'),require('bit')
local snapshot=assert(loadfile('work/seat_switch/src/snapshot.lua'))()
local profile=assert(loadfile('work/seat_switch/src/profile.lua'))()
local game=0x10000000
local regions={}
local function region(addr,n)local b=ffi.new('uint8_t[?]',n);regions[#regions+1]={a=addr,n=n,b=b};return b end
local function put(b,o,t,v)local x=ffi.new(t..'[1]',v);ffi.copy(b+o,x,ffi.sizeof(x)) end
local function u(b,o,v)put(b,o,'uint32_t',v)end
local function p(b,o,v)put(b,o,'uint64_t',v)end
local function hash(b,s)for i=1,8 do b[i-1]=tonumber(s:sub(17-i*2,18-i*2),16) end end
local function map(b,o,addr,key,value)
 p(b,o,addr);u(b,o+8,4);u(b,o+12,0xffffffff);u(b,o+16,0x9e3779b9)
 local rows=region(addr,32);for i=0,3 do u(rows,i*8,0xffffffff);u(rows,i*8+4,0xffffffff) end
 local slot=bit.band(tonumber(ffi.cast('uint32_t',ffi.new('uint64_t',key)*ffi.new('uint64_t',0x9e3779b9))),3)
 u(rows,slot*8,key);u(rows,slot*8+4,value)
end
local mission=region(0x20000000,0x44);local pm=region(0x20001000,0x400)
local avatars=region(0x21000000,0x54a000);local seater=region(0x22000000,0x100)
local collections=region(0x22001000,0x100);local session=region(0x23000000,0x16300)
local entities=0x24000000
local pointers={mission=0x20000000,player=0x20001000,entities=entities,avatar=0x21000000,seater=0x22000000,collection=0x22001000,session=0x23000000}
for name,rva in pairs(profile.globals) do p(region(game+rva,8),0,pointers[name]) end
u(mission,8,1);u(mission,0x40,2);u(pm,0x84,1);u(pm,0x88,1);u(pm,0x3a8,9)
local player=region(0x25000000,24);player[20]=1;p(pm,0xe8,0x25000000)
map(region(entities+profile.layout.entity_unit_map,20),0,0x25001000,9,0)
local av=region(entities+profile.layout.entity_records,24);hash(av,'4d1c334d294dfa97');u(av,8,0xabc98761);u(av,12,9);av[20]=1
map(avatars,0xf8,0x25002000,0xabc98761,0);u(avatars,0x6c,1);p(avatars,0x110,entities+profile.layout.entity_records);u(avatars,0x53e88c,0x40000)
u(seater,8,4);u(seater,0xc,2);map(seater,0x20,0x25003000,0xabc98761,0)
local sr=region(0x25004000,16);p(sr,0,entities+profile.layout.entity_records);p(seater,0x38,0x25004000)
local states=region(0x25005000,128);p(seater,0x48,0x25005000)
u(states,0,0xabc);u(states,4,26);u(states,8,1);u(states,0x14,0);u(states,0x18,0xffffffff);u(states,0x1c,0);u(states,0x20,0xffffffff)
u(states,64,0xabc);u(states,64+0x14,2);u(states,64+0x18,3);u(states,64+0x1c,2)
u(collections,8,4);u(collections,0xc,1);map(collections,0x20,0x25006000,0xabc,0)
local cr=region(0x25007000,8);p(cr,0,0x25008000);p(collections,0x38,0x25007000)
local vehicle=region(0x25008000,24);hash(vehicle,'cc21c7ffd3ebefb9');u(vehicle,8,0xabc);u(vehicle,16,33);vehicle[20]=1
local cs=region(0x25009000,100);u(cs,0,26);p(collections,0x48,0x25009000)
local mask=region(0x2500a000,12);u(mask,0,30);p(collections,0x50,0x2500a000)
local graph=region(game+profile.tables.m102.rva,40)
for i,v in ipairs({1,-1,0,-1,3,-1,2,-1,-1,-1}) do u(graph,(i-1)*4,v) end
local api={}
function api.read(a,n)for _,r in ipairs(regions) do if a>=r.a and a+n<=r.a+r.n then return ffi.string(r.b+(a-r.a),n) end end end
function api.pointer(b,o)if not b then return nil end;local x=ffi.new('uint64_t[1]');ffi.copy(x,b:sub((o or 0)+1),8);return tonumber(x[0])>65535 and tonumber(x[0]) or nil end
local s,why=snapshot.capture(api,game,profile);assert(s,why)
assert(s.node==0 and s.vehicle=='m102' and s.player_count==1 and s.peer_count==0)
assert(s.occupied[0] and not s.occupied[1] and s.occupied[2] and s.occupied[3] and not s.occupied[4])
assert(snapshot.current(api,s));u(mask,0,28);assert(not snapshot.current(api,s),'New occupancy must invalidate pending operation')
u(mask,0,31);assert(select(2,snapshot.capture(api,game,profile))=='current_seat_not_reserved')
u(mask,0,30);u(states,0x18,1);assert(select(2,snapshot.capture(api,game,profile))=='transition_pending');u(states,0x18,0xffffffff)
u(avatars,0x53e88c,0);assert(select(2,snapshot.capture(api,game,profile))=='native_vehicle_input_inactive');u(avatars,0x53e88c,0x40000)
vehicle[20]=0;s=assert(snapshot.capture(api,game,profile));assert(not s.owned);vehicle[20]=1
hash(vehicle,'1234567890abcdef');assert(select(2,snapshot.capture(api,game,profile)):match('unsupported_vehicle'))
u(cs,0,44);u(states,4,44);u(mask,0,14)
assert(select(2,snapshot.capture(api,game,profile)):match('unsupported_vehicle'),'Graph 44 alone must not authorize an unknown resource')
hash(vehicle,'b0c9faf4af8903f9')
local mg=region(game+profile.tables.maelstrom.rva,48)
for i,v in ipairs({-1,-1,-1,2,3,-1,3,1,-1,1,2,-1}) do u(mg,(i-1)*4,v) end
s=assert(snapshot.capture(api,game,profile));assert(s.vehicle=='maelstrom' and not s.provisional_identity and #s.profile.roles==4 and s.avatar_unit==9)
-- A different four-seat graph is never accepted by shape alone.
u(cs,0,42);u(states,4,42);assert(select(2,snapshot.capture(api,game,profile))=='transition_profile_mismatch')
u(pm,0x84,5);assert(not pcall(snapshot.capture,api,game,profile),'Corrupt bounds must fail closed')
print('PASS: current-build snapshot, entity identity, all seat claims, stale state, input bit, confirmed Maelstrom resource and bounds. Memory is synthetic.')
