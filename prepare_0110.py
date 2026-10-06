from pathlib import Path
W=Path(__file__).resolve().parent
R=W/'seat_configurable_network_test'
assert not R.exists();R.mkdir()
for p in (W/'seat_driver_weapon_diagnostic').iterdir():
 if p.is_file() and p.suffix in ('.lua','.py','.txt') and p.name not in ('bundled.lua','check.lua'):
  (R/p.name).write_text(p.read_text(encoding='utf-8').replace('seat_driver_weapon_diagnostic','seat_configurable_network_test').replace('0.10.5','0.11.0'),encoding='utf-8')
# Keep fixed-route regression tests; enable a separate optional arbitrary-target mode.
p=R/'probe.lua';s=p.read_text();s=s.replace('function M.new(adapter,emit,status,route)','function M.new(adapter,emit,status,route,dynamic)')
s=s.replace("if self.count==#route-1 then phase('finished')else phase('waiting_second_trigger')end", "if not dynamic and self.count==#route-1 then phase('finished')else phase('waiting_second_trigger')end")
start=s.index('  local source,target=route[self.count+1],route[self.count+2]')
end=s.index('  ticket=adapter:ticket(c,target);',start)
old=s[start:end]
new='''  local source,target
  if dynamic then
   source=c.seat;target=type(trigger)=='number'and trigger or nil
   local key=c.identity..'/'..tostring(source)..'/'..tostring(c.owner.owner)
   if not focused or not c.native or c.native.active or c.owner.busy then stable_since=nil;stable_key=nil;return end
   if stable_key~=key then stable_key=key;stable_since=now end
   if target==nil then return end
   if now-stable_since<3 or now<cooldown then event('trigger_rejected',{reason='settle_or_cooldown',target=target});return end
   if target<0 or target>4 or target%1~=0 or source==target then event('trigger_rejected',{reason='invalid_target',target=target});return end
   local ready,reason=adapter:eligible(c,source,c.owner.owner==c.owner.selfpeer,nil,target)
   if not ready then event('trigger_rejected',{reason=reason,target=target});return end
  else
'''+old+'''  end
'''
s=s[:start]+new+s[end:];p.write_text(s)
# Merge the independently verified local/outside and borrowed/remote-driver contexts.
p=R/'adapter.lua';s=p.read_text()
s=s.replace(" if not owned or o.owner~=o.selfpeer or not s.owned or not o.vehicle.owned_local or o.busy then return false,'already_local_authority_required'end", " local expected=owned and o.selfpeer or c.destination\n if o.owner~=expected or s.owned~=owned or o.vehicle.owned_local~=owned or o.busy then return false,'ownership_not_ready'end")
a=s.index(' local remote_count=0');b=s.index(' local destination=target',a)
s=s[:a]+''' local borrowed=ticket and not ticket.local_authority or not ticket and not owned
 if borrowed then
  if source==0 or target==0 or ticket and(ticket.source==0 or ticket.target==0)then return false,'borrowed_driver_target_not_enabled'end
  if not c.driver or c.driver.is_local or not seated(c.driver,o.vehicle,0,1)or not o.avatars[c.driver.id]or o.avatars[c.driver.id].owner~=c.destination then return false,'friend_must_remain_driver'end
  if ticket and(c.driver.id~=ticket.driver_id or c.driver.unit~=ticket.driver_unit)then return false,'remote_driver_changed'end
 else
  local remote_count=0
  for _,a in ipairs(c.sample.avatars)do if not a.is_local then
   remote_count=remote_count+1
   if a.seat and a.seat.collection==o.vehicle.id then return false,'friend_must_remain_outside'end
  end end
  if remote_count~=1 then return false,'one_remote_avatar_required'end
  if source==0 then
   if not c.driver or not c.driver.is_local or c.driver.id~=s.avatar or c.driver.unit~=s.avatar_unit then return false,'local_driver_identity_changed'end
  elseif c.driver then return false,'driver_seat_must_remain_empty'end
 end
'''+s[b:]
s=s.replace('source=c.seat,target=assert(target),avatar_binding=c.native.identity}', 'source=c.seat,target=assert(target),avatar_binding=c.native.identity,driver_id=c.driver and c.driver.id,driver_unit=c.driver and c.driver.unit}')
host=(W/'seat_host_weapon_diagnostic/adapter.lua').read_text()
a=host.index(' function self:request(c,t)');b=host.index(' function self:execute',a)
s=s.replace(" function self:request()error('ownership_transfers_disabled_in_driver_experiment')end\n",host[a:b])
s=s.replace("  assert(t.local_authority and t.original==t.selfpeer,'already_local_ticket_required')\n",'')
a=host.index(' function self:return_owned(c,t)');b=host.index(' return self',a)
s=s.replace(" function self:return_owned()error('ownership_transfers_disabled_in_driver_experiment')end\n",host[a:b]);p.write_text(s)
# Entry becomes a standalone diagnostic gameplay package: a single input owner.
p=R/'entry.lua';s=p.read_text().replace('owner_reader,trigger_keys,conflict','owner_reader,dispatcher,resolved_profile')
s=s.replace(' local text;local base=', ' resolved_profile=p\n local text;local base=')
s=s.replace(" for _,map in pairs(keys)do for _,binding in pairs(map)do if binding==1316 then conflict=true end end end\n trigger_keys=input.new({probe={trigger=1316}},api)\n",'')
s=s.replace('key_issues=#issues,key_conflict=conflict or false,','key_issues=#issues,')
s=s.replace('host_or_guest_M102_driver; already_local_only; route_0_4_0_2_0_3_0; max_six_manual_operations','standalone_INI_M102_two_players; local_outside_or_borrowed_remote_driver; normal_routes_other_vehicles')
s=s.replace('end,{0,4,0,2,0,3,0})', 'end,nil,true)\n local normal_native=bind_native(api,game,p,nil,nil,nil,\'normal\')\n dispatcher=seat_dispatcher.new(api,keys,input,policy,snapshot,normal_native,probe,emit)')
a=s.index("  local gameplay=rawget(_G,'VehicleSeatSwitch')");b=s.index('  local ok,s=pcall(reader.capture,reader)',a)
s=s[:a]+s[b:]
s=s.replace(" assert(not rawget(_G,'Hd2TankSeatSwitch')", " assert(not rawget(_G,'VehicleSeatSwitch'),'disable_gameplay_companion_for_standalone_test')\n assert(not rawget(_G,'Hd2TankSeatSwitch')")
s=s.replace(' local trigger=trigger_keys:poll(focused and not conflict and api.experiment_allowed())[1316]\n','')
s=s.replace(" if trigger and probe.phase=='finished'then emit({event='integrated_trigger_ignored',reason='six_operation_limit'})end\n",'')
a=s.index(" if conflict then status(");b=s.index('  if owner_reader.evidence then',a)
s=s[:a]+''' local good,s,reason=pcall(snapshot.capture,api,game,resolved_profile)
 if not good then reason=tostring(s);s=nil end
 dispatcher:update(s,reason)
 if now>=next_probe then
  next_probe=now+.1
'''+s[b:]
p.write_text(s)
# Build additions and standalone metadata are finalized separately.
p=R/'build.py';s=p.read_text()
s=s.replace("'test_entry','test_probe'", "'test_entry','test_dispatcher','test_probe','test_dynamic_probe','test_borrowed_adapter'")
s=s.replace("for name in ['profile','compat','module_hash','input']", "for name in ['profile','compat','module_hash','input','policy']")
s=s.replace("module('sync_adapter',R/'adapter.lua');", "module('bind_native',G/'native.lua');module('seat_dispatcher',R/'dispatcher.lua')\nmodule('sync_adapter',R/'adapter.lua');")
p.write_text(s)
print(R)
