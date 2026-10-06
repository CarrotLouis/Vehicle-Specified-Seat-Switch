local M={}
M.defaults={
 m102={driver='F1',front_passenger='F2',rear_left='F3',rear_right='F4',gunner='F5'},
 m103={driver='F1',front_passenger='F2',rear_left='F3',rear_right='F4'},
 m104={driver='F1',front_passenger='F2',flamer='F3'},
 bastion={driver='F1',gunner='F2',passenger_left='F3',passenger_right='F4'},
 maelstrom={driver='F1',gunner='F2',passenger_left='F3',passenger_right='F4'},
 tanker={driver='F1',gunner='F2'},
}
-- Windows virtual keys. Modifier requirements occupy four base-4 digits above
-- the low byte: Shift, Ctrl, Alt, Win; 0=absent, 1=either, 2=left, 3=right.
M.names={
 MOUSE1=1,MOUSE2=2,MOUSE3=4,MOUSE4=5,MOUSE5=6,
 LBUTTON=1,RBUTTON=2,MBUTTON=4,XBUTTON1=5,XBUTTON2=6,
 BACKSPACE=8,TAB=9,CLEAR=12,ENTER=13,RETURN=13,NUMPADENTER=13,
 SHIFT=16,CTRL=17,CONTROL=17,ALT=18,PAUSE=19,BREAK=3,CAPSLOCK=20,
 ESC=27,ESCAPE=27,SPACE=32,PAGEUP=33,PGUP=33,PAGEDOWN=34,PGDN=34,
 END=35,HOME=36,LEFT=37,UP=38,RIGHT=39,DOWN=40,
 PRINTSCREEN=44,PRTSC=44,INSERT=45,INS=45,DELETE=46,DEL=46,
 LWIN=91,RWIN=92,APPS=93,MENU=93,SLEEP=95,
 NUMPADMULTIPLY=106,NUMPADADD=107,NUMPADSEPARATOR=108,
 NUMPADSUBTRACT=109,NUMPADDECIMAL=110,NUMPADDIVIDE=111,
 NUMLOCK=144,SCROLLLOCK=145,LSHIFT=160,RSHIFT=161,
 LCTRL=162,RCTRL=163,LCONTROL=162,RCONTROL=163,LALT=164,RALT=165,
 BROWSER_BACK=166,BROWSER_FORWARD=167,BROWSER_REFRESH=168,BROWSER_STOP=169,
 BROWSER_SEARCH=170,BROWSER_FAVORITES=171,BROWSER_HOME=172,
 VOLUME_MUTE=173,VOLUME_DOWN=174,VOLUME_UP=175,
 MEDIA_NEXT=176,MEDIA_PREVIOUS=177,MEDIA_STOP=178,MEDIA_PLAY_PAUSE=179,
 LAUNCH_MAIL=180,LAUNCH_MEDIA=181,LAUNCH_APP1=182,LAUNCH_APP2=183,CALCULATOR=183,
 SEMICOLON=186,EQUALS=187,COMMA=188,MINUS=189,PERIOD=190,SLASH=191,
 BACKQUOTE=192,GRAVE=192,LBRACKET=219,BACKSLASH=220,RBRACKET=221,APOSTROPHE=222,
 OEM_102=226,
}
local modifiers={SHIFT={1,1},LSHIFT={1,2},RSHIFT={1,3},
 CTRL={2,1},CONTROL={2,1},LCTRL={2,2},LCONTROL={2,2},RCTRL={2,3},RCONTROL={2,3},
 ALT={3,1},LALT={3,2},RALT={3,3},WIN={4,1},LWIN={4,2},RWIN={4,3}}
local function single(value)
 if M.names[value] then return M.names[value] end
 if value:match('^[A-Z0-9]$') then return value:byte() end
 local f=tonumber(value:match('^F(%d+)$'))
 if f and f>=1 and f<=24 then return 111+f end
 local num=tonumber(value:match('^NUMPAD(%d)$'))
 if num then return 96+num end
end
function M.key(value)
 if type(value)~='string' then return nil end
 value=value:upper():match('^%s*(.-)%s*$')
 if value=='NONE' then return 0 end
 if not value:find('+',1,true) then return single(value) end
 local parts={};for p in (value..'+'):gmatch('(.-)%+') do
  p=p:match('^%s*(.-)%s*$');if p=='' then return nil end;parts[#parts+1]=p
 end
 if #parts<2 or #parts>5 then return nil end
 local primary=single(parts[#parts]);if not primary or modifiers[parts[#parts]] then return nil end
 local mask,seen=0,{}
 for i=1,#parts-1 do
  local m=modifiers[parts[i]];if not m or seen[m[1]] then return nil end
  seen[m[1]]=true;mask=mask+m[2]*4^(m[1]-1)
 end
 return primary+256*mask
end
function M.overlap(a,b)
 if a==0 or b==0 then return false end
 if a%256~=b%256 then
  local sides={ [16]={1,1},[160]={1,2},[161]={1,3},[17]={2,1},[162]={2,2},[163]={2,3},
   [18]={3,1},[164]={3,2},[165]={3,3},[91]={4,2},[92]={4,3} }
  local x,y=sides[a%256],sides[b%256]
  if x and y then return x[1]==y[1] and (x[2]==1 or y[2]==1 or x[2]==y[2]) end
  -- A standalone modifier would fire before its chord's primary key. Reject
  -- assigning it and an overlapping chord to different seats in one vehicle.
  if not x then x=sides[b%256];a,b=b,a end
  if not x then return false end
  local want=math.floor(math.floor(b/256)/4^(x[1]-1))%4
  return want~=0 and (x[2]==1 or want==1 or x[2]==want)
 end
 a=math.floor(a/256);b=math.floor(b/256)
 for _=1,4 do
  local x,y=a%4,b%4
  if (x==0)~=(y==0) or (x>=2 and y>=2 and x~=y) then return false end
  a=math.floor(a/4);b=math.floor(b/4)
 end
 return true
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
   if code~=0 then
    for previous in pairs(seen) do if M.overlap(previous,code) then conflict=true end end
    seen[code]=seat
   end
  end
  if conflict then
   -- Revert the entire vehicle mapping, avoiding cascading default conflicts.
   for seat,key in pairs(M.defaults[vehicle]) do keys[seat]=M.key(key) end
   issues[#issues+1]='Duplicate/overlapping key in '..vehicle..'; restored this vehicle defaults'
  end
 end
 return result,issues
end
function M.template()
 local rows={'; Vehicle Seat Switch — restart game after editing.',
 '; Location: %APPDATA%/Arrowhead/Helldivers2/VehicleSeatSwitch.ini',
 '; Keys: see KEYS_按键清单.txt in the mod ZIP. Defaults stay F1-F5.',
 '; Examples: CTRL+1, SHIFT+Q, CTRL+SHIFT+MOUSE4, RCTRL+NUMPAD1.',
 '; Press modifiers before the last key; extra modifiers do not match.',
 '; NUMPAD0-NUMPAD9 require Num Lock ON. NONE disables a binding.',
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
