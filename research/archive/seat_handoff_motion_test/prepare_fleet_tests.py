from pathlib import Path
import json
R=Path(__file__).resolve().parent;W=R.parent
source=(R/'test_sender.lua').read_text().split('local refused=',1)[0]
source=source.replace("local peer=ffi.new('uint64_t[1]');", "local function raw(v)return ffi.string(ffi.new('uint64_t[1]',v),8)end\nlocal allowed={}\nlocal peer=ffi.new('uint64_t[1]');")
source=source.replace('assert(dest==peer[0]and', "assert(allowed[raw(dest)]and")
source=source.replace("calls[#calls+1]='snapshot'", "calls[#calls+1]='snapshot:'..raw(dest)").replace("calls[#calls+1]='transition'", "calls[#calls+1]='transition:'..raw(dest);if drop_after_transition then mem[0x20000+0x162d8]=dword(2)end")
source=source.replace('local peer=','local drop_after_transition=false\nlocal peer=',1)
source+=r'''
local others={destination,'\1\2\3\4\5\6\7\128','\16\15\14\13\12\11\10\255'}
local function setup(n)
 calls={};allowed={};o.peer_count=n;o.members={[selfpeer]=true};local raw=selfpeer
 for i=1,n-1 do o.members[others[i]]=true;allowed[others[i]]=true;raw=raw..others[i]end
 mem[0x20000+0x162d8]=dword(n);mem[0x20000+0x162e0]=raw
 local peers={};for i=1,n-1 do peers[i]=others[i]end;return peers
end
local count=0
for n=2,4 do
 local peers=setup(n);local operation=send:prepare_all(o,peers,s,1);assert(#calls==0);operation(function()end)
 assert(#calls==(n-1)*4)
 for i=1,n-1 do local at=(i-1)*4
  assert(calls[at+1]=='snapshot:'..peers[i]and calls[at+2]=='transition:'..peers[i]and
    calls[at+3]=='weapon_pair'and calls[at+4]=='animation')
 end
 assert(not pcall(operation,function()end)and #calls==(n-1)*4);count=count+1
end
for _,change in ipairs({
 function()mem[0x20000+0x162d8]=dword(2)end,
 function()mem[0x20000+0x162e0]=selfpeer..others[2]..others[1]end,
 function()mem[0x40020]='changed!'end,
 function()binding_ok=false end,
})do
 local peers=setup(3);local operation=send:prepare_all(o,peers,s,1);change()
 assert(not pcall(operation,function()end)and #calls==0)
 mem[0x40020]=selfpeer;binding_ok=true;count=count+1
end
for _,peers in ipairs({{others[1],others[1]},{others[1],selfpeer},{others[1],'foreign!'},{others[1]}})do
 setup(3);assert(not pcall(send.prepare_all,send,o,peers,s,1)and #calls==0);count=count+1
end
local peers=setup(3);local operation=send:prepare_all(o,peers,s,1);drop_after_transition=true
assert(not pcall(operation,function()end)and #calls==4)
assert(not pcall(operation,function()end)and #calls==4,'Never repeat a partially delivered fanout');count=count+1
callbacks.snap:free();callbacks.transition:free()
print('PASS '..count..' actual FFI all-peer sender cases: exact high-bit 64-bit peers, per-peer seat/weapon/pose order, no self/broadcast/duplicates, membership/identity/schema guard and no retransmission after partial delivery; no wire acknowledgement claimed')
'''
# Lua needs byte escapes, not two literal backslashes from a Python raw string.
source=source.replace('\\\\','\\')
(R/'test_fleet_sender.lua').write_text(source)

