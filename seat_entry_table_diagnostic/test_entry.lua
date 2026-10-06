local f=assert(io.open('work/seat_entry_table_diagnostic/entry.lua'));local source=f:read('*a');f:close()
local recorder=assert(loadfile('work/seat_network_diagnostic/recorder.lua'))()
local now,prior,captures,files,fail=0,0,0,{},false
local env
CowboyBingusModLoader={version=16,api=1,open_log=function(n)
 local f={text='',write=function(s,v)s.text=s.text..v;return s end,flush=function()return true end,close=function(s)s.closed=true end};files[n]=f;return f
end}
local chunk=assert(loadstring(source))
local function init()
 VehicleSeatNetworkDiagnostic=nil
 env=setmetatable({profile={},compat_spec={},
  platform=function()return {now=function()return now end,pid=function()return 1 end,module=function()return 1 end,hash_module=function()return 'test'end}end,
  tables={extend=function(p)return p end,capture=function()captures=captures+1;if fail then error('synthetic_missing_table')end;return {event='entry_tables',tables={}}end},
  compat={start=function()return {step=function()return {compatibility={checked=1}}end}end},recorder=recorder,
  os={date=function()return 'test'end},
  update=function()prior=prior+1;return nil,'forwarded',nil,7 end,
  shutdown=function()return 'shutdown_forwarded'end}, {__index=_G})
 setfenv(chunk,env);chunk()
end
local function tick(n)for _=1,n do now=now+.02;local a,b,c,d=env.update();assert(a==nil and b=='forwarded' and c==nil and d==7)end end
init();tick(599);assert(captures==0);tick(1)
assert(captures==1 and VehicleSeatNetworkDiagnostic.status=='entry_tables_complete')
tick(500);assert(captures==1 and prior==1100)
local data=files[VehicleSeatNetworkDiagnostic.filename];assert(data.closed and data.text:find('"reason":"complete"',1,true))
assert(env.shutdown()=='shutdown_forwarded')
fail=true;init();tick(600)
assert(VehicleSeatNetworkDiagnostic.status=='disabled' and VehicleSeatNetworkDiagnostic.error:find('synthetic_missing_table'))
assert(files[VehicleSeatNetworkDiagnostic.filename].closed)
tick(50);assert(captures==2)
print('PASS one-shot entry: callback forwarding, no gameplay dependency, delayed capture, completion, failure closes log and stops')
