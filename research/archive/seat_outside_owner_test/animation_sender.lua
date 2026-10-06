-- One existing notification to the verified peer, only for this player's avatar.
-- The engine owns serialization/delivery. Returned calls are not a remote ACK.
return function(api,game,p,spec,compat,inspector,trace)
 local ffi=require('ffi')
 local args_type=ffi.typeof('struct { uint32_t type; uint32_t size; const void *value; }[3]')
 local function check_code(name)
  local d=assert(spec.records[name]);local at=game+assert(p.functions[name]).rva
  local b=api.read(at,d.length);assert(b and compat.match(b,d.chunks),'animation_code_'..name)
  return at
 end
 local function check(s,target)
  for _,name in ipairs({'anim_event_send','anim_event_adapter','anim_event_receive','anim_event_index','trace_send'})do check_code(name)end
  local b=assert(api.read(s.avatar_address,24),'animation_avatar_unreadable')
  local words=ffi.new('uint32_t[6]');ffi.copy(words,b,24)
  assert(tonumber(words[2])==s.avatar and tonumber(words[3])==s.avatar_unit,'animation_avatar_changed')
  local net=tonumber(words[4]);assert(net~=0 and net~=0xffffffff,'animation_avatar_network_ref')
  local x=inspector:capture({id=s.avatar,unit=s.avatar_unit,network_unit=net})
  assert(x.stable and x.dispatch_matches,'animation_notification_dispatch')
  local schema
  for _,m in ipairs(x.routing.messages)do if m.hash==0xbde53653 then schema=m end end
  assert(schema and schema.found and schema.flags[1]==1 and schema.flags[2]==1 and schema.parameter_count==3,'animation_notification_schema')
  for i,t in ipairs({256,567,106})do assert(schema.type_indices[i]==t,'animation_notification_parameter')end
  assert(#x.animators==1,'animation_notification_manager_count')
  local a=x.animators[1]
  assert(a.avatar_found and a.entity_matches and a.network_matches,'animation_notification_avatar_membership')
  local event
  for _,e in ipairs(x.events)do if e.name=='action_end' and e.hash==0xdab88e64 then event=e end end
  assert(event and event.found and event.roundtrip and event.index<x.event_count,'animation_action_end_dictionary')
  local boot
  if target==4 then
   for _,e in ipairs(x.events)do if e.name=='frv_enter_boot'and e.hash==0xe86f3c8c then boot=e end end
   assert(boot and boot.found and boot.roundtrip and boot.index<x.event_count,'animation_gunner_dictionary')
  end
  return net,event.index,x,boot and boot.index
 end
 return {prepare=function(_,s,dest,target)
  assert(target>=0 and target<=4 and target%1==0,'animation_gunner_scope')
  local net,index,evidence,boot=check(s,target)
  -- Match the native wrapper's three descriptors. All four bool bytes are zero,
  -- avoiding unspecified padding in the wrapper's one-byte stack spill.
  local values=ffi.new('uint32_t[3]',{net,index,0});local args=args_type()
  for i=0,2 do args[i].type=i==2 and 0 or 1;args[i].size=4;args[i].value=values+i end
  local invoke=ffi.cast('void (*)(uint32_t,uint64_t,const void *,uint32_t)',check_code('trace_send'))
  local used=false
  return {check=function()
   local n,i,_,b=check(s,target);assert(n==net and i==index and b==boot,'animation_prepared_identity_changed')
  end,send=function(emit)
   assert(not used,'animation_notification_already_invoked');trace:health();used=true
   -- FRV gunner snapshot restores attachments (action5) but emits no entry pose.
   -- Select the gunner animation before ending it; action_end alone keeps the old seated pose.
   if boot then
    values[1]=boot
    emit({event='sync_gunner_pose_invoking',avatar=s.avatar,event_hash=0xe86f3c8c,event_index=boot,flag=false,remote_success_not_confirmed=true})
    invoke(0xbde53653,dest,args,3)
    values[1]=index
   end
   emit({event='sync_animation_end_invoking',avatar=s.avatar,network_unit=net,event_index=index,
    event_hash=0xdab88e64,flag=false,preflight=evidence,remote_success_not_confirmed=true})
   invoke(0xbde53653,dest,args,3)
   -- Keep descriptor backing storage reachable across the synchronous call.
   assert(values[2]==0)
   emit({event='sync_animation_end_call_returned',avatar=s.avatar,remote_success_not_confirmed=true})
  end}
 end}
end
