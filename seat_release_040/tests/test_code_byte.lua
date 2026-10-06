-- Actual Windows protection/write/flush APIs and actual x64 branch behavior,
-- only in this offline test process's own allocated code page.
local ffi=require('ffi')
ffi.cdef[[
 void *VSSMenuTest_VirtualAlloc(void *,size_t,uint32_t,uint32_t) __asm__("VirtualAlloc");
 int VSSMenuTest_VirtualFree(void *,size_t,uint32_t) __asm__("VirtualFree");
 int VSSMenuTest_VirtualProtect(void *,size_t,uint32_t,uint32_t *) __asm__("VirtualProtect");
 typedef int(*VSSMenuTest_Function)(void);
]]
local k=ffi.load('kernel32');local p=k.VSSMenuTest_VirtualAlloc(nil,4096,0x3000,4);assert(p~=nil)
local bytes=ffi.cast('uint8_t *',p);local old=ffi.new('uint32_t[1]')
local original='\176\1\132\192\116\6\184\7\0\0\0\195\184\9\0\0\0\195'
for i=0,3 do ffi.copy(bytes+i*32,original,#original)end
assert(k.VSSMenuTest_VirtualProtect(p,4096,0x20,old)~=0)
local api={read=function(at,n)return ffi.string(at,n)end}
local write=assert(loadfile('work/seat_release_040/src/code_byte.lua'))()(api)
for i=0,3 do
 local at=bytes+i*32;local f=ffi.cast('VSSMenuTest_Function',at)
 assert(f()==7)
 local ok,why,changed=write(at+2,0x84,0x30);assert(ok and changed,tostring(why));assert(f()==9)
 assert(api.read(at,#original):sub(1,2)==original:sub(1,2))
 ok,why,changed=write(at+2,0x84,0x30);assert(not ok and why=='opcode_changed'and not changed)
 assert(write(at+2,0x30,0x84));assert(f()==7);assert(api.read(at,#original)==original)
 -- Query by temporarily changing protection, then restore exactly what was there.
 assert(k.VSSMenuTest_VirtualProtect(p,4096,0x20,old)~=0 and old[0]==0x20)
end
assert(k.VSSMenuTest_VirtualFree(p,0,0x8000)~=0)
print('PASS four actual x64 checks suppressed/restored; native one-byte write, expected-byte refusal, page protections and neighboring code preserved')
