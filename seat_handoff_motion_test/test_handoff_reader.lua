-- Frozen machine-code witnesses and synthetic heaps. No game process access.
local ffi,bit=require('ffi'),require('bit')
local root=assert(os.getenv('VSS_CAPTURE'))
local function file(name)local f=assert(io.open(root..'/'..name,'rb'));local b=f:read('*a');f:close();return b end
local modules,bases={}, {['game.dll']=0x10000000,['helldivers2.exe']=0x20000000}
for fn,hex in file('capture.txt'):gmatch('([^%s]+%.%d+_([%da-f]+)%.bin) name=')do
 for name,base in pairs(bases)do if fn:sub(1,#name)==name then modules[#modules+1]={base+tonumber(hex,16),file(fn)}end end
end
local p={functions={},engine_functions={},globals={session=0x3f00100}}
local spec={records={},core={},engine={},edges={}}
p,spec=assert(loadfile('work/seat_handoff_motion_test/handoff_spec.lua'))()(p,spec)
local compat=assert(loadfile('work/seat_switch/src/compat.lua'))()
local maker=assert(loadfile('work/seat_handoff_motion_test/handoff_reader.lua'))()
local function u32(x)local v=ffi.new('uint32_t[1]',x);return ffi.string(v,4)end
local function ptr(x)local v=ffi.new('uint64_t[1]',x);return ffi.string(v,8)end
local function floats(...)local t={...};local v=ffi.new('float[?]',#t,t);return ffi.string(v,#t*4)end
local function fixture(cached,collision)
 local memory={};local writes,calls=0,0;local tear_at
 local function allocate(a,n)for i=0,n-1 do memory[a+i]=0 end end
 local function put(a,b)for i=1,#b do memory[a+i-1]=b:byte(i)end end
 local function rawread(a,n)
  local out={};local exists=true
  for i=0,n-1 do if memory[a+i]==nil then exists=false;break end;out[#out+1]=string.char(memory[a+i])end
  if exists then return table.concat(out)end
  for _,r in ipairs(modules)do if a>=r[1]and a+n<=r[1]+#r[2]then
   local b=r[2]:sub(a-r[1]+1,a-r[1]+n);out={}
   for i=0,n-1 do out[i+1]=string.char(memory[a+i]or b:byte(i+1))end
   return table.concat(out)
  end end
 end
 local api={ffi=ffi,module=function(name)return ffi.cast('uint8_t *',bases[name])end}
 function api.read(a,n)
  local at=tonumber(ffi.cast('uintptr_t',a));local b=rawread(at,n)
  if at==tear_at then put(0x37000000+0x130,ptr(7))end
  return b
 end
 function api.pointer(b,o)
  o=o or 0;if not b or #b<o+8 then return nil end
  local v=ffi.new('uint64_t[1]');ffi.copy(v,b:sub(o+1,o+8),8)
  if tonumber(v[0])<65536 or tonumber(v[0])>=2^47 then return nil end
  return ffi.cast('uint8_t *',v[0])
 end
 api.replace=function()writes=writes+1;error('unexpected write')end
 api.call=function()calls=calls+1;error('unexpected native call')end
 local ref=p.handoff.refs.component_manager;local at=bases['game.dll']+p.functions[ref.record].rva+ref.offset
 local disp=ffi.new('int32_t[1]');ffi.copy(disp,assert(rawread(at+ref.disp,4)),4)
 local mgrref=at+ref.size+tonumber(disp[0])
 local v={name='m102',id=91,unit=0x800042,network_unit=713,resource='cc21c7ffd3ebefb9'}
 local resource=(v.resource:gsub('..',function(x)return string.char(tonumber(x,16))end)):reverse()
 local manager,rows,entities,entity=0x30000000,0x30001000,0x30002000,0x30003000
 allocate(mgrref,8);put(mgrref,ptr(manager));allocate(manager,0x80)
 put(manager+0x30,u32(1)..u32(0));put(manager+0x40,ptr(rows)..u32(8)..u32(0xffffffff)..u32(1))
 allocate(rows,64);for i=0,7 do put(rows+i*8,u32(0xffffffff)..u32(0xffffffff))end
 put(rows+v.id%8*8,u32(v.id)..u32(0));put(manager+0x58,ptr(entities));allocate(entities,8);put(entities,ptr(entity));allocate(entity,24)
 put(entity,resource..u32(v.id)..u32(v.unit)..u32(v.network_unit)..u32(0))
 local network,input,runtime=0x31000000,0x31001000,0x31002000
 put(manager+0x78,ptr(network));allocate(network,88)
 put(manager+0x60,ptr(input));allocate(input,16);put(input,floats(.3,.5,.7)..u32(1))
 put(manager+0x70,ptr(runtime));allocate(runtime,0x670)
 local session,engine,sm=0x36000000,0x37000000,0x38000000
 allocate(bases['game.dll']+p.globals.session,8);put(bases['game.dll']+p.globals.session,ptr(session))
 allocate(session+0xb390,8);put(session+0xb390,ptr(engine));allocate(engine,0x700)
 put(engine+0x18,ptr(sm));put(engine+0x20,ptr(1));put(engine+0x130,ptr(2))
 local nrows=0x39000000;put(engine+0x640,u32(8)..u32(0)..ptr(nrows)..ptr(0)..u32(1)..u32(8));allocate(nrows,8*0x248)
 local a=tonumber(ffi.cast('uint32_t',ffi.new('uint64_t',v.network_unit)*0x5bd1e995))
 a=bit.bxor(a,bit.rshift(a,24));if a<0 then a=a+2^32 end
 local bucket=tonumber(ffi.cast('uint32_t',ffi.new('uint64_t',a)*0x5bd1e995))%8
 local row=nrows+bucket*0x248
 if collision then put(row,u32(v.network_unit+1));put(row+0x240,u32((bucket+1)%8));row=nrows+(bucket+1)%8*0x248 end
 put(row,u32(v.network_unit)..u32(0)..u32(2116)..u32(123)..ptr(2))
 put(row+0x240,u32(0x7fffffff));put(row+0x23a,string.char(7,0,0,0))
 local raw,types,global,indices,hashes=0x3a000000,0x3b000000,0x3c000000,0x3d000000,0x3d010000
 allocate(raw,256);put(row+0x20,ptr(raw));allocate(sm,0x80)
 put(sm+0x18,ptr(global));put(sm+0x78,ptr(types));allocate(types,124*80);allocate(global,13*24)
 local kinds={[0]=0,[1]=1,[2]=2,[3]=3,[4]=4,[9]=9,[10]=10,[11]=10}
 for i,k in pairs(kinds)do put(global+i*24+0xc,string.char(k))end
 put(global+10*24+0x10,u32(2)..u32(3));put(global+11*24+0x10,u32(10)..u32(2))
 local list={0,11,9,2,3,10,3,4,2};local hs={0x100,0x200,0x791943f0,0x91f98cec,0x7615f45d,0x300,0xeeb1225e,0xcca43d10,0x5a8871e3}
 local descriptor=types+123*80;put(descriptor+0x18,u32(#list));put(descriptor+0x20,ptr(indices));put(descriptor+0x38,ptr(hashes))
 allocate(indices,#list*4);allocate(hashes,#list*4)
 for i,k in ipairs(list)do put(indices+(i-1)*4,u32(k));put(hashes+(i-1)*4,u32(hs[i]))end
 local data={motion_peer=ptr(2),motion_time=floats(10),linear_velocity=floats(3,4,0),position=floats(100,200,300),rotation=floats(0,0,0,1),steering=floats(.2)}
 local positions={motion_peer={40,0,2},motion_time={48,8,3},linear_velocity={52,12,4},position={80,24,6},rotation={92,36,7},steering={108,52,8}}
 for name,d in pairs(data)do put(raw+positions[name][1],d);put(network+positions[name][2],d)end
 local cache,cachevalues,cacheoffsets=0x3e000000,0x3e010000,0x3e020000
 if cached then
  allocate(cache,0x38);allocate(cachevalues,1024);allocate(cacheoffsets,#list*12)
  put(row+0x230,ptr(cache));put(cache,ptr(sm)..ptr(descriptor));put(cache+0x18,ptr(cachevalues));put(cache+0x28,ptr(cacheoffsets))
  for i=0,#list-1 do put(cacheoffsets+i*12+4,u32(i*64))end
  for _,index in ipairs({2,3,4})do put(global+index*24+0xe,string.char(1))end
  for name,d in pairs(data)do local ix=positions[name][3];put(cachevalues+ix*64+8,name=='linear_velocity'and floats(6,8,0)or d)end
 end
 local o={vehicle=v,session=ffi.cast('uint8_t *',session),engine=ffi.cast('uint8_t *',engine),selfpeer=ptr(1),coordinator=ptr(2),context='fixture-session'}
 local reader=maker(api,ffi.cast('uint8_t *',bases['game.dll']),p,compat)
 return function()return reader:read_vehicle(v,o)end,put,
  {v=v,o=o,manager=manager,rows=rows,entity=entity,engine=engine,row=row,sm=sm,descriptor=descriptor,indices=indices,hashes=hashes,
   global=global,raw=raw,input=input,network=network,cache=cache,cacheoffsets=cacheoffsets,cachevalues=cachevalues},
  function()return writes,calls end,function(a)tear_at=a end,reader
end
local cases=0
for _,cached in ipairs({false,true})do for _,collision in ipairs({false,true})do
 local read,put,f,counts,_,reader=fixture(cached,collision)
 local a=read();assert(a.property_type_index==123 and a.property_count==9 and a.property_buffer_bytes==112)
 assert(a.properties.linear_velocity.raw_engine.values[1]==3 and a.properties.linear_velocity.component.values[2]==4)
 assert(a.properties.position.raw_engine.values[3]==300 and a.properties.rotation.component.values[4]==1)
 assert(math.abs(a.properties.steering.raw_engine.values[1]-.2)<.001)
 assert(a.component_input_flag==1 and math.abs(a.component_input.values[1]-.3)<.001)
 assert(a.interpolation_cache_present==cached and a.properties.linear_velocity.serializer_source==(cached and 'interpolation_cache'or'raw_engine'))
 if cached then assert(a.properties.linear_velocity.cached.values[1]==6 and a.properties.linear_velocity.cached.values[2]==8)end
 local b=read();assert(b.schema_cache_hit and b.read_count<=2048)
 local w,c=counts();assert(w==0 and c==0);cases=cases+2
end end
local changes={
 function(put,f)f.v.name='m103'end,
 function(put,f)put(f.entity+12,u32(f.v.unit+1))end,
 function(put,f)put(f.entity,string.rep('\0',8))end,
 function(put,f)put(f.manager+0x48,u32(7))end,
 function(put,f)put(f.manager+0x30,u32(0))end,
 function(put,f)put(f.engine+0x20,ptr(2))end,
 function(put,f)put(f.engine+0x648,ptr(0))end,
 function(put,f)put(f.row+0x240,u32(0xfffffffe))end,
 function(put,f)put(f.row+0xc,u32(4096))end,
 function(put,f)put(f.row+0x20,ptr(0))end,
 function(put,f)put(f.descriptor+0x18,u32(513))end,
 function(put,f)put(f.hashes+16,u32(0))end,
 function(put,f)put(f.hashes+20,u32(0x7615f45d))end,
 function(put,f)put(f.global+3*24+0xc,string.char(2))end,
 function(put,f)put(f.global+11*24+0x10,u32(11))end,
 function(put,f)put(f.global+10*24+0x14,u32(4097))end,
 function(put,f)put(f.indices,u32(16384))end,
 function(put,f)put(f.cache+8,ptr(f.descriptor+80))end,
 function(put,f)put(f.cacheoffsets+4*12+4,u32(65537))end,
 function(put,f)put(f.raw+52,floats(0/0,4,0))end,
 function(put,f)put(bases['game.dll']+p.functions.handoff_component_state.rva,'\0')end,
}
for i,change in ipairs(changes)do
 local read,put,f,counts=fixture(true,false);change(put,f)
 assert(not pcall(read),'negative guard '..i);local w,c=counts();assert(w==0 and c==0);cases=cases+1
end
local read,put,f,counts,tear=fixture(true,false);tear(f.raw+52);assert(not pcall(read),'torn peer context')
local w,c=counts();assert(w==0 and c==0);cases=cases+1
local read,put,f,counts=fixture(true,false);assert(read());put(f.global+3*24+0xd,string.char(9))
assert(not pcall(read),'cached schema mutation');cases=cases+1
print('PASS handoff schema, raw/cache selection, nested offsets, collision and stale/invalid refusal cases '..cases..'; no native calls or writes; synthetic state, not live handoff')
