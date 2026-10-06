local ffi=require('ffi')
local mem={};local count=0
local function put(a,b)for i=1,#b do mem[a+i-1]=b:sub(i,i)end end
local function number(a,t,n)local v=ffi.new(t..'[1]',n);put(a,ffi.string(v,ffi.sizeof(v)))end
local function u(a,n)number(a,'uint32_t',n)end
local function ptr(a,n)number(a,'uint64_t',n)end
local function zeros(a,n)put(a,string.rep('\0',n))end
local base=0x10000000
local p={functions={anim_event_index={rva=0x100},anim_event_adapter={rva=0x200},anim_event_receive={rva=0x300},route_dispatch={rva=0x400}}}
local function rip(at,op,target)put(base+at,op);number(base+at+3,'int32_t',target-at-7)end
rip(0x104,'\76\139\21',0x1000);rip(0x234,'\72\139\5',0x1000)
rip(0x24c,'\72\139\45',0x2000);rip(0x406,'\76\141\5',0x3000)
local dict,hashrows,values,systems,manager,entities,entity=0x200000,0x210000,0x220000,0x230000,0x240000,0x250000,0x260000
ptr(base+0x1000,dict);ptr(base+0x2000,systems);ptr(base+0x3000+5*8,base+0x200)
local function hashmap(at,rows)
 ptr(at,rows);u(at+8,16);u(at+12,0xffffffff);u(at+16,1)
 for i=0,15 do u(rows+i*8,0xffffffff);u(rows+i*8+4,0xffffffff)end
end
hashmap(dict+8,hashrows);ptr(dict+0x20,values);u(dict+0x28,6)
local hashes={0xdab88e64,0xb32ac618,0x929e2ba1,0xd429c3f4,0xe86f3c8c,0x1e84c4c3};local used={}
for i,h in ipairs(hashes)do local slot=h%16;while used[slot]do slot=(slot+1)%16 end;used[slot]=true
 u(hashrows+slot*8,h);u(hashrows+slot*8+4,i-1);u(values+(i-1)*4,h)
end
u(systems+0x3e58,1);zeros(systems+0x3e60,16);ptr(systems+0x3e60,manager);u(systems+0x3e68,7)
hashmap(manager+0x48,0x270000);u(0x270000+7*8,7);u(0x270000+7*8+4,0)
ptr(manager+0x60,entities);ptr(entities,entity);zeros(entity,24);u(entity+8,7);u(entity+12,123);u(entity+16,4107);u(entity+20,1)
local api={in_image=function(_,r,n)return r>=0 and r+n<0x10000 end}
function api.pointer(b,o)local v=ffi.new('uint64_t[1]');ffi.copy(v,b:sub((o or 0)+1),8);return v[0]>65535 and tonumber(v[0])or nil end
function api.read(a,n)count=count+1;local out={};for i=0,n-1 do if not mem[a+i]then return nil end;out[#out+1]=mem[a+i]end;return table.concat(out)end
local route={capture=function()return {state='observed',messages={{hash=0xbde53653,found=true,index=5}}}end}
local inspector=assert(loadfile('work/seat_handoff_motion_test/inspect.lua'))().new(api,base,p,route)
local before={};for k,v in pairs(mem)do before[k]=v end
local a={id=7,unit=123,network_unit=4107};local result=inspector:capture(a)
assert(result.stable and result.dispatch_matches and #result.events==6 and #result.animators==1)
for _,r in ipairs(result.events)do assert(r.found and r.roundtrip)end
assert(result.animators[1].avatar_found and result.animators[1].entity_matches and result.animators[1].network_matches)
for k,v in pairs(before)do assert(mem[k]==v)end;for k,v in pairs(mem)do assert(before[k]==v)end
local ship=inspector:capture(nil);assert(ship.stable and ship.animators[1].avatar_found==nil)
u(0x270000+7*8,0xffffffff);local missing=inspector:capture(a);assert(not missing.animators[1].avatar_found)
u(0x270000+7*8,7);u(entity+12,124);assert(not inspector:capture(a).animators[1].entity_matches);u(entity+12,123)
u(values,0);assert(not inspector:capture(a).events[1].roundtrip);u(values,hashes[1])
u(dict+0x10,15);assert(not pcall(inspector.capture,inspector,a));u(dict+0x10,16)
u(systems+0x3e58,17);assert(not pcall(inspector.capture,inspector,a));u(systems+0x3e58,1)
local read=api.read;local seen=0
api.read=function(addr,n)
 local b=read(addr,n)
 if addr==base+0x1000 then seen=seen+1;if seen>1 then return string.rep('\0',8)end end
 return b
end
assert(not pcall(inspector.capture,inspector,a))
print('PASS read-only event dictionary roundtrip, animator membership, registry target, absent/stale entities, bounded maps and changing roots; no memory mutations')
