local ffi=require('ffi')
ffi.cdef[[void *GetForegroundWindow(void);]]
local factory=assert(loadfile('work/seat_outside_owner_test/input_gate.lua'))()
local helper=assert(loadfile('work/seat_outside_owner_test/input_helper.lua'))()
local policy=assert(loadfile('work/seat_switch/src/policy.lua'))()
local dir=assert(os.getenv('VSS_INPUT_TEST_DIR'))
local now,focused=10,true
local physical={[2]=true,[162]=true}
local api={now=function()return now end,input_allowed=function()return focused end,down=function(k)return physical[k]end}
local s={identity='av-car',node=1,vehicle='m102',active=false,occupied={[0]=true,[1]=true,[2]=false,[3]=false,[4]=false}}
local c={native=s,seat=1,owner={owner='friend',selfpeer='self'}}
local keys={m102={driver=88,front_passenger=2,rear_left=90+1024,rear_right=88+1024,gunner=2+1024}}
local events,queued,armed,suppressed={},{},{},{}
local health,drop,stop=0,0,0
local startcode,status,starts=1,1,0
local snapshot={predictions=function()return nil,nil end}
local eligible=function(_,_,_,_,target)return target~=0 end
local gate=factory(api,{log_directory=dir},helper,policy,snapshot,eligible,function(e)events[#events+1]=e end)
local original_load=ffi.load
local real=original_load('work/seat_outside_owner_test/vss_input_priority.dll')
assert(real.VSSI_version()==2 and real.VSSI_record_size()==40 and real.VSSI_start(nil)==-2,'actual ABI and no-game refusal')
local mock={VSSI_version=function()return 2 end,VSSI_record_size=function()return 40 end,VSSI_health=function()return health end,
 VSSI_dropped=function()return drop end,VSSI_stop=function()stop=stop+1;return 0 end,
 VSSI_start=function(h)assert(h==ffi.cast('void *',123));starts=starts+1;return startcode end,
 VSSI_status=function()return status end,
 VSSI_suppressed=function(k)return suppressed[k]and 1 or 0 end,
 VSSI_arm=function(items,n,source,until_,gen)
  armed={source=source,expires=until_,generation=gen,items={}}
  for i=0,n-1 do armed.items[tonumber(items[i].target)]=tonumber(items[i].binding)end
  return 0
 end,
 VSSI_drain=function(b,max)assert(max==256);local n=#queued
  for i,r in ipairs(queued)do for k,v in pairs(r)do b[i-1][k]=v end end;queued={};return n end}
ffi.load=function(name)if name=='user32'then return {GetForegroundWindow=function()return ffi.cast('void *',123)end}else return mock end end
gate:pulse(s,c,keys,true)
assert(gate.pending and not gate.active and starts==1 and not armed.source,'async startup is not a failure or armed')
gate:pulse(s,c,keys,true);assert(gate.pending and starts==1,'pending startup never installs twice')
status=0;gate:pulse(s,c,keys,true)
assert(gate.active and armed.source==1 and armed.expires==10200)
assert(armed.items[4]==1026 and armed.items[2]==1114 and not armed.items[0]and not armed.items[1])
suppressed[2]=true;assert(api.down(2)and not gate:control_down(2)and gate:control_down(162))
local function enqueue(gen,source,tick)
 queued[1]={sequence=1,tick=tick or 10000,generation=gen or armed.generation,binding=1026,source=source or 1,target=4,message=0x204}
end
enqueue();local pressed,records,discarded=gate:take(s)
assert(pressed[1026]and records[1026].count==1 and records[1026].sequence==1 and not next(discarded))
assert(not next((gate:take(s))),'native edge consumed exactly once')
enqueue(armed.generation-1);pressed,records,discarded=gate:take(s)
assert(not next(pressed)and not next(records)and discarded[1026])
local physical_edge={[1026]=true};gate:filter(physical_edge,{});assert(not next(physical_edge),'discarded token cannot reappear through physical polling')
physical_edge={[1026]=true};gate:filter(physical_edge,{[1026]=true});assert(physical_edge[1026])
enqueue(nil,2);assert(not next((gate:take(s))))
enqueue(nil,nil,9700);assert(not next((gate:take(s))))
enqueue(nil,nil,10001);assert(not next((gate:take(s))))
enqueue();s.identity='new-car';gate:pulse(s,c,keys,true);assert(not next((gate:take(s))),'old vehicle press cannot move new vehicle')
focused=false;gate:pulse(s,c,keys,true);assert(not next(armed.items));enqueue();assert(not next((gate:take(s))));focused=true
gate:pulse(s,c,keys,false);assert(not next(armed.items))
gate:pulse(s,c,keys,true);drop=1;gate:pulse(s,c,keys,true);assert(gate.failed);assert(gate:control_down(2),'failed gate never masks physical controls')
gate:close();assert(stop==2 and not gate.active)
gate:close();gate:pulse(s,c,keys,true);assert(stop==2 and starts==1,'closed gate cannot reopen or stop twice')
drop=0
-- Closing before the GUI responds must cancel a pending attachment.
local function newgate()return factory(api,{log_directory=dir},helper,policy,snapshot,eligible,function(e)events[#events+1]=e end)end
status=1;local waiting=newgate();waiting:pulse(s,c,keys,true);assert(waiting.pending and not waiting.active)
local n=stop;waiting:close();assert(stop==n+1 and waiting.closed and not waiting.pending)
waiting:pulse(s,c,keys,true);assert(starts==2,'closed pending startup cannot retry')
local timeout=newgate();timeout:pulse(s,c,keys,true);n=stop
status=-11;timeout:pulse(s,c,keys,true)
assert(timeout.failed and not timeout.pending and not timeout.active and stop==n+1)
timeout:pulse(s,c,keys,true);assert(starts==3,'timed out startup cannot silently fall back/retry')
startcode=-9;local denied=newgate();denied:pulse(s,c,keys,true);assert(denied.failed and not denied.active)
assert(events[#events-2].event=='input_priority_install_failure' and events[#events-2].code==-9)
-- A matching existing file must be verified; tampering refuses before library load.
local path=dir..'/VSSInputPriority-'..helper.sha256..'.dll';local f=assert(io.open(path,'wb'));f:write('changed');f:close()
local bad=factory(api,{log_directory=dir},helper,policy,snapshot,eligible,function()end)
local ok,err=pcall(bad.pulse,bad,s,c,keys,true);assert(not ok and tostring(err):find('input_helper_file_mismatch'))
ffi.load=original_load
print('PASS input DLL ABI2/outside-game refusal and gate: async pending/ready/cancel/timeout/refusal; no duplicate install/reopen; extraction/tamper, scope, physical masking, generation/expiry/focus and failure cleanup')
