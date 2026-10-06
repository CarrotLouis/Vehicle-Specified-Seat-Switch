local ffi=require('ffi')
local profile=assert(loadfile('work/seat_switch/src/profile.lua'))()
local exe=ffi.cast('uint8_t *',0x10000000)
local object=ffi.new('uint8_t[1024]');local machine=ffi.new('uint8_t[1024]')
local world=ffi.new('uint8_t[0x171000]')
local f=assert(io.open('work/animation_resources/4d1c334d294dfa97.state_machine.main','rb'))
local source=f:read('*a');f:close()
local resource=ffi.new('uint8_t[?]',#source);ffi.copy(resource,source,#source)
local regions={{b=object,n=1024},{b=machine,n=1024},{b=resource,n=#source},{b=world,n=0x171000}}
local function number(p)return tonumber(ffi.cast('uintptr_t',p))end
local function put(b,o,t,v)local v1=ffi.new(t..'[1]',v);ffi.copy(b+o,v1,ffi.sizeof(v1))end
put(object,0,'uintptr_t',number(exe+profile.animation.unit_vtable))
put(object,0x178,'uintptr_t',number(machine));put(machine,0x28,'uintptr_t',number(resource))
put(object,0x18,'uintptr_t',number(world))
local registry={};for name,p in pairs(profile.engine_functions) do registry[number(exe+p.rva)]={name=name,bytes=p.bytes} end
local current={};for i=0,30 do current[i]=i end
local writes=0;local api={module=function()return exe end}
function api.read(a,n)
 local addr=number(a);local r=registry[addr];if r then return r.bytes:sub(1,n) end
 if addr==number(exe+profile.animation.unit_vtable+0x1b0) then
  return ffi.string(ffi.new('uintptr_t[1]',number(exe+profile.engine_functions.animation_component.rva)),8)
 end
 for _,r1 in ipairs(regions) do local start=number(r1.b)
  if addr>=start and addr+n<=start+r1.n then return ffi.string(r1.b+(addr-start),n) end
 end
end
function api.pointer(b,o)
 if not b then return nil end
 local x=ffi.new('uintptr_t[1]');ffi.copy(x,b:sub((o or 0)+1),8)
 return x[0]>65535 and ffi.cast('uint8_t *',x[0]) or nil
end
function api.replace(address,before,after)
 assert(#before==4 and #after==4 and api.read(address,4)==before)
 ffi.copy(address,after,4);return true
end
api.ffi={new=ffi.new,cast=function(t,a)
 local r=registry[number(a)]
 if not r then return ffi.cast(t,a) end
 if r.name=='unit' then return function(id)assert(id==7);return object end end
 if r.name=='animation_set_states' then return function(id,states)
  assert(id==7 and states[32]==14);writes=writes+1
  for i=0,13 do if i==0 or i==13 then current[i]=tonumber(states[i]) else assert(states[i]==-1) end end
 end end
 if r.name=='animation_get_states' then return function(states,id)
  assert(id==7);for i=0,30 do states[i]=current[i] end;states[32]=31;return states
 end end
 error(r.name)
end}

local avatar=ffi.new('uint8_t[64]');regions[#regions+1]={b=avatar,n=64}
put(avatar,8,'uint32_t',77);put(avatar,12,'uint32_t',7)
local now=10;api.now=function()return now end
local events={};local watch=assert(loadfile('work/seat_driver_acquire_test/animation_watch.lua'))()(api,profile,function(e)events[#events+1]=e end)
local s={avatar=77,avatar_unit=7,avatar_address=avatar,node=1,pose_context={object=ffi.cast('uint8_t *',object),world=ffi.cast('uint8_t *',world)}}
local function snapshot()local out={};for _,r in ipairs(regions)do out[#out+1]=ffi.string(r.b,r.n)end;return table.concat(out)end
local original=snapshot();watch:arm(s);assert(watch.active and not watch.failed and events[#events].phase=='prepared')
assert(snapshot()==original and writes==0)
current[13]=41;watch:sample('before_update');assert(events[#events].states[14]==41)
current[13]=62;watch:sample('after_update');assert(events[#events].states[14]==62)
local q=profile.animation.queue
put(world,q.count_offset,'uint32_t',3)
for i=0,2 do local o=q.records_offset+i*q.stride
 put(world,o,'uint32_t',i==1 and 99 or 7);put(world,o+4,'uint32_t',0x929e2ba1);put(world,o+0x50,'uint32_t',i==2 and 4 or 3)
end
original=snapshot();watch:sample('queue_test');assert(#events[#events].queue_events==1 and events[#events].queue_events[1].hash==0x929e2ba1)
assert(snapshot()==original and writes==0)
put(world,q.count_offset,'uint32_t',513);watch:sample('queue_limit');assert(events[#events].queue_truncated and #events[#events].queue_events==0)
now=20;watch:sample('after_update');assert(not watch.active and events[#events].reason=='ten_seconds')
put(world,q.count_offset,'uint32_t',0);now=30;watch:arm(s)
put(avatar,12,'uint32_t',8);watch:sample('before_update');assert(watch.failed and not watch.active and events[#events].reason:find('avatar_changed'))
assert(not pcall(watch.arm,watch,s));assert(writes==0)
print('PASS animation watch actual FFI getter/queue reads; no writes; all-layer transitions, own-unit filtering, bounds, expiry, stale identity refusal')
