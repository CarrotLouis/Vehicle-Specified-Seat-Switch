-- Optional, reversible profiler shortcut suppression. Never changes keyboard
-- states or input mappings. OFF has no memory work; ON resolves once per session.
local M={}
local function bytes(hex)return (hex:gsub('..',function(x)return string.char(tonumber(x,16))end))end
local function i32(b,o)
 local a,c,d,e=b:byte(o+1,o+4);if not e then return nil end
 local v=a+c*256+d*65536+e*16777216;return v>=2147483648 and v-4294967296 or v
end
local function matches(b,proof)
 if not b or #b~=proof.length then return false end
 for _,c in ipairs(proof.chunks)do c.bytes=c.bytes or bytes(c.hex)
  if b:sub(c.offset+1,c.offset+#c.bytes)~=c.bytes then return false end
 end
 return true
end
function M.new(api,game,spec,write_byte,log)
 local self={enabled=false,status='off',written={}}
 local attempted,resolver,location=false,nil,nil
 local function valid(rva,patched)
  if not api.in_image(game,rva,spec.contract.length)then return false end
  local b=api.read(game+rva,spec.contract.length)
  if not b then return false end
  local page=api.describe(game+rva)
  if not(page and page.executable and page.readable)then return false end
  if patched then
   for _,site in ipairs(spec.sites)do
    if b:sub(site+1,site+2)~='\48\192' and not(patched=='mixed'and b:sub(site+1,site+2)=='\132\192')then return false end
    b=b:sub(1,site)..'\132'..b:sub(site+2)
   end
  end
  if not matches(b,spec.contract)then return false end
  local helper
  for _,q in ipairs(spec.queries)do
   local d=i32(b,q.offset+q.disp);if not d then return false end
   local target=rva+q.offset+q.size+d
   if helper and helper~=target then return false end;helper=target
  end
  if not helper or not api.in_image(game,helper,spec.helper.length)or
   not matches(api.read(game+helper,spec.helper.length),spec.helper)then return false end
  for _,r in ipairs(spec.strings)do
   local target=rva+r.offset+r.size+i32(b,r.offset+r.disp)
   if not api.in_image(game,target,#r.text+1)or api.read(game+target,#r.text+1)~=r.text..'\0'then return false end
  end
  return true
 end
 local function resolve()
  local seen={}
  for _,hint in ipairs(spec.hints)do
   if not seen[hint]then seen[hint]=true;if valid(hint,false)then return hint end end
  end
  -- Only a bounded neighborhood in game.dll's code, once on first enable.
  -- Ordinary seat use never starts this optional lookup.
  local hint=spec.hints[#spec.hints];local first=math.max(4096,hint-spec.radius)
  local last=hint+spec.radius;local candidates={};local needle='\51\210\185\66\61\176\123'
  for rva=first,last,32768 do
   local n=math.min(32768+spec.contract.length,last-rva+spec.contract.length)
   local page=api.describe(game+rva)
   if page and page.executable and page.readable and api.in_image(game,rva,n)then
    local block=api.read(game+rva,n)
    if block then
     local start=1
     while true do
      local at=block:find(needle,start,true);if not at then break end;start=at+1
      local candidate=rva+at-1
      if not candidates[candidate] and valid(candidate,false)then candidates[candidate]=true end
     end
    end
   end
   coroutine.yield()
  end
  local found
  for candidate in pairs(candidates)do if found then return nil,'ambiguous_profiler_input'end;found=candidate end
  return found,found and nil or 'profiler_input_not_compatible'
 end
 local function restore()
  if location and not valid(location,'mixed')then
   self.status='restore_failed';self.enabled=#self.written~=0
   log('performance_restore_refused; enclosing_code_changed; restart_required');return false
  end
  local failures={}
  for i=#self.written,1,-1 do
   local address=self.written[i]
   if api.read(address,2)=='\48\192'then
    local ok,why=write_byte(address,0x30,0x84)
    if not ok then failures[#failures+1]=why else table.remove(self.written,i)end
   else failures[#failures+1]='profiler_opcode_changed_by_other_code'end
  end
  self.enabled=#self.written~=0
  if #failures>0 then self.status='restore_failed';log('performance_restore_failed '..table.concat(failures,';'));return false end
  self.status='off';return true
 end
 function self:update(wanted)
  if self.closed then return end
  if not wanted then
   if self.enabled then restore()elseif self.status~='unavailable'and not resolver then self.status='off'end
   return
  end
  if self.enabled or self.status=='unavailable'or self.status=='restore_failed'then return end
  if not attempted then attempted=true;resolver=coroutine.create(resolve);self.status='checking'end
  if resolver then
   local ok,rva,why=coroutine.resume(resolver)
   if not ok then resolver=nil;self.status='unavailable';log('performance_block_unavailable '..tostring(rva));return end
   if coroutine.status(resolver)~='dead'then return end
   resolver=nil;location=rva
   if not location then self.status='unavailable';log('performance_block_unavailable '..tostring(why));return end
  end
  if not location or not valid(location,false)then self.status='unavailable';log('performance_contract_changed');return end
  for _,site in ipairs(spec.sites)do
   local address=game+location+site
   local ok,why,changed=write_byte(address,0x84,0x30)
   if changed then self.written[#self.written+1]=address end
   if not ok then restore();self.status='unavailable';log('performance_block_failed '..tostring(why));return end
  end
  self.enabled=true;self.status='on';log('performance_block_on; four_profiler_checks_only')
 end
 function self:close()
  if not self.closed then resolver=nil;if self.enabled then restore()end;self.closed=true end
 end
 -- Exposed to offline tests, not published to the game's global namespace.
 self.valid=valid
 return self
end
return M
