local ffi=require('ffi')
local sampler=assert(loadfile('work/seat_network_diagnostic/sampler.lua'))()
local profile=assert(loadfile('work/seat_switch/src/profile.lua'))()
local game=0x10000000
local regions={}
local function region(a,n)local b=ffi.new('uint8_t[?]',n);regions[#regions+1]={a=a,n=n,b=b};return b end
local function put(b,o,t,v)local p=ffi.new(t..'[1]',v);ffi.copy(b+o,p,ffi.sizeof(p))end
local function u(b,o,v)put(b,o,'uint32_t',v)end
local function p(b,o,v)put(b,o,'uint64_t',v)end
local function resource(b,s)for i=1,8 do b[i-1]=tonumber(s:sub(17-i*2,18-i*2),16)end end
local function map(b,o,a,items)
 p(b,o,a);u(b,o+8,8);u(b,o+12,0xffffffff);u(b,o+16,1)
 local rows=region(a,64);for i=0,7 do u(rows,i*8,0xffffffff)end
 for key,value in pairs(items) do u(rows,(key%8)*8,key);u(rows,(key%8)*8+4,value)end
end
local pointers={mission=0x20000000,player=0x20001000,session=0x21000000,avatar=0x22000000,seater=0x23000000,collection=0x23001000,entities=0x30000000}
for name,a in pairs(pointers)do p(region(game+profile.globals[name],8),0,a)end
local mission=region(pointers.mission,0x44);u(mission,8,1);u(mission,64,2)
local pm=region(pointers.player,0x400);u(pm,0x84,2);u(pm,0x88,1);u(pm,0x3a8,501)
local entity_map=region(pointers.entities+profile.layout.entity_unit_map,20)
map(entity_map,0,0x25000000,{[501]=0,[502]=1})
local entity_records=region(pointers.entities+profile.layout.entity_records,48)
local session=region(pointers.session,0x16300);u(session,0x162d8,2);p(session,0x162e0,0x7ff812345678);p(session,0x162e8,0x7ff811112222)
local am=region(pointers.avatar,0x54a000);u(am,0x6c,2)
local sm=region(pointers.seater,0x100);u(sm,8,2);u(sm,12,2);u(sm,16,1)
local cm=region(pointers.collection,0x100);u(cm,8,1);u(cm,12,1);u(cm,16,0)
map(sm,0x20,0x24000000,{[101]=0,[102]=1});map(cm,0x20,0x24001000,{[201]=0})
local sr=region(0x24002000,16);p(sm,0x38,0x24002000)
local states=region(0x24003000,128);p(sm,0x48,0x24003000)
local avatars={}
for i=0,1 do
 local a=0x24004000+i*0x100;local b=region(a,24);avatars[i+1]=b
 resource(b,'4d1c334d294dfa97');u(b,8,101+i);u(b,12,11+i);u(b,16,21+i);u(b,20,i==0 and 1 or 0)
 p(am,0x110+i*8,a);p(sr,i*8,a);u(am,0x53e88c+i*0x1238,0x40000)
 u(states,i*64,201);u(states,i*64+4,26);u(states,i*64+8,i==0 and 3 or 1)
 u(states,i*64+20,i==0 and 1 or 0);u(states,i*64+24,0xffffffff);u(states,i*64+28,i==0 and 1 or 0);u(states,i*64+32,0xffffffff)
end
for i=0,1 do ffi.copy(entity_records+i*24,avatars[i+1],24)end
local cr=region(0x24005000,8);p(cr,0,0x24006000);p(cm,0x38,0x24005000)
local vehicle=region(0x24006000,24);resource(vehicle,'cc21c7ffd3ebefb9');u(vehicle,8,201);u(vehicle,12,31);u(vehicle,16,41)
local cs=region(0x24007000,100);u(cs,0,26);p(cm,0x48,0x24007000)
local mask=region(0x24008000,12);u(mask,0,28);p(cm,0x50,0x24008000)
local api={}
function api.read(a,n)for _,r in ipairs(regions)do if a>=r.a and a+n<=r.a+r.n then return ffi.string(r.b+(a-r.a),n)end end end
function api.pointer(b,o)if not b then return nil end;local a=ffi.new('uint64_t[1]');ffi.copy(a,b:sub((o or 0)+1),8);local n=tonumber(a[0]);return n>=65536 and n or nil end
local read=sampler.new(api,game,profile)
local s=assert(read:capture())
assert(s.player_count==2 and #s.avatars==2 and #s.vehicles==1)
assert(s.avatars[1].is_local and not s.avatars[2].is_local)
-- Handle 501 differs from both entity ID 101 and unit 11; no flag fallback.
u(pm,0x3a8,502);s=assert(read:capture())
assert(not s.avatars[1].is_local and not s.avatars[2].is_local)
u(pm,0x3a8,0x7fff);s=assert(read:capture())
assert(not s.avatars[1].is_local and not s.avatars[2].is_local)
u(pm,0x3a8,501);u(entity_records,8,999);s=assert(read:capture())
assert(not s.avatars[1].is_local,'stale entity identity must not match')
u(entity_records,8,101);s=assert(read:capture());assert(s.avatars[1].is_local)
assert(s.avatars[1].owned_local and not s.vehicles[1].owned_local)
assert(s.peers[1]=='P1' and s.peers[2]=='P2')
-- Capture the exact mid-transition that gameplay snapshot intentionally rejects.
u(states,24,3);u(states,28,3);u(states,32,12);states[48]=1;u(states,40,99999)
s=assert(read:capture());assert(s.avatars[1].seat.current==1 and s.avatars[1].seat.target==3 and s.avatars[1].seat.reserved==3 and s.avatars[1].seat.transitioning==1)
u(vehicle,20,1);s=assert(read:capture());assert(s.vehicles[1].owned_local)
-- Peer array ordering is retained without guessing host or self.
p(session,0x162e0,0x7ff811112222);p(session,0x162e8,0x7ff812345678)
s=assert(read:capture());assert(s.peers[1]=='P2' and s.peers[2]=='P1')
-- Retain the previously observed vehicle after both players leave it.
u(states,0,0);u(states,64,0);u(mask,0,31)
s=assert(read:capture());assert(#s.vehicles==1 and s.vehicles[1].free_mask==31)
-- A race in the seat claim must be recorded as a gap, not as a coherent state.
local original=api.read;local n=0
api.read=function(a,size)
 if a==0x24003000 and size==64 then n=n+1;if n==2 then u(states,24,4)end end
 return original(a,size)
end
local no,why=read:capture();assert(not no and why=='state_changed_during_read');api.read=original
u(session,0x162d8,5);assert(not pcall(read.capture,read));u(session,0x162d8,2)
u(am,0x6c,99);assert(not pcall(read.capture,read));u(am,0x6c,2)
u(cs,0,44);assert(not pcall(read.capture,read));u(cs,0,26)
u(mission,8,0);s=assert(read:capture());assert(s.state=='not_in_mission' and #s.vehicles==0)
local function fingerprint()local t={};for _,r in ipairs(regions)do t[#t+1]=ffi.string(r.b,r.n)end;return table.concat(t)end
local before=fingerprint();assert(read:capture());assert(fingerprint()==before,'Read-only capture changed memory')
print('PASS sampler: two peers, local/remote ownership, in-progress claims, empty vehicle tracking, peer aliases, races, corrupt bounds, read-only synthetic memory')
