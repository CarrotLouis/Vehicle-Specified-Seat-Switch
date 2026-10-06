local profile=assert(loadfile('work/seat_switch/src/profile.lua'))()
local config=assert(loadfile('work/seat_switch/src/config.lua'))()
local policy=assert(loadfile('work/seat_switch/src/policy.lua'))()
local captured,initialized={},0
local keypath='work/seat_switch/tests/fixture_entry/VehicleSeatSwitch.ini'
os.remove(keypath)
CowboyBingusModLoader={api=1,version=16,log_directory='work/seat_switch/tests/fixture_entry',open_log=function()
 return {write=function(_,line)captured[#captured+1]=line end,flush=function()end,close=function()end}
end}
local api={module=function(name)return name=='game.dll' and 1 or 2 end,
 hash_module=function(m)return m==1 and profile.game_sha256 or profile.exe_sha256 end,
 config_directory=function()return 'work/seat_switch/tests/fixture_entry' end,read=function()return nil end,now=function()return 1 end}
local original_calls,shut=0,0
update=function(a,b)original_calls=original_calls+1;assert(a=='forwarded' and b==9);return nil,'returned',nil,42 end
shutdown=function(a)shut=shut+1;return a end
local entry=assert(io.open('work/seat_switch/src/entry.lua','rb')):read('*a')
local env=setmetatable({MODE='normal',profile=profile,config=config,policy=policy,platform=function()initialized=initialized+1;return api end,
 snapshot={capture=function(_,_,p)assert(p==profile);return nil,'not_in_mission' end,i32=function()return 0 end},
 bind_native=function()return {} end,Controller={new=function()return {update=function()return 'not_in_mission' end} end}}, {__index=_G})
local fn=assert(loadstring(entry));setfenv(fn,env);fn()
for _=1,180 do local a,b,c,d=env.update('forwarded',9);assert(a==nil and b=='returned' and c==nil and d==42) end
assert(initialized==1 and original_calls==180 and VehicleSeatSwitch.status=='not_in_mission')
local f=assert(io.open(keypath,'rb'));local txt=f:read('*a');f:close();assert(txt:match('%[maelstrom%]'))
-- Duplicate package/resource invocation must not install a second wrapper.
local installed=env.update;fn();assert(env.update==installed and initialized==1)
assert(env.shutdown('forwarded_shutdown')=='forwarded_shutdown' and shut==1)
-- A mismatched game hash must never reach native binding.
rawset(_G,'VehicleSeatSwitch',nil);api.hash_module=function()return 'unsupported' end
env.update=update;env.shutdown=shutdown;env.bind_native=function()error('UNSAFE native binding reached') end
fn();for _=1,180 do env.update('forwarded',9) end
assert(VehicleSeatSwitch.status=='disabled_after_error')
assert(table.concat(captured):match('Unsupported game.dll'))
rawset(_G,'VehicleSeatSwitch',nil)
print('PASS: addon startup, shared config creation, Maelstrom section, update/shutdown forwarding, duplicate guard and unsupported-build refusal. Game API mocked.')
