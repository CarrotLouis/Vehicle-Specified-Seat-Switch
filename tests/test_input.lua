local config=assert(loadfile('work/src/config.lua'))()
local input=assert(loadfile('work/src/input.lua'))()
local function key(s)return assert(config.key(s),s) end
for name,code in pairs(config.names) do assert(key(name:lower())==code,name) end
assert(key('Ctrl+1')==key('CONTROL+1') and key('Ctrl+Shift+Q')==key('shift + ctrl + q'))
assert(key('MOUSE4')==5 and key('MOUSE5')==6 and key('NUMPADENTER')==key('ENTER'))
for _,s in ipairs({'CTRL++1','+Q','SHIFT+','CTRL+NONE','CTRL+LCTRL+Q','FN','WHEELUP','ALT+MOUSE6','MOUSE4+MOUSE4+W','W+W'}) do
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
local api={chords=config.chords,down=function(c)return down[c] or false end,focused=function()return focused end}
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

local free,problems=config.parse('[m102]\ndriver=MOUSE4+W\nfront_passenger=MOUSE4+S\nrear_left=MOUSE4+A\nrear_right=MOUSE4+D\ngunner=MOUSE4+F\n')
assert(#problems==0 and free.m102.driver==key('XBUTTON1 + w'))
assert(key('Q+MOUSE4+E')==key('MOUSE4+Q+E'))
assert(key('MOUSE4+W')~=key('W+MOUSE4'),'Final key defines the trigger')
assert(not config.overlap(key('MOUSE4+W'),key('W')),'Do not forbid user-owned gameplay/binding conflicts')
down={};poll=input.new(free,api)
for _,letter in ipairs({'W','S','A','D','F'})do
 step({});assert(next(step({5}))==nil)
 only(step({5,letter:byte()}),'MOUSE4+'..letter)
 assert(next(step({5,letter:byte()}))==nil,'Free chord hold must not repeat')
 assert(next(step({letter:byte()}))==nil,'Prefix release must not trigger')
 step({});assert(next(step({letter:byte()}))==nil)
 assert(next(step({5,letter:byte()}))==nil,'Late prefix is not a fresh trigger')
end
step({},false);step({5,87},false);assert(next(step({5,87},true))==nil)
step({});assert(next(step({5,87,162}))==nil,'Extra modifiers still require explicit configuration')
-- No small chord-length limit: every distinct supported ordinary key can be
-- a prerequisite; aliases and modifier groups are normalized separately.
local names,physical_keys,seen={},{},{}
for name,code in pairs(config.names)do
 if code~=87 and code~=16 and code~=17 and code~=18 and code~=91 and code~=92 and not(code>=160 and code<=165)and not seen[code]then
  names[#names+1]=name;physical_keys[#physical_keys+1]=code;seen[code]=true
 end
end
names[#names+1]='W';local long=key(table.concat(names,'+'))
down={};poll=input.new({m={seat=long}},api);step(physical_keys)
physical_keys[#physical_keys+1]=87;assert(step(physical_keys)[long])
physical_keys[1]=nil;assert(not step(physical_keys)[long])
-- Modifiers may be the final trigger; ordinary keys can precede them.
down={};local last=key('MOUSE4+CTRL');poll=input.new({m={seat=last}},api)
step({5});assert(step({5,17,162})[last])
assert(key('CTRL+SHIFT') and key('Q+E') and key('MOUSE4+MOUSE5'))
print('PASS free keyboard/mouse prerequisites, five requested seats, aliases/order, modifier-final and long chords; focus/hold/release guards retained; no conflict suppression added')
