-- Suppress only name-based F2-F5 queries. Native bindings retain numeric IDs.
-- Existing keyboard lookup DATA is restored before native menus and rebinding.
-- No instruction writes, page protection changes, hooks or memory scans.
local M={}
local hashes={0x7bb03d42,0x994d302c,0x1b32ee96,0x6e5e947c}
local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);assert(e);return a+c*256+d*65536+e*16777216 end
local function bytes(hex)return(hex:gsub('..',function(s)return string.char(tonumber(s,16))end))end
function M.new(api,spec,log,keyboard_provider)
 local self={status='off',enabled=false,saved={},closed=false};local verified=false;local device,header
 local function keyboard()
  return keyboard_provider and keyboard_provider()or rawget(_G,'stingray')and stingray.Keyboard
 end
 local function native_guard()
  local exe=api.module('helldivers2.exe');if not exe then return false,'missing_executable'end
  for _,p in pairs(spec)do local b=bytes(p.hex)
   if api.read(exe+p.hint,#b)~=b then return false,'keyboard_lookup_layout_changed'end
  end
  verified=true;return true
 end
 local function locate()
  if not verified then local ok,why=native_guard();assert(ok,why)end
  local k=assert(keyboard(),'keyboard_api_missing')
  assert(type(k.button_id)=='function','keyboard_binding_missing')
  local _,value=debug.getupvalue(k.button_id,1)
  local ptr=api.ffi.cast('uint8_t *',value)
  assert(tonumber(api.ffi.cast('uintptr_t',ptr))>=65536,'keyboard_upvalue_unavailable')
  local h=assert(api.read(ptr+0x80,24),'keyboard_dictionary_unreadable')
  local table_ptr=assert(api.pointer(h),'keyboard_dictionary_pointer')
  local count,cap=u32(h,16),u32(h,20)
  assert(count>=4 and count<=512 and cap>=count and cap<=4096,'keyboard_dictionary_bounds')
  local p=api.describe(table_ptr);assert(p and p.writable and not p.executable,'keyboard_dictionary_not_writable_data')
  local found={}
  for i,hash in ipairs(hashes)do
   local index=hash%cap;local seen={}
   for n=1,64 do
    assert(index<cap and not seen[index],'keyboard_dictionary_chain');seen[index]=true
    local at=table_ptr+index*12;local row=assert(api.read(at,12),'keyboard_row_unreadable')
    if u32(row,0)==hash then
     local region=api.describe(at)
     assert(region and region.writable and not region.executable and region.region_remaining>=12,'keyboard_row_not_writable_data')
     local code=u32(row,4);assert(code==0x70+i,'keyboard_numeric_id_changed')
     assert(k.button_id('f'..(i+1))==code,'keyboard_public_id_disagrees')
     found[i]={address=at+4,before=row:sub(5,8),row_address=at,hash=row:sub(1,4)};break
    end
    index=u32(row,8);assert(index~=0x7fffffff and index~=0xfffffffe,'keyboard_name_missing')
   end
   assert(found[i],'keyboard_chain_budget')
  end
  device,header=ptr,h
  return found
 end
 local invalid='\255\255\255\255'
 local function restore()
  local failures=0
  for i=#self.saved,1,-1 do local r=self.saved[i]
   local h=api.read(device+0x80,24)
   if h~=header or api.read(r.row_address,4)~=r.hash then failures=failures+1
   elseif api.read(r.address,4)==invalid and api.replace(r.address,invalid,r.before)then table.remove(self.saved,i)
   elseif api.read(r.address,4)==r.before then table.remove(self.saved,i)
   else failures=failures+1 end
  end
  self.enabled=#self.saved>0
  if failures>0 then
   if self.status~='restore_failed'then log('performance_data_restore_failed; restart_required')end
   self.status='restore_failed';return false
  end
  self.status='off';return true
 end
 function self:update(wanted,allowed)
  if self.closed then return end
  if not wanted then if self.enabled then restore()else self.status='off'end;return end
  if allowed then
   local game=api.module('game.dll')
   local pointer=game and api.pointer(api.read(game+0x347ce28,8))
   local stack=pointer and api.read(pointer+0x429c,24)
   local depth=stack and u32(stack,20)
   -- Any native modal page pauses blocking; all control bindings remain intact.
   allowed=stack~=nil and depth==0
  end
  if not wanted or not allowed then if self.enabled then restore()else self.status='off'end;return end
  if self.enabled or self.status=='unavailable'or self.status=='restore_failed'then return end
  local ok,found=pcall(locate)
  if not ok then self.status='unavailable';log('performance_data_unavailable '..tostring(found));return end
  for _,r in ipairs(found)do
   if not api.replace(r.address,r.before,invalid)then
    restore();self.status='unavailable';log('performance_data_enable_refused');return
   end
   self.saved[#self.saved+1]=r
  end
  self.enabled=true;self.status='on';log('performance_data_on; four_name_lookup_values; native_numeric_bindings_unchanged')
 end
 function self:close()if not self.closed then if self.enabled then restore()end;self.closed=true end end
 return self
end
return M
