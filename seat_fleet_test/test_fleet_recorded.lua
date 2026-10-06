local M=assert(loadfile('work/seat_fleet_test/adapter.lua'))()
M.fleet=assert(loadfile('work/seat_fleet_test/fleet_policy.lua'))()
local profiles=assert(loadfile('work/seat_switch/src/profile.lua'))().tables
local frames=assert(loadfile('work/seat_fleet_test/fleet-recorded-fixture.lua'))()
local tested,accepted,refused,incomplete=0,0,0,0;local hosts,owners_elsewhere={},0
for _,r in ipairs(frames)do
 local v=r.vehicle;local profile=profiles[v.name];assert(profile)
 local c={sample={state='mission',player_count=r.players,peer_count=r.players,local_count=1,avatars=r.avatars},
  owner={owner=r.ownership.owner,selfpeer=r.local_peer,coordinator=r.coordinator,members={},peer_count=r.players,
   busy=r.ownership.busy,serial=r.ownership.serial,vehicle=v,avatars={}},identity='frozen/car/'..v.id}
 for _,peer in ipairs(r.peers)do c.owner.members[peer]=true end
 for _,a in ipairs(r.avatars)do
  c.owner.avatars[a.id]={owner=a.owner}
  if a.is_local then c.avatar=a end
  if a.seat.collection==v.id and a.seat.current==0 and a.seat.role==1 and a.seat.reserved==0 then c.driver=a end
  if a.owner==c.owner.owner and a.seat.collection~=0 and a.seat.collection~=v.id then owners_elsewhere=owners_elsewhere+1 end
 end
 local a=c.avatar;c.seat=a.seat.current;c.destination=c.owner.owner~=c.owner.selfpeer and c.owner.owner or r.peers[2]
 c.native={identity='frozen/avatar/'..a.id,avatar=a.id,avatar_unit=a.unit,vehicle=v.name,transition=v.transition_type,
  profile=profile,node=c.seat,player_count=r.players,peer_count=r.players,owned=v.owned_local,
  active=a.seat.active_passenger~=0,occupied={}}
 for node=0,#profile.roles-1 do c.native.occupied[node]=math.floor(v.free_mask/2^node)%2==0 end
 local room_ok,room_why=M.fleet.room(c)
 if not room_ok then
  assert(#r.avatars~=r.players and room_why=='room_avatar_count_disagrees',
   'Unexpected recorded peer mapping refusal '..tostring(room_why)..' car '..v.id..' host '..r.coordinator)
  incomplete=incomplete+1
 end
 for target=0,#profile.roles-1 do if target~=c.seat then
  local good=M.eligible(c,c.seat,v.owned_local,nil,target)
  if good then
   assert(room_ok,'Incomplete room must not permit a transaction')
   accepted=accepted+1;hosts[r.coordinator]=true
   local ticket={identity=c.identity,source=c.seat,target=target,selfpeer=c.owner.selfpeer,original=c.owner.owner,
    local_authority=v.owned_local,avatar_binding=c.native.identity,coordinator=c.owner.coordinator}
   ticket=M.fleet.ticket(c,target,ticket,M.layout)
   assert(M.eligible(c,c.seat,v.owned_local,ticket,target))
   c.native.occupied[target]=true;assert(not M.eligible(c,c.seat,v.owned_local,ticket,target));c.native.occupied[target]=false
  else refused=refused+1 end
  tested=tested+1
 end end
end
assert(accepted>0 and refused>0 and incomplete>0 and hosts.P1 and hosts.P2 and owners_elsewhere>0)
print('PASS '..#frames..' captured three-player car contexts / '..tested..' directions, '..accepted..' accepted preflights / '..refused..' conservative refusals, both host roles and owner driving another car; recorded relationships only, mutation/network/physics not replayed')
