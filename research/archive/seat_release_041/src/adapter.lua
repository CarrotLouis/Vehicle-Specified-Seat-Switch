-- Only fresh context capture is retained; no chassis-loan methods.
local M={}
local function seated(a,v,node,role)
 local s=a and a.seat
 return s and s.collection==v.id and s.current==node and s.reserved==node and s.role==role
  and s.target==-1 and s.action==-1 and s.transitioning==0 and s.queued_exit==0
end
function M.new(api,game,p,reader,owner_reader,snapshot,transaction,sender,trace,emit,encode)
 local self={}
 function self:capture(ticket)
  local sample,why=reader:capture();if not sample or sample.state~='mission'then return nil,why or 'not_in_mission'end
  -- Full owners for a stable fleet request; tracked-car lookups alone suffice
  -- for late-grant cleanup after cancellation or a membership-count change.
  local n=sample.player_count
  local need=n>=2 and n<=4 and #sample.avatars==n and 'all'or true
  if ticket and(ticket.cancel_reason or ticket.peer_count and n~=ticket.peer_count)then need=true end
  local o,reason=owner_reader:capture(sample,ticket and ticket.vehicle,need);if not o then return nil,reason end
  local a,driver,dest,n=nil,nil,nil,0
  for _,x in ipairs(sample.avatars)do
   if x.is_local then a=x end
   if seated(x,o.vehicle,0,1)then driver=x end
  end
  for peer in pairs(o.members)do if peer~=o.selfpeer then dest=peer;n=n+1 end end
  if n~=1 then
   local peers={};for peer in pairs(o.members)do if peer~=o.selfpeer then peers[#peers+1]=peer end end;table.sort(peers)
   dest=o.owner~=o.selfpeer and o.owner or peers[1]
  end
  -- A genuine empty-driver grant may change the car owner. Keep the original
  -- request destination pinned; notifications independently cover ALL peers.
  if ticket then dest=ticket.destination end
  local ok,s,err=pcall(snapshot.capture,api,game,p)
  if not ok then err=tostring(s);s=nil end
  if s and (not a or a.id~=s.avatar or a.unit~=s.avatar_unit or s.collection~=o.vehicle.id or s.collection_unit~=o.vehicle.network_unit or s.resource~=o.vehicle.resource)then s=nil;err='local_tracked_identity_disagrees'end
  local c={sample=sample,owner=o,native=s,native_reason=err,avatar=a,driver=driver,destination=dest,seat=s and s.node}
  -- Additional peers cancel switching but must not prevent return to the original owner.
  c.identity=o.context..'/'..o.vehicle.id..'/'..o.vehicle.unit..'/'..o.vehicle.network_unit..'/'..o.vehicle.resource..o.selfpeer
  return c
 end
 return self
end
return M
