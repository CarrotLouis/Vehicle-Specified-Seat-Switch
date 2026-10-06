-- Also covers native gunner/passenger routes: no chassis/seat/weapon mutation.
-- One reset per settled passenger visit, only if own Fall/Fall_Aim is observed.
return function(api,p,pose_factory,adapter,animation_sender,snapshot,layout,trace,emit)
 local ffi=api.ffi;local pose=pose_factory(api,p);local repaired=nil
 local function allowed(c,s)
  local o,a=c.owner,c.avatar;local d=layout(s)
  return d and s.vehicle=='bastion' and d.tank and d.roles[s.node+1]==3 and
   s.player_count==2 and s.peer_count==2 and c.sample.player_count==2 and c.sample.local_count==1 and
   o.peer_count==2 and not o.busy and c.native and c.native.identity==s.identity and c.native.node==s.node and
   type(c.destination)=='string' and #c.destination==8 and c.destination~=o.selfpeer and o.members[c.destination] and o.members[o.coordinator] and
   (o.coordinator==o.selfpeer or o.coordinator==c.destination) and
   a and a.id==s.avatar and a.unit==s.avatar_unit and a.is_local and a.owned_local and a.vehicle_input and
   o.avatars[s.avatar] and o.avatars[s.avatar].owner==o.selfpeer and
   a.seat and a.seat.collection==s.collection and a.seat.current==s.node and a.seat.reserved==s.node and
   a.seat.role==3 and a.seat.target==-1 and a.seat.action==-1 and a.seat.transitioning==0 and a.seat.queued_exit==0 and
   snapshot.current(api,s)
 end
 local function passenger(s)return s and s.vehicle=='bastion' and s.node>=2 and s.node<=3 and s.player_count==2 and s.peer_count==2 end
 return {needs_check=function(_,s)
  return passenger(s)and repaired~=s.identity..'/'..s.node
 end,update=function(_,s)
  if not passenger(s)then repaired=nil;return end
  local key=s.identity..'/'..s.node
  if repaired==key or not snapshot.current(api,s)then return end
  -- Captured residue is already present when entering the passenger seat.
  -- Check once per settled visit, including the ordinary native route.
  if not pose.fall_present(s)then repaired=key;return end
  assert(not api.experiment_allowed or api.experiment_allowed(),'Bastion repair logging unavailable')
  trace:health()
  local c=assert(adapter:capture(),'Bastion repair context unavailable')
  assert(allowed(c,s),'Bastion repair avatar/peer/seat context changed')
  assert(pose.check(s))
  local dest=ffi.new('uint64_t[1]');ffi.copy(dest,c.destination,8)
  local send=animation_sender:prepare_fall(s,dest[0]);send.check()
  local fresh=assert(adapter:capture(),'Bastion repair fresh context unavailable')
  assert(allowed(fresh,s) and fresh.identity==c.identity and fresh.destination==c.destination and
   fresh.owner.session==c.owner.session and fresh.owner.engine==c.owner.engine and fresh.owner.coordinator==c.owner.coordinator,
   'Bastion repair session changed')
  local done,old=pose.clear_fall(s);assert(done,'Bastion overlay changed before repair')
  repaired=key
  emit({event='bastion_native_passenger_fall_cleared',avatar=s.avatar,seat=s.node,old_overlay=old,other_layers_preserved=true})
  send.send(emit)
 end}
end
