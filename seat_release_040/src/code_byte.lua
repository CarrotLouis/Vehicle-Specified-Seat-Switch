-- One atomic opcode byte: TEST AL,AL <-> XOR AL,AL, same two-byte size.
-- The caller validates all four enclosing HUD-only input contracts first.
return function(api)
 local ffi=require('ffi')
 ffi.cdef[[
 int VSSMenu_VirtualProtect(void *,size_t,uint32_t,uint32_t *) __asm__("VirtualProtect");
 int VSSMenu_FlushInstructionCache(void *,const void *,size_t) __asm__("FlushInstructionCache");
 int VSSMenu_WriteProcessMemory(void *,void *,const void *,size_t,size_t *) __asm__("WriteProcessMemory");
 void *VSSMenu_GetCurrentProcess(void) __asm__("GetCurrentProcess");
 ]]
 local k=ffi.load('kernel32');local process=k.VSSMenu_GetCurrentProcess()
 local previous,scratch,count=ffi.new('uint32_t[1]'),ffi.new('uint32_t[1]'),ffi.new('size_t[1]')
 local b=ffi.new('uint8_t[1]')
 return function(address,from,to)
  assert((from==0x84 and to==0x30)or(from==0x30 and to==0x84),'unsupported_opcode_change')
  if api.read(address,2)~=string.char(from,0xc0)then return false,'opcode_changed',false end
  if k.VSSMenu_VirtualProtect(address,1,0x40,previous)==0 then return false,'code_protection_refused',false end
  local ok,reason,changed=false,'opcode_changed',false
  if api.read(address,2)==string.char(from,0xc0)then
   b[0]=to;count[0]=0
   ok=k.VSSMenu_WriteProcessMemory(process,address,b,1,count)~=0 and count[0]==1
   changed=api.read(address,2)==string.char(to,0xc0)
   reason=ok and changed and nil or 'code_write_failed'
   ok=ok and changed
  end
  if k.VSSMenu_FlushInstructionCache(process,address,2)==0 then ok=false;reason='instruction_cache_flush_failed'end
  if k.VSSMenu_VirtualProtect(address,1,previous[0],scratch)==0 then ok=false;reason='code_protection_restore_failed'end
  return ok,reason,changed
 end
end
