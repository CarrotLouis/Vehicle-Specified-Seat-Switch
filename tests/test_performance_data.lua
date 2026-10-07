local ffi=require('ffi');local spec=dofile('work/src/performance_data_spec.lua');local M=dofile('work/src/performance_data.lua')
local device=ffi.new('uint8_t[256]');local rows=ffi.new('uint32_t[?]',256*3)
local code={};for _,s in pairs(spec)do code[s.hint]=(s.hex:gsub('..',function(x)return string.char(tonumber(x,16))end))end
local function write32(at,n)local v=ffi.new('uint32_t[1]',n);ffi.copy(at,v,4)end
local hashes={0x7bb03d42,0x994d302c,0x1b32ee96,0x6e5e947c}
ffi.copy(device+0x80,ffi.new('void *[1]',rows),8);write32(device+0x90,4);write32(device+0x94,256)
for _,h in ipairs(hashes)do local n=h%256;rows[n*3]=h;rows[n*3+1]=0;rows[n*3+2]=0x7fffffff end
for i,h in ipairs(hashes)do rows[(h%256)*3+1]=0x70+i end
local owner=ffi.new('uint8_t[0x4400]');local game=0x1000000;local writes=0;local menu_open=false
local header=ffi.new('void *[1]',owner)
local api={ffi=ffi,module=function(name)return name=='game.dll'and game or 0 end,
 pointer=function(b)if not b then return nil end;local n=ffi.new('void *[1]');ffi.copy(n,b,8);return ffi.cast('uint8_t *',n[0])end,
 describe=function()return {readable=true,writable=true,executable=false,region_remaining=4096}end}
function api.read(at,n)
 if type(at)=='number'then
  if at==game+0x347ce28 then return ffi.string(header,8)end
  if code[at]then return code[at]:sub(1,n)end
  return nil
 end
 if at==owner+0x429c then local b=string.rep('\0',20)..(menu_open and'\1'or'\0')..'\0\0\0';return b end
 return ffi.string(at,n)
