local ffi=require('ffi')
local profile=assert(loadfile('work/src/profile.lua'))()
local exe=ffi.cast('uint8_t *',0x10000000)
local object=ffi.new('uint8_t[1024]');local machine=ffi.new('uint8_t[1024]')
local world=ffi.new('uint8_t[0x171000]')
local f=assert(io.open('work/local_data/animation_resources/4d1c334d294dfa97.state_machine.main','rb'))
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
 if r.name=='unit' then return function(id)assert(id==7);return not api.unit_dead and object or nil end end
 if r.name=='animation_set_states' then return function(id,states)
  assert(id==7 and (states[32]==14 or states[32]==9));writes=writes+1
  for i=0,tonumber(states[32])-1 do
   if states[32]==14 and(i==0 or i==13)or states[32]==9 and i==8 then current[i]=tonumber(states[i])
   else assert(states[i]==-1)end
  end
 end end
 if r.name=='animation_get_states' then return function(states,id)
  api.states_get_calls=(api.states_get_calls or 0)+1;assert(id==7);for i=0,30 do states[i]=current[i] end;states[32]=31;return states
 end end
 error(r.name)
end}
local pose=assert(loadfile('work/src/pose.lua'))()(api,profile)
profile=assert(loadfile('work/src/tank_spec.lua'))()(profile,{records={},core={},edges={},globals={driver={}}})
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
local flexible=assert(loadfile('work/src/pose.lua'))()(api,profile)
assert(flexible.check(s));accessor_ok=false;assert(not pcall(flexible.check,s));accessor_ok=true
put(object,0,'uintptr_t',0x70000000);assert(not pcall(flexible.check,s))
assert(writes==before,'Compatibility checks must never mutate animation')
print('PASS: animation resource hashes and bounds, both FRV gunner poses, both tank poses, preservation of 29 other layers, and pre-write refusal of altered graphs. Engine calls are mocked.')
print('PASS: relocated animation accessor/vtable, changed method and out-of-image pointer refusal without writes.')


