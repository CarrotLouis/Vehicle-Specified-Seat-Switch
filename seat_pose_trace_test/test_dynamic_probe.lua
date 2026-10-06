local factory=assert(loadfile('work/seat_pose_trace_test/probe.lua'))()
local c={identity='v',seat=0,native={},owner={owner='self',selfpeer='self',vehicle={owned_local=true}},summary='s'}
local calls,events={},{}
local a={capture=function()return c end,context=function(_,c,t)return c.identity==t.identity end}
function a:eligible(c,source,owned,t,target)return c.seat==source and not self.block,'blocked'end
function a:ticket(c,target)return {identity=c.identity,source=c.seat,target=target,selfpeer='self',original=c.owner.owner,local_authority=c.owner.owner=='self'}end
function a:execute(c,t)calls[#calls+1]='switch';c.seat=t.target;t.mutation_started=true;t.sync_returned=true end
function a:request(c,t)calls[#calls+1]='request';t.request_invoked=true end
function a:return_owned(c,t)calls[#calls+1]='return';t.return_invoked=true end
local p=factory.new(a,function(e)events[#events+1]=e end,function()end,nil,true)
local function operation(target,time,borrowed)
 p:step(nil,time,true);p:step(target,time+3.1,true);assert(p.pending)
 if borrowed then c.owner.owner='self';c.owner.vehicle.owned_local=true end
 p:step(nil,time+3.2,true);p:step(nil,time+3.3,true)
 if borrowed then c.owner.owner='friend';c.owner.vehicle.owned_local=false;p:step(nil,time+3.4,true)end
 p:step(nil,time+4,true);assert(not p.pending and c.seat==target)
end
for i,t in ipairs({4,2,1,3,0,4,0,2})do operation(t,i*25,false)end
assert(#calls==8 and p.count==8 and p.phase~='finished','no old six-operation ceiling')
-- A fresh vehicle between completed requests is valid, pending identity changes are not.
c.identity='v2';c.seat=1;c.owner.owner='friend';c.owner.vehicle.owned_local=false
operation(4,250,true);assert(table.concat(calls,','):sub(-21)=='request,switch,return')
p:step(nil,280,true);a.block=true;p:step(2,284,true);assert(not p.pending)
a.block=false;p:step(0,285,true);assert(p.pending,'target zero is a real request')
c.identity='v3';p:step(nil,286,true);assert(p.phase=='stopped')
print('PASS arbitrary target and driver0, >six operations, local and borrowed cleanup, new vehicle after completion, refusal and pending identity guard')
