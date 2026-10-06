local input=assert(loadfile('work/seat_switch/src/input.lua'))()
local config=assert(loadfile('work/seat_switch/src/config.lua'))()
local policy=assert(loadfile('work/seat_switch/src/policy.lua'))()
local rows=assert(loadfile('work/seat_outside_owner_test/lean_replay.lua'))()
local function fixture(path)
 local now,down,focused=0,{},true
 local api={now=function()return now end,down=function(k)return down[k]end,focused=function()return focused end,input_allowed=function()return focused end}
 local keys=config.parse('[m102]\ndriver=X\nfront_passenger=MOUSE2\nrear_left=CTRL+Z\nrear_right=CTRL+X\ngunner=CTRL+MOUSE2')
 local calls,events={},{}
 local p={phase='waiting',pending=false,ready_at=0,step=function(_,target)if type(target)=='number'then calls[#calls+1]=target end end}
 local snapshot={current=function()return true end,predictions=function()return nil end}
 local d=assert(loadfile(path))().new(api,keys,input,policy,snapshot,{},p,function(e)events[#events+1]=e end)
 local s={identity='ownavatar/newcar',vehicle='m102',node=3,player_count=2,peer_count=2,occupied={[0]=true,[1]=false,[2]=false,[3]=true,[4]=false}}
 local function tick(value,why,time,pressed,focus)
  if time then now=time else now=now+.1 end
  down=pressed or{};if focus~=nil then focused=focus end
  return d:update(value,why)
 end
 return d,s,p,calls,events,tick
end
for _,version in ipairs({'seat_configurable_network_test','seat_outside_owner_test'})do
 local d,s,p,calls,events,tick=fixture('work/'..version..'/dispatcher.lua')
 tick(s,nil,0,{[162]=true,[2]=true});assert(d.queued and #calls==0)
 p.ready_at=rows[#rows].t+3
 for i=2,#rows do local row=rows[i]
  if row.transitioning~=0 then tick(nil,'transition_in_progress',row.t)
  elseif row.action~=-1 or row.target~=-1 then tick(nil,'transition_pending',row.t)
  else s.active=row.active==1;tick(s,nil,row.t)end
  assert(#calls==0,'must not request authority using a transitional/unavailable snapshot')
 end
 s.active=false;p.ready_at=rows[#rows].t+3
 tick(s,nil,p.ready_at-.1);assert(#calls==0)
 tick(s,nil,p.ready_at+.1)
 if version=='seat_outside_owner_test'then assert(#calls==1 and calls[1]==4 and not d.queued)
 else assert(#calls==0 and not d.queued,'old version must reproduce captured lost request')end
end
for _,fault in ipairs({'unreadable','timeout','vehicle','seat','occupied','new_key','focus','driver_gap'})do
 local d,s,p,calls,events,tick=fixture('work/seat_outside_owner_test/dispatcher.lua')
 if fault=='driver_gap'then s.node=0 end
 tick(s,nil,0,{[162]=true,[2]=true});assert(d.queued)
 if fault=='unreadable'then tick(nil,'Unreadable state',.2)
 elseif fault=='timeout'then tick(nil,'transition_in_progress',9)
 elseif fault=='vehicle'then tick(nil,'transition_in_progress',.2);s.identity='different';tick(s,nil,.8)
 elseif fault=='seat'then tick(nil,'transition_pending',.2);s.node=2;tick(s,nil,.8)
 elseif fault=='occupied'then tick(nil,'transition_pending',.2);s.occupied[4]=true;tick(s,nil,.8)
 elseif fault=='new_key'then tick(nil,'transition_in_progress',.2);tick(nil,'transition_in_progress',.3,{[2]=true})
 elseif fault=='focus'then tick(nil,'transition_in_progress',.2,nil,false)
 else tick(nil,'transition_in_progress',.2)end
 assert(not d.queued and #calls==0,fault..' must cancel without authority/mutation')
end
print('PASS captured lean17/21 replay: original loses CTRL+MOUSE2 request, fixed waits then dispatches once; missing snapshot never mutates; identity/source/occupancy/key/focus/expiry/read-error guards')
