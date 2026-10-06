local ffi=require('ffi')
local factory=assert(loadfile('work/seat_fleet_test/steering_watch.lua'))()
local regions={};local function number(p)return tonumber(ffi.cast('uintptr_t',p))end
local function region(a,n)local b=ffi.new('uint8_t[?]',n);regions[#regions+1]={a=a,n=n,b=b};return b end
local function put(b,o,t,n)local x=ffi.new(t..'[1]',n);ffi.copy(b+o,x,ffi.sizeof(x))end
local function u(b,o,n)put(b,o,'uint32_t',n)end
local function ptr(b,o,n)put(b,o,'uint64_t',n)end
local global=region(0x10000,8);ptr(global,0,0x20000)
local manager=region(0x20000,0x80);u(manager,0x24,2);ptr(manager,0x38,0x30000);u(manager,0x40,4);u(manager,0x44,0xffffffff);u(manager,0x48,1)
local rows=region(0x30000,32);for i=0,3 do u(rows,i*8,0xffffffff)end;u(rows,8,9);u(rows,12,1)
ptr(manager,0x50,0x40000);local entities=region(0x40000,16);ptr(entities,8,0x50000)
local entity=region(0x50000,24);ffi.copy(entity,'\182\133\19\128\18\65\71\22',8);u(entity,8,9);u(entity,12,99);u(entity,16,909);u(entity,20,1)
ptr(manager,0x58,0x60000);local commands=region(0x60000,96);put(commands,48,'float',-1);commands[48+46]=1
ptr(manager,0x68,0x70000);local runtime=region(0x70000,0xd28*2);runtime[0xd28+0xd18]=1
local now,keys=0,{[65]=true};local events={};local api={ffi=ffi,now=function()return now end,down=function(k)return keys[k]end,
 replace=function()error('No writes')end}
function api.read(a,n)
 a=number(a);if a==0x80000 then return ('proof'):sub(1,n)end
 for _,r in ipairs(regions)do if a>=r.a and a+n<=r.a+r.n then return ffi.string(r.b+a-r.a,n)end end
end
function api.pointer(b)local v=ffi.new('uint64_t[1]');ffi.copy(v,b,8);return v[0]>65535 and ffi.cast('uint8_t *',v[0])or nil end
local p={driver={global=0x10000,proofs={{rva=0x80000,bytes='proof'}}},functions={tank_driver_active={rva=0x80000,bytes='proof'}}}
local v={id=9,unit=99,network_unit=909,name='bastion',resource='16474112801385b6',owned_local=true}
local a={id=7,is_local=true,seat={collection=9,current=0,role=1}}
local s={state='mission',mission_value=5,player_count=4,peer_count=4,avatars={a},vehicles={v}}
local watch=factory(api,ffi.cast('uint8_t *',0),p,function(e)events[#events+1]=e end)
local function bytes()local out={};for _,r in ipairs(regions)do out[#out+1]=ffi.string(r.b,r.n)end;return table.concat(out)end
local before=bytes();watch:update(s)
assert(events[1].event=='steering_watch_started' and events[2].event=='steering_watch_sample')
assert(events[2].driver_active==1 and events[2].command_floats_offset_00_to_28[1]==-1 and events[2].command_flags_offset_2c_to_2f[3]==1)
assert(bytes()==before);local n=#events;now=.02;watch:update(s);assert(#events==n)
-- Keep tracking when installer becomes passenger and a remote player takes over.
a.seat.current=2;a.seat.role=3;keys={};runtime[0xd28+0xd18]=0;u(entity,20,0);v.owned_local=false
s.avatars[2]={id=8,unit=88,network_unit=808,is_local=false,seat={collection=9,current=0,role=1}}
before=bytes();now=.2;watch:update(s)
assert(events[#events].driver_active==0 and events[#events].owned_local==false and #events[#events].occupants==2)
assert(events[#events].local_seat.current==2 and #events[#events].held_keys==0 and bytes()==before)
now=11;local n=#events;watch:update(s);assert(#events==n)
local cases=0
for _,change in ipairs({
 function()u(entity,12,100)end,function()u(entity,16,910)end,function()u(entity,20,1)end,
 function()u(manager,0x40,3)end,function()u(rows,12,0)end,
 function()runtime[0xd28+0xd18]=7 end,
 function()put(commands,48,'float',0/0)end,
})do
 u(entity,12,99);u(entity,16,909);u(entity,20,0);u(manager,0x40,4);u(rows,12,1)
 runtime[0xd28+0xd18]=1;put(commands,48,'float',-1)
 a.seat.current=0;a.seat.role=1;keys={[68]=true};now=0;events={};change()
 local x=factory(api,ffi.cast('uint8_t *',0),p,function(e)events[#events+1]=e end)
 before=bytes();x:update(s);assert(events[#events].event=='steering_watch_gap' and bytes()==before);cases=cases+1
end
print('PASS read-only steering watch: actual component-map bytes, precise entity/unit/network/resource/local flag, driver-to-passenger/remote takeover/held release/timeout, 7 failure guards; unchanged memory and no game calls. Motion not simulated.')
-- The moving-car observer reuses this checked component reader for FRVs.
u(entity,12,99);u(entity,16,909);u(entity,20,0);u(manager,0x40,4);u(rows,12,1)
runtime[0xd28+0xd18]=1;put(commands,48,'float',1)
v.name='m102';v.resource='cc210834077941cf'
local hash='';for pair in v.resource:gmatch('..')do hash=string.char(tonumber(pair,16))..hash end;ffi.copy(entity,hash,8)
before=bytes();local data=watch:read_vehicle(v)
assert(data.driver_active==1 and data.command_floats_offset_00_to_28[1]==1 and bytes()==before)
v.resource='16474112801385b6';assert(not pcall(watch.read_vehicle,watch,v)and bytes()==before)
print('PASS shared FRV command reader uses actual component/entity/resource guards, remains read-only and rejects stale resource identity; physical velocity not inferred')
