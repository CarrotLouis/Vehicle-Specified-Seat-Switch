local ffi=require('ffi')
local factory=assert(loadfile('work/seat_physics_motion_test/room_watch.lua'))()
local encode=assert(loadfile('work/seat_network_diagnostic/recorder.lua'))().encode
local now,reads=0,0;local rows={};local reader={peers={a='P1',b='P2',c='P3',d='P4'}}
local owner={send=function()error('Read-only observer must never send')end,evidence={stage='test'}}
local sample={state='mission',mission_value=1,local_count=1,player_count=4,peer_count=4,
 peers={'P1','P2','P3','P4'},avatars={},vehicles={{id=10,name='m102'},{id=20,name='bastion'}}}
for i,key in ipairs({'a','b','c','d'})do sample.avatars[i]={id=i,unit=i+10,network_unit=i+20,
 is_local=i==1,owned_local=i==1,seat={collection=i%2==0 and 20 or 10,current=i==1 and 1 or 0}} end
function owner:capture(s,v,need)
 assert(s==sample and need=='all');reads=reads+1
 if self.fail then error('bounded mock failure')end
 local o={members={a=true,b=true,c=true,d=true},selfpeer='a',coordinator='d',owner=v.id==10 and 'b'or'c',peer_count=4,
  avatars={},vehicle=v,context='session/'..string.char(0x80,0x99,0xff,0)..'/mission'}
 for i,key in ipairs({'a','b','c','d'})do o.avatars[i]={owner=key}end
 if self.foreign_avatar then o.avatars[4].owner='x'end
 return o
end
function owner:summary(o)return {owner=reader.peers[o.owner],coordinator=reader.peers[o.coordinator]}end
local api={now=function()return now end,replace=function()error('No writes')end}
local watch=factory(api,reader,owner,function(e)rows[#rows+1]=e end,encode)
local function update(dt,pending)now=now+(dt or .5);watch:update(sample,pending)end
update(.1)
assert(rows[1].event=='room_roster' and rows[2].event=='room_ownership_sample' and rows[2].vehicle.id==10)
assert(rows[2].coordinator=='P4' and rows[2].ownership.owner=='P2' and rows[2].avatar_owners_read==4 and rows[2].counts_agree)
assert(rows[2].session_context==nil and rows[2].session_context_hex:find('8099ff00',1,true))
local encoded=encode(rows[2]);assert(not encoded:find('[\128-\255]'),'Binary epoch must be logged as ASCII hex, not invalid UTF-8')
update(.01);assert(reads==1)
update(.5);assert(rows[#rows].vehicle.id==20 and rows[#rows].ownership.owner=='P3')
local before=reads;update(1,true);assert(reads==before)
owner.foreign_avatar=true;update();assert(rows[#rows].avatars[4].owner_in_session==false)
owner.fail=true;update();assert(rows[#rows].event=='room_ownership_gap');local n=#rows
-- Different collections each get their own bounded gap; no global input failure.
update();assert(#rows==n+1);owner.fail=false;owner.foreign_avatar=false
sample.player_count=3;sample.peer_count=3;sample.peers={'P1','P2','P3'}
update();assert(rows[#rows-1].event=='room_roster' and not rows[#rows].counts_agree)
sample.state='not_in_mission';before=reads;update();assert(reads==before and rows[#rows].event=='room_roster')
watch:update(nil,false);assert(reads==before)
print('PASS read-only room watch: four independently mapped peers, two vehicle owners different from coordinator, roster/join/count mismatch, rotation/throttle/pending skip/gap isolation; no send or write')
