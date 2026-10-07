-- One-shot bounded keyboard/input inspection. No game-memory writes.
local M={}
local hashes={0xba7e0b93,0x7bb03d42,0x994d302c,0x1b32ee96,0x6e5e947c}
local function u32(b,o)
 if not b or #b<o+4 then return nil end
 local a,c,d,e=b:byte(o+1,o+4);return a+c*256+d*65536+e*16777216
end
local function hex(b)return b and(b:gsub('.',function(c)return string.format('%02x',c:byte())end))or'unreadable'end
local function upvalue(fn,wanted)
 if type(fn)~='function'then return nil end
 for i=1,32 do local n,v=debug.getupvalue(fn,i);if not n then return nil end;if n==wanted then return v end end
end
local function profiler_devices(api,log)
 if type(api.module)~='function'then return end
 local game=api.module('game.dll');if not game then return end
 local at=game+0x12792d0;local query=api.read(at,40)
 if not query or query:sub(1,7)~='\51\210\185\66\61\176\123'or query:byte(36)~=0xe8 then
  log('profiler_query_schema_changed');return
 end
 local function signed(b,o)local n=u32(b,o);return n and(n>=2^31 and n-2^32 or n)end
 local helper=at+40+signed(query,36);local code=api.read(helper,90)
 if not code or code:sub(25,26)~='\139\5'or code:sub(52,54)~='\76\141\61'or
  code:sub(65,69)~='\65\131\60\191\3'or code:sub(83,90)~='\73\139\140\255\128\0\0\0'then
  log('profiler_device_reader_schema_changed');return
 end
 local count=u32(api.read(helper+30+signed(code,26),4),0)
 local types=helper+58+signed(code,54)
 log('profiler_device_count='..tostring(count))
 if not count or count>32 then return end
 for i=0,count-1 do
  local kind=u32(api.read(types+i*4,4),0)
  if kind==3 then
   local p=api.pointer(api.read(types+0x80+i*8,8))
   log('profiler_keyboard '..i..' pointer='..tostring(p)..' dictionary='..hex(p and api.read(p+0x80,24)))
  end
 end
end
function M.capture(api,log,engine,menu)
 local ffi=api.ffi
 engine=engine or rawget(_G,'stingray');menu=menu or rawget(_G,'ModBindingsMenu')
 local k=assert(engine and engine.Keyboard,'Keyboard_not_loaded')
 profiler_devices(api,log)
 local codes={}
 for i=1,5 do
  local ok,id=pcall(k.button_id,'f'..i);codes[i]=ok and tonumber(id)or nil
  local named,name=false,nil
  if codes[i]and type(k.button_name)=='function'then named,name=pcall(k.button_name,codes[i])end
  log('public_key f'..i..' id='..tostring(codes[i])..' name='..tostring(named and name or nil))
 end
 local name,value=debug.getupvalue(k.button_id,1)
 log('keyboard_upvalue name='..tostring(name)..' type='..type(value))
 local device=ffi.cast('uint8_t *',value)
 local numeric=tonumber(ffi.cast('uintptr_t',device))
 assert(numeric>=65536 and numeric<2^47,'invalid_device_pointer')
 log('device_header '..hex(api.read(device,0xa0)))
 local header=assert(api.read(device+0x80,24),'dictionary_header_unreadable')
 local rows=assert(api.pointer(header),'dictionary_pointer_unreadable')
 local count,cap=u32(header,16),u32(header,20)
 log('dictionary header='..hex(header)..' count='..count..' divisor='..cap)
 assert(count<=512 and cap>=1 and cap<=4096,'dictionary_bounds')
 local region=api.describe(rows)
 log('dictionary_region readable='..tostring(region.readable)..' writable='..tostring(region.writable)..
  ' executable='..tostring(region.executable)..' remaining='..tostring(region.region_remaining))
 -- Also inspect the bounded adjacent collision area; native lookups do not
 -- check their chain indices against the initial modulo divisor.
 local slots=math.min(cap+count,4096,math.floor((region.region_remaining or 0)/12))
 assert(region.readable and slots>=cap,'dictionary_region_bounds')
 local matches=0
 for first=0,slots-1,128 do
  local n=math.min(128,slots-first);local data=assert(api.read(rows+first*12,n*12),'dictionary_chunk_unreadable')
  for j=0,n-1 do
   local h,id,next_index=u32(data,j*12),u32(data,j*12+4),u32(data,j*12+8)
   for i=1,5 do
    if h==hashes[i]or codes[i]and id==codes[i]then
     matches=matches+1
     log(string.format('candidate f%d index=%d hash=%08x id=%u next=%08x outside_divisor=%s',
      i,first+j,h,id,next_index,tostring(first+j>=cap)))
    end
   end
  end
 end
 log('candidates='..matches..' inspected_slots='..slots)
 for i=1,5 do
  local index=hashes[i]%cap;local seen={}
  for step=1,12 do
   if index>=slots or seen[index]then log('chain_stop f'..i..' index='..index..' repeated='..tostring(seen[index]==true));break end
   seen[index]=true
   local b=assert(api.read(rows+index*12,12),'chain_unreadable')
   local h,id,next_index=u32(b,0),u32(b,4),u32(b,8)
   log(string.format('chain f%d step=%d index=%d hash=%08x id=%u next=%08x',i,step,index,h,id,next_index))
   if h==hashes[i]or next_index==0x7fffffff or next_index==0xfffffffe then break end
   index=next_index
  end
 end
 -- Assigned action identity comes from the actual menu registration. Never
 -- assume a fixed shared slot or inspect another mod's actions.
 local s=menu and upvalue(menu.register_binding,'state')
 log('bindings_menu api='..tostring(menu and menu.api)..' version='..tostring(menu and menu.version)..' state='..type(s))
 if type(s)=='table'and type(s.registry)=='table'and type(s.buckets)=='table'then
  for i=1,5 do
   local record=s.registry['vehicle_seat_tools.vss.seat'..i]
   local address=record and s.buckets[record.code]
   if type(address)=='number'and address>=65536 and address<2^47 then
    local at=ffi.cast('uint8_t *',address);local b=api.read(at,8)
    local code,n=u32(b,0),u32(b,4)
    if code==record.code and n and n<=16 then
     log('seat_action '..i..' code='..code..' count='..n..' mappings='..hex(n>0 and api.read(at+8,n*20)or''))
    else log('seat_action '..i..' stale_or_invalid')end
   else log('seat_action '..i..' not_ready')end
  end
 end
 log('capture_complete; memory_writes=0; no_inputs_injected')
 return true
end
return M
