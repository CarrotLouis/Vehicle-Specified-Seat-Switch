from pathlib import Path
R=Path(__file__).resolve().parent
for p in R.iterdir():
 if p.is_file()and p.suffix in ['.lua','.py','.md','.txt','.json']and p.name!='clone_update.py':
  try:s=p.read_text(encoding='utf-8')
  except UnicodeDecodeError:continue
  p.write_text(s.replace('seat_multi_peer_diagnostic','seat_motion_loan_test'),encoding='utf-8')
def edit(name,old,new):
 p=R/name;s=p.read_text();assert old in s,(name,old[:80]);p.write_text(s.replace(old,new),encoding='utf-8')
edit('adapter.lua'," local s,o=c.native,c.owner\n if not s", " if M.fleet and M.fleet.use(c,ticket)then return M.fleet.eligible(c,source,owned,ticket,target,confirmation,M.layout)end\n local s,o=c.native,c.owner\n if not s")
edit('adapter.lua',"local need=sample.player_count==2 and #sample.avatars==2 and 'all'or true", "local need=sample.player_count>=2 and sample.player_count<=4 and #sample.avatars==sample.player_count and 'all'or true")
edit('adapter.lua',"if n~=1 then dest=nil end", "if n~=1 then\n   local peers={};for peer in pairs(o.members)do if peer~=o.selfpeer then peers[#peers+1]=peer end end;table.sort(peers)\n   dest=o.owner~=o.selfpeer and o.owner or peers[1]\n  end")
edit('adapter.lua',"  local non_driver_owner=not t.local_authority and not c.driver", "  if M.fleet and M.fleet.use(c)then return M.fleet.ticket(c,target,t,M.layout)end\n  local non_driver_owner=not t.local_authority and not c.driver")
edit('adapter.lua',"  if t.seated_owner or t.outside_owner then options=", "  if t.fleet then options={mode='fleet_owner',source=t.source,target=t.target,vehicle_name=fresh.native.vehicle,\n   avatar=fresh.native.avatar,avatar_unit=fresh.native.avatar_unit,owner_avatar=t.owner_avatar,\n   validate=function()quiet(t);local last=assert(self:capture(t));local valid,reason=M.eligible(last,t.source,false,t);assert(valid,reason);\n    assert(last.owner.serial==fresh.owner.serial and snapshot.current(api,last.native),'fleet_request_state_changed')end}\n  elseif t.seated_owner or t.outside_owner then options=")
edit('adapter.lua',"  local send=sender:prepare(fresh.owner,t.destination,fresh.native,t.target)", "  local send=t.fleet and sender:prepare_all(fresh.owner,t.notifications,fresh.native,t.target)or sender:prepare(fresh.owner,t.destination,fresh.native,t.target)")
edit('entry.lua',"version='0.19.0'", "version='0.21.0'")
edit('entry.lua'," local adapter=sync_adapter.new", " sync_adapter.fleet=fleet_policy\n local adapter=sync_adapter.new")
for name in ['entry.lua','transaction.lua','driver.lua','tank_driver.lua']:
 edit(name,'s.player_count==2 and s.peer_count==2', 's.player_count>=2 and s.player_count<=4 and s.peer_count==s.player_count')
edit('dispatcher.lua',"or s.player_count~=2 or s.peer_count~=2 then event('cross_scope_unavailable')", "or s.player_count<2 or s.player_count>4 or s.peer_count~=s.player_count then event('cross_scope_unavailable')")
edit('room_watch.lua','session_context=o.context,', "session_context_hex=(o.context:gsub('.',function(ch)return string.format('%02x',ch:byte())end)),")
edit('build.py',"RELEASE='0.19.0'", "RELEASE='0.21.0'")
edit('build.py',"module('sync_adapter',R/'adapter.lua');", "module('fleet_policy',R/'fleet_policy.lua');module('sync_adapter',R/'adapter.lua');")
edit('build.py',"Vehicle-Seat-Weapon-Sync-Diagnostic-0.19.0.zip", "Vehicle-Seat-Weapon-Sync-Diagnostic-0.21.0.zip")
edit('transport.lua','0.19.0','0.21.0')
print('PASS isolated fleet clone updated; previous source/archive unchanged')
