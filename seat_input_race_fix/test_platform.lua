-- Real LuaJIT FFI and read-only Windows API calls; no game process is opened.
local ffi=require('ffi')
local gameplay=assert(loadfile('work/seat_switch/src/platform.lua'))()
local diagnostic=assert(loadfile('work/seat_input_race_fix/platform.lua'))()
local order=os.getenv('VSS_TEST_ORDER') or 'diagnostic-first'
local g,d
if order=='diagnostic-first' then d=diagnostic(function()end);g=gameplay()
else g=gameplay();d=diagnostic(function()end) end
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

local value=ffi.new('uint8_t[8]',{1,2,3,4,5,6,7,8})
assert(d.replace(value,'\1\2','\9\8'))
assert(value[0]==9 and value[1]==8 and value[2]==3)
assert(not d.replace(value,'\1\2','\0\0'))
print('PASS bounded data replacement and stale compare refusal')
