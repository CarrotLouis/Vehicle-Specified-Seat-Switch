-- At most four exact native peer keys and their current avatar identities.
-- Foreign occupants are pinned only for the vehicle actually being switched.
local M={}
function M.capture(c)
 local o,s=c.owner,c.native;local sample=c.sample
 local n=sample and sample.player_count
 if type(n)~='number'or n<2 or n>4 or n%1~=0 or sample.local_count~=1 or
  o.peer_count~=n or s and(s.player_count~=n or s.peer_count~=n)or
  sample.peer_count~=nil and sample.peer_count~=n or type(sample.avatars)~='table'or #sample.avatars~=n then
  return nil,'reservation_membership_not_settled'
 end
 local peers,count={},0
 for key,value in pairs(o.members or{})do
  if type(key)~='string'or #key~=8 or key==string.rep('\0',8)or value~=true then return nil,'reservation_member_key_invalid'end
  peers[#peers+1]=key;count=count+1
 end
 table.sort(peers)
 if count~=n or not o.members[o.selfpeer]or not o.members[o.coordinator]or not o.members[o.owner]then return nil,'reservation_native_members_disagree'end
 local seen,avatars,occupants,destinations={},{},{},{}
 local local_count=0
 for _,a in ipairs(sample.avatars)do
  local owner=o.avatars[a.id]and o.avatars[a.id].owner
  if not owner or not o.members[owner]or seen[owner]or type(a.id)~='number'or type(a.unit)~='number'or type(a.network_unit)~='number'
   or a.id<=0 or a.id>=0xffffffff or a.id%1~=0 or a.unit<=0 or a.unit>=0xffffffff or a.unit%1~=0
   or a.network_unit<=0 or a.network_unit>=0x7fff or a.network_unit%1~=0 then return nil,'reservation_avatar_membership_disagrees'end
  seen[owner]=true
  if a.is_local then local_count=local_count+1;if owner~=o.selfpeer or not a.owned_local then return nil,'reservation_local_avatar_owner_changed'end
  elseif owner==o.selfpeer or a.owned_local~=false then return nil,'reservation_remote_avatar_owner_changed'end
  avatars[#avatars+1]=table.concat({a.id,a.unit,a.network_unit},'/')..owner
  if not a.is_local and a.seat and a.seat.collection==o.vehicle.id then
   local seat=a.seat
   occupants[#occupants+1]=table.concat({a.id,a.unit,a.network_unit,seat.collection,seat.current or 0,seat.reserved or 0,seat.role or 0,
    seat.target or -1,seat.action or -1,seat.transitioning or 0,seat.queued_exit or 0},'/')
  end
 end
 if local_count~=1 then return nil,'reservation_local_avatar_count'end
 for _,key in ipairs(peers)do if key~=o.selfpeer then destinations[#destinations+1]=key end end
 table.sort(avatars);table.sort(occupants)
 return {count=n,destinations=destinations,signature=table.concat(peers)..o.coordinator..o.selfpeer..table.concat(avatars,';'),
  occupants=table.concat(occupants,';')}
end
return M
