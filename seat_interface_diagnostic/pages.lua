-- All addresses stay inside the diagnostic. Logs contain module-relative locations.
return function(api)
 local ffi,bit=require('ffi'),require('bit')
 ffi.cdef[[
 typedef struct {
  void *base; void *allocation_base; uint32_t allocation_protect; uint32_t padding1;
  size_t region_size; uint32_t state; uint32_t protect; uint32_t type; uint32_t padding2;
 } VSSI_MemoryInfo;
 size_t VSSI_Query(const void *,VSSI_MemoryInfo *,size_t) __asm__("VirtualQuery");
 uint32_t VSSI_ModuleName(void *,char *,uint32_t) __asm__("GetModuleFileNameA");
 uint32_t GetLastError(void);
 ]]
 assert(ffi.sizeof('VSSI_MemoryInfo')==48,'memory_query_ABI')
 local k=ffi.load('kernel32')
 local function address(p)return tonumber(ffi.cast('uintptr_t',p))end
 local function u32(b,o)
  if not b or #b<o+4 then return nil end
  local a,c,d,e=b:byte(o+1,o+4);return a+c*256+d*65536+e*16777216
 end
 local images={}
 local function image(base)
  local key=address(base);if images[key] then return images[key]end
  local h=api.read(base,64);if not h or h:sub(1,2)~='MZ' then return nil end
  local pe=u32(h,60);if pe<64 or pe>1048576 then return nil end
  local b=api.read(base+pe,88)
  if not b or b:sub(1,4)~='PE\0\0' or b:sub(5,6)~='\100\134' or b:sub(25,26)~='\11\2' then return nil end
  local size=u32(b,80);if size<4096 or size>1073741824 then return nil end
  local name=ffi.new('char[1024]');local n=tonumber(k.VSSI_ModuleName(base,name,1024))
  local label=n>0 and n<1024 and ffi.string(name,n):match('[^/\\]+$') or 'unidentified_image'
  local result={name=label,size=size};images[key]=result;return result
 end
 function api.in_image(base,rva,n)
  local m=image(base);return m and rva>=0 and n>0 and rva+n<=m.size or false
 end
 function api.describe(p)
  local mem=ffi.new('VSSI_MemoryInfo[1]')
  local n=k.VSSI_Query(p,mem,ffi.sizeof(mem[0]))
  if n~=ffi.sizeof(mem[0]) then return {query_error=tonumber(k.GetLastError())}end
  local m=mem[0];local protection=tonumber(m.protect);local low=bit.band(protection,255)
  local guard=bit.band(protection,0x100)~=0
  local row={state=tonumber(m.state),type=tonumber(m.type),protection=protection,
   allocation_protection=tonumber(m.allocation_protect),region_size=tonumber(m.region_size),
   region_remaining=address(m.base)+tonumber(m.region_size)-address(p),
   readable=not guard and (low==2 or low==4 or low==8 or low==32 or low==64 or low==128),
   writable=not guard and (low==4 or low==8 or low==64 or low==128),
   executable=not guard and (low==16 or low==32 or low==64 or low==128)}
  if m.type==0x1000000 and m.allocation_base~=nil then
   local base=ffi.cast('uint8_t *',m.allocation_base);local info=image(base)
   if info then local rva=address(p)-address(base)
    if rva>=0 and rva<info.size then row.module=info.name;row.rva=rva end
   end
  end
  return row
 end
 return api
end
