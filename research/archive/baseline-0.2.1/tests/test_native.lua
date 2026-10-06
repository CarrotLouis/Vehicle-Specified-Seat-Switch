local profile=assert(loadfile('work/seat_switch/src/profile.lua'))()
local calls,busy={},false
local game=0x10000000;local registry={}
local api={pointer=function(b)if b=='systems' then return 0x20000000 elseif b=='engine' then return 0x21000000 end end}
for name,p in pairs(profile.functions) do
 registry[game+p.rva]={name=name,bytes=p.bytes}
end
function api.read(a,n)
 if registry[a] then return registry[a].bytes end
 if a==game+profile.globals.entities then return 'systems' end
 if a==0x20000008 then return 'engine' end
end
api.ffi={cast=function(t,a)
 local name=assert(registry[a]).name
 return function(...)
  if name=='ownership_busy' then return busy end
  calls[#calls+1]={name,...}
 end
end}
local pose_ok=true
local function pose_factory()return {
 check=function(s)assert(pose_ok,'Animation identity changed');return true end,
 apply=function(s,target)calls[#calls+1]={'pose',s.avatar_unit,target};return 'pose_applied' end} end
local n=assert(loadfile('work/seat_switch/src/native.lua'))()(api,game,profile,pose_factory)
local s={owned=true,active=false,player_count=1,peer_count=1,collection_unit=20,
 profile=profile.tables.bastion,node=0,occupied={[0]=true,[1]=false,[2]=false,[3]=false},
 collections=0x30000000,collection_index=0,seaters=0x31000000,seater_index=0,avatar=7,collection=9,
 avatar_address=0x32000000,avatar_unit=21,vehicle='bastion',transition=43}
assert(n.available(s));busy=true;assert(select(2,n.available(s))=='vehicle_authority_changing');busy=false
s.player_count=2;assert(not n.available(s));assert(not pcall(n.direct,s,1) and #calls==0);s.player_count=1
s.peer_count=2;assert(not n.available(s));assert(not pcall(n.direct,s,1) and #calls==0);s.peer_count=1
s.owned=false;assert(not n.available(s));assert(not pcall(n.direct,s,1) and #calls==0);s.owned=true
for _,occupied in ipairs({true,'unknown'}) do s.occupied[1]=occupied;assert(not pcall(n.direct,s,1) and #calls==0) end
s.occupied[1]=nil;assert(not pcall(n.direct,s,1) and #calls==0);s.occupied[1]=false
assert(not pcall(n.direct,s,0) and not pcall(n.direct,s,0.5) and #calls==0)
n.direct(s,1)
local expected={'reserve','clear_vehicle_weapon','clear_vehicle_weapon','restore_personal_weapon','refresh_weapon_context','release','set_role','restore_seated','pose','authority'}
assert(#calls==#expected);for i,name in ipairs(expected) do assert(calls[i][1]==name,name) end
assert(calls[2][2]==s.avatar_address and calls[2][3]==0 and calls[3][3]==1)
assert(calls[1][4]==1 and calls[6][4]==0 and calls[7][4]==2)
assert(calls[8][2]==s.seaters and calls[8][3]==nil and calls[8][4]==7 and calls[8][5]==9 and calls[8][6]==1 and calls[8][7]==false)
assert(calls[10][4]==1 and calls[10][5]==7 and n.last_detail:match('pose_applied'))
-- Cover both gunner types and every departure destination, not just one index.
for _,vehicle in ipairs({'m102','m104','maelstrom'}) do
 s.vehicle=vehicle;s.profile=profile.tables[vehicle];s.transition=s.profile.transition
 for source=0,#s.profile.roles-1 do for target=0,#s.profile.roles-1 do if source~=target then
  s.node=source;s.occupied={};for i=0,#s.profile.roles-1 do s.occupied[i]=i==source end
  calls={};n.direct(s,target)
  local prep,rotation,smoke=false,false,false
  for i,c in ipairs(calls) do
   if c[1]=='seat_action' then
    prep=true;assert(c[2]==s.transition and c[3]==s.avatar and c[4]==(vehicle=='m102' and 4 or 2) and c[5]==target)
    assert(calls[i+1][1]=='restore_seated')
   elseif c[1]=='avatar_rotation' then rotation=true;assert(c[3]==s.avatar and c[4]==true)
   elseif c[1]=='remove_avatar_flag' then smoke=true;assert(c[3]==44) end
  end
  assert(prep==((vehicle=='m102' or vehicle=='m104') and s.profile.roles[target+1]==2))
  assert(rotation==((vehicle=='m102' or vehicle=='m104') and s.profile.roles[source+1]==2))
  assert(smoke==(vehicle=='maelstrom'))
 end end end
end
calls={};pose_ok=false;s.node=0;s.occupied[1]=false
assert(not n.available(s));assert(not pcall(n.direct,s,1) and #calls==0,'Pose mismatch must fail before reserving or clearing weapons')
pose_ok=true
local original=api.read;api.read=function(a,n)if a==game+profile.functions.release.rva then return string.rep('\0',n) end;return original(a,n) end
assert(not pcall(assert(loadfile('work/seat_switch/src/native.lua'))(),api,game,profile),'A changed native prologue must prevent binding')
print('PASS: native guards, both weapon channels, M102/M104 gunner preparation and departures, Maelstrom smoke cleanup, pose-before-authority ordering. Native calls are mocked.')
