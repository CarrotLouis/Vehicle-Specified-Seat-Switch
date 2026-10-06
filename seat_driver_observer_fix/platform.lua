-- Windows read-only adapter. No game function calls, writes or input injection.
return function(hash_module)
 local ffi=require('ffi')
 assert(ffi.abi('64bit'),'Windows x64 required')
 ffi.cdef[[
 void *GetModuleHandleA(const char *);
 void *GetCurrentProcess(void);
 uint32_t GetCurrentProcessId(void);
 uint64_t GetTickCount64(void);
 int ReadProcessMemory(void *,const void *,void *,size_t,size_t *);
 void *GetForegroundWindow(void);
 uint32_t GetWindowThreadProcessId(void *,uint32_t *);
 int16_t GetAsyncKeyState(int);
 typedef struct { uint32_t cbSize; uint32_t flags; void *cursor; int32_t x; int32_t y; } VSSNetCursorInfo;
 int VSSNetGetCursorInfo(VSSNetCursorInfo *) __asm__("GetCursorInfo");
 ]]
 local k,u=ffi.load('kernel32'),ffi.load('user32')
 local process=k.GetCurrentProcess()
 local buffer,read=ffi.new('uint8_t[32768]'),ffi.new('size_t[1]')
 local a={hash_module=hash_module,ffi=ffi}
 function a.module(name)
  local p=k.GetModuleHandleA(name)
  if p~=nil then return ffi.cast('uint8_t *',p) end
 end
 function a.read(p,n)
  if not p or n<1 or n>32768 or n%1~=0 then return nil end
  read[0]=0
  if k.ReadProcessMemory(process,p,buffer,n,read)==0 or tonumber(read[0])~=n then return nil end
  return ffi.string(buffer,n)
 end
 function a.pointer(b,o)
  o=o or 0;if not b or #b<o+8 then return nil end
  local p=ffi.new('uint64_t[1]');ffi.copy(p,b:sub(o+1,o+8),8)
  local n=tonumber(p[0]);if n<65536 or n>=2^47 then return nil end
  return ffi.cast('uint8_t *',p[0])
 end
 function a.now()return tonumber(k.GetTickCount64())/1000 end
 function a.pid()return tonumber(k.GetCurrentProcessId())end
 function a.focused()
  local w=u.GetForegroundWindow();if w==nil then return false end
  local pid=ffi.new('uint32_t[1]');u.GetWindowThreadProcessId(w,pid)
  return pid[0]==k.GetCurrentProcessId()
 end
 function a.input_allowed()
  if not a.focused() then return false end
  local info=ffi.new('VSSNetCursorInfo');info.cbSize=ffi.sizeof(info)
  -- FFI declarations are shared by every addon. Keep our struct signature on
  -- a private Lua symbol while resolving the unchanged Windows export.
  return u.VSSNetGetCursorInfo(info)~=0 and info.flags==0
 end
 function a.down(key)return key~=0 and u.GetAsyncKeyState(key)<0 end
 return a
end
