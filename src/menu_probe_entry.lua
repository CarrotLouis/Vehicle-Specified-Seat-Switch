-- Independent diagnostic tag/resource; compatible with the seat release.
if rawget(_G,'VehicleSeatMenuInputProbe')then return end
local state={version='0.1.1',done=false};rawset(_G,'VehicleSeatMenuInputProbe',state)
local old,old_shutdown=update,shutdown
if type(old)~='function'then return end
local ffi=require('ffi')
ffi.cdef[[
 void *VSSMP_Module(const char *) __asm__("GetModuleHandleA");
 void *VSSMP_Process(void) __asm__("GetCurrentProcess");
 int VSSMP_Read(void *,const void *,void *,size_t,size_t *) __asm__("ReadProcessMemory");
 uint64_t VSSMP_Clock(void) __asm__("GetTickCount64");
 typedef struct {void *base;void *allocation_base;uint32_t allocation_protect;uint32_t pad1;
  size_t region_size;uint32_t state;uint32_t protect;uint32_t type;uint32_t pad2;} VSSMP_Mem;
 size_t VSSMP_Query(const void *,VSSMP_Mem *,size_t) __asm__("VirtualQuery");
]]
local kernel=ffi.load('kernel32');local process=kernel.VSSMP_Process()
local api={ffi=ffi};local buffer=ffi.new('uint8_t[32768]');local received=ffi.new('size_t[1]')
function api.module(name)
 local p=kernel.VSSMP_Module(name);if p~=nil then return ffi.cast('uint8_t *',p)end
end
function api.read(at,n)
 if not at or n<1 or n>32768 then return nil end;received[0]=0
 if kernel.VSSMP_Read(process,at,buffer,n,received)==0 or received[0]~=n then return nil end
 return ffi.string(buffer,n)
end
function api.pointer(b)
 if not b or #b<8 then return nil end
 local p=ffi.new('uint64_t[1]');ffi.copy(p,b,8)
 local n=tonumber(p[0]);if n<65536 or n>=2^47 then return nil end
 return ffi.cast('uint8_t *',p[0])
end
function api.describe(at)
 local m=ffi.new('VSSMP_Mem[1]');if kernel.VSSMP_Query(at,m,ffi.sizeof(m[0]))~=ffi.sizeof(m[0])then return{}end
 local bit=require('bit');local low=bit.band(m[0].protect,255);local guard=bit.band(m[0].protect,256)~=0
 return {region_remaining=tonumber(ffi.cast('uintptr_t',m[0].base))+tonumber(m[0].region_size)-tonumber(ffi.cast('uintptr_t',at)),
  readable=not guard and(low==2 or low==4 or low==8 or low==32 or low==64 or low==128),
  writable=not guard and(low==4 or low==8 or low==64 or low==128),executable=low==16 or low==32 or low==64 or low==128}
end
local logfile;local started=tonumber(kernel.VSSMP_Clock());local next_try=started+15000
local function log(line)
 if logfile then logfile:write(os.date('%Y-%m-%d %H:%M:%S')..' '..line..'\n');logfile:flush()end
end
local function pack(...)return {n=select('#',...),...}end
update=function(...)
 local values=pack(old(...))
 if not state.done then
  local now=tonumber(kernel.VSSMP_Clock())
  if now>=next_try then
   next_try=now+5000
   local loader=rawget(_G,'CowboyBingusModLoader');local engine=rawget(_G,'stingray')
   if loader and engine and engine.Keyboard then
    local ok,err=pcall(function()
     logfile=logfile or assert(loader.open_log('VehicleSeatMenuInputProbe.log'))
     log('read_only_probe '..state.version)
     menu_probe.capture(api,log)
    end)
    if not ok then pcall(log,'capture_error '..tostring(err))end
    state.done=true;state.error=not ok and tostring(err)or nil
   elseif now-started>=60000 then state.done=true end
  end
 end
 return unpack(values,1,values.n)
end
shutdown=function(...)
 if logfile then pcall(logfile.close,logfile);logfile=nil end
 if type(old_shutdown)=='function'then return old_shutdown(...)end
end
