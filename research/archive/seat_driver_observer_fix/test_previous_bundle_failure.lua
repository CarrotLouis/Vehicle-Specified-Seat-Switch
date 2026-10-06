local components=assert(loadfile('work/seat_driver_observer_fix/previous_components.lua'))()
-- Actual frozen code, synthetic heap, mocked native read API outputs.
-- Separate Unicorn tests execute the actual velocity bridge/actor resolver.
local ffi,bit=require('ffi'),require('bit')
local root=assert(os.getenv('VSS_CAPTURE'))
local function file(name)local f=assert(io.open(root..'/'..name,'rb'));local b=f:read('*a');f:close();return b end
local report=file('capture.txt');local modules={};local bases={['game.dll']=0x10000000,['helldivers2.exe']=0x20000000}
for fn,hex in report:gmatch('([^%s]+%.%d+_([%da-f]+)%.bin) name=')do
 for name,base in pairs(bases)do if fn:sub(1,#name)==name then modules[#modules+1]={base+tonumber(hex,16),file(fn)}end end
end
local p={functions={},engine_functions={}};local spec={records={},core={},engine={},edges={}}
p,spec=assert(loadfile('work/seat_driver_observer_fix/motion_spec.lua'))()(p,spec)
p.engine_ranges={{rva=0x1000,size=0x13f3000,execute=true,readable=true}}
local compat=assert(loadfile('work/seat_switch/src/compat.lua'))()
local maker=components.physics_reader
local function u32(n)local a=ffi.new('uint32_t[1]',n);return ffi.string(a,4)end
local function ptr(n)local a=ffi.new('uint64_t[1]',n);return ffi.string(a,8)end
local function fixture(world,inline,count,shifted)
 count=count or 1
 local memory={};local regions={};local calls=0;local writes=0;local torn,nonfinite=false,false
 local function allocate(at,n)regions[#regions+1]={at,n};for i=0,n-1 do memory[at+i]=0 end end
 local function put(at,b)for i=1,#b do memory[at+i-1]=b:byte(i)end end
 local function rawread(a,n)
  local b={};local exists=true
  for i=0,n-1 do if memory[a+i]==nil then exists=false;break end;b[#b+1]=string.char(memory[a+i])end
  if exists then return table.concat(b)end
  for _,r in ipairs(modules)do if a>=r[1]and a+n<=r[1]+#r[2]then
   local b=r[2]:sub(a-r[1]+1,a-r[1]+n);local out={}
   for i=0,n-1 do out[i+1]=string.char(memory[a+i]or b:byte(i+1))end
   return table.concat(out)
  end end
 end
 local api=components.platform(function()return 'saved-capture'end)
 local adapter_ffi=api.ffi
 api.module=function(n)return ffi.cast('uint8_t *',bases[n])end
 function api.read(a,n)return rawread(tonumber(ffi.cast('uintptr_t',a)),n)end
 function api.pointer(b,o)
  o=o or 0;if not b or #b<o+8 then return nil end
  local v=ffi.new('uint64_t[1]');ffi.copy(v,b:sub(o+1,o+8),8)
  if tonumber(v[0])<65536 or tonumber(v[0])>=2^47 then return nil end;return ffi.cast('uint8_t *',v[0])
 end
 local function ref(name)
  local r=p.motion.refs[name];local d=p.motion.records[r.record];local a=bases[d.module=='game'and'game.dll'or'helldivers2.exe']+d.hint+r.offset
  local v=ffi.new('int32_t[1]');ffi.copy(v,assert(rawread(a+r.disp,4)),4);return a+r.size+tonumber(v[0])
 end
 local v={name='m102',id=91,unit=0x800042,network_unit=713,resource='cc21c7ffd3ebefb9',owned_local=false}
 local resource=(v.resource:gsub('..',function(x)return string.char(tonumber(x,16))end)):reverse()
 local manager,rows,entities,entity,rm,rr,units,poolrows,context,vt,lookup,velocity=0x30000000,0x30001000,0x30002000,0x30003000,0x31000000,0x32000000,0x33000000,0x34000000,0x35000000,0x35001000,0x35002000,0x35003000
 allocate(ref('component_manager'),8);put(ref('component_manager'),ptr(manager));allocate(manager,0x60)
 put(manager+0x40,ptr(rows)..u32(8)..u32(0xffffffff)..u32(1));allocate(rows,64)
 for i=0,7 do put(rows+i*8,u32(0xffffffff)..u32(0xffffffff))end
 put(rows+v.id%8*8,u32(v.id)..u32(0));put(manager+0x58,ptr(entities));allocate(entities,8);put(entities,ptr(entity));allocate(entity,24)
 put(entity,resource..u32(v.id)..u32(v.unit)..u32(v.network_unit)..u32(0))
 allocate(ref('resource_manager'),8);put(ref('resource_manager'),ptr(rm));allocate(rm+0xf12b80,8);put(rm+0xf12b80,ptr(rr));allocate(rr,0x600)
 local key=ffi.new('uint64_t[1]');ffi.copy(key,resource,8);local bucket=tonumber(key[0]%ffi.new('uint64_t',28))
 put(rr+bucket*16,resource..u32(1));local namehash=0x513720fa;put(rr+0x1c0+0x1c8+8,u32(namehash))
 allocate(ref('unit_components'),8);put(ref('unit_components'),ptr(units));local ur=units+bit.band(v.unit,0x3fffff)*24;allocate(ur,24)
 local aid=world*2^30+0x10000000+0x10007;local alist=inline and ur+8 or 0x33010000
 put(ur,u32(v.unit)..u32((inline and 0xc0000000 or 0x40000000)+count)..(inline and u32(aid)..string.rep('\0',12)or ptr(alist)..string.rep('\0',8)))
 if not inline then allocate(alist,count*4);put(alist+(count-1)*4,u32(aid))end
 local pool=ref('actor_pools')+(world*10+1)*64;allocate(pool,0x38)
 local stride,tag,off=shifted and 64 or 32,shifted and 4 or 0,shifted and 16 or 0
 local capacity=count>1 and 256 or 16
 put(pool,ptr(poolrows));put(pool+0x1c,u32(stride+tag*2^16+off*2^24));put(pool+0x24,u32(capacity)..u32(capacity-1));put(pool+0x34,u32(0x10000))
 allocate(poolrows,capacity*stride);local actor=poolrows+7*stride+off
 put(actor,u32(shifted and 0xfeed or aid)..u32(0x55)..u32(0)..u32(v.unit)..u32(0x66)..u32(0x222)..u32(namehash))
 local actor_tag=poolrows+7*stride+tag;put(actor_tag,u32(aid))
 for i=1,count-1 do
  local id=world*2^30+0x10000000+0x10000+16+i;local at=poolrows+(16+i)*stride
  put(at+off,u32(shifted and 0xbeef or id)..u32(0x55)..u32(0)..u32(v.unit)..u32(0x66)..u32(0x222+i)..u32(namehash+i))
  put(at+tag,u32(id));put(alist+(i-1)*4,u32(id))
 end
 allocate(ref('lookup_api'),8);put(ref('lookup_api'),ptr(lookup));allocate(lookup,32)
 put(lookup+0x10,ptr(bases['helldivers2.exe']+p.engine_functions.motion_actor_lookup.rva))
 allocate(ref('velocity_api'),8);put(ref('velocity_api'),ptr(velocity));allocate(velocity,0xb0)
 put(velocity+0xa8,ptr(bases['helldivers2.exe']+p.engine_functions.motion_actor_velocity.rva))
 put(velocity+0x50,ptr(bases['helldivers2.exe']+p.engine_functions.motion_actor_position.rva))
 allocate(ref('physics_worlds')+world*0xb0,8);put(ref('physics_worlds')+world*0xb0,ptr(context));allocate(context,8);put(context,ptr(vt));allocate(vt,0xa0)
 for _,off in ipairs({0x70,0x88,0x98})do put(vt+off,ptr(bases['helldivers2.exe']+p.engine_functions.motion_actor_velocity.rva))end
 local proxy=setmetatable({cast=function(signature,address)
  if signature=='void (*)(uint32_t,float *,float *)'then return function(id,l,a)
   assert(id==aid);calls=calls+1;l[0]=3;l[1]=4;l[2]=0;a[0]=.1;a[1]=.2;a[2]=.3
   if torn then put(actor+0xc,u32(v.unit+1))end
   if nonfinite then l[0]=0/0 end
  end end
  if signature=='void (*)(uint32_t,float *)'then return function(id,out)assert(id==aid);calls=calls+1;out[0]=100;out[1]=200;out[2]=300 end end
  return ffi.cast(signature,address)
 end},{__index=adapter_ffi})
 if adapter_ffi then api.ffi=proxy end;api.replace=function()writes=writes+1;error('unexpected physics write')end
 local reader=maker(api,ffi.cast('uint8_t *',bases['game.dll']),p,compat)
 local function read()return reader:read_vehicle(v)end
 return read,put,{v=v,entity=entity,manager=manager,rows=rows,ur=ur,pool=pool,actor=actor,velocity=velocity,vt=vt,ref=ref,aid=aid},
  function()return calls,writes end,function()torn=true end,function()nonfinite=true end,reader,api,p,compat
end
local read,_,_,counts,_,_,reader,api=fixture(2,false,41,false)
assert(api.ffi==nil,'prior adapter should reproduce the captured missing FFI')
local ok,why=pcall(read)
assert(not ok and tostring(why):find("upvalue 'ffi'"),tostring(why))
local calls,writes=counts();assert(calls==0 and writes==0)
print('PASS negative control: exact 0.25.0 deployment reproduces missing-ffi first-driver failure before native getters/hooks; no fabricated zero speed')
