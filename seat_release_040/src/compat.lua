-- Read-only interface resolver. Hashes label observations, never authorize calls.
-- Field displacements and local branches remain literal; only independently
-- identified relocatable references are masked in generated evidence.
local bit=require('bit')
local M={}
local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);assert(e,'short_compat_read');return a+c*256+d*65536+e*16777216 end
local function signed(b,o,n)local v=0;for i=n-1,0,-1 do v=v*256+b:byte(o+i+1) end;if v>=2^(n*8-1) then v=v-2^(n*8) end;return v end
local function copy(v)if type(v)~='table' then return v end;local t={};for k,x in pairs(v)do t[k]=copy(x)end;return t end
local function bytes(hex)return (hex:gsub('..',function(x)return string.char(tonumber(x,16))end))end
local function match(b,chunks)
 if not b then return false end
 for _,c in ipairs(chunks)do c.bytes=c.bytes or bytes(c.hex);if b:sub(c.offset+1,c.offset+#c.bytes)~=c.bytes then return false end end
 return true
end
M.match=match
function M.start(api,game,baseline,spec,mode,trace)
 local used,scanned=0,0
 local modules,resolved={},{}
 local output=copy(baseline);output.layout_schema=spec.schema
 output.capabilities={normal=false,enhanced=false};output.compatibility={strategy='interface_evidence_v1',relocated=0}
 local function log(s)if trace then trace('compat '..s)end end
 local function read(base,rva,n)
  used=used+n
  if used>262144 then used=0;coroutine.yield('checking_interfaces') end
  return api.read(base+rva,n)
 end
 local function inside(m,rva,n,kind)
  if type(rva)~='number' or rva<0 or n<1 or rva+n>m.size then return false end
  for _,s in ipairs(m.sections) do
   if rva>=s.rva and rva+n<=s.rva+s.size and (not kind or s[kind]) then return true end
  end
  return false
 end
 local function module(name)
  if modules[name] then return modules[name] end
  local base=name=='game' and game or assert(api.module('helldivers2.exe'),'missing_engine_module')
  local h=assert(read(base,0,64),'module_header_unreadable');assert(h:sub(1,2)=='MZ','module_not_PE')
  local pe=u32(h,60);assert(pe>=64 and pe<1048576,'invalid_PE_offset')
  local c=assert(read(base,pe,24),'PE_header_unreadable');assert(c:sub(1,4)=='PE\0\0' and c:sub(5,6)=='\100\134','expected_x64')
  local count=c:byte(7)+c:byte(8)*256;local optional=c:byte(21)+c:byte(22)*256
  assert(count>0 and count<=96 and optional>=64 and optional<=4096,'invalid_PE_layout')
  local o=assert(read(base,pe+24,optional),'PE_optional_unreadable');assert(o:sub(1,2)=='\11\2','expected_PE32plus')
  local m={base=base,size=u32(o,56),sections={}};assert(m.size>=4096 and m.size<=134217728,'invalid_image_size')
  local table_=assert(read(base,pe+24+optional,count*40),'PE_sections_unreadable')
  for i=0,count-1 do
   local p=i*40;local n,rva,flags=u32(table_,p+8),u32(table_,p+12),u32(table_,p+36)
   assert(rva+n<=m.size,'section_outside_image')
   if n>0 then m.sections[#m.sections+1]={rva=rva,size=n,execute=bit.band(flags,0x20000000)~=0,
    readable=bit.band(flags,0x40000000)~=0,writable=bit.band(flags,0x80000000)~=0} end
  end
  modules[name]=m;return m
 end
 local function branch(m,address,r)
  local b=assert(read(m.base,address+r.offset+r.disp,r.width),'reference_unreadable')
  return address+r.offset+r.size+signed(b,0,r.width)
 end
 local function valid(m,address,d,collect)
  if not inside(m,address,d.length,'execute') then return false end
  if not match(read(m.base,address,d.length),d.chunks) then return false end
  for _,c in ipairs(d.callees or {}) do
   local target=branch(m,address,c)
   if not inside(m,target,c.length,'execute') or not match(read(m.base,target,c.length),c.chunks) then return false end
  end
  -- Generic component initializers may share their entire masked body.
  -- Their global must equal the one used by an independently resolved
  -- semantic handler. A startup scan can collect candidates before that
  -- handler resolves; use is permitted only after the relationship holds.
  for _,r in ipairs(d.references or {})do
   local anchor=resolved[r.record]
   if not anchor then if not collect then return false end
   else
    if spec.records[r.record].module~=d.module then return false end
    local target=branch(m,address,r)
    if not inside(m,target,8,'writable')or target~=branch(m,anchor,r.reference)then return false end
   end
  end
  return true
 end
 local resolving={}
 local function resolve(key)
  if resolved[key] then return resolved[key] end
  local d=assert(spec.records[key],'unknown_interface');local m=module(d.module)
  assert(not resolving[key],'cyclic_interface_relationship');resolving[key]=true
  for _,r in ipairs(d.references or {})do resolve(r.record)end
  local address
  if valid(m,d.hint,d) then address=d.hint else
   log('locating '..key)
   -- All moved witnesses in one module share a single bounded pass. A large
   -- relink must not cause dozens of repeated whole-module reads.
   if not m.scan_result then
    local pending={};local tail_size=1;m.scan_result={}
    local groups={spec.core};if mode=='enhanced' then groups[#groups+1]=spec.enhanced;groups[#groups+1]=spec.engine end
    for _,group in ipairs(groups)do for _,name in ipairs(group)do
     local proof=spec.records[name]
     if proof.module==d.module and not valid(m,proof.hint,proof) then
      local row={name=name,proof=proof,needle=bytes(proof.needle.hex),matches={},seen={},limit=proof.references and 128 or 2}
      pending[#pending+1]=row;m.scan_result[name]=row;tail_size=math.max(tail_size,#row.needle-1)
     end
    end end
    for _,s in ipairs(m.sections)do if s.execute and s.readable then
     local offset=0;local tail=''
     while offset<s.size do
      local n=math.min(32768,s.size-offset);local b=read(m.base,s.rva+offset,n)
      scanned=scanned+n;assert(scanned<=256*1024*1024,'compat_scan_budget_exceeded')
      if b then
       local joined=tail..b
       for _,row in ipairs(pending)do
        local start=1
        while #row.matches<row.limit do
         local p=joined:find(row.needle,start,true);if not p then break end;start=p+1
         local candidate=s.rva+offset-#tail+p-1-row.proof.needle.offset
         if not row.seen[candidate] and valid(m,candidate,row.proof,true) then
          row.seen[candidate]=true;row.matches[#row.matches+1]=candidate
         end
        end
       end
       tail=joined:sub(-tail_size)
      else tail='';m.scan_incomplete=true end
      offset=offset+n
     end
    end end
   end
   local row=m.scan_result[key];local matches={}
   assert(not row or #row.matches<row.limit or not d.references,'interface_candidate_budget_'..key)
   for _,candidate in ipairs(row and row.matches or{})do if valid(m,candidate,d)then matches[#matches+1]=candidate end end
   assert(not m.scan_incomplete,'incomplete_scan_'..key)
   assert(#matches<=1,'ambiguous_interface_'..key)
   assert(#matches==1,'interface_not_compatible_'..key);address=matches[1]
   assert(valid(m,address,d),'interface_changed_during_scan_'..key)
   output.compatibility.relocated=output.compatibility.relocated+1
  end
  resolved[key]=address
  resolving[key]=nil
  if output.functions[key] and d.module=='game' then output.functions[key]={rva=address,bytes=assert(read(m.base,address,32))} end
  if output.engine_functions[key] and d.module=='exe' then output.engine_functions[key]={rva=address,bytes=assert(read(m.base,address,32))} end
  return address
 end
 local function edges()
  for _,e in ipairs(spec.edges)do if resolved[e.from] and resolved[e.to] then
   local m=module(spec.records[e.from].module)
   assert(branch(m,resolved[e.from],e)==resolved[e.to],'call_relationship_changed_'..e.from..'_'..e.to)
  end end
 end
 local function globals(names)
  local m=module('game')
  for _,name in ipairs(names)do
   local target,count=nil,0
   for _,r in ipairs(assert(spec.globals[name],'missing_global_evidence'))do if resolved[r.record] then
    local value=branch(m,resolved[r.record],r)
    assert(inside(m,value,8,'writable'),'global_outside_data_'..name)
    assert(not target or target==value,'inconsistent_global_'..name);target=value;count=count+1
   end end
   assert(count>=2,'insufficient_global_evidence_'..name)
   if name=='driver' then output.driver.global=target else output.globals[name]=target end
  end
 end
 local function adjacency()
  local m=module('game');local d=spec.adjacency;local a=branch(m,resolved[d.record],d)
  assert(inside(m,a,d.length,'execute'),'adjacency_outside_code')
  local b=assert(read(m.base,a,d.length));assert(match(b,d.chunks),'adjacency_dispatch_changed')
  local image=a+d.base_end+signed(b,d.base_disp,4);assert(image==0,'adjacency_base_changed')
  local table_=u32(b,d.table_disp);assert(inside(m,table_,45*4,'execute'),'adjacency_table_outside_code')
  for name,t in pairs(output.tables)do
   local dest=u32(assert(read(m.base,table_+(t.transition-1)*4,4)),0)
   assert(inside(m,dest,18,'execute'),'adjacency_case_outside_code')
   local code=assert(read(m.base,dest,18));local address
   if t.row==8 then
    assert(code:sub(1,6)==bytes('8bc2488d04c5') and code:sub(11,14)==bytes('4903c0c3'),'adjacency_case_changed_'..name)
    address=u32(code,6)
   else
    assert(t.row==12 and code:sub(1,9)==bytes('8bc2488d0c40498d80') and code:sub(14,18)==bytes('488d0488c3'),'adjacency_case_changed_'..name)
    address=u32(code,9)
   end
   assert(inside(m,address,t.size,'readable'),'adjacency_data_outside_image_'..name)
   t.rva=address
  end
 end
 local function run()
  for _,key in ipairs(spec.core)do resolve(key)end
  edges();globals({'mission','player','entities','avatar','seater','collection','session'});adjacency()
  output.capabilities.normal=true
  if mode=='enhanced' then
   local ok,why=pcall(function()
    for _,key in ipairs(spec.enhanced)do resolve(key)end
    for _,key in ipairs(spec.engine)do resolve(key)end
    edges();globals({'inventory','driver'})
    output.driver.proofs={}
    for _,offset in ipairs(spec.driver_proofs)do
     local rva=resolved._driver_input+offset
     output.driver.proofs[#output.driver.proofs+1]={rva=rva,bytes=assert(read(game,rva,7))}
    end
    output.animation.runtime_vtable=true
    output.animation.getter_bytes=bytes(spec.getter_hex)
    output.engine_ranges=module('exe').sections
    output.capabilities.enhanced=true
   end)
   if not ok then output.capabilities.enhanced_reason=tostring(why);log('enhanced_unavailable '..tostring(why)) end
  end
  output.compatibility.checked=0;for _ in pairs(resolved)do output.compatibility.checked=output.compatibility.checked+1 end
  log('ready schema='..spec.schema..' checked='..output.compatibility.checked..' relocated='..output.compatibility.relocated..' enhanced='..tostring(output.capabilities.enhanced))
  return output
 end
 local co=coroutine.create(run)
 return {step=function()
  local ok,value=coroutine.resume(co);if not ok then error(value)end
  if coroutine.status(co)=='dead' then return value end
  return nil,value
 end}
end
return M
