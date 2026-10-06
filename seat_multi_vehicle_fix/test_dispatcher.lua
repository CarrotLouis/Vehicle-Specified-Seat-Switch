local factory=assert(loadfile('work/seat_multi_vehicle_fix/dispatcher.lua'))()
local config=assert(loadfile('work/seat_switch/src/config.lua'))()
local input=assert(loadfile('work/seat_switch/src/input.lua'))()
local policy=assert(loadfile('work/seat_switch/src/policy.lua'))()
local now,down,focus,enabled=0,{},true,true
local api={now=function()return now end,down=function(k)return down[k]end,focused=function()return focus end,input_allowed=function()return focus end,experiment_allowed=function()return enabled end}
local keys=config.parse('[m102]\ndriver=CTRL+1\nfront_passenger=F2\nrear_left=SHIFT+Q\nrear_right=CTRL+SHIFT+MOUSE4\ngunner=F5')
local calls,events={},{}
local probe={phase='waiting',pending=false,ready_at=0,step=function(self,t)if type(t)=='number'then calls[#calls+1]='cross'..t;self.pending=true end end}
local current=true
local snapshot={current=function()return current end,predictions=function(s)
 if s.node==0 then return 1,nil elseif s.node==1 then return 0,nil elseif s.node==2 then return 3,nil elseif s.node==3 then return 2,nil end
end}
local s={vehicle='m102',identity='car',node=0,player_count=2,peer_count=2,occupied={[0]=false,[1]=false,[2]=false,[3]=false,[4]=false}}
local native={next=function()calls[#calls+1]='native'end}
local d=factory.new(api,keys,input,policy,snapshot,native,probe,function(e)events[#events+1]=e end)
local function tick(k,dt)down={};for _,v in ipairs(k or{})do down[v]=true end;now=now+(dt or .1);return d:update(s)end
tick({113});assert(calls[1]=='native'and d.pending)
tick({116});assert(#calls==1 and not d.queued,'native pending must discard cross input')
s.node=1;tick();tick({116},.5);assert(d.queued and #calls==1);tick({116});assert(#calls==1,'must await release')
tick();assert(calls[2]=='cross4'and probe.pending)
tick({113});tick({162,49});assert(#calls==2,'cross pending must suppress all native/second cross keys')
probe.pending=false;s.node=4;tick({162,49});assert(#calls==2,'held key must not reappear after completion')
tick();tick({162,49});tick();assert(calls[3]=='cross0')
probe.pending=false;s.node=1;tick();tick({113,116},1);assert(not d.queued and #calls==3 and events[#events].reason=='multiple_seat_keys')
tick();tick({160,81},1);assert(d.queued);tick({160,81});assert(#calls==3);tick();assert(calls[4]=='cross2')
probe.pending=false;tick();tick({162,160,5},1);assert(d.queued);tick({162,160,5});assert(#calls==4);tick();assert(calls[5]=='cross3')
probe.pending=false;tick();tick({116},1);s.occupied[4]=true;tick();assert(not d.queued and #calls==5)
s.occupied[4]=false;tick({116},1);focus=false;tick();assert(not d.queued and #calls==5)
tick({116});focus=true;tick({116});assert(not d.queued,'focus gain must not trigger held key');tick()
tick({116},1);tick({116},9);assert(not d.queued and #calls==5,'long hold expires')
tick();current=false;tick({116},1);assert(not d.queued);current=true
tick();tick({116},1);s.identity='new';tick();assert(not d.queued and #calls==5)
tick({116},1);enabled=false;tick();assert(not d.queued and #calls==5);enabled=true
probe.phase='stopped';tick();tick({113},1);assert(#calls==5,'unsafe stopped state must block normal input too')
-- M103 is now supported with two players (full route covered by test_multi_vehicle).
-- Its three-player path must still refuse before queueing an experiment.
probe.phase='waiting';s.vehicle='m103';s.node=1;s.player_count=3;tick();tick({114},1);assert(#calls==5 and not d.queued)
s.vehicle='m102';s.player_count=3;tick();tick({116},1);assert(#calls==5 and not d.queued)
s.player_count=2;s.active=true;tick();tick({116},1);assert(#calls==5 and d.queued)
tick();assert(#calls==5 and d.queued,'aiming must lower before switching')
s.active=false;probe.ready_at=now+3;tick();assert(#calls==5 and d.queued)
tick({},3.1);assert(calls[6]=='cross4'and not d.queued,'one press survives weapon lowering and settle')
print('PASS real INI/input dispatcher: native/cross arbitration, modifier and mouse bindings, release gate, no held/busy/focus replay, simultaneous keys, scope/occupancy/identity/expiry guards')
