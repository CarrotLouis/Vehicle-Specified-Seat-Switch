local M=assert(loadfile('work/seat_sync_diagnostic/adapter.lua'))()
local function candidate()
 return {sample={player_count=2,avatars={}},native={vehicle='bastion',transition=43,player_count=2,peer_count=2,owned=true,active=false,node=0,avatar=7,collection=9,occupied={[0]=true,[1]=false}},
 owner={peer_count=2,selfpeer='self',coordinator='host',members={self=true,host=true},owner='self',busy=false,vehicle={owned_local=true},avatars={[7]={owner='self'}}},
 avatar={owned_local=true,vehicle_input=true},destination='host'}
end
assert(M.eligible(candidate()))
local cases={
 function(c)c.native.vehicle='maelstrom'end,function(c)c.native.transition=44 end,
 function(c)c.native.player_count=1 end,function(c)c.owner.peer_count=3 end,
 function(c)c.owner.coordinator='self'end,function(c)c.destination='outsider'end,
 function(c)c.owner.members.host=nil end,function(c)c.native.owned=false end,
 function(c)c.owner.vehicle.owned_local=false end,function(c)c.owner.owner='host'end,
 function(c)c.avatar.owned_local=false end,function(c)c.owner.avatars[7].owner='host'end,
 function(c)c.owner.busy=true end,function(c)c.native.active=true end,
 function(c)c.native.node=2 end,function(c)c.native.occupied[1]=true end,
 function(c)c.avatar.vehicle_input=false end,
 function(c)c.sample.avatars={{is_local=false,seat={collection=9}}}end}
for _,change in ipairs(cases)do local c=candidate();change(c);assert(not M.eligible(c))end
-- Execute ordering, fresh comparison and post-local failure never sending.
local calls,c,fresh,allow,current
local api={input_allowed=function()return true end,down=function()return false end}
local trace={active=true,health=function()end}
local snap={current=function()return current end}
local tx={prepare=function()calls[#calls+1]='prepare_local';return function()calls[#calls+1]='local';c.native.node=1;c.seat=1;c.native.occupied={[0]=false,[1]=true};if not allow then c.owner.owner='host'end end end}
local send={prepare=function()calls[#calls+1]='prepare_send';return function()calls[#calls+1]='send'end end}
local adapter=M.new(api,0,{},nil,{summary=function()return {}end},snap,tx,send,trace,function()end,function()return ''end)
local function reset()
 calls={};c=candidate();c.identity='one';c.seat=0;c.owner.serial=1;c.owner.record_word0=4;c.owner.record_word1=5;current=true;allow=true;fresh=0
 adapter.capture=function()fresh=fresh+1;return c end
end
reset();local before={identity=c.identity,seat=0,owner=c.owner};adapter:execute(before,1)
assert(table.concat(calls,',')=='prepare_local,prepare_send,local,send'and fresh==3)
reset();allow=false;assert(not pcall(adapter.execute,adapter,c,1));assert(calls[#calls]=='local')
reset();current=false;assert(not pcall(adapter.execute,adapter,c,1));assert(#calls==2)
reset();adapter.capture=function()local v=candidate();v.identity='changed';v.seat=0;return v end
assert(not pcall(adapter.execute,adapter,c,1));assert(#calls==0)
reset();api.down=function(k)return k==65 end;assert(not pcall(adapter.execute,adapter,c,1));assert(#calls==0)
print('PASS 18 scope refusals, prepare/mutate/send ordering, input/freshness/ownership failures')
