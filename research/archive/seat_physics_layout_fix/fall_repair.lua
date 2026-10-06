-- Also covers native gunner/passenger routes: no chassis/seat/weapon mutation.
-- One reset per settled passenger visit, only if own Fall/Fall_Aim is observed.
return function(api,p,pose_factory,adapter,animation_sender,snapshot,layout,trace,emit,fleet)
 local ffi=api.ffi;local pose=pose_factory(api,p);local repaired=nil
 local function allowed(c,s)
  local o,a=c.owner,c.avatar;local d=layout(s)
  local peers_ok=s.player_count==2 and s.peer_count==2 and c.sample.player_count==2 and o.peer_count==2 and
   (o.coordinator==o.selfpeer or o.coordinator==c.destination)
  if s.player_count>=3 and fleet then peers_ok=fleet.room(c)and s.peer_count==s.player_count and
   s.player_count==c.sample.player_count end
  return d and s.vehicle=='bastion' and d.tank and d.roles[s.node+1]==3 and
   peers_ok and c.sample.local_count==1 and
   not o.busy and c.native and c.native.identity==s.identity and c.native.node==s.node and
   type(c.destination)=='string' and #c.destination==8 and c.destination~=o.selfpeer and o.members[c.destination] and o.members[o.coordinator] and
   a and a.id==s.avatar and a.unit==s.avatar_unit and a.is_local and a.owned_local and a.vehicle_input and
   o.avatars[s.avatar] and o.avatars[s.avatar].owner==o.selfpeer and
   a.seat and a.seat.collection==s.collection and a.seat.current==s.node and a.seat.reserved==s.node and
   a.seat.role==3 and a.seat.target==-1 and a.seat.action==-1 and a.seat.transitioning==0 and a.seat.queued_exit==0 and
   snapshot.current(api,s)
 end
 local function passenger(s)return s and s.vehicle=='bastion' and s.node>=2 and s.node<=3 and
   (s.player_count==2 or fleet and s.player_count>=3 and s.player_count<=4)and s.peer_count==s.player_count end
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
  local c
  if s.player_count>=3 then
   local good,value=pcall(adapter.capture,adapter)
   if not good or not value or not fleet.room(value)then return end
   c=value
  else c=assert(adapter:capture(),'Bastion repair context unavailable')end
  assert(allowed(c,s),'Bastion repair avatar/peer/seat context changed')
  assert(pose.check(s))
  local peers=s.player_count>=3 and fleet.keys(c.owner.members)or{c.owner.selfpeer,c.destination}
  local sends={}
  for _,key in ipairs(peers)do if key~=c.owner.selfpeer then
   local dest=ffi.new('uint64_t[1]');ffi.copy(dest,key,8)
   local send=animation_sender:prepare_fall(s,dest[0]);send.check();sends[#sends+1]=send
  end end
  local fresh
  if s.player_count>=3 then
   local good,value=pcall(adapter.capture,adapter)
   if not good or not value or not fleet.room(value)or
     not fleet.same(peers,fleet.keys(value.owner.members))or value.owner.coordinator~=c.owner.coordinator then return end
   fresh=value
  else fresh=assert(adapter:capture(),'Bastion repair fresh context unavailable')end
  assert(allowed(fresh,s) and fresh.identity==c.identity and fresh.destination==c.destination and
   fresh.owner.session==c.owner.session and fresh.owner.engine==c.owner.engine and fresh.owner.coordinator==c.owner.coordinator and
   (s.player_count==2 or fleet.same(peers,fleet.keys(fresh.owner.members))),
   'Bastion repair session changed')
  local done,old=pose.clear_fall(s);assert(done,'Bastion overlay changed before repair')
  repaired=key
  emit({event='bastion_native_passenger_fall_cleared',avatar=s.avatar,seat=s.node,old_overlay=old,other_layers_preserved=true})
  for _,send in ipairs(sends)do send.send(emit)end
 end}
end
