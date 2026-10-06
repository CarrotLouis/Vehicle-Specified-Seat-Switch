return function()
 local ffi=require('ffi')
 assert(ffi.abi('64bit'),'Windows x64 required')
 ffi.cdef[[
 void *GetModuleHandleA(const char *);
 uint32_t GetModuleFileNameW(void *,uint16_t *,uint32_t);
 void *GetCurrentProcess(void);
 uint32_t GetCurrentProcessId(void);
 uint64_t GetTickCount64(void);
 int ReadProcessMemory(void *,const void *,void *,size_t,size_t *);
 int WriteProcessMemory(void *,void *,const void *,size_t,size_t *);
 void *GetForegroundWindow(void);
 uint32_t GetWindowThreadProcessId(void *,uint32_t *);
 int16_t GetAsyncKeyState(int);
 typedef struct { uint32_t cbSize; uint32_t flags; void *cursor; int32_t x; int32_t y; } VSSCursorInfo;
 int GetCursorInfo(VSSCursorInfo *);
 void *CreateFileW(const uint16_t *,uint32_t,uint32_t,void *,uint32_t,uint32_t,void *);
 int ReadFile(void *,void *,uint32_t,uint32_t *,void *);
 int CloseHandle(void *);
 int CreateDirectoryA(const char *,void *);
 uint32_t GetFileAttributesA(const char *);
 int32_t BCryptOpenAlgorithmProvider(void **,const uint16_t *,const uint16_t *,uint32_t);
 int32_t BCryptCloseAlgorithmProvider(void *,uint32_t);
 int32_t BCryptCreateHash(void *,void **,void *,uint32_t,const void *,uint32_t,uint32_t);
 int32_t BCryptHashData(void *,const void *,uint32_t,uint32_t);
 int32_t BCryptFinishHash(void *,void *,uint32_t,uint32_t);
 int32_t BCryptDestroyHash(void *);
 ]]
 local k,u,c=ffi.load('kernel32'),ffi.load('user32'),ffi.load('bcrypt')
 local a={ffi=ffi};local process=k.GetCurrentProcess()
 local scratch=ffi.new('uint8_t[32768]');local transferred=ffi.new('size_t[1]')
 function a.config_directory()
  local base=assert(os.getenv('APPDATA'),'APPDATA unavailable')
  assert(base~='','APPDATA is empty')
  local directory=base..'/Arrowhead'
  for _,path in ipairs({directory,directory..'/Helldivers2'}) do
   local attributes=k.GetFileAttributesA(path)
   if attributes==0xffffffff then
    assert(k.CreateDirectoryA(path,nil)~=0,'Cannot create configuration directory: '..path)
   else assert(require('bit').band(attributes,0x10)~=0,'Configuration path is not a directory: '..path) end
  end
  return directory..'/Helldivers2'
 end
 function a.module(name)
  local v=k.GetModuleHandleA(name);if v~=nil then return ffi.cast('uint8_t *',v) end
 end
 function a.read(address,size)
  if not address or size<1 or size>32768 or size%1~=0 then return nil end
  transferred[0]=0
  if k.ReadProcessMemory(process,address,scratch,size,transferred)==0 or tonumber(transferred[0])~=size then return nil end
  return ffi.string(scratch,size)
 end
 function a.pointer(bytes,offset)
  offset=offset or 0;if not bytes or #bytes<offset+8 then return nil end
  local p=ffi.new('uint64_t[1]');ffi.copy(p,bytes:sub(offset+1,offset+8),8)
  local v=tonumber(p[0]);if v<65536 or v>=2^47 then return nil end
  return ffi.cast('uint8_t *',p[0])
 end
 function a.number(p)return tonumber(ffi.cast('uintptr_t',p))end
 function a.now()return tonumber(k.GetTickCount64())/1000 end
 function a.focused()
  local w=u.GetForegroundWindow();if w==nil then return false end
  local p=ffi.new('uint32_t[1]');u.GetWindowThreadProcessId(w,p)
  return p[0]==k.GetCurrentProcessId()
 end
 function a.down(code)return code~=0 and u.GetAsyncKeyState(code)<0 end
 function a.input_allowed()
  if not a.focused() then return false end
  local info=ffi.new('VSSCursorInfo');info.cbSize=ffi.sizeof(info)
  return u.GetCursorInfo(info)~=0 and info.flags==0
 end
 -- Compare-before-write for small validated data fields. No executable code patching.
 function a.replace(address,before,after)
  if #before~=#after or #after>24 or a.read(address,#before)~=before then return false end
  transferred[0]=0
  return k.WriteProcessMemory(process,address,after,#after,transferred)~=0 and tonumber(transferred[0])==#after
 end
 function a.hash_module(handle)
  local wide=ffi.new('uint16_t[32768]');local n=k.GetModuleFileNameW(handle,wide,32768)
  assert(n>0 and n<32768,'Module filename unavailable')
  local file=k.CreateFileW(wide,0x80000000,7,nil,3,0x08000000,nil)
  assert(file~=ffi.cast('void *',-1),'Module file unavailable')
  local algorithm,hash=ffi.new('void *[1]'),ffi.new('void *[1]')
  local ok,value=pcall(function()
   local sha=ffi.new('uint16_t[7]',{83,72,65,50,53,54,0})
   assert(c.BCryptOpenAlgorithmProvider(algorithm,sha,nil,0)==0,'SHA256 provider failed')
   assert(c.BCryptCreateHash(algorithm[0],hash,nil,0,nil,0,0)==0,'SHA256 initialization failed')
   local block,count=ffi.new('uint8_t[262144]'),ffi.new('uint32_t[1]')
   repeat
    assert(k.ReadFile(file,block,262144,count,nil)~=0,'Module read failed')
    if count[0]>0 then assert(c.BCryptHashData(hash[0],block,count[0],0)==0,'SHA256 read failed') end
   until count[0]==0
   local digest=ffi.new('uint8_t[32]');assert(c.BCryptFinishHash(hash[0],digest,32,0)==0,'SHA256 finish failed')
   local hex={};for i=0,31 do hex[#hex+1]=string.format('%02x',digest[i]) end;return table.concat(hex)
  end)
  if hash[0]~=nil then c.BCryptDestroyHash(hash[0]) end
  if algorithm[0]~=nil then c.BCryptCloseAlgorithmProvider(algorithm[0],0) end
  k.CloseHandle(file);if not ok then error(value) end;return value
 end
 return a
end
