-- Send existing game messages to ONE verified remote peer, never broadcast/self.
return function(api,game,p,spec,compat,trace,animation_sender,binding_sender,layout)
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
 local self={}
 function self:preflight(o,destination,s,target)
  assert(trace.active and destination~=o.selfpeer and o.members[destination]and destination==o.owner and not o.busy,'reserved_sender_peer')
  local d=layout and layout(s)
  assert(d and d.frv and not s.owned and s.node>=1 and s.node<#d.roles and target>=1 and target<#d.roles and target~=s.node,'reserved_sender_scope')
  trace:health();verify('trace_send');registry()
  verify('sync_snapshot_send');verify('sync_transition_send')
  local dest=peer(destination);local animation=assert(animation_sender):prepare(s,dest,target)
  assert(binding_sender):preflight(s,dest,target)
  animation.check();return true
 end
 function self:prepare(o,destination,s,target,reservation_grant)
  assert(trace.active,'sync_trace_inactive');trace:health()
  local reservation_layout=layout and layout(s)
  local reserved=reservation_grant and reservation_grant.source==s.node and reservation_grant.target==target and target~=s.node
   and reservation_layout and reservation_layout.frv and not s.owned and s.node>=1 and s.node<#reservation_layout.roles and target>=1 and target<#reservation_layout.roles
   and o.owner==destination and reservation_grant:check()
  assert(destination~=o.selfpeer and o.members[destination]and(o.owner==o.selfpeer or reserved)and not o.busy,'sync_sender_peer_or_owner')
  local d=layout and layout(s)or not layout and s.vehicle=='m102'and {roles={1,3,3,3,2}}
  assert(d and target>=0 and target<#d.roles and target%1==0,'sync_sender_scope')
  verify('trace_send');registry()
  -- The wrapper describes a four-byte bool slot. Supply a full zero word.
  local snap=ffi.cast('void (*)(uint64_t,uint32_t,uint32_t,int32_t,uint32_t)',verify('sync_snapshot_send'))
  local transition=ffi.cast('void (*)(uint64_t,uint32_t,int32_t,int32_t,int32_t,float)',verify('sync_transition_send'))
  local dest=peer(destination)
  local animation=assert(animation_sender):prepare(s,dest,target)
  local binding=assert(binding_sender):prepare(s,dest,target,reserved and reservation_grant or nil)
  local used=false
  return function(emit)
   assert(not used,'sync_pair_already_invoked')
   trace:health()
   assert(pointer(game+p.globals.session)==o.session and pointer(o.session+0xb390)==o.engine,'sync_session_changed')
   assert(read(o.engine+0x20,8)==o.selfpeer,'sync_identity_changed')
   if reservation_grant then assert(reservation_grant:check(),'sync_reservation_grant_changed')end
   animation.check()
   binding.check();used=true
   emit({event='sync_snapshot_invoking',avatar=s.avatar,collection=s.collection,target=target})
   snap(dest,s.avatar,s.collection,target,0)
   emit({event='sync_transition_invoking',avatar=s.avatar,target=target,action=-1})
   transition(dest,s.avatar,target,target,-1,0)
   binding.send(emit)
   animation.send(emit)
   emit({event='sync_pair_calls_returned',target=target,remote_success_not_confirmed=true})
  end
 end
 -- Preserve the tested packet order separately for every verified member.
 -- Freeze the complete native member table, never a guessed broadcast address.
 function self:prepare_all(o,destinations,s,target)
  local n=assert(o.peer_count)
  assert(n>=2 and n<=4 and #destinations==n-1,'sync_fleet_count')
  local raw=read(o.session+0x162e0,n*8)
  local count=ffi.new('uint32_t[1]');ffi.copy(count,read(o.session+0x162d8,4),4)
  assert(tonumber(count[0])==n,'sync_fleet_native_count')
  local seen,members={},{}
  for i=0,n-1 do local key=raw:sub(i*8+1,i*8+8)
   assert(o.members[key]and not members[key],'sync_fleet_native_members');members[key]=true
  end
  assert(members[o.selfpeer],'sync_fleet_self_missing')
  local sends={}
  for _,destination in ipairs(destinations)do
   assert(destination~=o.selfpeer and members[destination]and not seen[destination],'sync_fleet_destination')
   seen[destination]=true;sends[#sends+1]=self:prepare(o,destination,s,target)
  end
  local expected_count=read(o.session+0x162d8,4);local used=false
  return function(emit)
   assert(not used,'sync_fleet_already_invoked')
   assert(read(o.session+0x162d8,4)==expected_count and read(o.session+0x162e0,n*8)==raw,'sync_fleet_members_changed')
   used=true
   emit({event='sync_fleet_begin',peer_count=n,destinations=#sends,avatar=s.avatar,target=target})
   for i,send in ipairs(sends)do
    -- A mid-send departure never causes a resend of a partly delivered change.
    assert(read(o.session+0x162d8,4)==expected_count and read(o.session+0x162e0,n*8)==raw,'sync_fleet_members_changed')
    send(emit);emit({event='sync_fleet_peer_returned',peer_index=i,target=target,remote_success_not_confirmed=true})
   end
  end
 end
 return self
end
