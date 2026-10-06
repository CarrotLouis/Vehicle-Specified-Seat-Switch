-- Real FFI arguments and native-call routing; native physics effects simulated.
local ffi=require('ffi');local profiles=assert(loadfile('work/seat_switch/src/profile.lua'))().tables
local layout=assert(loadfile('work/seat_physics_motion_test/adapter.lua'))().layout
local regions={};local function number(p)return tonumber(ffi.cast('uintptr_t',p))end
local function region(a,n)local b=ffi.new('uint8_t[?]',n);regions[#regions+1]={a=a,n=n,b=b};return b end
local function put(b,o,t,n)local v=ffi.new(t..'[1]',n);ffi.copy(b+o,v,ffi.sizeof(v))end
local function u(b,o,n)put(b,o,'uint32_t',n)end
local function ptr(b,o,n)put(b,o,'uint64_t',n)end
local global=region(0x10000,8);ptr(global,0,0x20000)
local manager=region(0x20000,0x80);u(manager,0x24,2);ptr(manager,0x38,0x30000);u(manager,0x40,4);u(manager,0x44,0xffffffff);u(manager,0x48,1)
local rows=region(0x30000,32);for i=0,3 do u(rows,i*8,0xffffffff)end;u(rows,8,9);u(rows,12,1)
ptr(manager,0x50,0x40000);local entities=region(0x40000,16);ptr(entities,8,0x50000)
local entity=region(0x50000,24);u(entity,8,9);u(entity,16,909);entity[20]=1
ptr(manager,0x58,0x60000);local commands=region(0x60000,96);ffi.fill(commands,96,0x5a)
ptr(manager,0x68,0x70000);local runtime=region(0x70000,0xd28*2);ffi.fill(runtime,0xd28*2,0x5a)
local calls=0
local cb=ffi.cast('void (*)(void *,uint32_t,bool)',function(first,id,active)
 assert(first==nil and id==9 and not active);calls=calls+1;runtime[0xd28+0xd18]=0
end)
local p={driver={global=0x10000},functions={tank_driver_active={rva=number(cb),bytes='proof'}}}
local api={ffi=ffi}
function api.read(a,n)
 a=number(a);if a==number(cb)then return ('proof'):sub(1,n)end
 for _,r in ipairs(regions)do if a>=r.a and a+n<=r.a+r.n then return ffi.string(r.b+(a-r.a),n)end end
end
function api.pointer(b)local v=ffi.new('uint64_t[1]');ffi.copy(v,b,8);return v[0]>65535 and ffi.cast('uint8_t *',v[0])or nil end
local emit=function()end;local d=assert(loadfile('work/seat_physics_motion_test/tank_driver.lua'))()(api,ffi.cast('uint8_t *',0),p,layout,emit)
local s={collection=9,collection_unit=909,collection_address=ffi.cast('uint8_t *',0x50000),owned=true,player_count=2,peer_count=2,node=0}
for _,name in ipairs({'bastion','maelstrom'})do for _,active in ipairs({0,1})do
 s.vehicle=name;s.profile=profiles[name];s.transition=s.profile.transition;runtime[0xd28+0xd18]=active
 local before=ffi.string(runtime,0xd28*2);local cmds=ffi.string(commands,96);local old=calls
 local run=d:prepare(s);assert(calls==old);run()
 assert(calls==old+1 and runtime[0xd28+0xd18]==0 and ffi.string(commands,96)==cmds)
 local at=0xd28+0xd18
 assert(ffi.string(runtime,0xd28*2)==before:sub(1,at)..'\0'..before:sub(at+2))
 assert(not pcall(run)and calls==old+1)
end end
runtime[0xd28+0xd18]=1;local old=calls;local run=d:prepare(s)
entity[20]=0;assert(not pcall(run)and calls==old);entity[20]=1
run=d:prepare(s);u(rows,12,0);assert(not pcall(run)and calls==old);u(rows,12,1)
for _,change in ipairs({function()s.owned=false end,function()s.peer_count=3 end,function()s.node=2 end,
 function()s.transition=43 end,function()s.vehicle='m102';s.profile=profiles.m102;s.transition=26 end,
 function()u(entity,16,910)end,function()runtime[0xd28+0xd18]=7 end})do
 s.vehicle='maelstrom';s.profile=profiles.maelstrom;s.transition=44;s.owned=true;s.peer_count=2;s.node=0;u(entity,16,909);runtime[0xd28+0xd18]=1
 change();assert(not pcall(d.prepare,d,s)and calls==old)
end
cb:free()
print('PASS tank native-exit FFI: both layouts, active/inactive, exact null/entity/false arguments, one-shot, ownership/network identity/moved component/invalid flag guards; no writes to neighbour or command buffers. Physics mocked.')