# Actual authority reader and send preflight over immutable code captures.
# Synthetic session rows deliberately put the chassis owner in another car.
request_base=(R/'test_room_observe.lua').read_text().split('local cases=0',1)[0]
request_cases=r'''
local function request_setup(n,host,name)
 room_setup(n,host)
 local t=p.tables[name];vehicle.name=name;vehicle.transition_type=t.transition;vehicle.seat_count=#t.roles
 local own=s.avatars[1];own.seat.collection=vehicle.id;own.seat.current=1;own.seat.reserved=1
 own.seat.role=t.roles[2];own.seat.transition_type=t.transition;own.vehicle_input=true
 local original=s.avatars[2];original.vehicle_input=false
 local options={mode='fleet_owner',vehicle_name=name,source=1,target=#t.roles-1,
  avatar=own.id,avatar_unit=own.unit,owner_avatar={id=original.id,unit=original.unit,network_unit=original.network_unit}}
 local checked=0;options.validate=function()checked=checked+1 end
 return observer:capture(s,vehicle,'all'),options,function()return checked end
end
local cases=0
for n=2,4 do for host=1,n do for _,name in ipairs({'m102','m103','m104','bastion','maelstrom'})do
 local o,options,checked=request_setup(n,host,name);local before=#sends;local marked=false
 observer:send(o,FRIEND,LOCAL,function()marked=true end,options)
 local sent=sends[#sends]
 assert(marked and checked()==1 and #sends==before+1 and sent[1]==FRIEND and sent[2]==vehicle.network_unit and sent[3]==LOCAL)
 cases=cases+1
end end end
for _,change in ipairs({
 function(o)s.peer_count=2 end,function(o)s.local_count=2 end,function(o)s.player_count=5 end,
 function(o)o.source=0 end,function(o)o.target=0.5 end,function(o)o.vehicle_name='m103'end,
 function(o)o.owner_avatar.unit=99 end,function(o)o.owner_avatar.network_unit=99 end,
 function(o)s.avatars[2].owned_local=true end,function(o)s.avatars[1].vehicle_input=false end,
 function(o)s.avatars[1].seat.transitioning=1 end,function(o)s.avatars[1].seat.role=2 end,
 function(o)put(S+0x162e0,LOCAL..FRIEND..PEERS[3]..PEERS[3])end,
 function(o)put(E+0x130,LOCAL);put(S+0xb3a8,LOCAL)end,
 function(o)put(BUSY+0x201c,'\1')end,
 function(o)o.validate=function()error('roster/vacancy changed before invocation')end end,
})do
 local o,options=request_setup(4,4,'m102');local before=#sends;local marked=false;change(options)
 assert(not pcall(observer.send,observer,o,FRIEND,LOCAL,function()marked=true end,options)and not marked and #sends==before)
 cases=cases+1
end
print('PASS '..cases..' actual authority reader/send fleet preflights: 2/3/4 peers, all hosts/five models, original owner driving another car with remote input false, full uint64 peers; invalid counts/units/host/vacancy/ownership refuse before invocation. Engine sender mocked, no wire acknowledgement.')
'''
(R/'test_fleet_request.lua').write_text(request_base+request_cases)
(R/'test_fleet_fall.lua').write_text((R/'test_tank_pose.lua').read_text()+'\n'+(R/'fleet_fall_cases.lua').read_text())
def lua(x):
 if x is None:return 'nil'
 if isinstance(x,bool):return str(x).lower()
 if isinstance(x,(int,float)):return repr(x)
 if isinstance(x,str):return json.dumps(x,ensure_ascii=True)
 if isinstance(x,list):return '{'+','.join(lua(v)for v in x)+'}'
 return '{'+','.join('['+lua(k)+']='+lua(v)for k,v in x.items())+'}'
rows=[];seen=set()
capture=W/'seat_multi_peer_research/capture-20261002-0190'
for path in sorted(capture.glob('VehicleSeatIntegrated-*.log')):
 for line in path.read_bytes().decode('utf-8-sig',errors='surrogateescape').splitlines():
  if 'room_ownership_sample'not in line:continue
  r=json.loads(line)
  if r['players']<3 or not r['counts_agree']:continue
  own=next((a for a in r['avatars']if a['is_local']),None);v=r['vehicle']
  if not own or not own['vehicle_input']or own['seat']['collection']!=v['id']or not own['seat']['role']in (1,2,3):continue
  seat=own['seat']
  if seat['target']!=-1 or seat['action']!=-1 or seat['transitioning']or seat['queued_exit']or seat['current']!=seat['reserved']:continue
  identity=(path.name,r['coordinator'],v['name'],r['ownership']['owner'],seat['current'],
   tuple((a['owner'],a['seat']['collection'],a['seat']['current'])for a in r['avatars']if not a['is_local']))
  if identity in seen:continue
  seen.add(identity)
  rows.append({k:r[k]for k in ['players','local_peer','coordinator','ownership','peers','avatars','vehicle']})
assert rows,'No actual three-player own-car frames'
(R/'fleet-recorded-fixture.lua').write_text('return '+lua(rows)+'\n')
(R/'fleet-recorded-fixture.json').write_text(json.dumps({'source':'frozen 0.19.0 host and guest captures; own settled car frames, distinct contexts only','three_player_frames':len(rows),'rows':rows},ensure_ascii=True,indent=2))
print('Prepared real FFI fanout guards and',len(rows),'actual settled three-player car contexts')
