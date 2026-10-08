-- Real Windows Unicode IO, SHA-256, LoadLibraryExW and export resolution on
-- authored helpers in a fresh workspace fixture. No game process/window.
local ffi=require('ffi');local factory=dofile('work/src/native_library.lua')
local transport=dofile('work/build/helper.lua');local input=dofile('work/src/input_helper.lua')
local root=assert(os.getenv('VSS_NATIVE_TEST_DIR'))
local logs={};local cache=factory.new(function(s)logs[#logs+1]=s end,root..'/辅助模块-ü')
local types={VSST_version='uint32_t (*)(void)',VSST_record_size='uint32_t (*)(void)'}
local lib,path=cache.load(transport,'VSSTransport',types)
assert(lib.VSST_version()==4 and lib.VSST_record_size()==256)
assert(path:find('辅助模块-ü',1,true)and #logs==1)
assert(cache.load(transport,'VSSTransport',types)==lib and #logs==1)
local keys,kpath=cache.load(input,'VSSInputPriority',{VSSI_version='uint32_t (*)(void)',VSSI_record_size='uint32_t (*)(void)',VSSI_start='int (*)(void *)'})
assert(keys.VSSI_version()==2 and keys.VSSI_record_size()==40 and keys.VSSI_start(nil)==-2)
assert(#logs==2 and logs[1]:find('dependencies=System32',1,true))
-- Changed embedded hash is not silently used as a cache filename.
local bad={size=transport.size,hex=transport.hex,sha256=string.rep('0',64)}
local ok,err=pcall(cache.load,bad,'VSSTransport',types)
assert(not ok and err:find('native_payload_hash_mismatch'))
ok,err=pcall(cache.load,transport,'../VSSTransport',types);assert(not ok and err:find('native_helper_kind'))
ok,err=pcall(factory.new,function()end,root..'/../escape');assert(not ok and err:find('path_traversal'))
-- Validate the non-ASCII cached bytes via the same locked Unicode reader in a
-- fresh resolver; this is also the normal next-launch reuse path.
local reused=factory.new(function()end,root..'/辅助模块-ü').load(transport,'VSSTransport',types)
assert(reused.VSST_version()==4)
-- A same-size corruption with the correct hash in its NAME is still refused.
local bytes=transport.hex:gsub('..',function(s)return string.char(tonumber(s,16))end)
local tamper_path=root..'/VSSTransport-'..transport.sha256..'.dll'
local f=assert(io.open(tamper_path,'wb'));assert(f:write(bytes:sub(1,-2)..string.char((bytes:byte(-1)+1)%256)));f:close()
ok,err=pcall(factory.new(function()end,root).load,transport,'VSSTransport',types)
assert(not ok and err:find('native_cache_bytes_mismatch'))
-- Unknown exports cannot be called even when the DLL itself is trusted.
ok,err=pcall(factory.new(function()end,root..'/辅助模块-ü').load,transport,'VSSTransport',{not_a_helper_export='int (*)(void)'})
assert(not ok and err:find('native_export_missing'))
print('PASS Unicode cache extraction/reuse, real CNG payload hashes, System32-only loading, exact loaded path, helper ABIs and invalid payload/kind/path refusal; no game launched')
