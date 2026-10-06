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
local fn=assert(loadfile('work/seat_handoff_motion_test/observe.lua'))
setfenv(fn,setmetatable({require=function(name)return name=='ffi'and proxy or require(name)end},{__index=_G}))
local observer=fn().new(api,game,p,spec,compat,reader,trace)

local PEERS={LOCAL,FRIEND,peer(0x76543213,0xfedcba98),peer(0x76543214,0xfedcba98)}
for i,key in ipairs(PEERS)do reader.peers[key]='P'..i end
local fleet={vehicle,
 {id=722,unit=8391233,network_unit=4119,resource='fixture2',name='bastion',seat_count=4,owned_local=false},
 {id=723,unit=8391234,network_unit=4120,resource='fixture3',name='m104',seat_count=3,owned_local=false}}
local original_setup=setup
local function room_setup(count,host)
 original_setup()
 s.player_count=count;s.peer_count=count;s.vehicles=fleet;s.peers={};s.avatars={}
 local raw='';for i=1,count do raw=raw..PEERS[i];s.peers[i]='P'..i end
 put(S+0x162d8,le(count));put(S+0x162e0,raw)
 put(E+0x130,PEERS[host]);put(S+0xb3a8,PEERS[host])
 local owners,units={},{}
 for i,v in ipairs(fleet)do
  owners[v.network_unit]=PEERS[(i%count)+1];units[#units+1]=v.network_unit
 end
 for i=1,count do
  local a={id=i*11,unit=100+i,network_unit=4100+i,is_local=i==1,owned_local=i==1,
   vehicle_input=i~=count,seat={collection=i==1 and fleet[1].id or i==2 and fleet[2].id or 0,
   current=0,reserved=0,role=1,target=-1,action=-1,transitioning=0,queued_exit=0}}
  s.avatars[i]=a;owners[a.network_unit]=PEERS[i];units[#units+1]=a.network_unit
 end
 put(E+0x640,le(32)..le(32));put(E+0x648,ptr(ROWS)..ptr(0)..le(#units)..le(32))
 local free,links={},{ }
 for i=0,31 do free[i]=true;put(ROWS+i*0x248+0x240,le(0xfffffffe))end
 for _,unit in ipairs(units)do
  local h=mul(unit,0x5bd1e995);h=bit.bxor(h,bit.rshift(h,24));if h<0 then h=h+4294967296 end
  local index=mul(h,0x5bd1e995)%32
  if not free[index]then
   local tail=index;while links[tail]do tail=links[tail]end
   for k=0,31 do if free[k]then index=k;break end end
   links[tail]=index;put(ROWS+tail*0x248+0x240,le(index))
  end
  free[index]=nil;indices[unit]=index
  local at=ROWS+index*0x248
  put(at,le(unit));put(at+8,le(7)..le(unit));put(at+16,owners[unit])
  put(at+0x23a,'\1\0\0\0');put(at+0x240,le(0x7fffffff))
 end
 put(BUSY+0xb020,ptr(BHASH)..le(8)..le(0xffffffff)..le(1))
 for i=0,7 do put(BHASH+i*8,le(0xffffffff)..le(0xffffffff))end
 for i,v in ipairs(fleet)do
  put(BHASH+(v.network_unit%8)*8,le(v.network_unit)..le(i-1));put(BUSY+0x201c+i-1,'\0')
 end
 return owners
end
local cases=0
for count=1,4 do for host=1,count do
 local owners=room_setup(count,host)
 for _,v in ipairs(fleet)do
  local o=assert(observer:capture(s,v,'all'))
  assert(o.peer_count==count and o.coordinator==PEERS[host] and o.owner==owners[v.network_unit] and not o.busy)
  local actual=0;for raw in pairs(o.members)do actual=actual+1 end;assert(actual==count)
  for i,a in ipairs(s.avatars)do assert(o.avatars[a.id].owner==PEERS[i] and o.members[o.avatars[a.id].owner])end
  local summary=observer:summary(o);assert(summary.owner==reader.peers[owners[v.network_unit]])
  cases=cases+1
 end
end end
local owners=room_setup(4,4)
put(BUSY+0x201d,'\1');assert(observer:capture(s,fleet[2],'all').busy and not observer:capture(s,fleet[1],'all').busy)
-- Observed membership/owner changes must never turn into an authority request.
assert(#sends==0)
for _,change in ipairs({
 function()put(S+0x162e0,LOCAL..FRIEND..PEERS[3]..PEERS[3])end,
 function()put(S+0x162d8,le(5))end,
 function()put(S+0xb3a8,LOCAL)end,
 function()put(E+0x65c,le(0))end,
})do
 room_setup(4,4);change();assert(not pcall(observer.capture,observer,s,fleet[1],'all'))
end
assert(#sends==0)
print('PASS '..cases..' real ownership-reader fleet cases: 1/2/3/4 peers, every coordinator, three independent vehicles, all-avatar owners including another car/outside, per-vehicle busy, full-width peer IDs, 4 malformed-room guards; zero game calls/sends. Engine memory synthetic; code from immutable capture.')
