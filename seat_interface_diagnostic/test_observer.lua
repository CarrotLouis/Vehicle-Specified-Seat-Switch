local M=assert(loadfile('work/seat_interface_diagnostic/observer.lua'))()
local root,services,network,target=0x30000,0x40000,0x50000,0x60000
local base,entry=0x100000,0x1000
local refs={0x5b,0xa9,0x158,0x21c,0x25a}
local function le(n)local t={};for _=1,4 do t[#t+1]=string.char(n%256);n=math.floor(n/256)end;return table.concat(t)end
local mem={}
for _,o in ipairs(refs)do mem[base+entry+o]='\72\139\5'..le(root-entry-o-7)end
mem[base+root]='SERVICES';mem[services+0x38]='NETWORK!';mem[network+0x38]='TARGET01';mem[network+0x40]='TARGET02'
mem[target]=string.rep('\204',64);mem[target+0x100]=string.rep('\144',64)
local pointers={SERVICES=services,['NETWORK!']=network,TARGET01=target,TARGET02=target+0x100}
local calls,mutate=0,false
local api={read=function(a,n)
 calls=calls+1
 if mutate and a==base+root and calls>1 then return 'CHANGED!'end
 local b=mem[a];return b and #b>=n and b:sub(1,n)or nil
end,pointer=function(b)return pointers[b]end,in_image=function(_,r,n)return r>=0 and r+n<0x40000 end,
describe=function(p)return {state=4096,readable=true,executable=p>=target,region_remaining=512,protection=p>=target and 32 or 4}end}
local p={functions={trace_send={rva=entry}}}
assert(M.locate(api,base,p)==root)
local reader=M.new(api,base,p);calls=0
local s=reader:capture();assert(s.state=='observed' and #s.slots==2 and #s.slots[1].head_hex==128)
assert(s.slots[1].offset==0x38 and s.slots[2].offset==0x40)
mem[network+0x38]=nil;s=reader:capture();assert(s.state=='changed_during_read' and #s.slots==0)
mem[network+0x38]='TARGET01';calls=0;mutate=true;s=reader:capture();assert(s.state=='changed_during_read' and #s.slots==0)
mutate=false;mem[base+root]=nil;s=reader:capture();assert(s.state=='services_unavailable')
mem[base+root]='SERVICES';mem[services+0x38]=nil;s=reader:capture();assert(s.state=='network_api_unavailable')
mem[base+entry+refs[1]]='\72\139\5'..le(root-entry-refs[1]-6)
local ok,why=pcall(M.locate,api,base,p);assert(not ok and why:find('inconsistent_network_api_reference'))
mem[base+entry+refs[1]]='INVALID';ok,why=pcall(M.locate,api,base,p);assert(not ok and why:find('reference_instruction_changed'))
print('PASS interface observer: stable chain, unreadable slots, replaced root, null pointers, inconsistent/invalid references')

-- Real Windows metadata adapter in this test process, never in the game.
local ffi=require('ffi')
local platform=assert(loadfile('work/seat_network_diagnostic/platform.lua'))()
local pages=assert(loadfile('work/seat_interface_diagnostic/pages.lua'))()
local actual=pages(platform(function()return 'unused'end))
local block=ffi.new('uint8_t[32]');local row=actual.describe(block)
assert(row.state==4096 and row.readable and row.writable and not row.executable)
local kernel=assert(actual.module('kernel32.dll'))
assert(actual.in_image(kernel,0,64) and not actual.in_image(kernel,2^31,8))
row=actual.describe(kernel);assert(row.module:lower()=='kernel32.dll' and row.rva==0)
row=actual.describe(ffi.cast('void *',1));assert(not row.executable)
assert(actual.read(ffi.cast('void *',1),8)==nil)
print('PASS real Windows metadata queries: own heap, module identity/bounds, inaccessible pointer; no game access')
