local ffi=require('ffi')
ffi.cdef[[void *GetForegroundWindow(void);]]
local factory=assert(loadfile('work/seat_input_priority_test/input_gate.lua'))()
local helper=assert(loadfile('work/seat_input_priority_test/input_helper.lua'))()
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
local snapshot={predictions=function()return nil,nil end}
local eligible=function(_,_,_,_,target)return target~=0 end
local gate=factory(api,{log_directory=dir},helper,policy,snapshot,eligible,function(e)events[#events+1]=e end)
local original_load=ffi.load
local real=original_load('work/seat_input_priority_test/vss_input_priority.dll')
assert(real.VSSI_version()==1 and real.VSSI_record_size()==40 and real.VSSI_start(nil)==-2,'actual ABI and no-game refusal')
local mock={VSSI_version=function()return 1 end,VSSI_record_size=function()return 40 end,VSSI_health=function()return health end,
 VSSI_dropped=function()return drop end,VSSI_stop=function()stop=stop+1;return 0 end,
 VSSI_start=function(h)assert(h==ffi.cast('void *',123));return 0 end,
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
assert(gate.active and armed.source==1 and armed.expires==10200)
assert(armed.items[4]==1026 and armed.items[2]==1114 and not armed.items[0]and not armed.items[1])
suppressed[2]=true;assert(api.down(2)and not gate:control_down(2)and gate:control_down(162))
local function enqueue(gen,source,tick)
 queued[1]={sequence=1,tick=tick or 10000,generation=gen or armed.generation,binding=1026,source=source or 1,target=4,message=0x204}
end
enqueue();assert(gate:take(s)[1026]);assert(not next(gate:take(s)),'native edge consumed exactly once')
enqueue(armed.generation-1);assert(not next(gate:take(s)))
local physical_edge={[1026]=true};gate:filter(physical_edge,{});assert(not next(physical_edge),'discarded token cannot reappear through physical polling')
physical_edge={[1026]=true};gate:filter(physical_edge,{[1026]=true});assert(physical_edge[1026])
enqueue(nil,2);assert(not next(gate:take(s)))
enqueue(nil,nil,9700);assert(not next(gate:take(s)))
enqueue(nil,nil,10001);assert(not next(gate:take(s)))
enqueue();s.identity='new-car';gate:pulse(s,c,keys,true);assert(not next(gate:take(s)),'old vehicle press cannot move new vehicle')
focused=false;gate:pulse(s,c,keys,true);assert(not next(armed.items));enqueue();assert(not next(gate:take(s)));focused=true
gate:pulse(s,c,keys,false);assert(not next(armed.items))
gate:pulse(s,c,keys,true);drop=1;gate:pulse(s,c,keys,true);assert(gate.failed);assert(gate:control_down(2),'failed gate never masks physical controls')
gate:close();assert(stop==1 and not gate.active)
-- A matching existing file must be verified; tampering refuses before library load.
local path=dir..'/VSSInputPriority-'..helper.sha256..'.dll';local f=assert(io.open(path,'wb'));f:write('changed');f:close()
local bad=factory(api,{log_directory=dir},helper,policy,snapshot,eligible,function()end)
local ok,err=pcall(bad.pulse,bad,s,c,keys,true);assert(not ok and tostring(err):find('input_helper_file_mismatch'))
ffi.load=original_load
print('PASS real input DLL ABI/outside-game refusal and gate: extraction/tamper, exact scope, physical vs consumed controls, single edge, identity/generation/expiry/focus checks, failure/close')
