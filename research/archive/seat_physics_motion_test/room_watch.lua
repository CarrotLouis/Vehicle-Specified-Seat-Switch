-- Read-only fleet/peer evidence. This observer never invokes authority send,
-- seat transactions or animation/weapon calls, even when the room has 3/4 peers.
return function(api,reader,owner_reader,emit,encode)
 local next_sample,cursor,last_roster,last_gap=0,0,nil,nil
 local function alias(key)return reader.peers[key] or 'unlabelled_peer' end
 local function avatar(a,owner)
  return {id=a.id,unit=a.unit,network_unit=a.network_unit,resource=a.resource,
   is_local=a.is_local,owned_local=a.owned_local,vehicle_input=a.vehicle_input,seat=a.seat,
   owner=owner and alias(owner.owner) or nil}
 end
 return {update=function(_,sample,pending)
  if not sample then return end
  local roster={state=sample.state,mission=sample.mission_value,players=sample.player_count,
   local_count=sample.local_count,peer_count=sample.peer_count,peers=sample.peers,avatars={}}
  for _,a in ipairs(sample.avatars or {})do
   roster.avatars[#roster.avatars+1]={id=a.id,unit=a.unit,network_unit=a.network_unit,is_local=a.is_local}
  end
  local key=encode(roster)
  if key~=last_roster then
   last_roster=key;cursor=0;last_gap=nil
   emit({event='room_roster',data=roster,read_only=true})
  end
  local now=api.now()
  if sample.state~='mission' or pending or now<next_sample then return end
  next_sample=now+.5
  local vehicles=sample.vehicles or {}
  if #vehicles==0 then return end
  -- One vehicle per interval; at most eight watched collections from the sampler.
  cursor=cursor%#vehicles+1
  local v=vehicles[cursor]
  local ok,o,why=pcall(owner_reader.capture,owner_reader,sample,v,'all')
  if not ok or not o then
   local reason=ok and why or tostring(o)
   local gap=tostring(v.id)..'/'..tostring(reason)
   if gap~=last_gap then
    last_gap=gap;emit({event='room_ownership_gap',collection=v.id,vehicle=v.name,reason=reason,
     evidence=owner_reader.evidence,read_only=true})
   end
   return
  end
  last_gap=nil
  local peers,count={},0
  for raw in pairs(o.members)do count=count+1;peers[#peers+1]=alias(raw) end
  table.sort(peers)
  local avatars,owners,local_match={},0,true
  for _,a in ipairs(sample.avatars)do
   local own=o.avatars[a.id]
   local row=avatar(a,own)
   row.owner_in_session=own and o.members[own.owner] or false
   if own then owners=owners+1 end
   if a.is_local and(not own or own.owner~=o.selfpeer)then local_match=false end
   avatars[#avatars+1]=row
  end
  emit({event='room_ownership_sample',read_only=true,
   session_context_hex=(o.context:gsub('.',function(ch)return string.format('%02x',ch:byte())end)),players=sample.player_count,local_count=sample.local_count,
   sampler_peer_count=sample.peer_count,engine_peer_count=o.peer_count,peers=peers,
   local_peer=alias(o.selfpeer),coordinator=alias(o.coordinator),
   vehicle=v,ownership=owner_reader:summary(o),owner_in_session=o.members[o.owner] or false,
   avatars=avatars,avatar_owners_read=owners,local_avatar_owner_matches=local_match,
   counts_agree=sample.player_count==sample.peer_count and sample.peer_count==o.peer_count and count==o.peer_count})
 end}
end
