-- Local aliases for the actual game codes observed in the menu logs. This
-- leaves the upstream text module and other addons' shared registry unchanged.
return function(Text)
 local aliases={tc='zh-Hant',pt='pt-BR',ms='es-419',uk='en',gb='en',['en-GB']='en'}
 return {new=function(english,bundled,log)
  local tr=Text.new(english,bundled,log)
  function tr:refresh()
   local registry=Text.registry();local raw=Text.language();local language=aliases[raw]or raw
   if self.texts and self.serial==registry.serial and self.language==language then return false end
   self:resolve(language,registry);return true
  end
  return tr
 end}
end
