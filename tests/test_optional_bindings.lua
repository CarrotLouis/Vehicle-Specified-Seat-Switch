local T=dofile('work/src/bingus_text.lua');T.registry().steam_language='en'
local Menu=dofile('work/src/menu.lua');local locales=dofile('work/src/menu_locales.lua')
local specs,values={},{}
ModOptionsMenu={api=1,version=3,register_option=function(id,s)specs[id]=s;values[id]=s.default;return true end,get=function(id)return values[id]end}
ModBindingsMenu=nil
local m=Menu.new(dofile('work/src/i18n.lua')(T),locales,function()end)
m:update();assert(m.strategy=='ini'and not m.registered.strategy and specs[Menu.prefix..'strategy']==nil)
assert(m.available and specs[Menu.prefix..'mode']and specs[Menu.prefix..'block_perf_data'])
-- Installing/loading the optional menu later may register the strategy.
local label
ModBindingsMenu={api=1,version=3,register_binding=function(id,fn)if id==Menu.ids[1]then label=fn end;return true end,is_down=function()return false end}
m:update();assert(m.registered.strategy)
values[Menu.prefix..'strategy']=2
-- The page label reads the applied choice even if no gameplay update ran.
assert(label()==locales.en.strings.seat1)
ModBindingsMenu=nil;m:update();assert(m.strategy=='ini')
assert(label()==locales.en.strings.hint..' | '..locales.en.strings.seat1)
ModOptionsMenu=nil;m:update();assert(not m.available and m.strategy=='ini')
print('PASS missing MBM locks INI with no menu strategy option; delayed API registration and direct label refresh')
