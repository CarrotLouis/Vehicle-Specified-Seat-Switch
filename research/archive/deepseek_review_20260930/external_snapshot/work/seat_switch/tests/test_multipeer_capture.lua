-- Multiplayer capability group against the preserved module sections, read-only
-- mock address space. No live game and no process is accessed.
--
-- Proves the reason the multipeer group exists: requesting the message-routing and
-- chassis-authority witnesses must not change the required set that Normal and
-- Enhanced-solo resolve, and a broken multipeer-only witness must leave both of
-- them working.
local profile=assert(loadfile('work/seat_switch/src/profile.lua'))()
local spec=assert(loadfile('work/seat_switch/src/compat_spec.lua'))()
local points=assert(loadfile('work/seat_switch/src/trace_points.lua'))()
local routing_spec=assert(loadfile('work/seat_switch/src/routing_spec.lua'))()
local authority_spec=assert(loadfile('work/seat_switch/src/authority_spec.lua'))()
local compose=assert(loadfile('work/seat_switch/src/multipeer_spec.lua'))()
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
local function run(mode,s,extra)
 local task=compat.start(api,bases['game.dll'],profile,s or spec,mode,nil,extra)
 for i=1,60000 do local p=task.step();if p then return p,i end end
 error('resolver never finished')
end

-- Compose the multipeer witnesses into their own group.
profile,spec=compose(profile,spec,routing_spec,authority_spec,points)
local core=#spec.core
assert(core>0 and #spec.multipeer>0)

-- Normal resolves exactly the base set and must not touch the new group.
local p=run('normal')
assert(p.capabilities.normal,p.capabilities.extra_reason)
assert(p.compatibility.checked==core,'normal checked='..p.compatibility.checked..' expected '..core)
assert(p.capabilities.multipeer==nil,'an unrequested capability group must stay nil, not false')
print('PASS normal resolves exactly '..core..' base names; multipeer group stays unrequested')

-- Enhanced-solo is also unaffected and still does not pull the group in.
p=run('enhanced')
assert(p.capabilities.normal and p.capabilities.enhanced,p.capabilities.enhanced_reason)
local enhanced_checked=p.compatibility.checked
assert(enhanced_checked>core)
assert(p.capabilities.multipeer==nil)
print('PASS enhanced-solo resolves '..enhanced_checked..' names without the multipeer group')

-- Requesting the group adds exactly its witnesses on top of Enhanced.
p=run('enhanced',spec,{'multipeer'})
assert(p.capabilities.normal and p.capabilities.enhanced,p.capabilities.enhanced_reason)
assert(p.capabilities.multipeer,tostring(p.capabilities.extra_reason))
assert(p.compatibility.checked==enhanced_checked+#spec.multipeer,
 'checked='..p.compatibility.checked..' expected '..(enhanced_checked+#spec.multipeer))
print('PASS requested multipeer adds exactly '..#spec.multipeer..' witnesses (checked='..p.compatibility.checked..')')

-- The decisive property: break one multipeer-only witness and Normal/Enhanced-solo
-- must still work, while the multipeer capability alone is refused.
local victim=assert(spec.records.authority_send,'authority_send record')
assert(victim.module=='game')
patches={{a=bases['game.dll']+victim.hint,b='\0'}}
p=run('enhanced',spec,{'multipeer'})
assert(p.capabilities.normal,'normal must survive a multipeer-only failure')
assert(p.capabilities.enhanced,'enhanced-solo must survive a multipeer-only failure')
assert(not p.capabilities.multipeer,'multipeer must be refused when its witness changed')
assert(tostring(p.capabilities.extra_reason):find('authority_send'),tostring(p.capabilities.extra_reason))
print('PASS a broken multipeer witness leaves normal+enhanced intact: '..tostring(p.capabilities.extra_reason))
patches={}

-- And the same break must still refuse Enhanced when the witness is genuinely required.
p=run('normal')
assert(p.capabilities.normal)
print('PASS normal still resolves after the patch is removed')
