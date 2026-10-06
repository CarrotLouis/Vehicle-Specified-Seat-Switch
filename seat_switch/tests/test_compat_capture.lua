-- Actual preserved module sections, read-only mock address space. No live game.
local profile=assert(loadfile('work/seat_switch/src/profile.lua'))()
local spec=assert(loadfile('work/seat_switch/src/compat_spec.lua'))()
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
local p,frames=run('enhanced')
assert(p.capabilities.normal and p.capabilities.enhanced,p.capabilities.enhanced_reason)
assert(p.globals.player==profile.globals.player and p.globals.inventory==profile.globals.inventory)
for name,t in pairs(profile.tables)do assert(p.tables[name].rva==t.rva,name)end
assert(p.animation.runtime_vtable and p.animation.getter_bytes==string.char(0x48,0x8b,0x81,0x78,1,0,0,0xc3))
print('PASS captured compatibility '..root..' enhanced, frames='..frames..' checked='..p.compatibility.checked)

-- A broken engine capability must not disable ordinary seat switching.
patches={{a=bases['helldivers2.exe'],b='XX'}}
p=run('enhanced');assert(p.capabilities.normal and not p.capabilities.enhanced)
p=run('normal');assert(p.capabilities.normal)
patches={}
if os.getenv('VSS_EXTENDED_COMPAT')~='1' then return end

local function le(n)local a=ffi.new('int32_t[1]',n);return ffi.string(a,4)end
local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);return a+c*256+d*65536+e*16777216 end
local function getref(address,r)
 local b=api.read(address+r.offset+r.disp,r.width);local n=u32(b,0);if n>=2147483648 then n=n-4294967296 end
 return address+r.offset+r.size+n
end
-- A RIP global displacement changes while instruction/field shapes stay valid.
for _,r in ipairs(spec.globals.player)do
 local d=spec.records[r.record];local a=bases['game.dll']+d.hint+r.offset+r.disp
 local b=rawread(a,4);local n=u32(b,0);if n>=2147483648 then n=n-4294967296 end
 patches[#patches+1]={a=a,b=le(n+0x100)}
end
p=run('normal');assert(p.globals.player==profile.globals.player+0x100,'Global should be decoded, not taken from old profile')
table.remove(patches);assert(not pcall(run,'normal'),'Conflicting independent global references must fail')
patches={}

-- Move actual next() bytes, rebasing every generated masked reference using a
-- precomputed list. This changes only this synthetic address space.
local f=assert(io.open('work/update_25480438/relocation_fixture.lua','rb'));local text=f:read('*a');f:close()
local relocation=assert(loadstring(text))()
local function hex(s)return (s:gsub('..',function(x)return string.char(tonumber(x,16))end))end
patches={{a=bases['game.dll']+relocation.old,b=string.rep('\0',relocation.length)},
         {a=bases['game.dll']+relocation.new,b=hex(relocation.hex)}}
p,frames=run('normal');assert(p.functions.next.rva==relocation.new and p.compatibility.relocated==1)
print('PASS moved native function + decoded RIP globals, frames='..frames)
patches[#patches+1]={a=bases['game.dll']+relocation.duplicate,b=hex(relocation.duplicate_hex)}
local ok,why=pcall(run,'normal');assert(not ok and tostring(why):find('ambiguous_interface_next'),tostring(why))
patches={{a=bases['game.dll']+spec.records.next.hint+0x66,b='\0'}}
ok,why=pcall(run,'normal');assert(not ok,'Changed structure access must not enable native calls')
patches={{a=bases['game.dll'],b='XX'}}
assert(not pcall(run,'normal'))
patches={{a=bases['game.dll']+spec.records.reserve.hint,b='\0'}}
p,frames=run('enhanced')
assert(p.capabilities.normal and not p.capabilities.enhanced and p.capabilities.enhanced_reason:find('interface_not_compatible_reserve'),p.capabilities.enhanced_reason)
assert(frames>1,'Exercise coroutine yields through Enhanced protected fallback')
print('PASS ambiguity, schema corruption, inconsistent references, bad PE, independent Enhanced fallback')
