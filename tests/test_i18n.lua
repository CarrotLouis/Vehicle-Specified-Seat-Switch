local T=dofile('work/src/bingus_text.lua')
local wrapper=dofile('work/src/i18n.lua')(T)
local locales=dofile('work/src/menu_locales.lua')
local tr=wrapper.new(locales.en,locales.bundled)
for _,pair in ipairs({{'tc','zh-Hant'},{'pt','pt-BR'},{'ms','es-419'},{'us','en'},{'uk','en'},{'gb','en'},
 {'cn','zh-Hans'},{'jp','ja'},{'kr','ko'},{'de','de'},{'fr','fr'},{'it','it'},{'es','es'},{'pl','pl'},{'ru','ru'}})do
 local raw,expected=pair[1],pair[2]
 local tag=T.GAME_CODES[raw]or raw;T.registry().game_language=tag
 local locale=expected=='en'and locales.en or locales.bundled[expected]
 for key,value in pairs(locale.strings)do assert(tr(key)==value)end
 assert(T.registry().game_language==tag,'project aliases must not mutate shared language')
end
for language,locale in pairs(locales.bundled)do
 T.registry().game_language=language
 for key,value in pairs(locale.strings)do assert(tr(key)==value)end
end
print('PASS actual tc/pt/ms aliases and all bundled texts; English variants and shared registry unchanged')
