local ffi=require('ffi')
local profile=assert(loadfile('work/seat_switch/src/profile.lua'))()
local factory=assert(loadfile('work/seat_multi_vehicle_fix/driver.lua'))()
local game=0x10000000;local regions={};local writes=0
local function region(a,n)local b=ffi.new('uint8_t[?]',n);regions[#regions+1]={a=a,n=n,b=b};return b end
local function put(b,o,t,v)local x=ffi.new(t..'[1]',v);ffi.copy(b+o,x,ffi.sizeof(x)) end
local function u(b,o,v)put(b,o,'uint32_t',v)end
local function p(b,o,v)put(b,o,'uint64_t',v)end
local global=region(game+profile.driver.global,8);p(global,0,0x20000000)
local manager=region(0x20000000,0x80);u(manager,0x24,2)
p(manager,0x38,0x21000000);u(manager,0x40,4);u(manager,0x44,0xffffffff);u(manager,0x48,1)
local rows=region(0x21000000,32)
for i=0,3 do u(rows,i*8,0xffffffff) end;u(rows,8,9);u(rows,12,1)
p(manager,0x50,0x22000000);local owners=region(0x22000000,16);p(owners,8,0x23000000)
local entity=region(0x23000000,24);u(entity,8,9);entity[20]=1
p(manager,0x58,0x24000000);local states=region(0x24000000,96)
ffi.fill(states,96,0x5a)
local api={ffi=ffi}
function api.read(a,n)
 for _,proof in ipairs(profile.driver.proofs) do if a==game+proof.rva then return proof.bytes end end
 for _,r in ipairs(regions) do if a>=r.a and a+n<=r.a+r.n then return ffi.string(r.b+(a-r.a),n) end end
end
function api.pointer(b)if not b or #b<8 then return nil end;local x=ffi.new('uint64_t[1]');ffi.copy(x,b,8);return tonumber(x[0])>=65536 and tonumber(x[0]) or nil end
function api.replace(a,b,c)
 assert(a==0x24000000+48+24 and #b==24 and #c==24)
 if api.read(a,#b)~=b then return false end
 ffi.copy(states+72,c,24);writes=writes+1;return true
end
local s={owned=true,vehicle="m102",player_count=2,peer_count=2,profile=profile.tables.m102,node=0,collection=9,collection_address=0x23000000}
local d=factory(api,game,profile)
for _,steer in ipairs({-1,1}) do
 for i=0,4 do put(states,72+i*4,'float',i==2 and steer or 1) end
 states[92]=1;states[93]=0x55;states[94]=1;states[95]=1
 local untouched=ffi.string(states,72);d.prepare(s)()
 assert(ffi.string(states,72)==untouched,'Other vehicle/camera vectors modified')
 assert(ffi.string(states+72,20)==string.rep('\0',20),'Throttle/brake/steer/directional commands remain')
 assert(states[92]==1 and states[93]==0x55 and states[94]==0 and states[95]==0,'Mode flags/held buttons wrong')
end
local count=writes
local run=d.prepare(s);put(states,80,'float',0.5);assert(not pcall(run) and writes==count,'Concurrent input change must refuse stale write')
run=d.prepare(s);u(rows,12,0);assert(not pcall(run) and writes==count,'Component move must refuse stale write');u(rows,12,1)
entity[20]=0;assert(not pcall(d.prepare,s) and writes==count,'Lost ownership must refuse');entity[20]=1
s.player_count=3;assert(not pcall(d.prepare,s) and writes==count,'Three players must refuse');s.player_count=2
s.node=2;assert(not pcall(d.prepare,s) and writes==count,'Passenger must not clear driver input')
local layout=assert(loadfile('work/seat_multi_vehicle_fix/adapter.lua'))().layout
d=factory(api,game,profile,layout)
for _,name in ipairs({'m102','m103','m104','bastion','maelstrom'})do
 s.vehicle=name;s.profile=profile.tables[name];s.transition=s.profile.transition;s.node=0
 for _,steer in ipairs({-1,1})do
  ffi.fill(states,96,0x5a);for i=0,4 do put(states,72+i*4,'float',i==2 and steer or 1)end
  states[92]=1;states[93]=0x55;states[94]=1;states[95]=1
  local other=ffi.string(states,72);d.prepare(s)()
  assert(ffi.string(states,72)==other and ffi.string(states+72,20)==string.rep('\0',20))
  assert(states[92]==1 and states[93]==0x55 and states[94]==0 and states[95]==0)
 end
 local before=writes;s.transition=99;assert(not pcall(d.prepare,s)and writes==before)
end
print('PASS ten real driver neutralization cases across five layouts; stale/wrong transition blocked; other records preserved')
print('PASS: both turning directions and all five retained driver commands neutralized; other vehicle/camera vectors and mode flags preserved; input races, identity, ownership and multiplayer guards. Memory synthetic.')
