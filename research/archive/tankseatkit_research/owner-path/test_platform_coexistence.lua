local function tank_declarations()
 local f=assert(io.open('work/tankseatkit_research/tank_seat_kit.lua','rb'));local src=f:read('*a');f:close()
 local n=0
 for body in src:gmatch('ffi%.cdef%s*%[%[(.-)%]%]')do require('ffi').cdef(body);n=n+1 end
 assert(n==2)
end
if os.getenv('TANK_DECLARATIONS_LAST')~='1'then tank_declarations()end
-- Real LuaJIT FFI and read-only Windows API calls; no game process is opened.
local ffi=require('ffi')
local gameplay=assert(loadfile('work/seat_switch/src/platform.lua'))()
local diagnostic=assert(loadfile('work/seat_network_diagnostic/platform.lua'))()
local order=os.getenv('VSS_TEST_ORDER') or 'diagnostic-first'
local g,d
if order=='diagnostic-first' then d=diagnostic(function()end);g=gameplay()
else g=gameplay();d=diagnostic(function()end) end
if os.getenv('TANK_DECLARATIONS_LAST')=='1'then tank_declarations()end
-- Force the cursor branch even though this offline process has no foreground window.
g.focused=function()return true end;d.focused=function()return true end
local gok,gv=pcall(g.input_allowed)
local dok,dv=pcall(d.input_allowed)
if os.getenv('VSS_EXPECT_OLD_CONFLICT')=='1' then
 assert(not (gok and dok),'expected pre-fix conflict')
 assert(tostring(gok and dv or gv):find('cannot convert',1,true))
 print('REPRODUCED '..order..': '..tostring(gok and dv or gv))
else
 assert(gok,tostring(gv));assert(dok,tostring(dv))
 assert(type(gv)=='boolean' and type(dv)=='boolean')
 for _=1,100 do assert(type(g.input_allowed())=='boolean');assert(type(d.input_allowed())=='boolean') end
 assert(type(g.now())=='number' and type(d.now())=='number')
 print('PASS real FFI coexistence '..order..': both cursor checks, 100 repeated polls')
end
