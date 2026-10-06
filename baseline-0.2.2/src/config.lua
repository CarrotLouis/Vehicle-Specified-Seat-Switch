local M={}
M.defaults={
 m102={driver='F1',front_passenger='F2',rear_left='F3',rear_right='F4',gunner='F5'},
 m103={driver='F1',front_passenger='F2',rear_left='F3',rear_right='F4'},
 m104={driver='F1',front_passenger='F2',flamer='F3'},
 bastion={driver='F1',gunner='F2',passenger_left='F3',passenger_right='F4'},
 maelstrom={driver='F1',gunner='F2',passenger_left='F3',passenger_right='F4'},
 tanker={driver='F1',gunner='F2'},
}
function M.key(value)
 if type(value)~='string' then return nil end
 value=value:upper():match('^%s*(.-)%s*$')
 if value=='NONE' then return 0 end
 if value:match('^[A-Z0-9]$') then return value:byte() end
 local f=tonumber(value:match('^F(%d+)$'))
 if f and f>=1 and f<=24 then return 111+f end
 local num=tonumber(value:match('^NUMPAD(%d)$'))
 if num then return 96+num end
 return nil
end
function M.parse(text)
 local result,issues={},{}
 for vehicle,keys in pairs(M.defaults) do
  result[vehicle]={};for seat,key in pairs(keys) do result[vehicle][seat]=M.key(key) end
 end
 local section
 for line in (text or ''):gmatch('[^\r\n]+') do
  line=line:gsub('^\239\187\191',''):gsub('[;#].*$',''):match('^%s*(.-)%s*$')
  local header=line:match('^%[([%w_]+)%]$')
  if header then section=header:lower()
  elseif line~='' then
   local name,value=line:match('^([%w_]+)%s*=%s*(.-)%s*$')
   if section and result[section] and name and result[section][name:lower()]~=nil then
    local code=M.key(value)
    if code then result[section][name:lower()]=code else issues[#issues+1]='Invalid key: '..section..'.'..name end
   else issues[#issues+1]='Unknown configuration line: '..line end
  end
 end
 for vehicle,keys in pairs(result) do
  local seen,conflict={}
  for seat,code in pairs(keys) do
   if code~=0 then if seen[code] then conflict=true end;seen[code]=seat end
  end
  if conflict then
   -- Revert the entire vehicle mapping, avoiding cascading default conflicts.
   for seat,key in pairs(M.defaults[vehicle]) do keys[seat]=M.key(key) end
   issues[#issues+1]='Duplicate key in '..vehicle..'; restored this vehicle defaults'
  end
 end
 return result,issues
end
function M.template()
 local rows={'; Vehicle Seat Switch — restart game after editing.',
 '; Location: %APPDATA%/Arrowhead/Helldivers2/VehicleSeatSwitch.ini',
 '; Keys: F1-F24, NUMPAD0-NUMPAD9 (Num Lock ON), A-Z, 0-9, NONE.',
 '; F2/F3/F5 may also toggle game performance overlays. Change keys if needed.',
 '; Example for M102: NUMPAD1, NUMPAD2, NUMPAD3, NUMPAD4, NUMPAD5.',
 '; Use a different key for each seat in the same vehicle.',
 '; Choose Normal / Enhanced in Arsenal, not in this file.'}
 for _,vehicle in ipairs({'m102','m103','m104','bastion','maelstrom','tanker'}) do
  rows[#rows+1]='';rows[#rows+1]='['..vehicle..']'
  local seats=(vehicle=='bastion' or vehicle=='maelstrom') and {'driver','gunner','passenger_left','passenger_right'}
   or vehicle=='tanker' and {'driver','gunner'}
   or {'driver','front_passenger','rear_left','rear_right','gunner','flamer'}
  for _,seat in ipairs(seats) do
   if M.defaults[vehicle][seat] then rows[#rows+1]=seat..'='..M.defaults[vehicle][seat] end
  end
 end
 return table.concat(rows,'\r\n')..'\r\n'
end
function M.load(directory,legacy_directory)
 local path=directory..'/VehicleSeatSwitch.ini'
 local function read(p)
  local f=io.open(p,'rb');if not f then return nil end
  local text=f:read('*a');f:close();assert(text,'Cannot read key configuration');return text
 end
 local text=read(path);local origin='existing'
 if text==nil then
  text=legacy_directory and read(legacy_directory..'/VehicleSeatSwitch.ini') or nil
  origin=text and 'migrated_legacy' or 'created_defaults'
  text=text or M.template()
  local f=assert(io.open(path,'wb'),'Cannot create key configuration: '..path)
  local ok,why=f:write(text);f:close();assert(ok,why)
 end
 local keys,issues=M.parse(text)
 return keys,issues,path,origin
end
return M
