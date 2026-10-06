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
local pose=assert(loadfile('work/seat_switch/src/pose.lua'))()(api,profile)
local expected={m102={{108,64},{112,68},{106,62},{110,66},{104,60}},m104={{108,64},{112,68},{104,60}},
 bastion={{123,102},{121,96},{123,102},{123,102}},maelstrom={{123,102},{121,96},{123,102},{123,102}}}
for vehicle,seats in pairs(expected) do
 local s={vehicle=vehicle,avatar_unit=7};assert(pose.check(s))
 for target,pair in ipairs(seats) do
  assert(pose.apply(s,target-1):match('entry_action_skipped=true'))
  assert(current[0]==pair[1] and current[13]==pair[2])
  for i=1,30 do if i~=13 then assert(current[i]==i,'Unrelated animation layer reset') end end
 end
end
-- Pending entry events must not undo the immediate pose on the next frame.
local s1={vehicle='m104',avatar_unit=7};local q=profile.animation.queue
local function command(i,unit_id,event,kind)
 local b=world+q.records_offset+i*q.stride
 put(b,0,'uint32_t',unit_id);put(b,4,'uint32_t',event);put(b,0x50,'uint32_t',kind or 3)
end
command(0,7,0xe86f3c8c);put(world,q.count_offset,'uint32_t',1)
assert(pose.check(s1))
command(1,7,0xe86f3c8c);command(2,8,0xe86f3c8c);command(3,7,0x9b7741d3);command(4,7,0xe86f3c8c,4)
put(world,q.count_offset,'uint32_t',5)
local before_queue=ffi.string(world+q.records_offset,5*q.stride)
assert(pose.apply(s1,2):match('entry_events_replaced=1'))
local after_queue=ffi.string(world+q.records_offset,5*q.stride)
assert(after_queue==before_queue:sub(1,q.stride+4)..q.end_event..before_queue:sub(q.stride+9))
assert(pose.check(s1));put(world,q.count_offset,'uint32_t',0)
assert(not pcall(pose.apply,s1,2),'A consumed/reset command batch must be refused')
local s={vehicle='m102',avatar_unit=7};local before=writes
put(resource,4,'uint32_t',30);assert(not pcall(pose.check,s));put(resource,4,'uint32_t',31)
-- Even equal state counts are insufficient: a modded state index must be rejected.
local index=assert(source:find(profile.animation.states.frv_gunner[1].hash,1,true))
resource[index-1]=0;assert(not pcall(pose.check,s));resource[index-1]=source:byte(index)
put(object,0,'uintptr_t',number(exe+profile.animation.unit_vtable)+8);assert(not pcall(pose.check,s))
assert(writes==before)
-- A relocated vtable/accessor is accepted by its actual method and resource
-- identities, without relying on their previous RVAs.
profile.animation.runtime_vtable=true
profile.animation.getter_bytes=profile.engine_functions.animation_component.bytes:sub(1,8)
profile.engine_ranges={{rva=0x1000,size=0x2000000,readable=true,execute=true}}
local moved_vtable=exe+profile.animation.unit_vtable+0x100
local moved_getter=exe+profile.engine_functions.animation_component.rva+0x100
local previous_read=api.read
local accessor_ok=true
function api.read(a,n)
 if number(a)==number(moved_vtable+0x1b0) then return ffi.string(ffi.new('uintptr_t[1]',number(moved_getter)),8)end
 if number(a)==number(moved_getter) then return accessor_ok and profile.animation.getter_bytes or string.rep('\0',n)end
 return previous_read(a,n)
end
put(object,0,'uintptr_t',number(moved_vtable))
local flexible=assert(loadfile('work/seat_switch/src/pose.lua'))()(api,profile)
assert(flexible.check(s));accessor_ok=false;assert(not pcall(flexible.check,s));accessor_ok=true
put(object,0,'uintptr_t',0x70000000);assert(not pcall(flexible.check,s))
assert(writes==before,'Compatibility checks must never mutate animation')
print('PASS: animation resource hashes and bounds, both FRV gunner poses, both tank poses, preservation of 29 other layers, and pre-write refusal of altered graphs. Engine calls are mocked.')
print('PASS: relocated animation accessor/vtable, changed method and out-of-image pointer refusal without writes.')
