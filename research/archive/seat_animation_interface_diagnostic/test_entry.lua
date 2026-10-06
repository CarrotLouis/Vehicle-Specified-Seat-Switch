local source=assert(io.open('work/seat_animation_interface_diagnostic/entry.lua')):read('*a')
local recorder=assert(loadfile('work/seat_network_diagnostic/recorder.lua'))()
local now,mission,seated,multi,gap,inspections,previous_calls=0,false,false,false,false,0,0
local files={}
CowboyBingusModLoader={version=16,api=1,open_log=function(n)
 local f={text='',write=function(self,s)self.text=self.text..s;return self end,flush=function()return true end,close=function()end};files[n]=f;return f
end}
local function sample()
 if gap then error('synthetic_state_gap')end
 return {state=mission and 'mission'or'not_in_mission',player_count=multi and 2 or 1,peer_count=multi and 2 or 1,
 avatars=mission and {{id=7,is_local=true,seat={collection=9,current=seated and 1 or -1,transitioning=0}}}or{},vehicles={{name='m102',id=9}}}
end
local env=setmetatable({profile={},compat_spec={},
 platform=function()return {module=function()return 1 end,now=function()return now end,pid=function()return 1 end}end,
 pages=function(a)return a end,compat={start=function(_,_,_,_,mode)assert(mode=='diagnostic');return {step=function()return {}end}end},
 sampler={new=function()return {capture=sample}end},routing={new=function()return {}end},
 animation_inspect={new=function()return {capture=function()inspections=inspections+1;return {event='animation_interface',stable=true}end}end},
 recorder=recorder,os={date=function()return 'test'end},
 update=function()previous_calls=previous_calls+1;return nil,7,nil,'ok'end,shutdown=function()return 'closed'end}, {__index=_G})
local original=env.update
local function start()
 VehicleSeatNetworkDiagnostic=nil;env.update=original
 local f=assert(loadstring(source));setfenv(f,env);f()
end
local function tick(n)for i=1,n do now=now+.1;local a,b,c,d=env.update();assert(a==nil and b==7 and c==nil and d=='ok')end end
start();tick(400);assert(VehicleSeatNetworkDiagnostic.status:find('waiting_for_solo'),tostring(VehicleSeatNetworkDiagnostic.error)..' '..VehicleSeatNetworkDiagnostic.status)
mission=true;seated=true;multi=true;tick(150);assert(not VehicleSeatNetworkDiagnostic.status:find('complete'))
multi=false;tick(40);assert(VehicleSeatNetworkDiagnostic.status:find('sampling_M102'))
gap=true;tick(30);gap=false;tick(45);assert(not VehicleSeatNetworkDiagnostic.status:find('^complete'))
tick(80);assert(VehicleSeatNetworkDiagnostic.status:find('^complete'))
local before=inspections;tick(100);assert(inspections==before and previous_calls>0)
assert(env.shutdown()=='closed')
assert(files[VehicleSeatNetworkDiagnostic.filename].text:find('five_seated_samples'))
start();mission=false;seated=false;tick(180)
files[VehicleSeatNetworkDiagnostic.filename].write=function()error('synthetic_disk_failure')end
tick(25);assert(VehicleSeatNetworkDiagnostic.status=='disabled')
print('PASS passive entry waits for solo seated M102, requires consecutive samples, stops after completion, preserves callback results, records gaps and handles disk failure')


