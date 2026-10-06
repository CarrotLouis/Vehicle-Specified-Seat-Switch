-- Actual Lua/FFI reader; relation/asset/native helpers are explicit fixtures.
local ffi=require('ffi');local scope=assert(loadfile('work/seat_reservation_frv_test/scope.lua'))()
local factory=assert(loadfile('work/seat_reservation_frv_test/mounted_reader.lua'))()
local function addr(x)return tonumber(ffi.cast('uintptr_t',x))end
local function bytes(typ,n)local a=ffi.new(typ..'[1]',n);return ffi.string(a,ffi.sizeof(a))end
local tags=ffi.new('uint32_t[5]',{1234,0,0,0,0});local calls,owned,unit=0,false,180
local callbacks={};local mutate=false;local mem={}
callbacks.lookup=ffi.cast('void *(*)(void *,uint32_t *,uint32_t,uint32_t)',function(_,out,car,tag)
 assert(car==9 and tag==1234);calls=calls+1;out[0]=80;return ffi.cast('void *',out)
end)
callbacks.tags=ffi.cast('void *(*)(uint32_t,uint32_t)',function(typ,target)assert(typ==26 and target==4);return tags end)
local game=ffi.cast('uint8_t *',addr(callbacks.lookup)-0x1000)
local p={functions={}};local spec={records={}}
for name,at in pairs({reservation_related_weapon_lookup=addr(callbacks.lookup),reservation_mounted_joint_tags=addr(callbacks.tags),reservation_related_weapon_resource=addr(game+0x900)})do
 p.functions[name]={rva=at-addr(game)};spec.records[name]={length=1,chunks={}};mem[at]='x'
end
local root,manager,rows,objects=game+0x40000,game+0x50000,game+0x51000,game+0x52000
local instr=game+p.functions.reservation_related_weapon_lookup.rva+0x28
mem[addr(instr)]='\72\139\45'..bytes('int32_t',tonumber(root-instr)-7)
mem[addr(root)]=bytes('uint64_t',addr(manager))
mem[addr(manager+0x20)]=bytes('uint64_t',addr(rows))..bytes('uint32_t',2)..bytes('uint32_t',4294967295)..bytes('uint32_t',1)
mem[addr(rows)]=bytes('uint32_t',4294967295)..bytes('uint32_t',4294967295)..bytes('uint32_t',9)..bytes('uint32_t',0)
mem[addr(manager+0x38)]=bytes('uint64_t',addr(objects));mem[addr(objects)]=bytes('uint64_t',addr(game+0x30000))
local api={ffi=ffi,read=function(at,n)
 at=addr(at);if at==addr(tags)then return ffi.string(tags,n)end
 for base,b in pairs(mem)do if at>=base and at+n<=base+#b then return b:sub(at-base+1,at-base+n)end end
end,pointer=function(b)local v=ffi.new('uint64_t[1]');ffi.copy(v,b,8);return ffi.cast('uint8_t *',v[0])end}
local inspector={entity=function(_,id)assert(id==80);return {id=id,unit=unit,network_unit=1080,flags=owned and 1 or 0}end}
local events={};local read=factory(api,game,p,spec,{match=function(b)return b=='x'end},inspector,scope,function(e)events[#events+1]=e end)
local c={native={collection=9,collection_address=game+0x30000,avatar=7,vehicle='m102',transition=26,profile={row=8,roles={1,3,3,3,2}}}}
assert(read:prepare(c,2)==nil and calls==0)
local ticket=read:prepare(c,4);assert(#ticket.children==1 and calls==1 and not read:ready(c,ticket))
owned=true;assert(read:ready(c,ticket));unit=181;assert(not pcall(read.ready,read,c,ticket));unit=180
tags[0]=4294967295;local before=calls;assert(not pcall(read.prepare,read,c,4)and calls==before);tags[0]=1234
tags[1]=1234;assert(not pcall(read.prepare,read,c,4));tags[1]=0
local saved=mem[addr(rows)];mem[addr(rows)]=string.rep('\255',16);before=calls
assert(not pcall(read.prepare,read,c,4)and calls==before,'missing car must never invoke unbounded native map search');mem[addr(rows)]=saved
mem[addr(objects)]=bytes('uint64_t',addr(game+0x30008));assert(not pcall(read.prepare,read,c,4));mem[addr(objects)]=bytes('uint64_t',addr(game+0x30000))
assert(read:ready(c,ticket));callbacks.lookup:free();callbacks.tags:free()
print('PASS actual bounded mounted-reader FFI, authentic child identity/local owner readiness, wildcard/duplicate/missing-car/entity drift refusals; chassis untouched')
