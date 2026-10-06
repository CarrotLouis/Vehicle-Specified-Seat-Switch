-- Public menu APIs only. Stable IDs own settings, never the INI/native mappings.
local M={prefix='vehicle_seat_tools.vss.'}
M.ids={};for i=1,5 do M.ids[i]=M.prefix..'seat'..i end
function M.new(text,locales,log)
 local self={mode='normal',strategy='ini',block_perf=false,registered={},binding_registered={}}
 local tr=text.new(locales.en,locales.bundled,log)
 local function t(key)return function()return tr(key)end end
 local function value(menu,id,default)
  local ok,v=pcall(menu.get,M.prefix..id);return ok and v~=nil and v or default
 end
 function self:update()
  local menu=rawget(_G,'ModOptionsMenu')
  if menu and menu.api==1 and (menu.version or 0)>=2 and type(menu.register_option)=='function' then
   if menu~=self.options then
    self.options=menu;self.registered={}
    local specs={
     {'mode',{type='choice',label=t('mode'),choices={t('normal'),t('enhanced')},default=1,description=t('mode_description')}},
     {'strategy',{type='choice',label=t('strategy'),choices={'VehicleSeatSwitch.ini','ModBindingsMenu'},default=1,description=t('keys_description')}},
     {'block_perf',{type='toggle',label=t('block_perf'),default=false,description=t('perf_description')}},
    }
    for _,row in ipairs(specs)do
     row[2].mod='Vehicle Specified Seat Switch';row[2].mod_id='vehicle_seat_tools.vss'
     local ok,accepted,why=pcall(menu.register_option,M.prefix..row[1],row[2])
     self.registered[row[1]]=ok and accepted==true
     if not self.registered[row[1]]then log('menu_option_refused '..row[1]..' '..tostring(ok and why or accepted))end
    end
   end
   if self.registered.mode then self.mode=value(menu,'mode',1)==2 and 'enhanced' or 'normal'end
   if self.registered.strategy then self.strategy=value(menu,'strategy',1)==2 and 'menu' or 'ini'end
   if self.registered.block_perf then self.block_perf=value(menu,'block_perf',false)==true end
  end
  local bindings=rawget(_G,'ModBindingsMenu')
  if bindings and bindings.api==1 and (bindings.version or 0)>=3 and type(bindings.register_binding)=='function' and bindings~=self.bindings then
   self.bindings=bindings;self.binding_registered={}
   for index,id in ipairs(M.ids)do
    local i=index
    local function label()
     -- The public API has labels, not a description row. Use the first label
     -- for the inactive-strategy notice; do not spend another shared action.
     if i==1 and self.strategy=='ini'then return tr('hint')..' | '..tr('seat1')end
     return tr('seat'..i)
    end
    local ok,accepted,why=pcall(bindings.register_binding,id,label,nil,{category='Vehicle Specified Seat Switch'})
    self.binding_registered[i]=ok and accepted==true
    if not self.binding_registered[i]then log('menu_binding_refused seat'..i..' '..tostring(ok and why or accepted))end
   end
  end
 end
 return self
end
return M
