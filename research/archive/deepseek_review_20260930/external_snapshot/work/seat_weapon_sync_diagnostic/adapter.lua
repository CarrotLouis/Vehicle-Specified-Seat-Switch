local M={}
local function seated(a,v,node,role)
 local s=a and a.seat
 return s and s.collection==v.id and s.current==node and s.reserved==node and s.role==role
  and s.target==-1 and s.action==-1 and s.transitioning==0 and s.queued_exit==0
end
function M.eligible(c,source,owned,ticket)
 local s,o=c.native,c.owner
 if not s then return false,c.native_reason or 'local_seat_unavailable'end
 if s.vehicle~='m102'or s.transition~=26 or #s.profile.roles~=5 then return false,'M102_only'end
 if c.sample.player_count~=2 or c.sample.local_count~=1 or s.player_count~=2 or s.peer_count~=2 or o.peer_count~=2 then return false,'two_players_required'end
 if o.coordinator==o.selfpeer or c.destination~=o.coordinator or not o.members[c.destination]then return false,'friend_must_host'end
 local expected=owned and o.selfpeer or c.destination
 if o.owner~=expected or s.owned~=owned or o.vehicle.owned_local~=owned or o.busy then return false,'ownership_not_ready'end
 if not c.avatar or not c.avatar.is_local or not c.avatar.owned_local or not o.avatars[s.avatar]or o.avatars[s.avatar].owner~=o.selfpeer then return false,'avatar_owner_unconfirmed'end
 if s.node~=source or(source~=1 and source~=4)or s.active or not c.avatar.vehicle_input or not seated(c.avatar,o.vehicle,source,source==4 and 2 or 3)then return false,'sit_still_in_expected_passenger'end
 if not c.driver or c.driver.is_local or not seated(c.driver,o.vehicle,0,1)or not o.avatars[c.driver.id]or o.avatars[c.driver.id].owner~=c.destination then return false,'friend_must_remain_driver'end
 if s.occupied[5-source]~=false then return false,'target_occupied_or_reserved'end
 if ticket and (c.identity~=ticket.identity or s.identity~=ticket.avatar_binding or c.driver.id~=ticket.driver_id or c.driver.unit~=ticket.driver_unit)then return false,'operation_identity_changed'end
 return true
