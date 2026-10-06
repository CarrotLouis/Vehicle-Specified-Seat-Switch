from pathlib import Path
W=Path(__file__).resolve().parent;R=W/'seat_driver_weapon_diagnostic'
p=R/'adapter.lua';s=p.read_text();a=s.index('function M.eligible(');b=s.index('function M.new(',a)
s=s[:a]+'''function M.eligible(c,source,owned,ticket,target)
 local s,o=c.native,c.owner
 if not s then return false,c.native_reason or 'local_seat_unavailable'end
 if s.vehicle~='m102'or s.transition~=26 or #s.profile.roles~=5 then return false,'M102_only'end
 if not owned or o.owner~=o.selfpeer or not s.owned or not o.vehicle.owned_local or o.busy then return false,'already_local_authority_required'end
 if c.sample.player_count~=2 or c.sample.local_count~=1 or s.player_count~=2 or s.peer_count~=2 or o.peer_count~=2 then return false,'two_players_required'end
 if not c.destination or c.destination==o.selfpeer or not o.members[c.destination]or not o.members[o.coordinator]or(o.coordinator~=o.selfpeer and o.coordinator~=c.destination)then return false,'two_peer_host_identity_required'end
 if not c.avatar or not c.avatar.is_local or not c.avatar.owned_local or not o.avatars[s.avatar]or o.avatars[s.avatar].owner~=o.selfpeer then return false,'avatar_owner_unconfirmed'end
 if s.node~=source or source<0 or source>4 or source%1~=0 or s.active or not c.avatar.vehicle_input or not seated(c.avatar,o.vehicle,source,s.profile.roles[source+1])then return false,'sit_still_in_expected_seat'end
 local remote_count=0
 for _,a in ipairs(c.sample.avatars)do if not a.is_local then
  remote_count=remote_count+1
  if a.seat and a.seat.collection==o.vehicle.id then return false,'friend_must_remain_outside'end
 end end
 if remote_count~=1 then return false,'one_remote_avatar_required'end
 if source==0 then
  if not c.driver or not c.driver.is_local or c.driver.id~=s.avatar or c.driver.unit~=s.avatar_unit then return false,'local_driver_identity_changed'end
 elseif c.driver then return false,'driver_seat_must_remain_empty'end
 local destination=target or(ticket and(source==ticket.source and ticket.target or ticket.source))
 if not destination or destination<0 or destination>4 or destination%1~=0 or destination==source then return false,'invalid_experiment_target'end
 if s.occupied[destination]~=false then return false,'target_occupied_or_reserved'end
 if ticket and(c.identity~=ticket.identity or s.identity~=ticket.avatar_binding or c.destination~=ticket.destination or o.coordinator~=ticket.coordinator)then return false,'operation_identity_changed'end
 return true
end
'''+s[b:]
s=s.replace('source=c.seat,target=target or(5-c.seat),avatar_binding=c.native.identity,driver_id=c.driver.id,driver_unit=c.driver.unit','source=c.seat,target=assert(target),avatar_binding=c.native.identity')
a=s.index(' function self:request(');b=s.index(' function self:execute(',a)
s=s[:a]+" function self:request()error('ownership_transfers_disabled_in_driver_experiment')end\n"+s[b:]
s=s.replace(' function self:execute(c,t)\n'," function self:execute(c,t)\n  assert(t.local_authority and t.original==t.selfpeer,'already_local_ticket_required')\n")
a=s.index(' function self:return_owned(');b=s.index(' return self\nend\nreturn M',a)
s=s[:a]+" function self:return_owned()error('ownership_transfers_disabled_in_driver_experiment')end\n"+s[b:];p.write_text(s)
def edit(name,pairs):
 p=R/name;s=p.read_text()
 for old,new in pairs:assert old in s,(name,old);s=s.replace(old,new)
 p.write_text(s,encoding='utf-8')
edit('probe.lua',[("route[1]==1","(route[1]==0 or route[1]==1)"),('a>=1 and a<=4','a>=0 and a<=4'),('b>=1 and b<=4','b>=0 and b<=4'),('(a==4 or b==4)','(a==4 or b==4 or a==0 or b==0)')])
edit('transaction.lua',[
 ('return function(api,game,p,pose_factory,personal_factory,emit)','return function(api,game,p,pose_factory,personal_factory,emit,driver_factory)'),
 ("assert((s.node>=1 and s.node<=3 and s.node%1==0 and target==4)or(s.node==4 and target>=1 and target<=3 and target%1==0),'integrated_transaction_direction')","assert(s.node>=0 and s.node<=4 and s.node%1==0 and target>=0 and target<=4 and target%1==0 and s.node~=target,'integrated_transaction_direction')"),
 ('(s.node==4 and 2 or 3)','(s.node==0 and 1 or s.node==4 and 2 or 3)'),('(target==4 and 2 or 3)','(target==0 and 1 or target==4 and 2 or 3)'),
 ('  return function()','  local neutralize\n  if s.node==0 then neutralize=assert(driver_factory,\'driver_factory_required\')(api,game,p).prepare(s)end\n  return function()'),
 ("   stage('reserve');","   if neutralize then stage('neutralize_own_driver_commands');neutralize()end\n   stage('reserve');")])
edit('binding_sender.lua',[('if target==4 then','if target==4 or s.node~=4 then'),('target>=1 and target<=3','target>=0 and target<=3')])
edit('animation_sender.lua',[('target>=1 and target<=4','target>=0 and target<=4')])
edit('sender.lua',[('target>=1 and target<=4','target>=0 and target<=4')])
edit('entry.lua',[('host_or_guest_M102_rear_weapon; local_or_borrowed_authority; route_1_4_2_4_3_4_1','host_or_guest_M102_driver; already_local_only; route_0_4_0_2_0_3_0'),('transaction(api,game,p,observed_pose,personal,emit)','transaction(api,game,p,observed_pose,personal,emit,driver)'),('{1,4,2,4,3,4,1}','{0,4,0,2,0,3,0}')])
edit('build.py',[("['personal','transaction','sender']","['personal','driver','transaction','sender']"),("'test_binding_inspect']","'test_binding_inspect','test_driver']")])
edit('prepare_tests.py',[('((1,4),(4,2),(2,4),(4,3),(3,4),(4,1))','((0,4),(4,0),(0,2),(2,0),(0,3),(3,0))'),('(2 if source==4 else 3)','(1 if source==0 else 2 if source==4 else 3)'),('(2 if target==4 else 3)','(1 if target==0 else 2 if target==4 else 3)')])
print('Configured local-owned M102 driver experiment; no authority transfer path')
