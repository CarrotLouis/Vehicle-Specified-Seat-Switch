-- Native-only observation; no callback enters Lua from a game/network thread.
return function(api,game,p,loader,writer,reader,points,messages,helper)
 local ffi=require('ffi')
 ffi.cdef[[
 typedef struct {
  uint64_t sequence,tick,qpc,peer,caller;
  uint32_t kind,thread,message,count,valid,reserved;
  uint64_t values[8];uint32_t types[8],sizes[8];
 } VSSP_Record;
 typedef struct {
  uint32_t stage,win32_error,hook_index,enabling;
  uint64_t patch_address,region_base,region_size;
  uint32_t protection,allocation_protection,state,type,query_error,rollback_status;
 } VSSP_Failure;
 uint32_t VSSP_failure(VSSP_Failure *);
 uint32_t VSSP_version(void);
 uint32_t VSSP_record_size(void);
 uint64_t VSSP_frequency(void);
 uint64_t VSSP_dropped(void);
 uint32_t VSSP_drain(VSSP_Record *,uint32_t);
 int VSSP_start(void **,const uint8_t *,uint32_t);
 int VSSP_stop(void);
 ]]
 local self={active=false,aliases={},mapped={},alias_count=0,seen=0,last_drop=0}
 local lib,buffer
 local function peer(value)
  local signed=tonumber(ffi.cast('int64_t',value))
  if signed==0 then return 'null' end
  if signed<0 and signed>=-4 then return 'native_destination_'..signed end
  local key=ffi.new('uint64_t[1]',value);key=ffi.string(key,8)
  if reader.peers[key] then return reader.peers[key] end
  if not self.aliases[key] then
   if self.alias_count>=64 then return 'unmapped_peer_limit' end
   self.alias_count=self.alias_count+1;self.aliases[key]='Q'..self.alias_count
  end
  return self.aliases[key]
 end
 function self:start()
  assert(not lib,'protocol_already_started')
  local bytes=helper.hex:gsub('..',function(x)return string.char(tonumber(x,16))end)
  assert(#bytes==helper.size and bytes:sub(1,2)=='MZ','helper_payload_invalid')
  local path=assert(loader.log_directory,'missing_log_directory')..'/VSSProtocol-'..helper.sha256..'.dll'
  local f=io.open(path,'rb')
  if f then local existing=f:read('*a');f:close();assert(existing==bytes,'helper_file_mismatch')
  else
   local temp=path..'.tmp';f=assert(io.open(temp,'wb'),'helper_create_failed')
   assert(f:write(bytes),'helper_write_failed');assert(f:close(),'helper_close_failed')
   assert(os.rename(temp,path),'helper_rename_failed')
  end
  -- Verify the complete embedded DLL before loading, including the existing-file case.
  f=assert(io.open(path,'rb'));local actual=f:read('*a');f:close();assert(actual==bytes,'helper_verify_failed')
  lib=ffi.load(path);self.library=lib
  assert(lib.VSSP_version()==2 and lib.VSSP_record_size()==ffi.sizeof('VSSP_Record'),'helper_ABI_mismatch')
  buffer=ffi.new('VSSP_Record[256]')
  local targets,expected=ffi.new('void *[8]'),ffi.new('uint8_t[256]')
  local located={}
  for i,point in ipairs(points) do
   local d=assert(p.functions['trace_'..point.name]);local current=api.read(game+d.rva,32)
   assert(current==d.bytes,'protocol_interface_changed_'..point.name)
   targets[i-1]=game+d.rva;ffi.copy(expected+(i-1)*32,current,32)
   located[#located+1]={name=point.name,rva=d.rva}
  end
  local code=lib.VSSP_start(targets,expected,8)
  if code~=0 then
   local f=ffi.new('VSSP_Failure[1]');local stage=tonumber(lib.VSSP_failure(f));local d=f[0]
   local point=points[tonumber(d.hook_index)+1]
   local base=tonumber(ffi.cast('uintptr_t',game))
   self.failure={event='protocol_install_failure',code=tonumber(code),stage=stage,
    win32_error=tonumber(d.win32_error),hook=point and point.name or 'unknown',
    enabling=d.enabling~=0,patch_rva=stage>0 and tonumber(d.patch_address)-base or nil,
    region_rva=d.region_base~=0 and tonumber(d.region_base)-base or nil,region_size=tonumber(d.region_size),
    protection=tonumber(d.protection),allocation_protection=tonumber(d.allocation_protection),
    state=tonumber(d.state),type=tonumber(d.type),query_error=tonumber(d.query_error),rollback_status=tonumber(d.rollback_status)}
   writer:write(self.failure,api.now())
   error('protocol_install_failed_'..tonumber(code)..'_win32_'..tonumber(d.win32_error)..'_hook_'..self.failure.hook)
  end
  self.active=true
  writer:write({event='protocol_ready',version='0.2.1',helper_sha256=helper.sha256,
   frequency=tonumber(lib.VSSP_frequency()),hooks=located,
   boundary='native_send_and_handler_entry; handler_entry_is_not_proof_of_remote_delivery'},api.now())
 end
 function self:drain()
  if not self.active then return end
  for key,label in pairs(self.aliases)do
   local session_label=reader.peers[key]
   if session_label and not self.mapped[key] then
    writer:write({event='protocol_peer_alias',from=label,to=session_label},api.now());self.mapped[key]=true
   end
  end
  for _=1,8 do
   local n=tonumber(lib.VSSP_drain(buffer,256))
   for i=0,n-1 do
    local r=buffer[i];local values,types,sizes={},{},{}
    for j=0,math.min(tonumber(r.count),8)-1 do
     values[#values+1]=tonumber(r.values[j]);types[#types+1]=tonumber(r.types[j]);sizes[#sizes+1]=tonumber(r.sizes[j])
    end
    -- Only the low byte of the snapshot's bool is defined by its native ABI.
    if r.kind==4 and values[4] then values[4]=values[4]%256 end
    local name=points[tonumber(r.kind)+1].name
    writer:write({event=r.kind==0 and 'native_send' or 'native_handler',name=name,
     message=r.kind==0 and messages[tonumber(r.message)] or nil,
     sequence=tonumber(r.sequence),native_tick=tonumber(r.tick),qpc=tonumber(r.qpc),thread=tonumber(r.thread),
     peer=peer(r.peer),caller_rva=tonumber(r.caller),argument_count=tonumber(r.count),valid_mask=tonumber(r.valid),
     values=values,types=types,sizes=sizes},tonumber(r.tick)/1000)
    self.seen=self.seen+1
   end
   if n<256 then break end
  end
  local lost=tonumber(lib.VSSP_dropped())
  if lost~=self.last_drop then writer:write({event='protocol_gap',dropped_total=lost},api.now());self.last_drop=lost end
 end
 function self:stop(reason)
  if not lib then return end
  local code=tonumber(lib.VSSP_stop())
  self:drain();self.active=false
  if not writer.closed then writer:write({event='protocol_stopped',reason=reason,disable_status=code,events=self.seen,dropped_total=tonumber(lib.VSSP_dropped())},api.now()) end
  -- DLL is pinned by native initialization. Never free live trampolines.
 end
 return self
end
