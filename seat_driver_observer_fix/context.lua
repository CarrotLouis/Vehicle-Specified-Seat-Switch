-- Read only the concrete session context required by the existing property reader.
-- No authority requests/transfers, dispatch hooks, registry iteration or send API.
return function(api,game,p)
 local exe=assert(api.module('helldivers2.exe'));local ffi=require('ffi')
 local function hex(b)return(b:gsub('.',function(x)return string.format('%02x',x:byte())end))end
 local reads,guards
 local function get(a,n)
  reads=reads+1;assert(reads<=24,'driver_context_read_budget')
  local b=assert(api.read(a,n),'driver_context_unreadable');assert(#b==n,'driver_context_short_read');return b
 end
 local function stable(a,n)local b=get(a,n);guards[#guards+1]={a,b};return b end
 local function pointer(a)return assert(api.pointer(stable(a,8)),'driver_context_pointer')end
 local f=assert(p.engine_functions.authority_constructor)
 local function expected_vtable()
  local at=exe+f.rva+0x12;local b=get(at,7)
  assert(b:sub(1,3)=='\72\141\5','driver_context_constructor_reference')
  local d=ffi.new('int32_t[1]');ffi.copy(d,b:sub(4,7),4);return at+7+tonumber(d[0])
 end
 local self={}
 function self:read(s,v)
  reads=0;guards={}
  assert(s and s.state=='mission'and s.player_count==2 and s.peer_count==2 and s.local_count==1,'driver_context_room_scope')
  assert(v and v.name=='m102','driver_context_vehicle_scope')
  local session=pointer(game+p.globals.session);local engine=pointer(session+0xb390)
  local vt=pointer(engine);assert(vt==expected_vtable(),'driver_context_concrete_session_changed')
  local local_getter,host_getter=pointer(vt+0x68),pointer(vt+0x98)
  assert(get(local_getter,5)=='\72\139\65\32\195','driver_context_local_getter_changed')
  assert(get(host_getter,8)=='\72\139\129\48\1\0\0\195','driver_context_host_getter_changed')
  local selfpeer=stable(engine+0x20,8);local coordinator=stable(engine+0x130,8)
  assert(selfpeer~=string.rep('\0',8)and coordinator~=string.rep('\0',8),'driver_context_peer_not_ready')
  assert(stable(session+0xb398,8)==selfpeer and stable(session+0xb3a8,8)==coordinator,'driver_context_peer_disagreement')
  local epoch=stable(engine+0x60e4,4)
  for _,g in ipairs(guards)do assert(get(g[1],#g[2])==g[2],'driver_context_changed_during_read')end
  return {session=session,engine=engine,selfpeer=selfpeer,coordinator=coordinator,vehicle=v,
   context=tostring(session)..'/'..tostring(engine)..'/'..epoch..'/'..s.mission_value,
   local_peer_hex=hex(selfpeer),coordinator_hex=hex(coordinator),read_count=reads}
 end
 return self
end
