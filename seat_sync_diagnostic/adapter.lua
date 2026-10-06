-- Scope and fresh-state checks are separate from the native transaction.
local M={}
function M.eligible(c)
 local s,o,a=c.native,c.owner,c.avatar
 if s.vehicle~='bastion' or s.transition~=43 then return false,'TD220_only' end
 if c.sample.player_count~=2 or s.player_count~=2 or s.peer_count~=2 or o.peer_count~=2 then return false,'exactly_two_players_required' end
 if o.selfpeer==o.coordinator then return false,'friend_must_host_this_experiment' end
 if not c.destination or c.destination~=o.coordinator or not o.members[c.destination] then return false,'remote_host_not_confirmed' end
 if not s.owned or not o.vehicle.owned_local or o.owner~=o.selfpeer then return false,'vehicle_not_owned_locally' end
 if not a.owned_local or not o.avatars[s.avatar] or o.avatars[s.avatar].owner~=o.selfpeer then return false,'avatar_not_owned_locally' end
 if o.busy then return false,'vehicle_authority_busy' end
 if s.active or (s.node~=0 and s.node~=1) then return false,'driver_or_gunner_seated_required' end
 if not a.vehicle_input then return false,'vehicle_input_inactive' end
 if s.occupied[1-s.node]~=false then return false,'target_occupied_or_reserved' end
 for _,other in ipairs(c.sample.avatars)do
  if not other.is_local and other.seat and other.seat.collection==s.collection then return false,'friend_must_remain_outside_tank' end
 end
 return true
end
function M.new(api,game,p,reader,owner_reader,snapshot,transaction,sender,trace,emit,encode)
 local self={eligible=M.eligible}
 -- Method-compatible wrapper; the pure function above is tested independently.
 function self:eligible(c)return M.eligible(c)end
 function self:capture()
  local sample,why=reader:capture();if not sample or sample.state~='mission'then return nil,why or 'not_in_mission'end
  local s,reason=snapshot.capture(api,game,p);if not s then return nil,reason end
  if s.vehicle~='bastion'then return nil,'TD220_only'end
  local a,v
  for _,x in ipairs(sample.avatars)do if x.is_local and x.id==s.avatar then a=x;break end end
  for _,x in ipairs(sample.vehicles)do if x.id==s.collection then v=x;break end end
  assert(a and v and a.unit==s.avatar_unit and v.network_unit==s.collection_unit and v.resource==s.resource,'sync_sample_identity_disagrees')
  assert(a.seat and a.seat.collection==s.collection and a.seat.current==s.node,'sync_sample_seat_disagrees')
  local o,err=owner_reader:capture(sample,v,true);if not o then return nil,err end
  local dest,count=nil,0
  for peer in pairs(o.members)do if peer~=o.selfpeer then dest=peer;count=count+1 end end
  if count~=1 then dest=nil end
  local c={sample=sample,native=s,owner=o,avatar=a,destination=dest,seat=s.node}
  c.identity=o.context..'/'..s.identity..o.selfpeer..(dest or '')
  c.summary=encode({seat=s.node,role=s.profile.roles[s.node+1],vehicle=s.vehicle,ownership=owner_reader:summary(o)})
  return c
 end
 local function identity_same(a,b)
  return a.identity==b.identity and a.owner.owner==b.owner.owner and a.owner.serial==b.owner.serial
   and a.owner.record_word0==b.owner.record_word0 and a.owner.record_word1==b.owner.record_word1
 end
 function self:execute(before,target)
  assert(trace.active,'sync_trace_inactive');trace:health()
  assert(api.input_allowed(),'sync_input_blocked')
  for _,key in ipairs({1,2,4,5,6,32,65,68,69,81,83,87})do assert(not api.down(key),'release_movement_fire_and_action_inputs')end
  local c=assert(self:capture());assert(identity_same(before,c)and before.seat==c.seat,'sync_state_changed_before_prepare')
  local ok,why=M.eligible(c);assert(ok,why)
  assert(target==1-c.seat,'sync_wrong_target')
  local local_switch=transaction:prepare(c.native,target)
  local send=sender:prepare(c.owner,c.destination,c.native,target)
  local fresh=assert(self:capture());ok,why=M.eligible(fresh);assert(ok,why)
  assert(identity_same(c,fresh)and fresh.seat==c.seat and snapshot.current(api,c.native),'sync_state_changed_before_mutation')
  emit({event='sync_preflight_passed',source=c.seat,target=target,ownership=owner_reader:summary(c.owner)})
  local_switch()
  local after=assert(self:capture());ok,why=M.eligible(after);assert(ok,why)
  assert(identity_same(c,after)and after.seat==target,'sync_post_local_state_disagrees')
  assert(snapshot.current(api,after.native),'sync_post_local_snapshot_changed')
  send(emit)
 end
 return self
end
return M
