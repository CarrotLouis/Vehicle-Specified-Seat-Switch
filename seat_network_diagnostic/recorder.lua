local M={}
local function encode(value)
 local t=type(value)
 if t=='string' then return '"'..value:gsub('[%z\1-\31\\"]',function(c)
  if c=='"' then return '\\"' elseif c=='\\' then return '\\\\' end
  return string.format('\\u%04x',c:byte()) end)..'"' end
 if t=='number' then assert(value==value and value~=math.huge and value~=-math.huge,'invalid_json_number');return tostring(value) end
 if t=='boolean' then return tostring(value) end
 if t=='nil' then return 'null' end
 assert(t=='table','invalid_json_type')
 local keys={};for k in pairs(value) do keys[#keys+1]=k end
 if #keys==0 or type(keys[1])=='number' then
  local out={};for i=1,#value do out[i]=encode(value[i]) end;return '['..table.concat(out,',')..']'
 end
 table.sort(keys);local out={}
 for _,k in ipairs(keys) do out[#out+1]=encode(k)..':'..encode(value[k]) end
 return '{'..table.concat(out,',')..'}'
end
M.encode=encode
function M.new(file,now,limit)
 local self={file=file,start=now,last_flush=now,last_state=-math.huge,bytes=0,events=0,limit=limit or 32*1024*1024,closed=false}
 function self:write(event,now)
  if self.closed then return false end
  event.t=math.floor((now-self.start)*1000+0.5)
  local line=encode(event)..'\n'
  if self.bytes+#line>self.limit then
   assert(self.file:write('{"event":"size_limit"}\n'));self.file:flush();self.file:close();self.closed=true;return false
  end
  assert(self.file:write(line),'log_write_failed');self.bytes=self.bytes+#line;self.events=self.events+1
  if now-self.last_flush>=1 then assert(self.file:flush(),'log_flush_failed');self.last_flush=now end
  return true
 end
 function self:sample(snapshot,now,frame)
  local signature=encode(snapshot)
  if signature~=self.previous or now-self.last_state>=2 then
   self.previous=signature;self.last_state=now
   return self:write({event='state',frame=frame,data=snapshot},now)
  end
  if now-self.last_flush>=1 and not self.closed then assert(self.file:flush(),'log_flush_failed');self.last_flush=now end
  return true
 end
 function self:close(now,reason)
  if self.closed then return end
  self:write({event='end',reason=reason},now)
  if not self.closed then self.file:flush();self.file:close();self.closed=true end
 end
 return self
end
return M
