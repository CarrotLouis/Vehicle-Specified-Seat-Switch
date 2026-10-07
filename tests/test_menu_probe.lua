local ffi=require('ffi');local probe=dofile('work/src/menu_probe.lua')
local device=ffi.new('uint8_t[256]');local rows=ffi.new('uint32_t[?]',64*3)
ffi.copy(device+0x80,ffi.new('void *[1]',rows),8)
ffi.cast('uint32_t *',device+0x90)[0]=5;ffi.cast('uint32_t *',device+0x94)[0]=16
local hashes={0xba7e0b93,0x7bb03d42,0x994d302c,0x1b32ee96,0x6e5e947c}
for i,h in ipairs(hashes)do local n=15+i;rows[n*3]=h;rows[n*3+1]=0x6f+i;rows[n*3+2]=0x7fffffff end
local function id(name)local d=device;assert(d~=nil);return 0x6f+tonumber(name:sub(2))end
local logs,reads={},0
local api={ffi=ffi,read=function(at,n)reads=reads+1;return ffi.string(at,n)end,
 pointer=function(b)local p=ffi.new('void *[1]');ffi.copy(p,b,8);return ffi.cast('uint8_t *',p[0])end,
 describe=function()return{region_remaining=64*12,readable=true,writable=true,executable=false}end,
 replace=function()error('read-only probe attempted a write')end}
local before=ffi.string(rows,64*12)
assert(probe.capture(api,function(s)logs[#logs+1]=s end,{Keyboard={button_id=id,button_name=function(n)return'f'..(n-0x6f)end}},{api=1,version=3}))
assert(before==ffi.string(rows,64*12)and reads<80)
local text=table.concat(logs,'\n')
assert(text:find('outside_divisor=true',1,true)and text:find('capture_complete',1,true))
assert(text:find('f2 id=113',1,true))
-- Exercise the real RIP-relative reader with declared executable/data doubles.
local raw_read=api.read;local base=0x1000000
local q=base+0x12792d0;local helper,number,types=base+0x1300000,base+0x1400000,base+0x1500000
local query=ffi.new('uint8_t[40]');ffi.copy(query,'\51\210\185\66\61\176\123',7);query[35]=0xe8
ffi.cast('int32_t *',query+36)[0]=helper-q-40
local code=ffi.new('uint8_t[90]');ffi.copy(code+24,'\139\5',2);ffi.cast('int32_t *',code+26)[0]=number-helper-30
ffi.copy(code+51,'\76\141\61',3);ffi.cast('int32_t *',code+54)[0]=types-helper-58
ffi.copy(code+64,'\65\131\60\191\3',5);ffi.copy(code+82,'\73\139\140\255\128\0\0\0',8)
local chunks={[q]=ffi.string(query,40),[helper]=ffi.string(code,90),[number]='\1\0\0\0',
 [types]='\3\0\0\0',[types+0x80]=ffi.string(ffi.new('void *[1]',device),8)}
api.module=function()return ffi.cast('uint8_t *',base)end
api.read=function(at,n)
 local a=tonumber(ffi.cast('uintptr_t',at))
 if chunks[a]then assert(#chunks[a]==n);return chunks[a]end
 return raw_read(at,n)
end
logs={};assert(probe.capture(api,function(s)logs[#logs+1]=s end,{Keyboard={button_id=id}},{api=1,version=3}))
text=table.concat(logs,'\n');assert(text:find('profiler_device_count=1',1,true)and text:find('profiler_keyboard 0',1,true))
chunks[number]='\33\0\0\0';logs={}
assert(probe.capture(api,function(s)logs[#logs+1]=s end,{Keyboard={button_id=id}},{api=1,version=3}))
assert(not table.concat(logs,'\n'):find('profiler_keyboard ',1,true),'invalid device count must not inspect records')
assert(before==ffi.string(rows,64*12))
print('PASS bounded one-shot keyboard probe; outside-divisor candidates retained; no game-memory writes or input injection')
