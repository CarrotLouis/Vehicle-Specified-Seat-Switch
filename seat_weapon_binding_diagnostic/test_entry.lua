local f=assert(io.open('work/seat_weapon_binding_diagnostic/entry.lua'));local source=f:read('*a');f:close()
local recorder=assert(loadfile('work/seat_network_diagnostic/recorder.lua'))()
local now,calls,closed=0,0,0;local files={};local failed=false
local env=setmetatable({},{__index=_G});env._G=env
env.CowboyBingusModLoader={api=1,version=17,open_log=function(name)
 local f={text='',write=function(self,b)self.text=self.text..b;return self end,flush=function()return true end,close=function()closed=closed+1;return true end};files[name]=f;return f
end}
env.update=function()calls=calls+1;return nil,'kept',nil,4 end;env.shutdown=function()return 5 end
env.platform=function()return {now=function()return now end,pid=function()return 1 end,module=function()return 1 end}end
env.pages=function(a)return a end
env.compat={start=function()return {step=function()return {capabilities={enhanced=true}}end}end}
env.recorder=recorder;env.sampler={new=function()return {capture=function()return {state='mission',avatars={{id=7,is_local=true}},vehicles={},peers={}}end}end}
env.binding_inspect={new=function()return {interface=function()return {}end,capture=function()if failed then error('unreadable')end;return {slots={}}end}end}
env.routing={new=function()return {}end}
local c=assert(loadstring(source));setfenv(c,env);c()
for i=1,200 do now=now+.1;local a,b,c,d=env.update();assert(a==nil and b=='kept'and c==nil and d==4)end
assert(calls==200 and env.VehicleSeatNetworkDiagnostic.status:find('ready_read_only'),tostring(env.VehicleSeatNetworkDiagnostic.error))
local filename=env.VehicleSeatNetworkDiagnostic.filename
assert(files[filename].text:find('binding_sample')and files[filename].text:find('binding_interface'))
failed=true;for i=1,10 do now=now+.3;env.update()end
assert(files[filename].text:find('unreadable')and env.VehicleSeatNetworkDiagnostic.status~='disabled')
local original=env.update;local duplicate=assert(loadstring(source));setfenv(duplicate,env);duplicate();assert(env.update==original)
assert(env.shutdown()==5 and closed==2)
print('PASS passive entry callback forwarding, no gameplay dependency, recoverable read gaps, duplicate guard and shutdown')
