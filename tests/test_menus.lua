-- Actual public menu implementations, never their native update routines.
-- Assignments/values/logs are confined to a fresh test directory.
local root='work/'
local source=assert(os.getenv('VSS_MENU_SOURCE'))
local fixture=assert(os.getenv('VSS_MENU_FIXTURE'))
local f=assert(io.open(fixture..'/probe','wb'));f:close()
CowboyBingusModLoader={api=1,version=19,log_directory=fixture,
 open_log=function(name)return assert(io.open(fixture..'/'..name,'wb'))end}
update=function()end
local T=assert(loadfile(root..'src/bingus_text.lua'))()
T.registry().steam_language='en'
if source=='installed'then
 dofile('work/research/archive/menu_integration_research/installed/ModOptionsMenu-fd50351f21814b0e.lua')
 dofile('work/research/archive/menu_integration_research/installed/ModBindingsMenu-ace3bd664062daa9.lua')
else
 local vendor='work/research/archive/menu_integration_research/vendor/'
 local function files(folder)return setmetatable({}, {__index=function(t,n)local chunk=assert(loadfile(folder..'/src/'..n..'.lua'));rawset(t,n,chunk);return chunk end})end
 local mom=vendor..'ModOptionsMenu';mom_files=files(mom);mom_text={module=T,locales={en=dofile(mom..'/locales/en.lua'),bundled={}}};dofile(mom..'/src/mod_options_menu.lua')
 local mbm=vendor..'ModBindingsMenu';mbm_files=files(mbm);mbm_text={module=T,locales={en=dofile(mbm..'/locales/en.lua'),bundled={}}};dofile(mbm..'/src/mod_bindings_menu.lua')
end
assert(ModOptionsMenu and ModBindingsMenu and not ModOptionsMenu.ready()and not ModBindingsMenu.ready())
local Menu=assert(loadfile(root..'src/menu.lua'))()
local locales=assert(loadfile(root..'src/menu_locales.lua'))()
local logs={};local m=Menu.new(dofile(root..'src/i18n.lua')(T),locales,function(s)logs[#logs+1]=s end);m:update()
for _,id in ipairs({'mode','strategy','block_perf_data'})do assert(m.registered[id],table.concat(logs,';'))end
for i=1,5 do assert(m.binding_registered[i],table.concat(logs,';'))end
assert(m.mode=='normal'and m.strategy=='ini'and m.block_perf==false)
assert(ModOptionsMenu.set(Menu.prefix..'mode',2));assert(ModOptionsMenu.set(Menu.prefix..'strategy',2));m:update()
assert(m.mode=='enhanced'and m.strategy=='menu'and m.block_perf==false)
local function upvalue(fn,wanted)
 for i=1,60 do local n,v=debug.getupvalue(fn,i);if n==wanted then return v end;if not n then break end end
 error('missing upvalue '..wanted)
end
assert(ModOptionsMenu.get(Menu.prefix..'block_perf')==nil,'withdrawn instruction patch must not register a toggle')
local native=upvalue(ModBindingsMenu.register_binding,'state')
for language,locale in pairs(locales.bundled)do
 T.registry().game_language=language
 local first=native.registry[Menu.ids[1]]
 local label=first.label();assert(label==locale.strings.seat1 and T.length(label)<=127)
 assert(ModOptionsMenu.set(Menu.prefix..'strategy',1));m:update();label=first.label()
 assert(label==locale.strings.hint..' | '..locale.strings.seat1 and T.length(label)<=127)
 for i=2,5 do assert(native.registry[Menu.ids[i]].label()==locale.strings['seat'..i])end
 assert(ModOptionsMenu.set(Menu.prefix..'strategy',2));m:update()
end
-- Repeated registration/update keeps exactly five reservations, not 5 per frame.
local revision=ModBindingsMenu.revision
for i=1,100 do m:update()end
if revision then assert(revision==ModBindingsMenu.revision)end
local count=0;for id in pairs(native.registry)do if id:sub(1,#Menu.prefix)==Menu.prefix then count=count+1 end end;assert(count==5)
assert(ModBindingsMenu.is_down(Menu.ids[1])==nil,'an unavailable native source must not fake an INI press')
if shutdown then shutdown()end
print('PASS '..source..' actual menu APIs: 3 options / 5 actions, defaults, applied settings, 13 locales, strategy hint and stable reservations')