end
function api.replace(at,before,after)
 if ffi.string(at,#before)~=before then return false end
 writes=writes+1;ffi.copy(at,after,#after);return true
end
local function id(name)
 local d=device -- First upvalue models the native closure's device pointer.
 assert(d~=nil);local n=tonumber(name:match('f(%d+)'))-1;local v=tonumber(rows[(hashes[n]%256)*3+1]);return v~=0xffffffff and v or nil
end
local block=M.new(api,spec,function()end,function()return {button_id=id}end)
-- The profiler resolves names for each press; native actions hold numeric IDs
-- from the previously loaded binding map. These are separate consumers.
local cached,pressed={},{[0x71]=true,[0x72]=false,[0x73]=true,[0x74]=false}
for i=1,4 do cached[i]=id('f'..(i+1))end
local function action(i)return pressed[cached[i]]==true end
local function monitor(i)local code=id('f'..(i+1));return code~=nil and pressed[code]==true end
local before={};for i=1,4 do before[i]=action(i);assert(monitor(i)==before[i])end
block:update(false,true);assert(writes==0)
block:update(true,true);assert(block.status=='on'and writes==4)
for i,h in ipairs(hashes)do
 assert(id('f'..(i+1))==nil)
 assert(not monitor(i)and action(i)==before[i],'numeric action was affected by name filtering')
end
for n=1,100 do block:update(true,true)end;assert(writes==4)
menu_open=true;block:update(true,true);assert(not block.enabled and writes==8)
for i,h in ipairs(hashes)do assert(id('f'..(i+1))==0x70+i)end
menu_open=false;block:update(true,true);assert(block.enabled and writes==12)
block:close();assert(not block.enabled and writes==16)
local function new()return M.new(api,spec,function()end,function()return {button_id=id}end)end
local initial=writes;local lookup=spec.lookup.hint;local original=code[lookup];code[lookup]='unknown'
local changed=new();changed:update(true,true);assert(changed.status=='unavailable'and writes==initial);code[lookup]=original
local absent=M.new(api,spec,function()end,function()return {button_id=math.abs}end)
absent:update(true,true);assert(absent.status=='unavailable'and writes==initial)
local describe=api.describe;api.describe=function()return {writable=true,executable=true,region_remaining=4096}end
local executable=new();executable:update(true,true);assert(executable.status=='unavailable'and writes==initial);api.describe=describe
-- A broken chain refuses within its budget, without a write.
local index=hashes[1]%256;local row=ffi.string(rows+index*3,12)
rows[index*3]=0;rows[index*3+2]=index
local cyclic=new();cyclic:update(true,true);assert(cyclic.status=='unavailable'and writes==initial)
ffi.copy(rows+index*3,row,12)
-- Failure after one edit rolls it back instead of leaving a partial filter.
local replace=api.replace;local attempt=0
function api.replace(...)
 attempt=attempt+1;if attempt==2 then return false end;return replace(...)
end
local partial=new();partial:update(true,true);assert(not partial.enabled and partial.status=='unavailable')
for i=1,4 do assert(id('f'..(i+1))==cached[i])end
api.replace=replace
-- A failed rollback keeps its failure state and saved data for a safe retry.
attempt=0
function api.replace(...)
 attempt=attempt+1;if attempt==2 or attempt==3 then return false end;return replace(...)
end
local failed_rollback=new();failed_rollback:update(true,true)
assert(failed_rollback.enabled and failed_rollback.status=='restore_failed')
api.replace=replace;failed_rollback:close();assert(not failed_rollback.enabled)
-- Preserve foreign changes rather than blindly overwriting them.
local logs={};local drift=M.new(api,spec,function(s)logs[#logs+1]=s end,function()return {button_id=id}end)
drift:update(true,true);rows[index*3+1]=0x88
drift:update(false,true);assert(drift.status=='restore_failed'and rows[index*3+1]==0x88)
local logged=#logs;for i=1,10 do drift:update(false,true)end;assert(#logs==logged)
rows[index*3+1]=0xffffffff;drift:close();assert(not drift.enabled)
for i=1,4 do assert(id('f'..(i+1))==cached[i]and action(i)==before[i])end
print('PASS four data fields; cached numeric actions survive name filtering; menu/shutdown restoration, no active rewrites, unknown/absent/executable/cyclic refusal, partial rollback and foreign-value preservation')

-- Reproduce the observed 319-bucket, 62 -> 326 F3 collision with a native
-- name lookup consumer independent of the filter's traversal implementation.
local geometry=dofile('work/tests/fixtures/keyboard_collision.lua')
local extra_device=ffi.new('uint8_t[256]')
local capacity=geometry.divisor+geometry.count
local extra_rows=ffi.new('uint32_t[?]',capacity*3)
for n=0,capacity-1 do extra_rows[n*3+2]=0xfffffffe end
for n,r in pairs(geometry.rows)do for j=1,3 do extra_rows[n*3+j-1]=r[j]end end
ffi.copy(extra_device+0x80,ffi.new('void *[1]',extra_rows),8)
write32(extra_device+0x90,geometry.count);write32(extra_device+0x94,geometry.divisor)
local function extra_id(name)
 local d=extra_device;assert(d~=nil)
 local i=assert(tonumber(name:match('f(%d+)')))-1;local hash=hashes[i];assert(hash)
 local at=hash%geometry.divisor
 for step=1,64 do
  assert(at<capacity);local row=extra_rows+at*3
  if row[0]==hash then return row[1]~=0xffffffff and tonumber(row[1])or nil end
  at=tonumber(row[2]);if at==0x7fffffff or at==0xfffffffe then return nil end
 end
 error('fixture native lookup loop')
end
local saved_describe=api.describe
function api.describe(at)
 local n=tonumber(ffi.cast('uintptr_t',at));local start=tonumber(ffi.cast('uintptr_t',extra_rows))
 if n>=start and n<start+ffi.sizeof(extra_rows)then
  return{readable=true,writable=true,executable=false,region_remaining=start+ffi.sizeof(extra_rows)-n}
 end
 return saved_describe(at)
end
local logs={};local old=dofile('work/tests/fixtures/performance_042.lua').new(api,spec,function(s)logs[#logs+1]=s end,function()return{button_id=extra_id}end)
initial=writes;old:update(true,true)
assert(old.status=='unavailable'and writes==initial and table.concat(logs,'\n'):find('keyboard_dictionary_chain',1,true))
local fixed=M.new(api,spec,function()end,function()return{button_id=extra_id}end)
fixed:update(true,true);assert(fixed.status=='on'and writes==initial+4)
for i=1,4 do assert(extra_id('f'..(i+1))==nil)end
for n=1,100 do fixed:update(true,true)end;assert(writes==initial+4)
menu_open=true;fixed:update(true,true);assert(not fixed.enabled and writes==initial+8)
for i=1,4 do assert(extra_id('f'..(i+1))==0x70+i)end
-- Genuine out-of-storage indices still refuse all writes.
menu_open=false;extra_rows[62*3+2]=capacity
local corrupt=M.new(api,spec,function()end,function()return{button_id=extra_id}end)
initial=writes;corrupt:update(true,true);assert(corrupt.status=='unavailable'and writes==initial)
extra_rows[62*3+2]=326
local foreign_link=M.new(api,spec,function()end,function()return{button_id=extra_id}end)
foreign_link:update(true,true);assert(foreign_link.enabled)
extra_rows[326*3+2]=329;foreign_link:update(false,true)
assert(foreign_link.status=='restore_failed'and extra_rows[326*3+2]==329)
extra_rows[326*3+2]=328;foreign_link:close();assert(not foreign_link.enabled)
fixed:close();api.describe=saved_describe
print('PASS captured F3 collision reproduces shipped rejection; corrected traversal filters/restores four keys without scans; invalid storage still refuses all writes')
