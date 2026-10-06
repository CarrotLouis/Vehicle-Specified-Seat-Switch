local config=assert(loadfile('work/src/config.lua'))()
local input=assert(loadfile('work/src/input.lua'))()
local function key(s)return assert(config.key(s),s) end
for name,code in pairs(config.names) do assert(key(name:lower())==code,name) end
assert(key('Ctrl+1')==key('CONTROL+1') and key('Ctrl+Shift+Q')==key('shift + ctrl + q'))
assert(key('MOUSE4')==5 and key('MOUSE5')==6 and key('NUMPADENTER')==key('ENTER'))
for _,s in ipairs({'CTRL++1','+Q','SHIFT+','A+Q','CTRL+NONE','CTRL+LCTRL+Q','FN','WHEELUP','CTRL+SHIFT','ALT+MOUSE6'}) do
 assert(config.key(s)==nil,'Invalid binding accepted: '..s)
end
assert(config.overlap(key('CTRL+1'),key('LCTRL+1')))
assert(not config.overlap(key('LCTRL+1'),key('RCTRL+1')))
assert(not config.overlap(key('CTRL+1'),key('1')))
assert(config.overlap(key('CTRL'),key('LCTRL')))
assert(config.overlap(key('CTRL'),key('CTRL+1')))
assert(config.overlap(key('CTRL+SHIFT+MOUSE4'),key('LSHIFT')))
assert(not config.overlap(key('LCTRL'),key('RCTRL+1')))
local parsed,issues=config.parse('[m102]\ndriver=CTRL+1\nfront_passenger=LCTRL+1\n')
assert(#issues==1 and parsed.m102.driver==112,'Overlapping generic/side modifiers must be rejected')
parsed,issues=config.parse('[m102]\ndriver=1\nfront_passenger=CTRL+1\nrear_left=SHIFT+Q\nrear_right=CTRL+SHIFT+MOUSE4\ngunner=RCTRL+NUMPAD1\n')
assert(#issues==0)
local down,focused={},true
local api={down=function(c)return down[c] or false end,focused=function()return focused end}
local poll=input.new(parsed,api)
local function step(keys,focus)
 down={};for _,c in ipairs(keys or {}) do down[c]=true end
 if focus~=nil then focused=focus end
 return poll:poll(focused)
end
local function only(result,name)
 assert(result[key(name)],'Missing '..name)
 local count=0;for _ in pairs(result) do count=count+1 end;assert(count==1,'Ambiguous trigger')
end
only(step({49}),'1');assert(next(step({49}))==nil,'Hold must not repeat')
step({});step({162});only(step({162,49}),'CTRL+1')
assert(next(step({162,49}))==nil)
assert(next(step({49}))==nil,'Releasing Ctrl while holding 1 must not trigger 1')
step({});step({49});assert(next(step({49,162}))==nil,'Modifier pressed after primary must not trigger')
step({});only(step({160,81}),'SHIFT+Q')
step({});assert(next(step({160,162,81}))==nil,'Extra modifier must not match')
step({});only(step({162,160,5}),'CTRL+SHIFT+MOUSE4')
step({});assert(next(step({162,97}))==nil,'Wrong Ctrl side must not match')
step({});only(step({163,97}),'RCTRL+NUMPAD1')
step({});assert(next(step({162,163,97}))==nil,'Both sides must not match side-specific binding')
step({},false);step({162,49},false);assert(next(step({162,49},true))==nil,'Focus gain must not activate a held chord')
step({});only(step({162,49}),'CTRL+1')
-- Side buttons are independent, including a modifier+mouse binding.
local mouse=input.new({m={a=key('MOUSE4'),b=key('ALT+MOUSE5')}},api)
down={};mouse:poll(true);down={[5]=true};only(mouse:poll(true),'MOUSE4')
down={};mouse:poll(true);down={[164]=true,[6]=true};only(mouse:poll(true),'ALT+MOUSE5')
-- Entry/focus starts with held keys, which must be released before activation.
local held=input.new(parsed,api);assert(next(held:poll(true))==nil)
print('PASS: named keyboard/mouse keys; chord aliases/overlap; Ctrl+1, Shift+Q, sided modifiers and mouse side chords; no repeats, extra modifiers, modifier-release or focus-gain activation. Input states simulated; no keys injected.')
