return function(api,game,p,loader,writer,reader,observer,route_reader,messages,helper)
 local ffi,bit=require('ffi'),require('bit')
 ffi.cdef[[
 typedef struct {void **slot;void *target;uint8_t head[32];} VSST_Binding;
 typedef struct {void **slot;void *target;} VSST_Guard;
 typedef struct {
  uint64_t sequence,tick,qpc,caller;
  uint32_t kind,thread,message,count,valid,caller_module,peer_count,peer_valid;
  uint64_t values[8],peers[8];uint32_t types[8],sizes[8];
 } VSST_Record;
 uint32_t VSST_version(void);uint32_t VSST_record_size(void);
 uint64_t VSST_frequency(void);uint64_t VSST_dropped(void);
 uint32_t VSST_drain(VSST_Record *,uint32_t);
 uint32_t VSST_health(void);uint32_t VSST_stop(void);
 int VSST_start(const VSST_Binding *,const VSST_Guard *);
 ]]
 local self={active=false,seen=0,last_drop=0,aliases={},mapped={},alias_count=0}
 local lib,buffer
 local expected_counts={switch_request=4,accepted=3,snapshot=4,transition=5,switch_denied=2,entry_request=3,exit_request=4,entry_denied=2,entering=3,release_request=2,release_retry=2,exit_accepted=4,exit_denied=2,authority_request=2,authority_owned=2}
 local function pointer(a)return assert(api.pointer(api.read(a,8)),'transport_pointer_unavailable')end
 local function peer(value)
  if value==0 then return 'null'end
  local raw=ffi.new('uint64_t[1]',value);local key=ffi.string(raw,8)
  if reader.peers[key]then return reader.peers[key]end
  if not self.aliases[key]then
   if self.alias_count>=64 then return 'unmapped_peer_limit'end
   self.alias_count=self.alias_count+1;self.aliases[key]='Q'..self.alias_count
  end
  return self.aliases[key]
 end
 function self:start()
  assert(not lib,'transport_already_started')
  local routed=route_reader:capture()
  assert(routed.state=='observed'and routed.callback.matches_dispatch and routed.callback.stable,'receive_preflight_failed')
  assert(#routed.messages==15,'registry_message_count_changed')
  for _,m in ipairs(routed.messages)do
   assert(m.found and expected_counts[m.name]==m.parameter_count,'message_schema_changed_'..m.name)
  end
  self.registry=routed.messages
  local exe=assert(api.module('helldivers2.exe'),'missing_engine_module')
  local root=observer.locate(api,game,p)
  local services=pointer(game+root);local network=pointer(services+0x38);local session=pointer(game+p.globals.session)
  local at={network+0x38,network+0x40,session+0xb3f8}
  local expected={exe+p.engine_functions.route_send_one.rva,exe+p.engine_functions.route_send_many.rva,game+p.functions.route_dispatch.rva}
  local bindings,guards=ffi.new('VSST_Binding[3]'),ffi.new('VSST_Guard[3]')
  local refs={game+root,services+0x38,game+p.globals.session};local values={services,network,session}
  for i=1,3 do
   assert(pointer(at[i])==expected[i],'transport_target_changed_'..i)
   local page=api.describe(at[i]);assert(page.state==4096 and page.protection==4,'transport_slot_not_plain_writable_'..i)
   bindings[i-1].slot=ffi.cast('void **',at[i]);bindings[i-1].target=expected[i]
   ffi.copy(bindings[i-1].head,assert(api.read(expected[i],32),'target_head_unreadable'),32)
   guards[i-1].slot=ffi.cast('void **',refs[i]);guards[i-1].target=values[i]
  end
  local bytes=helper.hex:gsub('..',function(x)return string.char(tonumber(x,16))end)
  assert(#bytes==helper.size and bytes:sub(1,2)=='MZ','helper_payload_invalid')
  local path=assert(loader.log_directory,'missing_log_directory')..'/VSSTransport-'..helper.sha256..'.dll'
  local f=io.open(path,'rb')
  if f then local existing=f:read('*a');f:close();assert(existing==bytes,'helper_file_mismatch')
  else local temp=path..'.tmp';f=assert(io.open(temp,'wb'));assert(f:write(bytes));assert(f:close());assert(os.rename(temp,path))end
  f=assert(io.open(path,'rb'));local actual=f:read('*a');f:close();assert(actual==bytes,'helper_verify_failed')
  lib=ffi.load(path);self.library=lib
  assert(lib.VSST_version()==1 and lib.VSST_record_size()==ffi.sizeof('VSST_Record'),'transport_ABI_mismatch')
  buffer=ffi.new('VSST_Record[256]')
  local code=tonumber(lib.VSST_start(bindings,guards))
  if code~=0 then writer:write({event='transport_install_failure',code=code},api.now());error('transport_install_failed_'..code)end
  self.active=true
  writer:write({event='transport_ready',version='0.18.2',helper_sha256=helper.sha256,frequency=tonumber(lib.VSST_frequency()),
   strategy='three_writable_data_slots; original_calls_forwarded',
   boundary='send_invocation_and_receive_dispatch; neither_proves_seat_acceptance',registry=routed.messages},api.now())
 end
 function self:drain()
  if not self.active then return end
  for key,label in pairs(self.aliases)do
   if reader.peers[key]and not self.mapped[key]then writer:write({event='protocol_peer_alias',from=label,to=reader.peers[key]},api.now());self.mapped[key]=true end
  end
  for _=1,8 do
   local n=tonumber(lib.VSST_drain(buffer,256))
   for i=0,n-1 do
    local r=buffer[i];local values,types,sizes,peers={},{},{},{}
    for j=0,math.min(tonumber(r.count),8)-1 do
     local value
     if (r.message==0xe29b4d18 or r.message==0xf8a9d630)and j==1 then
      -- Never turn a peer handle into a Lua double or expose it as an ID.
      value=bit.band(tonumber(r.valid),2^j)~=0 and r.types[j]==9 and r.sizes[j]==8 and peer(r.values[j])or'unreadable_peer'
     else value=tonumber(r.values[j])end
     values[#values+1]=value;types[#types+1]=tonumber(r.types[j]);sizes[#sizes+1]=tonumber(r.sizes[j])
    end
    for j=0,math.min(tonumber(r.peer_count),8)-1 do peers[#peers+1]=bit.band(tonumber(r.peer_valid),2^j)~=0 and peer(r.peers[j])or'unreadable_peer'end
    writer:write({event=r.kind==2 and 'native_receive_dispatch'or'native_send',
     route=({'send_one','send_many','receive_dispatch'})[tonumber(r.kind)+1],message=messages[tonumber(r.message)],
     sequence=tonumber(r.sequence),native_tick=tonumber(r.tick),qpc=tonumber(r.qpc),thread=tonumber(r.thread),
     caller_module=({'game.dll','helldivers2.exe'})[tonumber(r.caller_module)],caller_rva=tonumber(r.caller),
     argument_count=tonumber(r.count),valid_mask=tonumber(r.valid),values=values,types=types,sizes=sizes,
     peer_count=tonumber(r.peer_count),peer_valid_mask=tonumber(r.peer_valid),peers=peers},tonumber(r.tick)/1000)
    self.seen=self.seen+1
   end
   if n<256 then break end
  end
  local lost=tonumber(lib.VSST_dropped());if lost~=self.last_drop then writer:write({event='protocol_gap',dropped_total=lost},api.now());self.last_drop=lost end
 end
 function self:health()
  if self.active then local flags=tonumber(lib.VSST_health());assert(flags==0,'transport_bindings_changed_'..flags)end
 end
 function self:stop(reason)
  if not lib then return end
  local code=tonumber(lib.VSST_stop());self:drain();self.active=false
  if not writer.closed then writer:write({event='transport_stopped',reason=reason,restore_flags=code,events=self.seen,dropped_total=tonumber(lib.VSST_dropped())},api.now())end
  -- Native module remains pinned; in-flight callbacks keep valid code/originals.
 end
 return self
end
