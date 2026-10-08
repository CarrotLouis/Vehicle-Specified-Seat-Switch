-- Native window callbacks consume game input; physical polling still sees keys.
return function(api,loader,helper,policy,snapshot,eligible,emit)
 local ffi=require('ffi')
 ffi.cdef[[
 typedef struct {uint32_t binding,target;} VSSI_Item;
 typedef struct {uint64_t sequence,tick,generation;uint32_t binding,source,target,message;} VSSI_Record;
 uint32_t VSSI_version(void);uint32_t VSSI_record_size(void);
 int VSSI_start(void *);int VSSI_status(void);int VSSI_arm(const VSSI_Item *,uint32_t,uint32_t,uint64_t,uint64_t);
 uint32_t VSSI_health(void);uint32_t VSSI_stop(void);uint32_t VSSI_dropped(void);
 uint32_t VSSI_suppressed(uint32_t);uint32_t VSSI_drain(VSSI_Record *,uint32_t);
 ]]
 local self={active=false,pending=false,failed=false,generation=0,closed=false}
 local lib,buffer,items,identity,node
 local function event(name,data)data=data or {};data.event='input_priority_'..name;emit(data)end
 local function fail(reason)
  if not self.failed then
   self.failed=true;self.pending=false;self.active=false;event('failed',{reason=reason})
   if lib then local ok,code=pcall(lib.VSSI_stop);event('stopped',{code=ok and tonumber(code)or -1})end
  end
 end
 local function ready()
  self.pending=false;self.active=true
  event('ready',{helper_sha256=helper.sha256,strategy='own_window_messages; asynchronous_GUI_attach; physical_poll_retained; matched_primary_consumed'})
 end
 local function open()
  assert(not lib,'input_priority_already_loaded')
  lib,self.library_path=assert(api.native_library,'native_library_loader_missing')(helper,'VSSInputPriority',{
   VSSI_version='uint32_t (*)(void)',VSSI_record_size='uint32_t (*)(void)',VSSI_start='int (*)(void *)',
   VSSI_status='int (*)(void)',VSSI_arm='int (*)(const VSSI_Item *,uint32_t,uint32_t,uint64_t,uint64_t)',
   VSSI_health='uint32_t (*)(void)',VSSI_stop='uint32_t (*)(void)',VSSI_dropped='uint32_t (*)(void)',
   VSSI_suppressed='uint32_t (*)(uint32_t)',VSSI_drain='uint32_t (*)(VSSI_Record *,uint32_t)'})
  self.library=lib
  assert(lib.VSSI_version()==2 and lib.VSSI_record_size()==ffi.sizeof('VSSI_Record'),'input_priority_ABI_mismatch')
  buffer=ffi.new('VSSI_Record[256]');items=ffi.new('VSSI_Item[5]')
  local u=ffi.load('user32');local code=tonumber(lib.VSSI_start(u.GetForegroundWindow()))
  if code==0 then ready()
  elseif code==1 then self.pending=true;event('install_pending',{strategy='own_GUI_thread_message',timeout_ms=2000})
  else event('install_failure',{code=code});fail('input_priority_install_failed_'..code)end
 end
 function self:control_down(key)
  return api.down(key) and (not self.active or self.failed or lib.VSSI_suppressed(key)==0)
 end
 function self:pulse(s,c,keys,enabled)
  local focused=api.input_allowed()
  if self.closed then return end
  if not lib and focused and enabled and not self.failed then open()end
  if self.pending then
   local code=tonumber(lib.VSSI_status())
   if code==0 then ready()
   elseif code~=1 then event('install_failure',{code=code});fail('input_priority_install_failed_'..code)end
  end
  if not self.active or self.failed then return end
  local health=tonumber(lib.VSSI_health());local drops=tonumber(lib.VSSI_dropped())
  if health~=0 or drops~=0 then fail('window_health='..health..' dropped='..drops);return end
  local n=0
  if focused and enabled and s and not s.active and s.node>=0 and s.node<=4 then
   if identity~=s.identity or node~=s.node then identity=s.identity;node=s.node;self.generation=self.generation+1 end
   local seats=policy.seats[s.vehicle]or{}
   local nextseat,previous=snapshot.predictions(s)
   for target=0,#seats-1 do
    if target~=s.node and s.occupied[target]==false then
     local normal=policy.check('normal',s.vehicle,seats[s.node+1],seats[target+1],false)
     local permitted=normal and(nextseat==target or previous==target)
     if not normal and policy.check('enhanced',s.vehicle,seats[s.node+1],seats[target+1],false)and c and c.native and c.native.identity==s.identity and c.seat==s.node then
      permitted=eligible(c,s.node,c.owner.owner==c.owner.selfpeer,nil,target)
     end
     local binding=keys[s.vehicle][seats[target+1]]
     if permitted and binding~=0 then items[n].binding=binding;items[n].target=target;n=n+1 end
    end
   end
  end
  assert(lib.VSSI_arm(items,n,s and s.node or 0,math.floor(api.now()*1000)+200,self.generation)==0,'input_priority_arm_refused')
 end
 function self:take(s)
  local pressed,records,discarded={},{},{}
  if not self.active then return pressed,records,discarded end
  local n=tonumber(lib.VSSI_drain(buffer,256))
  for i=0,n-1 do
   local r=buffer[i];local age=api.now()*1000-tonumber(r.tick)
   local valid=not self.failed and s and api.input_allowed() and s.identity==identity and s.node==tonumber(r.source)
     and tonumber(r.generation)==self.generation and age>=0 and age<=250
   event(valid and 'consumed' or 'discarded',{binding=tonumber(r.binding),source=tonumber(r.source),target=tonumber(r.target),message=tonumber(r.message),input_tick=tonumber(r.tick),generation=tonumber(r.generation),sequence=tonumber(r.sequence)})
   if valid then
    local binding=tonumber(r.binding);pressed[binding]=true
    local previous=records[binding]
    records[binding]={count=previous and previous.count+1 or 1,source=tonumber(r.source),target=tonumber(r.target),
     tick=tonumber(r.tick),generation=tonumber(r.generation),sequence=tonumber(r.sequence)}
   else discarded[tonumber(r.binding)]=true end
  end
  return pressed,records,discarded
 end
 function self:filter(pressed,consumed)
  -- Discarded native intents cannot reappear as physical edges on another seat.
  if self.active and not self.failed then for binding in pairs(pressed)do
   if lib.VSSI_suppressed(binding%256)~=0 and not consumed[binding]then pressed[binding]=nil end
  end end
 end
 function self:close()
  if not self.closed then
   self.closed=true
   if lib then local code=tonumber(lib.VSSI_stop());event('stopped',{code=code})end
   self.active=false;self.pending=false
  end
 end
 return self
end