end
function M.new(api,game,p,reader,owner_reader,snapshot,transaction,sender,trace,emit,encode)
 local self={}
 -- One-shot, read-only layout probe. It decides which pointer the engine's own
 -- owner_enter (0x636920) can be given as its first argument, without hooking
 -- anything: the worker at 0x636a30 needs [+0x20] a hash-table base, [+0x28] its
 -- count, [+0x2c] a scalar compared against row ids, and [+0x48] a row array of
 -- 0x64-byte rows. Anything whose layout does not match that is excluded.
 -- Wrapped in pcall so it can never disturb a switch, and gated by a flag so it
 -- emits at most once per session.
 local probed=false
 local function probe_layout(s,seat)
  -- Emitted before any read so a later failure is distinguishable from "never ran".
  emit({event='probe_layout_begin',seat=seat})
  local ffi=require('ffi')
  -- Addresses arrive as Lua numbers (doubles). Casting a double straight to a pointer
  -- truncates to 32 bits, which silently breaks every heap address above 4 GB; going via
  -- uint64 first preserves the full address.
  local function at(a)return ffi.cast('uint8_t *',ffi.cast('uint64_t',a))end
  -- 0.9.2 crashed the game on boarding: probe_layout_begin was the last line written, so an
  -- unguarded dereference faulted. FFI reads must never be issued against an address that has
  -- not been proved readable, so every read is gated on VirtualQuery first.
  pcall(ffi.cdef,[[
   typedef struct { void *BaseAddress; void *AllocationBase; uint32_t AllocationProtect;
    uint16_t PartitionId; uint64_t RegionSize; uint32_t State; uint32_t Protect; uint32_t Type; } VSST_MBI;
   uint64_t VirtualQuery(const void *, VSST_MBI *, uint64_t);
  ]])
  local kernel=ffi.load('kernel32',true)
  local function readable(a,n)
   if not a or a==0 then return false end
   local ok,span=pcall(function()
    local mbi=ffi.new('VSST_MBI')
    if kernel.VirtualQuery(at(a),mbi,ffi.sizeof(mbi))==0 then return false end
    if mbi.State~=0x1000 then return false end          -- MEM_COMMIT only
    local p=mbi.Protect
    if p==0x01 or p==0x100 then return false end        -- PAGE_NOACCESS / PAGE_GUARD
    local base=tonumber(ffi.cast('uint64_t',mbi.BaseAddress))
    return a+n<=base+tonumber(mbi.RegionSize)
   end)
   return ok and span==true
  end
  local function u64at(a)
   if not a or a==0 or not readable(a,8) then return nil end
   local ok,v=pcall(function()return tonumber(ffi.cast('uint64_t *',at(a))[0])end)
   if not ok then return nil end
   return v
  end
  local function u32at(a)
   if not a or a==0 or not readable(a,4) then return nil end
   local ok,v=pcall(function()return tonumber(ffi.cast('uint32_t *',at(a))[0])end)
   if not ok then return nil end
   return v
  end
  -- Snapshot fields are FFI pointers, not numbers, so tonumber alone is not enough.
  local function addr_of(p)
   if not p then return nil end
   if type(p)=='number' then if p==0 then return nil end return p end
   local ok,v=pcall(function()return tonumber(ffi.cast('uintptr_t',p))end)
   if ok and v and v~=0 then return v end
   local ok2,v2=pcall(tonumber,p)
   if ok2 and v2 and v2~=0 then return v2 end
   return nil
  end
  local function hx(v)
   -- A zero pointer must read as absent, not as "0x0": Lua treats 0 as truthy, so an
   -- unchecked format would make a non-matching candidate look like a matching one.
   if not v or v==0 then return nil end
   return string.format('0x%x',v)
  end
  local out={}
  -- The container class is shared (collections, seaters and one global all match the shape),
  -- so shape cannot identify the context. Instead run the ENGINE'S OWN lookup for a known id
  -- and report which candidate actually contains it - exactly the worker's algorithm:
  --   idx = (i + id*[+0x30]) & ([+0x28]-1);  key = u32 at [+0x20] + idx*8
  --   key == [+0x2c] -> empty slot, stop;  key == id -> hit, value = u32 at entry+4
  local key=nil
  if type(s.collection)=='number'and s.collection~=0 then key=s.collection end
  local function lookup(a)
   if not key then return nil end
   local cnt=u32at(a+0x28);local mult=u32at(a+0x30)
   local tbl=u64at(a+0x20);local empty=u32at(a+0x2c)
   if not cnt or cnt==0 or cnt>65536 then return nil end
   -- 0.9.5 hung the game here: non-containers carry garbage counts (0.9.4 saw n28=4028275024),
   -- and looping that many times with a gated read each froze the process. The engine masks with
   -- count-1, so a real container's count is a power of two; anything else is not a container and
   -- must be skipped rather than walked.
   local p=1;while p<cnt do p=p*2 end
   if p~=cnt then return nil end
   if not mult or mult==0 or mult>65536 then return nil end
   if not tbl or empty==nil then return nil end
   for i=0,cnt-1 do
    local idx=(i+key*mult)%cnt
    local k=u32at(tbl+idx*8)
    if k==key then
     local val=u32at(tbl+idx*8+4)
     local hit={found=true,slot=idx,value=val}
     -- The table's value is a ROW INDEX, not data: the worker then does
     -- imul rcx,r14,0x64 over [+0x48] and uses that row's first dword as a vehicle-type id in
     -- a 45-case dispatch. Reading it is the tie-breaker when two candidates both contain the
     -- vehicle id - only the real context can yield a row whose id is a valid type.
     local rows=u64at(a+0x48)
     if rows and val and val<65536 then
      local row=rows+val*0x64
      hit.row0=u32at(row);hit.row4=u32at(row+4)
      if hit.row0 and hit.row0>=1 and hit.row0<=45 then hit.type_valid=true end
     end
     return hit
    end
    if k==empty then break end
   end
   return {found=false}
  end
  local function one(label,p)
   local a=addr_of(p)
   if not a then out[label]={none=true};return end
   local e={addr=hx(a)}
   -- The four fields the engine worker at 0x636a30 consumes.
   e.p20=hx(u64at(a+0x20));e.n28=u32at(a+0x28);e.n2c=u32at(a+0x2c)
   -- The worker also multiplies by [ctx+0x30] while probing, so that word discriminates
   -- between containers of the same family (collections and seaters both match the shape).
   e.n30=u32at(a+0x30)
   local r48=u64at(a+0x48);e.p48=hx(r48)
   -- The offsets the project's own snapshot reaches through, so the two views can be
   -- related: it uses [+0x50] and [+0x58] and reads a count at +0xc.
   local r50=u64at(a+0x50);local r58=u64at(a+0x58)
   e.p50=hx(r50);e.p58=hx(r58)
   if r48 and r48>0x1000 then
    e.row0_id=u32at(r48);e.row1_id=u32at(r48+0x64);e.row2_id=u32at(r48+0xc8)
   end
   if r50 and r50>0x1000 then e.c50=u32at(r50+0xc)end
   if r58 and r58>0x1000 then e.c58=u32at(r58+0xc)end
   local hit=lookup(a)
   if hit then
    e.lookup_id=key
    e.lookup_found=hit.found
    if hit.found then
     e.lookup_slot=hit.slot;e.lookup_value=hit.value
     e.lookup_row0=hit.row0;e.lookup_row4=hit.row4
     e.lookup_type_valid=hit.type_valid and true or false
    end
   end
   out[label]=e
  end
  local function safe_one(label,p)
   local ok,err=pcall(one,label,p)
   if not ok then out[label]={error=tostring(err)} end
  end
  safe_one('collections',s.collections)
  safe_one('seaters',s.seaters)
  -- The globals live in the module image, so this needs a real module base; without one
  -- (unit tests) the scan is skipped rather than dereferencing a fabricated address.
  if game and game~=0 then
   for i,rva in ipairs({0x3326698,0x3326490,0x3326308,0x33266b8,0x346bf98})do
    local obj=nil
    -- Normalise to a number first: the readability gate compares the address against a
    -- region bound, and a cdata pointer there silently fails the comparison (the 0.9.3 run
    -- reported every global as none for exactly this reason).
    local ok,v=pcall(function()return u64at(addr_of(game+rva))end)
    if ok then obj=v end
    safe_one('global'..i..'_'..string.format('%x',rva),obj)
   end
  end
  emit({event='probe_layout',seat=seat,layout=out})
 end
 function self:capture(ticket)
  local sample,why=reader:capture();if not sample or sample.state~='mission'then return nil,why or 'not_in_mission'end
  local o,reason=owner_reader:capture(sample,ticket and ticket.vehicle,true);if not o then return nil,reason end
  local a,driver,dest,n=nil,nil,nil,0
  for _,x in ipairs(sample.avatars)do
   if x.is_local then a=x end
   if seated(x,o.vehicle,0,1)then driver=x end
  end
  for peer in pairs(o.members)do if peer~=o.selfpeer then dest=peer;n=n+1 end end
  if n~=1 then dest=nil end
  local ok,s,err=pcall(snapshot.capture,api,game,p)
  if not ok then err=tostring(s);s=nil end
  if s and (not a or a.id~=s.avatar or a.unit~=s.avatar_unit or s.collection~=o.vehicle.id or s.collection_unit~=o.vehicle.network_unit or s.resource~=o.vehicle.resource)then s=nil;err='local_tracked_identity_disagrees'end
  local c={sample=sample,owner=o,native=s,native_reason=err,avatar=a,driver=driver,destination=dest,seat=s and s.node}
  -- Additional peers cancel switching but must not prevent return to the original owner.
  c.identity=o.context..'/'..o.vehicle.id..'/'..o.vehicle.unit..'/'..o.vehicle.network_unit..'/'..o.vehicle.resource..o.selfpeer
  c.summary=encode({seat=c.seat,ownership=owner_reader:summary(o),local_ready=s~=nil})
  if s and not probed then
   probed=true
   local ok,err=pcall(probe_layout,s,c.seat)
   if not ok then pcall(emit,{event='probe_layout_error',message=tostring(err)})end
  end
  return c
 end
 function self:eligible(c,source,owned,ticket)return M.eligible(c,source,owned,ticket)end
 function self:ticket(c)
  return {identity=c.identity,vehicle=c.owner.vehicle,selfpeer=c.owner.selfpeer,original=c.destination,
   source=c.seat,target=5-c.seat,avatar_binding=c.native.identity,driver_id=c.driver.id,driver_unit=c.driver.unit}
 end
 function self:context(c,t)
  return c.identity==t.identity and c.owner.selfpeer==t.selfpeer and c.owner.members[t.original]
 end
 local function quiet()
  assert(api.input_allowed(),'focus_or_input_blocked')
  for _,k in ipairs({1,2,4,5,6,32,65,68,69,81,83,87})do assert(not api.down(k),'release_movement_fire_action_inputs')end
 end
 function self:request(c,t)
  assert(not api.experiment_allowed or api.experiment_allowed(),'experiment_logging_unavailable')
  assert(trace.active,'trace_inactive');trace:health();quiet()
  local fresh=assert(self:capture(t));local ok,why=M.eligible(fresh,t.source,false,t);assert(ok,why)
  owner_reader:send(fresh.owner,t.original,t.selfpeer,function()t.request_invoked=true end)
 end
 function self:execute(c,t)
  assert(not api.experiment_allowed or api.experiment_allowed(),'experiment_logging_unavailable')
  trace:health();quiet()
  local fresh=assert(self:capture(t));local ok,why=M.eligible(fresh,t.source,true,t);assert(ok,why)
  local perform=transaction:prepare(fresh.native,t.target)
  local send=sender:prepare(fresh.owner,t.original,fresh.native,t.target)
  local final=assert(self:capture(t));ok,why=M.eligible(final,t.source,true,t);assert(ok,why)
  assert(final.owner.serial==fresh.owner.serial and snapshot.current(api,fresh.native),'state_changed_before_mutation')
  emit({event='integrated_preflight_passed',source=t.source,target=t.target,ownership=owner_reader:summary(final.owner)})
  t.mutation_started=true;perform()
  local after=assert(self:capture(t));ok,why=M.eligible(after,t.target,true,t);assert(ok,why)
  assert(snapshot.current(api,after.native),'state_changed_before_sync')
  send(emit);t.sync_returned=true
 end
 function self:return_owned(c,t)
  assert(not t.return_invoked,'return_already_invoked')
  assert(trace.active,'trace_inactive');trace:health()
  local fresh=assert(self:capture(t));assert(self:context(fresh,t),'return_context_changed')
  local o=fresh.owner
  assert(o.owner==t.selfpeer and o.vehicle.owned_local and not o.busy,'return_owner_not_ready')
  -- Recovery may run after local exit/read failure; never require a local seat.
  -- Do not give the chassis away underneath a new/different driver.
  if fresh.driver then
   assert(not fresh.driver.is_local and fresh.driver.id==t.driver_id and fresh.driver.unit==t.driver_unit,'return_driver_changed')
   assert(o.avatars[fresh.driver.id]and o.avatars[fresh.driver.id].owner==t.original,'return_driver_owner_changed')
  end
  owner_reader:send(o,t.selfpeer,t.original,function()t.return_invoked=true end)
 end
 return self
end
return M
