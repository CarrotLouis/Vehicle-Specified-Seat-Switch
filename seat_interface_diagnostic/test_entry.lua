local recorder=assert(loadfile('work/seat_network_diagnostic/recorder.lua'))()
local file=assert(io.open('work/seat_interface_diagnostic/entry.lua'));local source=file:read('*a');file:close()
local now,count,original_calls,fail=0,0,0,false
local files={}
local function setup()
 local globals={}
 globals.CowboyBingusModLoader={version=16,api=1,open_log=function(name)
  local f={text='',write=function(self,b)self.text=self.text..b;return self end,flush=function()return true end,close=function(self)self.closed=true;return true end}
  files[name]=f;return f
 end}
 local env=setmetatable({_G=globals,profile={},compat_spec={},
  platform=function()return {now=function()return now end,pid=function()return 1 end,module=function()return 1 end}end,
  pages=function(a)return a end,compat={start=function()return {step=function()return {}end}end},
  observer={new=function()return {capture=function()count=count+1;if fail then error('synthetic_read_failure')end;return {event='interface_snapshot',state='observed'}end}end},
  routing={new=function()return {capture=function()if fail then error('synthetic_routing_gap')end;return {state='observed'}end}end},
  recorder=recorder,update=function()original_calls=original_calls+1;return nil,4,nil,8 end,
  shutdown=function()return 'forwarded'end,os={date=function()return 'test'end}}, {__index=_G})
 local chunk=assert(loadstring(source));setfenv(chunk,env);chunk()
 return env,globals,chunk
end
local env,g,chunk=setup()
local function tick(n)for _=1,n do now=now+.02;local a,b,c,d=env.update();assert(a==nil and b==4 and c==nil and d==8)end end
tick(179);assert(count==0);tick(2000);assert(count==10 and g.VehicleSeatNetworkDiagnostic.status:match('^complete '))
local old=env.update;chunk();assert(env.update==old,'same resource guard')
assert(env.shutdown()=='forwarded')
local log=files[g.VehicleSeatNetworkDiagnostic.filename];assert(log.closed and log.text:find('snapshot_limit'))
fail=true;count=0;env,g=setup();tick(2200)
assert(count==10 and files[g.VehicleSeatNetworkDiagnostic.filename].text:find('read_gap'))
assert(files[g.VehicleSeatNetworkDiagnostic.filename].text:find('routing_gap'))
assert(g.VehicleSeatNetworkDiagnostic.status:match('^complete '))
print('PASS interface entry: bounded sampling, read-failure recording, forwarding including nils, duplicate guard, shutdown')
