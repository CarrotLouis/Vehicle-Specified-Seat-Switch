return function(policy,snapshot,input)
 local C={};C.__index=C
 function C.new(mode,keys,api,native,log)
  assert(mode=='normal' or mode=='enhanced')
  local self=setmetatable({mode=mode,keys=keys,api=api,native=native,log=log,cooldown=0},C)
  self:reset();return self
 end
 function C:reset()
  self.input=input.new(self.keys,self.api)
 end
 function C:update(s,reason)
  local focused=self.api.focused() and (not self.api.input_allowed or self.api.input_allowed())
  local pressed=self.input:poll(focused)
  if not focused then self.pending=nil;self.preparing=nil;return 'not_focused' end
  if self.preparing then
   local p=self.preparing
   if self.api.now()>p.started+6 then self.preparing=nil;return 'prepare_expired' end
   if not s then return 'lowering_personal_weapon' end
   if s.identity~=p.identity then self.preparing=nil;return 'vehicle_changed' end
   if s.active then return 'lowering_personal_weapon' end
   local seat=policy.seats[s.vehicle][p.target+1]
   local current=policy.seats[s.vehicle][s.node+1]
   local allowed,why=policy.check(self.mode,s.vehicle,current,seat,s.occupied[p.target])
   local available,issue=self.native.available(s)
   if not allowed or not available then self.preparing=nil;return why or issue end
   if not self.api.focused() or (self.api.input_allowed and not self.api.input_allowed()) or not snapshot.current(self.api,s) then self.preparing=nil;return 'snapshot_changed' end
   self.preparing=nil;self.pending={identity=s.identity,target=p.target,started=self.api.now()}
   self.log('request direct_solo_test '..s.vehicle..' '..current..' -> '..seat)
   self.native.direct(s,p.target)
   if self.native.last_detail then self.log(self.native.last_detail) end
   return 'requested'
  end
  if self.pending then
   local p=self.pending
   if not s or s.identity~=p.identity then
    if self.api.now()>p.started+6 then self.log('request_expired '..tostring(reason));self.pending=nil end
   elseif s.node==p.target then
    self.log('observed_target vehicle='..s.vehicle..' node='..s.node..' (network/in-game observation still required)')
    self.pending=nil
   elseif self.api.now()>p.started+6 then
    self.log('request_not_completed actual='..s.node..' wanted='..p.target);self.pending=nil
   end
   return 'waiting_for_completion'
  end
  if not s then return reason end
  local target,seat
  for i,name in ipairs(policy.seats[s.vehicle]) do
   if pressed[self.keys[s.vehicle][name]] then
    if target then return 'multiple_seat_keys' end
    target=i-1;seat=name
   end
  end
  if target==nil then return 'ready' end
  if self.api.now()<self.cooldown then return 'cooldown' end
  self.cooldown=self.api.now()+0.35
  local current=policy.seats[s.vehicle][s.node+1]
  local allowed,why=policy.check(self.mode,s.vehicle,current,seat,s.occupied[target])
  if not allowed then self.log('rejected '..why..' '..s.vehicle..' '..current..' -> '..seat);return why end
  local nextseat,previous=snapshot.predictions(s)
  local operation=nextseat==target and 'next' or previous==target and 'previous' or nil
  if not operation and (self.mode=='normal' or policy.direct_allowed and not policy.direct_allowed())then self.log('no_native_route '..s.vehicle);return 'no_native_route' end
  if not operation then
   local ok,issue=self.native.available(s)
   if not ok then self.log('direct_blocked '..issue);return issue end
  end
  if not self.api.focused() or (self.api.input_allowed and not self.api.input_allowed()) or not snapshot.current(self.api,s) then return 'snapshot_changed' end
  if not operation and s.active then
   self.preparing={identity=s.identity,target=target,started=self.api.now()}
   self.log('lower_personal_weapon_before_switch '..s.vehicle)
   self.native.prepare(s);return 'lowering_personal_weapon'
  end
  self.pending={identity=s.identity,target=target,started=self.api.now()}
  self.log('request '..(operation or 'direct_solo_test')..' '..s.vehicle..' '..current..' -> '..seat)
  if operation then self.native[operation](s.seaters,s.avatar) else self.native.direct(s,target) end
  if not operation and self.native.last_detail then self.log(self.native.last_detail) end
  return 'requested'
 end
 return C
end
