-- Actual adapter capture and destination pinning; observation is simulated.
local M=assert(loadfile('work/seat_multiplayer_reservation_test/adapter.lua'))()
local function seat(node,role)return {collection=9,current=node,reserved=node,role=role,target=-1,action=-1,transitioning=0,queued_exit=0}end
local av={id=7,unit=701,network_unit=4107,is_local=true,seat=seat(2,3)}
local sample={state='mission',player_count=3,avatars={av,{id=8,seat={collection=55}}, {id=9,seat={collection=0}}}}
local o={context='room',owner='third!!!',selfpeer='selfpeer',members={selfpeer=true,['second!!']=true,['third!!!']=true},
 vehicle={id=9,unit=901,network_unit=4123,resource='actual',name='bastion'}}
local native={avatar=7,avatar_unit=701,collection=9,collection_unit=4123,resource='actual',node=2}
local need
local owner_reader={capture=function(_,s,tracked,request)need=request;return o end,summary=function()return {}end}
local adapter=M.new({},0,{}, {capture=function()return sample end},owner_reader,
 {capture=function()return native end},nil,nil,nil,function()end,function()return ''end)
local c=assert(adapter:capture());assert(need=='all'and c.destination=='third!!!'and c.avatar==av)
local ticket={destination=c.destination,peer_count=3,vehicle=o.vehicle}
o.owner='selfpeer';native.node=0;av.seat=seat(0,1)
c=assert(adapter:capture(ticket));assert(need=='all'and c.destination=='third!!!'and c.driver==av,'acquisition changed request peer to a different observer')
c=assert(adapter:capture());assert(c.destination=='second!!')
sample.player_count=4;c=assert(adapter:capture(ticket));assert(need==true and c.destination=='third!!!')
sample.player_count=3;ticket.cancel_reason='late';c=assert(adapter:capture(ticket));assert(need==true)
print('PASS real adapter asks for all current avatar owners; acquired foreign owner remains pinned when another observer sorts first; late/cancelled count drift does not invent owner records')
