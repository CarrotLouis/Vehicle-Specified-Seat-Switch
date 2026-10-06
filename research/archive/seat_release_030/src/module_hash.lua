-- Read-only SHA-256 of a loaded module's on-disk file.
return function(module)
 local ffi=require('ffi')
 ffi.cdef[[
 uint32_t GetModuleFileNameW(void *,uint16_t *,uint32_t);
 void *CreateFileW(const uint16_t *,uint32_t,uint32_t,void *,uint32_t,uint32_t,void *);
 int ReadFile(void *,void *,uint32_t,uint32_t *,void *);
 int CloseHandle(void *);
 int32_t BCryptOpenAlgorithmProvider(void **,const uint16_t *,const uint16_t *,uint32_t);
 int32_t BCryptCloseAlgorithmProvider(void *,uint32_t);
 int32_t BCryptCreateHash(void *,void **,void *,uint32_t,const void *,uint32_t,uint32_t);
 int32_t BCryptHashData(void *,const void *,uint32_t,uint32_t);
 int32_t BCryptFinishHash(void *,void *,uint32_t,uint32_t);
 int32_t BCryptDestroyHash(void *);
 ]]
 local k,c=ffi.load('kernel32'),ffi.load('bcrypt')
 local path=ffi.new('uint16_t[32768]');local length=k.GetModuleFileNameW(module,path,32768)
 assert(length>0 and length<32768,'Module path unavailable')
 local file=k.CreateFileW(path,0x80000000,7,nil,3,0x08000000,nil)
 assert(file~=ffi.cast('void *',-1),'Module file unavailable')
 local algorithm,digest=ffi.new('void *[1]'),ffi.new('void *[1]')
 local ok,result=pcall(function()
  local name=ffi.new('uint16_t[7]',{83,72,65,50,53,54,0})
  assert(c.BCryptOpenAlgorithmProvider(algorithm,name,nil,0)==0,'SHA256 provider failed')
  assert(c.BCryptCreateHash(algorithm[0],digest,nil,0,nil,0,0)==0,'SHA256 initialization failed')
  local buffer,count=ffi.new('uint8_t[262144]'),ffi.new('uint32_t[1]')
  repeat
   assert(k.ReadFile(file,buffer,262144,count,nil)~=0,'Module read failed')
   if count[0]>0 then assert(c.BCryptHashData(digest[0],buffer,count[0],0)==0,'Hash update failed') end
  until count[0]==0
  local bytes=ffi.new('uint8_t[32]');assert(c.BCryptFinishHash(digest[0],bytes,32,0)==0,'Hash finish failed')
  local hex={};for i=0,31 do hex[#hex+1]=string.format('%02x',bytes[i]) end;return table.concat(hex)
 end)
 if digest[0]~=nil then c.BCryptDestroyHash(digest[0]) end
 if algorithm[0]~=nil then c.BCryptCloseAlgorithmProvider(algorithm[0],0) end
 k.CloseHandle(file)
 if not ok then error(result) end
 return result
end
