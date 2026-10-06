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
local fn=assert(loadfile('work/seat_rear_weapon_diagnostic/observe.lua'))
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

for _,node in ipairs({1,2,3,4})do
 setup();s.avatars[1].seat.current=node;s.avatars[1].seat.reserved=node;s.avatars[1].seat.role=node==4 and 2 or 3
 local value=assert(observer:capture(s));local invoked=false;local before=#sends
 observer:send(value,FRIEND,LOCAL,function()invoked=true end)
 assert(invoked and #sends==before+1)
 s.avatars[2].seat.current=2;invoked=false
 assert(not pcall(observer.send,observer,value,FRIEND,LOCAL,function()invoked=true end));assert(not invoked)
 s.avatars[2].seat.current=0
end
print('PASS new handoff observer passenger/gunner request, driver change refusal, before-invoke marker; runtime code/schema guards')
