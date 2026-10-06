-- Real Lua/FFI factory; asset and pure native lookup backends are explicit fixtures.
local ffi=require('ffi')
local factory=assert(loadfile('work/seat_reservation_test/entrance.lua'))()
local function address(x)return tonumber(ffi.cast('uintptr_t',x))end
local function bytes(typ,value)local a=ffi.new(typ..'[1]',value);return ffi.string(a,ffi.sizeof(a))end
local game=ffi.cast('uint8_t *',0);local mem={};local keep={};local sends,lookups=0,0
local map={7,9,5,8,6};local rows={4,2,0,3,1};local changed,badptr,changedread=false,false,false
local asset=ffi.new('uint8_t[0x450]');local aaddr=address(asset)
local function setasset(n)
 ffi.fill(asset,0x450,0)
 for i=0,n-1 do ffi.cast('float *',asset+i*0x88+12)[0]=2;ffi.cast('uint32_t *',asset+i*0x88+20)[0]=100+i end
end
setasset(5)
local function setrows()
 local b='';for i=1,5 do b=b..bytes('int32_t',rows[i])..bytes('int32_t',-1)end;mem[0x20000+40]=b
end
setrows()
keep.node=ffi.cast('int32_t (*)(uint32_t,uint32_t,uint32_t)',function(typ,id,e)
 assert(typ==26 and id==9 and e<=7);lookups=lookups+1;return map[e+1]or 99
end)
keep.resource=ffi.cast('void *(*)(void *)',function()return asset end)
keep.preferences=ffi.cast('void *(*)(uint32_t,uint32_t)',function(typ,node)
 assert(typ==26 and node>=5 and node<=9);return ffi.cast('void *',0x20000+node*8+(badptr and 8 or 0))
end)
local peer=bytes('uint64_t',ffi.new('uint64_t',0xfedcba98)*ffi.new('uint64_t',4294967296)+0x76543210)
local function checkpeer(v)assert(bytes('uint64_t',v)==peer)end
keep.entry=ffi.cast('void (*)(uint64_t,uint32_t,uint32_t,uint32_t)',function(dest,car,av,e)
 checkpeer(dest);assert(car==9 and av==7 and e==4);sends=sends+1
end)
keep.release=ffi.cast('void (*)(uint64_t,uint32_t,int32_t)',function(dest,car,slot)
 checkpeer(dest);assert(car==9 and slot==1);sends=sends+1
end)
local p={functions={adjacency={rva=address(keep.preferences)},route_dispatch={rva=0x800}},tables={}}
local spec={records={}}
for name,where in pairs({reservation_entrance_node=address(keep.node),reservation_interaction_resource=address(keep.resource),
 reservation_interaction_update=0x900,reservation_entry_send=address(keep.entry),reservation_release_send=address(keep.release),reservation_accepted_adapter=0xa00})do
 p.functions[name]={rva=where};spec.records[name]={length=1,chunks={}};mem[where]='x'
end
mem[0x809]=bytes('int32_t',0x1000-0x80d);mem[0x1008]=bytes('uint64_t',0xa00)
local api={read=function(at,n)
 at=address(at)
 if at==aaddr then
  local b=ffi.string(asset,n);if changedread then return b:sub(1,-2)..'\1'end;changedread=changed;return b
 end
 for base,b in pairs(mem)do if at>=base and at+n<=base+#b then return b:sub(at-base+1,at-base+n)end end
end,pointer=function(b)local v=ffi.new('uint64_t[1]');ffi.copy(v,b,8);return ffi.cast('uint8_t *',v[0])end}
local function schema(name,hash,types,index)return {name=name,hash=hash,type_indices=types,parameter_count=#types,index=index,found=true,flags={1,1}}end
local trace={active=true,health=function()end,registry={
 schema('entry_request',0x3a44e090,{256,256,29},0),schema('accepted',0x2e986f01,{256,256,87},1),
 schema('entry_denied',0xf2a7f3e4,{256,256},2),schema('release_request',0xc698216f,{256,87},3)}}
local events={};local obj=factory(api,game,p,spec,{match=function(b)return b=='x'end},trace,function(e)events[#events+1]=e end)
local s={vehicle='m102',transition=26,collection=9,avatar=7,owned=false,collection_address=ffi.cast('void *',0x3000),profile={row=8,rva=0x20000,roles={1,3,3,3,2}}}
local c={native=s,owner={owner=peer,selfpeer='selfpeer',busy=false},destination=peer}
assert(obj:find(s,2)==4 and lookups==5)
local send,e=obj:prepare_request(c,2);assert(e==4 and sends==0);send();assert(sends==1 and not pcall(send))
local release=obj:prepare_release(c,1);release();assert(sends==2 and not pcall(release))
-- Changing table content, not ordinal seat guesses, changes the inverse.
rows={4,3,0,2,1};setrows();assert(obj:find(s,2)==3);rows={4,2,0,3,1};setrows()
-- Duplicate/missing rows, OOB/pointer/layout/schema/code drift: no send.
rows={2,2,0,3,1};setrows();assert(not pcall(obj.prepare_request,obj,c,2));rows={4,2,0,3,1};setrows()
badptr=true;assert(not pcall(obj.prepare_request,obj,c,2));badptr=false
changed=true;changedread=false;assert(not pcall(obj.prepare_request,obj,c,2));changed=false;changedread=false
setasset(0);assert(not pcall(obj.prepare_request,obj,c,2));setasset(8);lookups=0
assert(obj:find(s,2)==4 and lookups==8);setasset(5)
ffi.cast('float *',asset+12)[0]=-1;assert(not pcall(obj.prepare_request,obj,c,2));setasset(5)
trace.registry[1].type_indices[3]=87;assert(not pcall(obj.prepare_request,obj,c,2));trace.registry[1].type_indices[3]=29
mem[0x1008]=bytes('uint64_t',0xb00);assert(not pcall(obj.prepare_request,obj,c,2));mem[0x1008]=bytes('uint64_t',0xa00)
mem[p.functions.reservation_entry_send.rva]='y';assert(not pcall(obj.prepare_request,obj,c,2))
assert(sends==2)
for _,f in pairs(keep)do f:free()end
print('PASS real entrance factory/FFI, bounded asset reads, dynamic inverse mapping, exact peer/net wrapper arguments and all unsafe layout/schema/code refusals')