-- Added and reordered ordinary overlay states are metadata fixtures; native
-- animation setters are the declared effect double above, not live outcomes.
put(object,0,'uintptr_t',number(exe+profile.animation.unit_vtable));profile.animation.runtime_vtable=false
local function u32at(ptr,o)return tonumber(ffi.cast('uint32_t *',ptr+o)[0])end
local groups=resource+u32at(resource,8)
local old_offset=u32at(groups,4+8*4);local old_layer=groups+old_offset
local old_count=u32at(old_layer,8);assert(old_count==332)
local hashes={}
for i=0,old_count-1 do hashes[i+1]=ffi.string(old_layer+u32at(old_layer,12+i*4),8)end
local added=ffi.new('uint8_t[32768]');regions[#regions+1]={b=added,n=32768}
local function replace_overlay(list)
 ffi.fill(added,32768);put(added,8,'uint32_t',#list)
 local offset_=12+#list*4
 for i,hash in ipairs(list)do put(added,12+(i-1)*4,'uint32_t',offset_);ffi.copy(added+offset_,hash,8);offset_=offset_+8 end
 -- Redirect a single group-table entry to our independent test region. API
 -- intercepts layer reads instead of inventing a native relative pointer.
end
-- Benchmark the validated baseline metadata path only, using real process
-- reads of our OWN allocated fixture buffers. Engine calls remain doubles.
local baseline_pose=assert(loadfile('work/tests/fixtures/pose_045.lua'))()(api,profile)
local optimized_pose=assert(loadfile('work/src/pose.lua'))()(api,profile)
local saved_read=api.read
ffi.cdef[[int VSSBenchRead(void *,const void *,void *,size_t,size_t *) __asm__("ReadProcessMemory");
 void *VSSBenchProcess(void) __asm__("GetCurrentProcess");
 int VSSBenchQPC(int64_t *) __asm__("QueryPerformanceCounter");
 int VSSBenchQPF(int64_t *) __asm__("QueryPerformanceFrequency");]]
local kernel=ffi.load('kernel32');local handle=kernel.VSSBenchProcess()
local qpc,qpf=ffi.new('int64_t[1]'),ffi.new('int64_t[1]');assert(kernel.VSSBenchQPF(qpf)~=0)
local function clock()assert(kernel.VSSBenchQPC(qpc)~=0);return tonumber(qpc[0])/tonumber(qpf[0])end
local buf,bytes_read=ffi.new('uint8_t[32768]'),ffi.new('size_t[1]')
local calls,bytes_total=0,0
function api.read(a,n)
 calls=calls+1;bytes_total=bytes_total+n
 local addr=number(a)
 for _,region in ipairs(regions)do local lo=number(region.b)
  if addr>=lo and addr+n<=lo+region.n then
   assert(kernel.VSSBenchRead(handle,a,buf,n,bytes_read)~=0 and bytes_read[0]==n)
   return ffi.string(buf,n)
  end
 end
 return saved_read(a,n)
end
local bs={vehicle='bastion',avatar_unit=7}
local function bench(module,label)
 for _=1,20 do assert(module.check(bs))end
 calls=0;bytes_total=0;local worst,total=0,0
 for _=1,1000 do local t=clock();assert(module.check(bs));local dt=clock()-t;total=total+dt;worst=math.max(worst,dt)end
 print(string.format('BENCH %s own-fixture RPM checks=1000 reads/check=%.0f bytes/check=%.0f mean_ms=%.4f worst_ms=%.4f',label,calls/1000,bytes_total/1000,total,worst*1000))
end
bench(baseline_pose,'0.4.5');bench(optimized_pose,'optimized');api.read=saved_read
local actual_read=api.read
local overlay_reads=0
function api.read(a,n)
 local addr=number(a);local start=number(old_layer)
 if addr>=start and addr<start+32768 then
  overlay_reads=overlay_reads+1;return ffi.string(added+addr-start,n)
 end
 return actual_read(a,n)
end
local pose=assert(loadfile('work/src/pose.lua'))()(api,profile)
local s={vehicle='bastion',avatar_unit=7,profile=profile.tables.bastion,transition=43,node=2}
local list={};for i,hash in ipairs(hashes)do list[i]=hash end
list[#list+1]='MAPLIGHT';replace_overlay(list)
assert(pose.check(s) and s.bastion_overlay.fall==237)
current[0]=123;current[13]=102;current[7]=3;current[17]=18;current[8]=237
assert(pose.clear_fall(s)and current[8]==0)
current[8]=332;local n=writes;assert(not pose.clear_fall(s)and writes==n and current[8]==332,'Unrelated map/light state was reset')
-- Move Fall/Fall_Aim by inserting states before them. Find by identity, and
-- reuse the resolved indices while checking their hashes on every request.
table.insert(list,100,'LIGHTONE');table.insert(list,101,'LIGHTTWO');replace_overlay(list)
assert(pose.check(s) and s.bastion_overlay.fall==239 and s.bastion_overlay.aim==240)
current[8]=240;assert(pose.clear_fall(s)and current[8]==0)
local first=overlay_reads;assert(pose.check(s));assert(overlay_reads-first<=5,'Resolved layer was rescanned')
list[240]='MISSING!';replace_overlay(list);n=writes
assert(not pcall(pose.clear_fall,s)and writes==n,'Missing named state did not refuse')
list[240]=hashes[238];list[#list+1]=hashes[238];replace_overlay(list)
-- Force lookup by shifting all remaining expected hints.
list[241]='CHANGED!';n=writes;assert(not pcall(pose.clear_fall,s)and writes==n,'Ambiguous graph did not refuse')
put(added,8,'uint32_t',100000);assert(not pcall(pose.check,s))
print('PASS real baseline plus appended/moved Bastion states, untouched map/light action, cached named identities and missing/ambiguous/oversize refusal')
