-- Per-car, installer-only scope for stable three/four-peer rooms. Other cars
-- may keep moving: only this car's occupants and the owner's avatar identity
-- are frozen for a seat transaction. No game calls or writes in this policy.
local M={}
local function keys(m)local out={};for k in pairs(m or{})do out[#out+1]=k end;table.sort(out);return out end
local function same(a,b)if #a~=#b then return false end;for i=1,#a do if a[i]~=b[i]then return false end end;return true end
local function seated(a,v,node,role)
 local s=a and a.seat
 return s and s.collection==v.id and s.current==node and s.reserved==node and s.role==role
  and s.target==-1 and s.action==-1 and s.transitioning==0 and s.queued_exit==0
end
function M.room(c)
 local o,s=c.owner,c.sample;local n=s and s.player_count
 if not o or not n or n<2 or n>4 or n%1~=0 or s.local_count~=1 or
   s.peer_count and s.peer_count~=n or o.peer_count~=n then return false,'room_counts_disagree'end
 local peers=keys(o.members)
 if #peers~=n or not o.members[o.selfpeer]or not o.members[o.coordinator]or not o.members[o.owner]then return false,'room_peer_identity_unconfirmed'end
 if #s.avatars~=n then return false,'room_avatar_count_disagrees'end
 local seen,local_count={},0
 for _,a in ipairs(s.avatars)do
  local owner=o.avatars[a.id]and o.avatars[a.id].owner
  if not owner or not o.members[owner]or seen[owner]then return false,'room_avatar_owner_unconfirmed'end
  seen[owner]=true
  if a.is_local then
   local_count=local_count+1
   if owner~=o.selfpeer or not a.owned_local then return false,'local_avatar_owner_unconfirmed'end
  elseif owner==o.selfpeer or a.owned_local~=false then return false,'remote_avatar_owner_unconfirmed'end
 end
 if local_count~=1 then return false,'one_local_avatar_required'end
 return true,peers
end
function M.use(c,t)
 if t and t.fleet then return true end
 if c.sample.player_count>2 then return true end
 local o=c.owner
 if o.owner~=o.selfpeer then for _,a in ipairs(c.sample.avatars)do
  if o.avatars[a.id]and o.avatars[a.id].owner==o.owner and a.seat and
     a.seat.collection~=0 and a.seat.collection~=o.vehicle.id then return true end
 end end
 return false
end
local function occupants(c)
 local out={}
 for _,a in ipairs(c.sample.avatars)do if not a.is_local and a.seat and a.seat.collection==c.owner.vehicle.id then
  out[a.id]={unit=a.unit,network_unit=a.network_unit,resource=a.resource,node=a.seat.current,
   owner=c.owner.avatars[a.id]and c.owner.avatars[a.id].owner}
 end end
 return out
end
local function same_occupants(a,b)
 for id,x in pairs(a)do local y=b[id]
  if not y or x.unit~=y.unit or x.network_unit~=y.network_unit or x.resource~=y.resource or
   x.node~=y.node or x.owner~=y.owner then return false end
 end
 for id in pairs(b)do if not a[id]then return false end end
 return true
end
function M.eligible(c,source,owned,t,target,confirmation,layout)
 local s,o=c.native,c.owner
 if not s then return false,c.native_reason or'local_seat_unavailable'end
 local d=layout(s);if not d then return false,'validated_vehicle_layout_required'end
 local good,peers=M.room(c);if not good then return false,peers end
 if s.player_count~=c.sample.player_count or s.peer_count~=o.peer_count then return false,'room_counts_disagree'end
 local expected=owned and o.selfpeer or t and t.original or o.owner
 if o.owner~=expected or not owned and expected==o.selfpeer or s.owned~=owned or o.vehicle.owned_local~=owned or o.busy then return false,'ownership_not_ready'end
 local a=c.avatar
 if not a or not a.is_local or not a.owned_local or a.id~=s.avatar or a.unit~=s.avatar_unit or not a.vehicle_input or
   source<0 or source>=#d.roles or source%1~=0 or s.node~=source or
   (s.active and(not confirmation or d.roles[source+1]~=3))or not seated(a,o.vehicle,source,d.roles[source+1])then return false,'sit_still_in_expected_seat'end
 local destination=target or t and(source==t.source and t.target or t.source)
 if not destination or destination<0 or destination>=#d.roles or destination%1~=0 or destination==source then return false,'invalid_experiment_target'end
 if s.occupied[destination]~=false then return false,'target_occupied_or_reserved'end
 local retracting=false
 for _,x in ipairs(c.sample.avatars)do if not x.is_local and x.seat and x.seat.collection==o.vehicle.id then
  local node=x.seat.current;local role=type(node)=='number'and d.roles[node+1]
  local rs=x.seat
  local retract=s.vehicle=='m102'and role==3 and rs.reserved==node and rs.target==node and
   rs.action==20 and rs.transitioning==1 and rs.queued_exit==0
  if type(node)~='number'or node<0 or node>=#d.roles or node%1~=0 or node==source or
    s.occupied[node]~=true or(not seated(x,o.vehicle,node,role)and not retract)then
   return false,'car_occupant_not_settled'
  end
  retracting=retracting or retract
 end end
 local original=t and t.original or o.owner
 if c.driver then
  local driver_owner=o.avatars[c.driver.id]and o.avatars[c.driver.id].owner
  if c.driver.is_local then
   if source~=0 or c.driver.id~=s.avatar or not owned then return false,'local_driver_identity_changed'end
  elseif source==0 or destination==0 or driver_owner~=original or
    not seated(c.driver,o.vehicle,0,1)then return false,'remote_driver_context_changed'end
 elseif source==0 then return false,'local_driver_identity_changed'end
 if t then
  if c.identity~=t.identity or s.identity~=t.avatar_binding or o.coordinator~=t.coordinator or
    not same(peers,t.peers)or not same_occupants(occupants(c),t.occupants)then return false,'operation_identity_changed'end
  local owner_avatar
  for _,x in ipairs(c.sample.avatars)do if x.id==t.owner_avatar.id then owner_avatar=x end end
  if not owner_avatar or owner_avatar.unit~=t.owner_avatar.unit or owner_avatar.network_unit~=t.owner_avatar.network_unit or
    o.avatars[owner_avatar.id].owner~=t.original then return false,'original_owner_avatar_changed'end
 end
 if retracting then return false,'friend_passenger_retracting',true end
 return true
end
function M.ticket(c,target,t,layout)
 local ok,peers=M.room(c);assert(ok,peers)
 t.fleet=true;t.peers=peers;t.occupants=occupants(c);t.notifications={}
 for _,peer in ipairs(peers)do if peer~=t.selfpeer then t.notifications[#t.notifications+1]=peer end end
 for _,a in ipairs(c.sample.avatars)do if c.owner.avatars[a.id].owner==t.original then
  t.owner_avatar={id=a.id,unit=a.unit,network_unit=a.network_unit}
 end end
 assert(t.owner_avatar,'original_owner_avatar_unconfirmed')
 local d=assert(layout(c.native))
 t.driver_acquire=not t.local_authority and target==0 and c.seat>=1 and not(d.frv and c.seat==1)
 return t
end
M.keys=keys;M.same=same
return M
