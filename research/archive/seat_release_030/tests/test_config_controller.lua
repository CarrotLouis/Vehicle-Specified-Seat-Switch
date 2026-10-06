local config=assert(loadfile('work/seat_release_030/src/config.lua'))()
local policy=assert(loadfile('work/seat_release_030/src/policy.lua'))()
local keys,issues=config.parse(config.template());assert(#issues==0)
assert(keys.tanker.driver==112 and keys.tanker.gunner==113)
assert(keys.maelstrom.driver==112 and keys.maelstrom.gunner==113 and keys.maelstrom.passenger_left==114 and keys.maelstrom.passenger_right==115)
local customized=config.parse('[Maelstrom]\ndriver=F8\n');assert(customized.maelstrom.driver==119 and customized.bastion.driver==112)
local bad,warnings=config.parse('[M102]\ndriver=F2\nfront_passenger=F2\n[Tanker]\ngunner=NO_KEY\n')
assert(bad.m102.driver==112 and bad.m102.front_passenger==113 and #warnings==2)
assert(config.parse('[M104]\nflamer=NONE').m104.flamer==0)
local down,focus,time,calls={},true,1,{}
local api={down=function(k)return down[k] or false end,focused=function()return focus end,now=function()return time end}
local fresh=true
local snap={current=function()return fresh end,predictions=function(s)return s.predicted,s.previous end}
local native={available=function(s)return s.owned,'vehicle_owned_by_other_peer' end}
native.next=function()calls[#calls+1]='next' end
native.previous=function()calls[#calls+1]='previous' end
native.direct=function()calls[#calls+1]='direct' end
local input=assert(loadfile('work/seat_release_030/src/input.lua'))()
local C=assert(loadfile('work/seat_release_030/src/controller.lua'))()(policy,snap,input)
local function state(vehicle,node,target,owned)
 local occupied={};for i=0,#policy.seats[vehicle]-1 do occupied[i]=i==node end
 return {vehicle=vehicle,node=node,predicted=target,owned=owned,occupied=occupied,identity='one',seaters=1,avatar=7}
end
local c=C.new('normal',keys,api,native,function()end)
local s=state('m102',0,1,true);down[113]=true
assert(c:update(s)=='requested' and #calls==1)
c:update(s);assert(#calls==1,'Held key must not repeat')
s.node=1;c:update(s);assert(c.pending==nil)
down[113]=false;c:update(s);time=time+1
down[114]=true;s.predicted=2;s.occupied[2]=false
assert(c:update(s)=='normal_restriction' and #calls==1)
local e=C.new('enhanced',keys,api,native,function()end)
down[114]=false;e:update(s);down[114]=true;s.occupied[2]=true
assert(e:update(s)=='occupied' and #calls==1)
time=time+1;down[114]=false;e:update(s);down[114]=true;s.occupied[2]=false;s.predicted=nil;s.owned=false
assert(e:update(s)=='vehicle_owned_by_other_peer' and #calls==1)
time=time+1;down[114]=false;e:update(s);down[114]=true;s.owned=true;fresh=false
assert(e:update(s)=='snapshot_changed' and #calls==1)
time=time+1;fresh=true;down[114]=false;e:update(s);down[114]=true
assert(e:update(s)=='requested' and calls[2]=='direct')
e.pending=nil;focus=false;down[114]=false;e:update(s);down[114]=true;e:update(s);focus=true
e:update(s);assert(#calls==2,'Focus gain with held key must not act')
local menu=false;api.input_allowed=function()return not menu end
time=time+1;down[114]=false;e:update(s);menu=true;down[114]=true;e:update(s);menu=false;e:update(s)
assert(#calls==2,'Closing menu while holding key must not act')
native.prepare=function()calls[#calls+1]='lower' end
time=time+1;s.active=true;down[114]=false;e:update(s);down[114]=true
assert(e:update(s)=='lowering_personal_weapon' and calls[3]=='lower')
assert(e:update(nil,'transition_in_progress')=='lowering_personal_weapon')
s.active=false;s.occupied[2]=true
assert(e:update(s)=='occupied' and #calls==3,'Occupied seat after lowering must reject without switching')
s.occupied[2]=false;s.active=true;time=time+1;down[114]=false;e:update(s);down[114]=true
assert(e:update(s)=='lowering_personal_weapon' and calls[4]=='lower')
s.active=false;assert(e:update(s)=='requested' and calls[5]=='direct')
-- A configured numpad key reaches the same seat action; F2 is no longer used.
local numkeys=config.parse('[m102]\nfront_passenger=NUMPAD2\n')
local nc=C.new('normal',numkeys,api,native,function()end)
down={};time=time+1;s=state('m102',0,1,true);nc:update(s)
down[113]=true;nc:update(s);assert(#calls==5,'Old default must not trigger custom mapping')
down[113]=false;nc:update(s);down[98]=true
assert(nc:update(s)=='requested' and calls[6]=='next','Custom key must reach the configured seat')
local chordkeys=config.parse('[m102]\nfront_passenger=CTRL+1\n')
down={};time=time+1
local cc=C.new('normal',chordkeys,api,native,function()end);cc:update(s)
down[49]=true;cc:update(s);assert(#calls==6,'Primary alone must not trigger chord')
down={};cc:update(s);down[162]=true;cc:update(s);down[49]=true
assert(cc:update(s)=='requested' and calls[7]=='next','Ctrl+1 must reach the configured seat')
print('PASS: key configuration, occupancy rejection, normal restrictions, stale state, authority guard, key edges and focus. Native calls are mocked.')
