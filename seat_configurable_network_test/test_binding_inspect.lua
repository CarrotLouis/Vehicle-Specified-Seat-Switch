local ffi=require('ffi')
local M=assert(loadfile('work/seat_configurable_network_test/binding_inspect.lua'))()
local memory={};local reads=0;local unstable=false
local function w(a,b)for i=1,#b do memory[a+i-1]=b:sub(i,i)end end
local function u(a,n)local b=ffi.new('uint32_t[1]',n);w(a,ffi.string(b,4))end
local function q(a,n)local b=ffi.new('uint64_t[1]',n);w(a,ffi.string(b,8))end
local api={in_image=function()return true end}
function api.read(a,n)
 reads=reads+1;if unstable and reads>20 then return nil end
 local b={};for i=0,n-1 do if not memory[a+i]then return nil end;b[#b+1]=memory[a+i]end;return table.concat(b)
end
function api.pointer(b)local p=ffi.new('uint64_t[1]');ffi.copy(p,b,8);local n=tonumber(p[0]);if n>0 then return n end end
local game=0x10000
local p={globals={entities=0x1010},layout={entity_records=0xf32f18},functions={binding_entity_lookup={rva=0x500},binding_clear_avatar={rva=0x100},avatar_rotation={rva=0x200},route_dispatch={rva=0x300},binding_clear_adapter={rva=0x400}}}
local function rel(rva,op,target)w(game+rva,op);u(game+rva+3,target-(game+rva+7))end
rel(0x11d,'\72\139\53',0x11000);rel(0x20c,'\76\139\21',0x11008);rel(0x306,'\76\141\5',0x12000)
rel(0x510,'\76\139\21',0x11010)
q(0x11000,0x20000);q(0x11008,0x21000);q(0x12010,game+0x400)
local function map(manager,rows)
 q(manager+0x30,rows);u(manager+0x38,2);u(manager+0x3c,0xffffffff);u(manager+0x40,1)
 u(rows,0xffffffff);u(rows+4,0xffffffff);u(rows+8,7);u(rows+12,0)
end
map(0x20000,0x22000);map(0x21000,0x22100)
u(0x20020,1);q(0x20048,0x23000);q(0x23000,0x24000);w(0x24000,string.rep('\0',24));u(0x24008,7);u(0x2400c,9);u(0x24010,11)
q(0x20060,0x25000);q(0x21058,0x26000);w(0x26071,'\1')
for i=0,4 do u(0x25000+i*0x50,100+i);u(0x25004+i*0x50,0xffffffff)end
local inspector=M.new(api,game,p)
local a={id=7,unit=9,network_unit=11,is_local=true,seat={current=4}}
local out=inspector:capture(a);assert(out.stable and #out.slots==5 and out.slots[1].weapon==100 and out.slots[5].channel==4 and out.rotation_flag==1)
local r=inspector:interface({capture=function()return {state='observed',messages={{hash=0x423a4034,index=2,found=true}}}end});assert(r.clear_dispatch_matches)
q(0x12010,123);assert(not inspector:interface({capture=function()return r end}).clear_dispatch_matches)
a.is_local=false;assert(not pcall(inspector.capture,inspector,a));a.is_local=true
u(0x24010,12);assert(not pcall(inspector.capture,inspector,a));u(0x24010,11)
u(0x20038,0xffffffff);reads=0;assert(not pcall(inspector.capture,inspector,a)and reads<10);u(0x20038,2)
u(0x20020,0);assert(not pcall(inspector.capture,inspector,a));u(0x20020,1)
unstable=true;reads=0;assert(not pcall(inspector.capture,inspector,a))
unstable=false
q(0x11010,0x30000);q(0x30000+0xf1aeb0,0x40000)
u(0x30000+0xf1aeb8,2);u(0x30000+0xf1aebc,0xffffffff);u(0x30000+0xf1aec0,1)
u(0x40000,90);u(0x40004,0);u(0x40008,0xffffffff);u(0x4000c,0xffffffff)
w(0x30000+0xf32f18,string.rep('\0',24));u(0x30000+0xf32f20,90);u(0x30000+0xf32f24,190);u(0x30000+0xf32f28,1090)
local weapon=inspector:entity(90);assert(weapon.id==90 and weapon.unit==190 and weapon.network_unit==1090)
assert(not pcall(inspector.entity,inspector,91))
u(0x30000+0xf32f28,0x7fff);assert(not pcall(inspector.entity,inspector,90));u(0x30000+0xf32f28,1090)
u(0x30000+0xf1aeb8,0xffffffff);assert(not pcall(inspector.entity,inspector,90))
print('PASS binding reader identity, slots, schema handler, bounds, unreadable/stale data; no writes/sends in production observer')
