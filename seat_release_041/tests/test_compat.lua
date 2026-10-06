-- Actual preserved module sections, read-only mock address space. No live game.
local profile=assert(loadfile('work/seat_release_041/src/profile.lua'))()
local spec=assert(loadfile('work/seat_release_041/src/compat_spec.lua'))()
local points=assert(loadfile('work/seat_release_041/src/trace_points.lua'))()
for _,point in ipairs(points)do profile.functions['trace_'..point.name]={rva=point.rva}end
profile,spec=assert(loadfile('work/seat_release_041/src/routing_spec.lua'))()(profile,spec)
profile,spec=assert(loadfile('work/seat_release_041/src/authority_spec.lua'))()(profile,spec)
profile,spec=assert(loadfile('work/seat_release_041/src/sync_spec.lua'))()(profile,spec)
profile,spec=assert(loadfile('work/seat_release_041/src/animation_spec.lua'))()(profile,spec)
local compat=assert(loadfile('work/seat_release_041/src/compat.lua'))()
profile,spec=assert(loadfile('work/seat_release_041/src/binding_spec.lua'))()(profile,spec)
profile,spec=assert(loadfile('work/seat_release_041/src/tank_spec.lua'))()(profile,spec)
profile,spec=assert(loadfile('work/seat_release_041/src/spin_spec.lua'))()(profile,spec)
profile,spec=assert(loadfile('work/seat_release_041/src/pose_spec.lua'))()(profile,spec)
profile,spec=assert(loadfile('work/seat_release_041/src/reservation_spec.lua'))()(profile,spec)
profile,spec=assert(loadfile('work/seat_release_041/src/binding_counts_spec.lua'))()(profile,spec)
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
local p,frames=run('enhanced')
assert(p.capabilities.normal and p.capabilities.enhanced,p.capabilities.enhanced_reason)
assert(p.globals.player==profile.globals.player and p.globals.inventory==profile.globals.inventory)
for name,t in pairs(profile.tables)do assert(p.tables[name].rva==t.rva,name)end
assert(p.animation.runtime_vtable and p.animation.getter_bytes==string.char(0x48,0x8b,0x81,0x78,1,0,0,0xc3))
print('PASS captured compatibility '..root..' enhanced, frames='..frames..' checked='..p.compatibility.checked)

for _,point in ipairs(points)do assert(p.functions['trace_'..point.name].rva==point.rva)end
print('PASS eight protocol entrypoints resolved before hooks')

api.in_image=function()return true end
local route=assert(loadfile("work/seat_release_041/src/routing.lua"))()
assert(route.new(api,bases["game.dll"],p,{}))
print("PASS resolved receive initializer, session, dispatcher and engine registry reference relationships")

assert(p.functions.authority_send and p.engine_functions.authority_constructor)
print("PASS authority witnesses resolved with gameplay and routing")

assert(p.functions.sync_snapshot_send and p.functions.sync_transition_send)
print('PASS sender and receiver sync witnesses')

assert(p.functions.anim_event_adapter.rva==0xbba250 and p.functions.anim_event_receive.rva==0x808810)
assert(loadfile('work/seat_release_041/src/inspect.lua'))().new(api,bases['game.dll'],p,{})
print('PASS actual notification handler and shared dictionary/system RIP references')

for _,name in ipairs({'reservation_entry_send','reservation_release_send','reservation_entrance_node','reservation_accepted_adapter','reservation_interaction_resource','reservation_interaction_update','reservation_mounted_joint_tags','reservation_related_weapon_lookup','reservation_related_weapon_resource'})do assert(p.functions[name]and spec.records[name])end
print('PASS nine new reservation witnesses resolved with all existing relationships')

assert(p.functions.binding_manager_add_total and p.functions.binding_manager_add_prefix and p.binding_counts.total==0x18)
local relocated={};for k,v in pairs(spec)do relocated[k]=v end;relocated.records={}
for k,v in pairs(spec.records)do relocated.records[k]=v end
for _,name in ipairs({'binding_manager_add_total','binding_manager_add_prefix'})do
 local d={};for k,v in pairs(spec.records[name])do d[k]=v end;d.hint=0;relocated.records[name]=d
end
local moved=run('enhanced',relocated)
assert(moved.capabilities.enhanced and moved.compatibility.relocated==p.compatibility.relocated+2,tostring(moved.capabilities.enhanced_reason)..' relocated='..moved.compatibility.relocated)
assert(moved.functions.binding_manager_add_total.rva==p.functions.binding_manager_add_total.rva)
assert(moved.functions.binding_manager_add_prefix.rva==p.functions.binding_manager_add_prefix.rva)
print('PASS generic initializer relocation disambiguated by independently verified weapon-manager root; one module scan shared by both')
-- A root reference can change while every masked literal still matches.
local at=bases['game.dll']+p.functions.binding_manager_add_total.rva+p.binding_counts.reference_offset+3
local disp=ffi.new('int32_t[1]');ffi.copy(disp,assert(rawread(at,4)),4);disp[0]=disp[0]+8
patches={{a=at,b=ffi.string(disp,4)}}
assert(not pcall(run,'enhanced'),'different generic manager root was accepted');patches={}
print('PASS changed weapon-manager relationship refuses initialization despite identical masked initializer bytes')
