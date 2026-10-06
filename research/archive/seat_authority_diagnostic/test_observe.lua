-- Actual preserved module sections, read-only mock address space. No live game.
local profile=assert(loadfile('work/seat_switch/src/profile.lua'))()
local spec=assert(loadfile('work/seat_protocol_diagnostic/compat_spec.lua'))()
local points=assert(loadfile('work/seat_protocol_diagnostic/trace_points.lua'))()
for _,point in ipairs(points)do profile.functions['trace_'..point.name]={rva=point.rva}end
profile,spec=assert(loadfile('work/seat_interface_diagnostic/routing_spec.lua'))()(profile,spec)
profile,spec=assert(loadfile('work/seat_authority_diagnostic/authority_spec.lua'))()(profile,spec)
local compat=assert(loadfile('work/seat_switch/src/compat.lua'))()
local ffi=require('ffi')
local root=assert(os.getenv('VSS_CAPTURE'),'VSS_CAPTURE required')
local f=assert(io.open(root..'/capture.txt','rb'));local report=f:read('*a');f:close()
local modules={};local bases={['game.dll']=0x10000000,['helldivers2.exe']=0x20000000}
local function file(name)local h=assert(io.open(root..'/'..name,'rb'));local b=h:read('*a');h:close();return b end
for name,base in pairs(bases)do
 local rows={{a=base,b=file(name..'.headers.bin')}}
 for fn,hex in report:gmatch('([^%s]+%.%d+_([%da-f]+)%.bin) name=')do
  if fn:sub(1,#name)==name then rows[#rows+1]={a=base+tonumber(hex,16),b=file(fn)}end
 end
 modules[name]=rows
end
local patches={}
local function rawread(a,n)
 for _,rows in pairs(modules)do for _,r in ipairs(rows)do if a>=r.a and a+n<=r.a+#r.b then return r.b:sub(a-r.a+1,a-r.a+n)end end end
end
local api={module=function(name)return bases[name]end}
function api.read(a,n)
 local b=rawread(a,n);if not b then return nil end
 for _,p in ipairs(patches)do
  local lo,hi=math.max(a,p.a),math.min(a+n,p.a+#p.b)
  if lo<hi then b=b:sub(1,lo-a)..p.b:sub(lo-p.a+1,hi-p.a)..b:sub(hi-a+1)end
 end
 return b
end
local function run(mode,s)
 local task=compat.start(api,bases['game.dll'],profile,s or spec,mode)
 for i=1,30000 do local p=task.step();if p then return p,i end end
 error('resolver never finished')
end

-- Appended to the immutable capture fixture by build.py. Actual game functions
-- are never executed: the single FFI send signature is replaced in this fixture.
local p=run('diagnostic');local game,exe=bases['game.dll'],bases['helldivers2.exe']
local bit=require('bit');local extra={};local regions={};local rawapi=api.read
local pointers=os.getenv('VSS_TEST_POINTERS')=='1'
local function number(a)return type(a)=='cdata'and tonumber(ffi.cast('uintptr_t',a))or a end
if pointers then
 game,exe=ffi.cast('uint8_t *',game),ffi.cast('uint8_t *',exe)
 local original_module=api.module;api.module=function(name)return ffi.cast('uint8_t *',original_module(name))end
end
local function put(a,b)extra[#extra+1]={a=number(a),b=b}end
local function le(n)local v=ffi.new('uint32_t[1]',n);return ffi.string(v,4)end
local function ptr(n)local v=ffi.new('uint64_t[1]',number(n));return ffi.string(v,8)end
local function peer(lo,hi)local v=ffi.new('uint32_t[2]',{lo,hi});return ffi.string(v,8)end
function api.read(a,n)
 a=number(a)
 local b=rawapi(a,n)
 if not b then for _,r in ipairs(regions)do if a>=number(r[1])and a+n<=number(r[1])+r[2]then b=string.rep('\0',n);break end end end
 if not b then return nil end
 for _,r in ipairs(extra)do
  local lo,hi=math.max(a,r.a),math.min(a+n,r.a+#r.b)
  if lo<hi then b=b:sub(1,lo-a)..r.b:sub(lo-r.a+1,hi-r.a)..b:sub(hi-a+1)end
 end
 return b
end
function api.pointer(b,o)
 o=o or 0;if not b or #b<o+8 then return nil end
 local v=ffi.new('uint64_t[1]');ffi.copy(v,b:sub(o+1,o+8),8);local n=tonumber(v[0]);return n>=65536 and n<2^47 and (pointers and ffi.cast('uint8_t *',v[0])or n)or nil
end
local function displacement(a)
 local v=ffi.new('int32_t[1]');ffi.copy(v,assert(api.read(a+3,4)),4);return a+7+tonumber(v[0])
end
local S,E,SERVICES,API,ROWS,ENTITIES,BUSY,BHASH=0x50010000,0x50040000,0x50050000,0x50051000,0x50060000,0x50070000,0x50080000,0x50090000
regions={{0x50000000,0x100000},{game+p.globals.session,8},{game+p.globals.entities,8}}
local root=displacement(game+p.functions.authority_apply.rva+0xd);regions[#regions+1]={root,8}
local vt=displacement(exe+p.engine_functions.authority_constructor.rva+0x12)
local dispatch=displacement(game+p.functions.route_dispatch.rva+6)
local LOCAL=peer(0x76543211,0xfedcba98);local FRIEND=peer(0x76543212,0xfedcba98)
local vehicle={id=721,unit=8391232,network_unit=4118,resource='fixture',name='m102',seat_count=5,owned_local=false}
local s={state='mission',mission_value=99,player_count=2,local_count=1,vehicles={vehicle},avatars={
 {id=11,is_local=true,network_unit=4107,seat={collection=721,current=1,reserved=1,role=3,target=-1,action=-1,transitioning=0,queued_exit=0}},
 {id=22,is_local=false,network_unit=274,seat={collection=721,current=0,reserved=0,role=1,target=-1,action=-1,transitioning=0,queued_exit=0}}}}
local reader={peers={[LOCAL]='P1',[FRIEND]='P2'},capture=function()return s end}
local trace={registry={{name='authority_owned',hash=0xf8a9d630,flags={1,1},parameter_count=2,type_indices={107,91},index=575}}}
local function mul(a,b)return tonumber(ffi.cast('uint32_t',ffi.new('uint64_t',a)*ffi.new('uint64_t',b)))end
local indices={}
local function setup()
 extra={};indices={}
 put(game+p.globals.session,ptr(S));put(S+0xb390,ptr(E));put(root,ptr(SERVICES));put(SERVICES+0x40,ptr(API))
 for off,name in pairs({[0x98]='api_exists',[0x138]='api_request',[0x140]='api_transfer',[0x160]='api_owner'})do put(API+off,ptr(exe+p.engine_functions['authority_'..name].rva))end
 put(E,ptr(vt))
 for off,name in pairs({[0xf8]='exists',[0x110]='transfer',[0x128]='request',[0x178]='owner'})do put(vt+off,ptr(exe+p.engine_functions['authority_'..name].rva))end
 -- These leaf getters are not individually scanned. Their table relationships
 -- and exact bytes are checked by the production observer.
 put(vt+0x68,ptr(exe+0x292bd0));put(vt+0x98,ptr(exe+0x292cc0))
 put(E+0x20,LOCAL);put(E+0x130,FRIEND);put(S+0xb398,LOCAL);put(S+0xb3a8,FRIEND)
 put(S+0x162d8,le(2));put(S+0x162e0,LOCAL..FRIEND);put(E+0x60e4,le(42))
 put(dispatch+575*8,ptr(game+p.functions.authority_adapter.rva))
 put(E+0x640,le(8)..le(8));put(E+0x648,ptr(ROWS)..ptr(0)..le(3)..le(8))
 local free={};for i=0,7 do free[i]=true;put(ROWS+i*0x248+0x240,le(0xfffffffe))end
 local unitpeers={[4118]=FRIEND,[4107]=LOCAL,[274]=FRIEND}
 for _,unit in ipairs({4118,4107,274})do
  local a=mul(unit,0x5bd1e995);a=bit.bxor(a,bit.rshift(a,24));if a<0 then a=a+4294967296 end
  local i=mul(a,0x5bd1e995)%8
  if not free[i]then local j=i;while indices['next'..j]do j=indices['next'..j]end
   for k=0,7 do if free[k]then i=k;break end end
   put(ROWS+j*0x248+0x240,le(i));indices['next'..j]=i
  end
  free[i]=nil;indices[unit]=i;local at=ROWS+i*0x248
  put(at,le(unit));put(at+8,le(7)..le(unit));put(at+16,unitpeers[unit]);put(at+0x23a,'\1\0\0\0');put(at+0x240,le(0x7fffffff))
 end
 put(game+p.globals.entities,ptr(ENTITIES));put(ENTITIES+8,ptr(BUSY))
 put(BUSY+0xb020,ptr(BHASH)..le(2)..le(0xffffffff)..le(1))
 put(BHASH,le(0xffffffff)..le(0xffffffff)..le(0xffffffff)..le(0xffffffff))
 put(BHASH+(vehicle.network_unit%2)*8,le(vehicle.network_unit)..le(0));put(BUSY+0x201c,'\0')
end
local sends={};local proxy=setmetatable({}, {__index=ffi})
proxy.cast=function(signature,address)
 if signature=='void (*)(uint64_t,uint32_t,uint64_t)'then
  assert(address==game+p.functions.authority_send.rva)
  return function(dest,unit,target)
   local d,t=ffi.new('uint64_t[1]',dest),ffi.new('uint64_t[1]',target)
   sends[#sends+1]={ffi.string(d,8),unit,ffi.string(t,8)}
  end
 end
 return ffi.cast(signature,address)
end
local fn=assert(loadfile('work/seat_authority_diagnostic/observe.lua'))
setfenv(fn,setmetatable({require=function(name)return name=='ffi'and proxy or require(name)end},{__index=_G}))
local observer=fn().new(api,game,p,spec,compat,reader,trace)
setup();local o=assert(observer:capture(s));assert(o.owner==FRIEND and o.selfpeer==LOCAL and not o.busy)
local summary=observer:summary(o);assert(summary.owner=='P2'and summary.local_peer=='P1')
observer:send(o,FRIEND,LOCAL);assert(#sends==1 and sends[1][1]==FRIEND and sends[1][3]==LOCAL)
-- Adjacent 64-bit values above 2^53 must remain different throughout the call.
assert(sends[1][1]~=sends[1][3])
local bad={
 function()put(S+0xb398,FRIEND)end,
 function()put(S+0xb3a8,LOCAL)end,
 function()put(E,ptr(vt+8))end,
 function()put(API+0x140,ptr(exe+p.engine_functions.authority_api_request.rva))end,
 function()put(vt+0x178,ptr(exe+p.engine_functions.authority_exists.rva))end,
 function()put(dispatch+575*8,ptr(game+p.functions.authority_send.rva))end,
 function()put(E+0x65c,le(0))end,
 function()put(S+0x162e0,LOCAL..LOCAL)end,
 function()put(BUSY+0xb028,le(3))end,
 function()put(game+p.functions.authority_send.rva,'\204')end,
}
for i,change in ipairs(bad)do setup();change();local ok=pcall(observer.capture,observer,s);assert(not ok,'guard '..i)end
setup();put(BUSY+0x201c,'\1');assert(observer:capture(s).busy)
setup()
local old_busy=assert(loadfile('work/seat_authority_diagnostic/regression_052_observe.lua'))().new(api,game,p,spec,compat,reader,trace)
local old_ok,old_why=pcall(old_busy.capture,old_busy,s)
assert(not old_ok and tostring(old_why):find('busy_entity_missing'))
assert(observer:capture(s).busy==false)
-- A valid entry for the wrong identifier must not silently answer the query.
put(BHASH,le(vehicle.unit)..le(1)..le(vehicle.network_unit)..le(0));put(BUSY+0x201d,'\1')
assert(old_busy:capture(s).busy==true and observer:capture(s).busy==false)
assert(observer.evidence.busy_lookup.key==vehicle.network_unit and #observer.evidence.busy_lookup.nodes==2)
setup();put(ROWS+indices[4118]*0x248+8,le(77)..le(88));local fields=observer:capture(s);assert(fields.record_word0==77 and fields.record_word1==88 and fields.owner==FRIEND)
-- A failure must identify the bad traversal and retain bounded, stable evidence.
for _,kind in ipairs({'range','cycle'})do
 setup();local at=ROWS+indices[4118]*0x248
 put(at,le(123));put(at+0x240,le(kind=='range'and 999999 or indices[4118]))
 local ok,why=pcall(observer.capture,observer,s)
 assert(not ok and tostring(why):find(kind=='range'and 'index_out_of_range'or'chain_cycle'))
 local detail=observer.evidence.lookups[1]
 assert(detail.kind=='vehicle'and detail.total_slots==8 and detail.unchanged_after_read and #detail.nodes==1)
end
setup()
local saved_read=api.read;local times=0
api.read=function(a,n)
 if number(a)==E+0x640 and n==32 then
  times=times+1;if times==2 then put(E+0x658,le(4))end
 end
 return saved_read(a,n)
end
local ok,why=pcall(observer.capture,observer,s)
assert(not ok and tostring(why):find('table_changed_during_read'))
assert(observer.evidence.lookups[1].unchanged_after_read==false)
api.read=saved_read
-- Sender performs fresh reads: stale callers cannot use cached preflight.
setup();o=assert(observer:capture(s));put(E+0x60e4,le(43));assert(not pcall(observer.send,observer,o,FRIEND,LOCAL));assert(#sends==1)
setup();o=assert(observer:capture(s));put(ROWS+indices[4118]*0x248+16,LOCAL);assert(not pcall(observer.send,observer,o,FRIEND,LOCAL));assert(#sends==1)
setup();o=assert(observer:capture(s));assert(not pcall(observer.send,observer,o,LOCAL,FRIEND));assert(#sends==1)
setup();assert(observer:capture({state='not_in_mission'})==nil)
assert(observer:capture(s,{id=721,unit=1,network_unit=4118,resource='fixture'})==nil)
print('PASS authority observer on captured code: dynamic interface/identity/map guards, fresh-send checks, tracked identity and exact 64-bit FFI ABI (mock call only)')

-- Native-generated buckets independently exercise the production Lua lookup.
local cases=assert(loadfile('work/seat_authority_diagnostic/lookup_oracle.lua'))()
local old_observer=assert(loadfile('work/seat_authority_diagnostic/regression_051_observe.lua'))().new(api,game,p,spec,compat,reader,trace)
local regression_seen=false
for _,c in ipairs(cases)do
 setup();vehicle.network_unit=c.unit
 put(BHASH,le(0xffffffff)..le(0xffffffff)..le(0xffffffff)..le(0xffffffff))
 put(BHASH+(c.unit%2)*8,le(c.unit)..le(0))
 put(E+0x640,le(c.total)..le(c.total));put(E+0x648,ptr(ROWS)..ptr(0)..le(c.collision and 2 or 1)..le(c.cap))
 local bytes=ffi.new('uint8_t[?]',c.total*0x248)
 local function word(off,value)ffi.copy(bytes+off,le(value),4)end
 for i=0,c.total-1 do word(i*0x248+0x240,0xfffffffe)end
 if c.collision then word(c.bucket*0x248,(c.cap==319 and c.unit==421)and 307 or c.unit+1);word(c.bucket*0x248+0x240,c.index)end
 word(c.index*0x248,c.unit);word(c.index*0x248+0x240,0x7fffffff)
 ffi.copy(bytes+c.index*0x248+8,le(7)..le(c.unit)..FRIEND,16)
 -- Old incorrect offset contains a different value so mirroring cannot pass.
 ffi.copy(bytes+c.index*0x248+0x232,'\99\0\8\9',4)
 ffi.copy(bytes+c.index*0x248+0x23a,'\13\0\1\2',4)
 -- Large independent table region, separated from session and busy-map fixtures.
 local separate=0x100010000
 regions[#regions+1]={separate,c.total*0x248}
 put(E+0x648,ptr(separate));put(separate,ffi.string(bytes,c.total*0x248))
 if c.cap==319 and c.unit==421 and c.index==367 then
  local ok,why=pcall(old_observer.capture,old_observer,s,vehicle,false)
  assert(not ok and tostring(why):find('index_out_of_range'))
  local d=old_observer.evidence.lookups[1]
  assert(d.bucket==242 and d.current_index==367 and d.capacity==319 and d.nodes[1].key==307)
  regression_seen=true
 end
 for repeat_index=1,20 do
  local actual=assert(observer:capture(s,vehicle,false))
  assert(actual.owner==FRIEND and actual.serial==13 and actual.flags[1]==1 and actual.flags[2]==2)
 end
end
vehicle.network_unit=4118
assert(regression_seen,'must reproduce the actual 0.5.1 defect with the original reader')
print('PASS native-oracle lookup cases with hot loops; pointer mode='..tostring(pointers))
