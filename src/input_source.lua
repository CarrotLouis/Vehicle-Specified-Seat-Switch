-- A single dispatch poller, with independent INI and native-action providers.
-- Read native action pulses every game frame; the seat loop may run slower.
local M={}
function M.new(ini,api,input,policy,menus,ids)
 local self={strategy='ini',bindings={},keys={},pending={},last={},menu_focused=false}
 local physical=input.new(ini,api)
 local virtual={};for i=1,5 do virtual[i]=0x100000+i*256 end -- no Windows primary
 for vehicle,map in pairs(ini)do self.keys[vehicle]={};for seat,code in pairs(map)do self.keys[vehicle][seat]=code end end
 self.bindings=physical.bindings
 function self:sample_menu(focused)
  if self.strategy~='menu'then return end
  local b=menus.bindings
  for i,id in ipairs(ids)do
   local ok,down=false,nil
   if b and menus.binding_registered[i]then ok,down=pcall(b.is_down,id)end
   local held=ok and down==true
   if focused and self.menu_focused and held and self.last[i]==false then self.pending[virtual[i]]=true end
   -- nil -> true is not an edge: a provider returning after loading/errors
   -- must first report a released state, just like focus or source changes.
   self.last[i]=ok and down~=nil and held or nil
   if ok and down==false then self.last[i]=false end
  end
  self.menu_focused=focused
  if not focused then self.pending={}end
 end
 function self:set_strategy(strategy)
  assert(strategy=='ini' or strategy=='menu')
  self.strategy=strategy;self.pending={};self.last={};self.menu_focused=false
  physical:poll(false)
  self.bindings={}
  for vehicle,seats in pairs(policy.seats)do
   for i,name in ipairs(seats)do
    local code=strategy=='ini' and ini[vehicle][name] or virtual[i]
    self.keys[vehicle][name]=code
    if code~=0 then self.bindings[code]=true end
   end
  end
 end
 function self:poll(focused)
  if self.strategy=='ini'then return physical:poll(focused)end
  local p=focused and self.pending or {};self.pending={}
  if not focused then self.menu_focused=false end
  return p
 end
 function self:held()
  if self.strategy=='menu'then return next(self.pending)~=nil end
  for code in pairs(self.bindings)do if api.down(code%256)then return true end end
  return false
 end
 function self:flush()
  physical:poll(false);self.pending={};self.last={};self.menu_focused=false
 end
 return self
end
return M
