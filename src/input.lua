-- Per-frame, non-consuming key polling. Never injects keys or hooks a window.
local M={}
local groups={{16,160,161},{17,162,163},{18,164,165},{nil,91,92}}
local primary_group={ [16]=1,[160]=1,[161]=1,[17]=2,[162]=2,[163]=2,
 [18]=3,[164]=3,[165]=3,[91]=4,[92]=4 }
function M.new(keys,api)
 local self={api=api,bindings={},codes={},previous={},focused=false}
 for _,map in pairs(keys) do for _,code in pairs(map) do if code~=0 then
  self.bindings[code]=true;self.codes[code%256]=true
  for _,held in ipairs(api.chords and api.chords[code]or{})do self.codes[held]=true end
 end end end
 for _,g in ipairs(groups) do for _,c in pairs(g) do self.codes[c]=true end end
 for code in pairs(self.codes) do self.previous[code]=api.down(code) end
 self.focused=api.focused() and (not api.input_allowed or api.input_allowed())
 function self:poll(focused)
  local now,pressed={},{}
  for code in pairs(self.codes) do now[code]=self.api.down(code) end
  for binding in pairs(self.bindings) do
   local key,mask=binding%256,math.floor(binding/256)
   if focused and self.focused and now[key] and not self.previous[key] then
    local match=true
    for _,held in ipairs(self.api.chords and self.api.chords[binding]or{})do if not now[held]then match=false end end
    for i,g in ipairs(groups) do
     local want=mask%4;mask=math.floor(mask/4)
     if primary_group[key]~=i then
      local left,right=now[g[2]],now[g[3]]
      local any=left or right or (g[1] and now[g[1]])
      if (want==0 and any) or (want==1 and not any)
       or (want==2 and (not left or right)) or (want==3 and (not right or left)) then match=false end
     end
    end
    if match then pressed[binding]=true end
   end
  end
  self.previous=now;self.focused=focused
  return pressed
 end
 return self
end
return M
