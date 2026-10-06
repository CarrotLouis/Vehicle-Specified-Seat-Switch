-- Send existing game messages to ONE verified remote peer, never broadcast/self.
return function(api,game,p,spec,compat,trace,animation_sender)
 local ffi=require('ffi')
 local function read(a,n)local b=api.read(a,n);assert(b and #b==n,'sync_sender_read');return b end
 local function verify(name)
  local d=assert(spec.records[name]);local f=assert(p.functions[name])
  assert(compat.match(read(game+f.rva,d.length),d.chunks),'sync_sender_code_'..name)
  return game+f.rva
 end
 local function peer(raw)local a=ffi.new('uint64_t[1]');ffi.copy(a,raw,8);return a[0]end
 local function pointer(a)return assert(api.pointer(read(a,8)),'sync_sender_pointer')end
 local function registry()
  local r=p.functions.route_dispatch.rva;local b=read(game+r+9,4)
  local d=ffi.new('int32_t[1]');ffi.copy(d,b,4)
  local table_=game+r+13+tonumber(d[0])
  for name,expected in pairs({snapshot={0xd4f97316,{256,256,87,106},'sync_snapshot_adapter'},
                            transition={0xdcc32107,{256,87,87,517,518},'sync_transition_adapter'}})do
   local found
   for _,m in ipairs(trace.registry or {})do if m.name==name then found=m;break end end
   assert(found and found.found and found.hash==expected[1]and found.flags[1]==1 and found.flags[2]==1 and found.parameter_count==#expected[2],'sync_registry_'..name)
   for i,t in ipairs(expected[2])do assert(found.type_indices[i]==t,'sync_parameter_'..name)end
   assert(pointer(table_+found.index*8)==verify(expected[3]),'sync_dispatch_'..name)
  end
 end
 return {prepare=function(_,o,destination,s,target)
  assert(trace.active,'sync_trace_inactive');trace:health()
  assert(destination~=o.selfpeer and o.members[destination]and o.owner==o.selfpeer and not o.busy,'sync_sender_peer_or_owner')
  assert(s.vehicle=='m102'and(target==1 or target==4),'sync_sender_scope')
  verify('trace_send');registry()
  -- The wrapper describes a four-byte bool slot. Supply a full zero word.
  local snap=ffi.cast('void (*)(uint64_t,uint32_t,uint32_t,int32_t,uint32_t)',verify('sync_snapshot_send'))
  local transition=ffi.cast('void (*)(uint64_t,uint32_t,int32_t,int32_t,int32_t,float)',verify('sync_transition_send'))
  -- The engine's own seat-change notification. A whole-image search shows the
  -- entry_request hash lives in exactly one wrapper (0xbe36a0), which only resolves two
  -- entities and calls the generic sender: no transition and no animation. The engine
  -- calls it from owner_enter and owner_switch, which is why the passenger->gunner leg
  -- already emits it while our manual gunner->passenger leg emitted nothing at all.
  -- Argument order mirrors the observed payload 4118,4107,4 = vehicle, avatar, seat.
  local release=ffi.cast('void (*)(uint64_t,uint32_t,uint32_t)',verify('sync_release_request_send'))
  local dest=peer(destination)
  local animation=assert(animation_sender):prepare(s,dest,target)
  return function(emit)
   trace:health()
   assert(pointer(game+p.globals.session)==o.session and pointer(o.session+0xb390)==o.engine,'sync_session_changed')
   assert(read(o.engine+0x20,8)==o.selfpeer,'sync_identity_changed')
   animation.check()
   emit({event='sync_snapshot_invoking',avatar=s.avatar,collection=s.collection,target=target})
   snap(dest,s.avatar,s.collection,target,0)
   emit({event='sync_transition_invoking',avatar=s.avatar,target=target,action=-1})
   transition(dest,s.avatar,target,target,-1,0)
   -- Only on the way OUT of the gunner seat. Entering it already produces this message
   -- from the engine itself, so sending our own there would duplicate it.
   if target==1 then
    -- Leaving the gunner seat: tell the host the weapon is released. entry_request is deliberately
    -- NOT sent here - it released the turret in 0.8.4 but detached the avatar on the remote.
    emit({event='sync_release_request_invoking',avatar=s.avatar,seat=s.node,target=target})
    release(dest,s.avatar,s.node)
   end
   animation.send(emit)
   emit({event='sync_pair_calls_returned',target=target,remote_success_not_confirmed=true})
  end
 end}
end
