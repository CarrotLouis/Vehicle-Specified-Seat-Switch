-- Native helpers are shipped with the addon, verified against their embedded
-- bytes and SHA-256, and loaded only from an explicit private cache path.
local M={}
function M.new(log,cache_override)
 local ffi,bit=require('ffi'),require('bit')
 ffi.cdef[[
 int VSSNL_UTF16(uint32_t,uint32_t,const char *,int,uint16_t *,int) __asm__("MultiByteToWideChar");
 uint32_t VSSNL_Attributes(const uint16_t *) __asm__("GetFileAttributesW");
 int VSSNL_Mkdir(const uint16_t *,void *) __asm__("CreateDirectoryW");
 void *VSSNL_Open(const uint16_t *,uint32_t,uint32_t,void *,uint32_t,uint32_t,void *) __asm__("CreateFileW");
 int VSSNL_Read(void *,void *,uint32_t,uint32_t *,void *) __asm__("ReadFile");
 int VSSNL_Write(void *,const void *,uint32_t,uint32_t *,void *) __asm__("WriteFile");
 int VSSNL_Close(void *) __asm__("CloseHandle");
 int VSSNL_Move(const uint16_t *,const uint16_t *,uint32_t) __asm__("MoveFileExW");
 int VSSNL_Delete(const uint16_t *) __asm__("DeleteFileW");
 uint32_t VSSNL_Error(void) __asm__("GetLastError");
 uint32_t VSSNL_Pid(void) __asm__("GetCurrentProcessId");
 void *VSSNL_Load(const uint16_t *,void *,uint32_t) __asm__("LoadLibraryExW");
 int VSSNL_Free(void *) __asm__("FreeLibrary");
 void *VSSNL_Symbol(void *,const char *) __asm__("GetProcAddress");
 uint32_t VSSNL_ModulePath(void *,uint16_t *,uint32_t) __asm__("GetModuleFileNameW");
 int VSSNL_Compare(const uint16_t *,int,const uint16_t *,int,int) __asm__("CompareStringOrdinal");
 int32_t VSSNL_HashOpen(void **,const uint16_t *,const uint16_t *,uint32_t) __asm__("BCryptOpenAlgorithmProvider");
 int32_t VSSNL_HashClose(void *,uint32_t) __asm__("BCryptCloseAlgorithmProvider");
 int32_t VSSNL_HashNew(void *,void **,void *,uint32_t,const void *,uint32_t,uint32_t) __asm__("BCryptCreateHash");
 int32_t VSSNL_HashAdd(void *,const void *,uint32_t,uint32_t) __asm__("BCryptHashData");
 int32_t VSSNL_HashFinish(void *,void *,uint32_t,uint32_t) __asm__("BCryptFinishHash");
 int32_t VSSNL_HashDestroy(void *) __asm__("BCryptDestroyHash");
 ]]
 local k,c=ffi.load('kernel32'),ffi.load('bcrypt')
 local invalid=ffi.cast('void *',-1);local loaded={};local serial=0
 local root=cache_override or(assert(os.getenv('LOCALAPPDATA'),'LOCALAPPDATA_missing')..'/CowboyBingus/Helldivers2/VehicleSeatSwitch/Native')
 root=root:gsub('/','\\'):gsub('\\+$','')
 assert(root:match('^%a:\\')and not root:find('%z')and #root<32000,'native_cache_absolute_local_path_required')
 for part in root:sub(4):gmatch('[^\\]+')do assert(part~='.'and part~='..','native_cache_path_traversal')end
 local function wide(s)
  local n=k.VSSNL_UTF16(65001,8,s,#s,nil,0);assert(n>0,'native_path_utf8')
  local b=ffi.new('uint16_t[?]',n+1);assert(k.VSSNL_UTF16(65001,8,s,#s,b,n)==n,'native_path_conversion');return b
 end
 local function mkdirs()
  local current=root:sub(1,3)
  for part in root:sub(4):gmatch('[^\\]+')do
   current=current:gsub('\\+$','')..'\\'..part;local w=wide(current)
   local attr=k.VSSNL_Attributes(w)
   if attr==0xffffffff then
    if k.VSSNL_Mkdir(w,nil)==0 then assert(k.VSSNL_Error()==183,'native_cache_create_failed')end
    attr=k.VSSNL_Attributes(w)
   end
   assert(attr~=0xffffffff and bit.band(attr,16)~=0,'native_cache_not_directory')
  end
 end
 local function hash(bytes)
  local algorithm,digest=ffi.new('void *[1]'),ffi.new('void *[1]')
  local ok,result=pcall(function()
   assert(c.VSSNL_HashOpen(algorithm,wide('SHA256'),nil,0)==0,'native_hash_provider')
   assert(c.VSSNL_HashNew(algorithm[0],digest,nil,0,nil,0,0)==0,'native_hash_create')
   assert(c.VSSNL_HashAdd(digest[0],bytes,#bytes,0)==0,'native_hash_update')
   local b=ffi.new('uint8_t[32]');assert(c.VSSNL_HashFinish(digest[0],b,32,0)==0,'native_hash_finish')
   local parts={};for i=0,31 do parts[#parts+1]=string.format('%02x',b[i])end;return table.concat(parts)
  end)
  if digest[0]~=nil then c.VSSNL_HashDestroy(digest[0])end
  if algorithm[0]~=nil then c.VSSNL_HashClose(algorithm[0],0)end
  if not ok then error(result)end;return result
 end
 local function write_new(path,bytes)
  serial=serial+1;local temp=path..'.tmp-'..tonumber(k.VSSNL_Pid())..'-'..serial;local w=wide(temp)
  local h=k.VSSNL_Open(w,0x40000000,0,nil,1,0x80,nil)
  assert(h~=invalid,'native_temp_create_failed')
  local count=ffi.new('uint32_t[1]');local ok=k.VSSNL_Write(h,bytes,#bytes,count,nil)~=0 and count[0]==#bytes
  local closed=k.VSSNL_Close(h)~=0
  if not ok or not closed then k.VSSNL_Delete(w);error('native_cache_write_failed')end
  -- No overwrite flag: a concurrently created destination is re-verified.
  if k.VSSNL_Move(w,wide(path),0)==0 then
   local why=k.VSSNL_Error();k.VSSNL_Delete(w)
   assert(why==183 or why==80,'native_cache_rename_failed')
  end
 end
 local function load(spec,kind,types)
  assert(kind=='VSSTransport'or kind=='VSSInputPriority','native_helper_kind')
  assert(type(spec.sha256)=='string'and #spec.sha256==64 and not spec.sha256:find('[^0-9a-f]'),'native_helper_hash')
  assert(spec.size>=512 and spec.size<=65536 and #spec.hex==spec.size*2 and not spec.hex:find('[^0-9a-f]'),'native_helper_payload')
  local bytes=spec.hex:gsub('..',function(s)return string.char(tonumber(s,16))end)
  assert(bytes:sub(1,2)=='MZ'and hash(bytes)==spec.sha256,'native_payload_hash_mismatch')
  local key=kind..'-'..spec.sha256;local path=root..'\\'..key..'.dll'
  if loaded[key]then return loaded[key],path end
  mkdirs();local w=wide(path);local attr=k.VSSNL_Attributes(w)
  if attr==0xffffffff then
   assert(k.VSSNL_Error()==2 or k.VSSNL_Error()==3,'native_cache_attributes_failed');write_new(path,bytes);attr=k.VSSNL_Attributes(w)
  end
  assert(attr~=0xffffffff and bit.band(attr,0x410)==0,'native_cache_reparse_or_directory_refused')
  -- Only read sharing: hold the verified file against write/delete replacement
  -- through LoadLibraryExW. This does not defend a compromised addon package.
  local file=k.VSSNL_Open(w,0x80000000,1,nil,3,0x00200000,nil)
  assert(file~=invalid,'native_cache_lock_failed')
  local handle;local ok,result=pcall(function()
   local b=ffi.new('uint8_t[?]',spec.size+1);local n=ffi.new('uint32_t[1]')
   assert(k.VSSNL_Read(file,b,spec.size+1,n,nil)~=0 and n[0]==spec.size,'native_cache_size_mismatch')
   local actual=ffi.string(b,spec.size);assert(actual==bytes,'native_cache_bytes_mismatch')
   -- Full Unicode path for the target; dependencies restricted to System32.
   handle=k.VSSNL_Load(w,nil,0x00000800);assert(handle~=nil,'native_load_failed_'..tonumber(k.VSSNL_Error()))
   local actual_path=ffi.new('uint16_t[32768]');local length=k.VSSNL_ModulePath(handle,actual_path,32768)
   assert(length>0 and length<32768 and k.VSSNL_Compare(w,-1,actual_path,-1,1)==2,'native_loaded_path_mismatch')
   local lib={};for name,signature in pairs(types)do
    local symbol=k.VSSNL_Symbol(handle,name);assert(symbol~=nil,'native_export_missing_'..name)
    lib[name]=ffi.cast(signature,symbol)
   end
   -- Own the library reference for process lifetime. The native bridges also
   -- pin themselves on activation, because callbacks can outlive Lua cleanup.
   lib._handle=handle;loaded[key]=lib
   log('native_helper_verified kind='..kind..' sha256='..spec.sha256..' bytes='..spec.size..' path='..path..' dependencies=System32')
   return lib
  end)
  k.VSSNL_Close(file)
  if not ok then if handle~=nil then k.VSSNL_Free(handle)end;error(result)end
  return result,path
 end
 return {load=load,root=root}
end
return M
