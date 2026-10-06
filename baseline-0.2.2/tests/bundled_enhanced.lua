-- HD2-Addon: mods/vehicle_seat_tools/vehicle_seat_switch
local MODE="enhanced"
local profile=(function()
local function bytes(hex)return hex:gsub("..",function(x)return string.char(tonumber(x,16)) end) end
return {enabled=true, source_build=25327279, experimental=true, direct_solo_only=true,
game_sha256="73374bd4e38386beb9a23bef480082b67d457ebc77485fbec5f488b4e95e201f",
exe_sha256="d8e23968d1412b07e06785321727d63edf74e711214d6f6adeb3bfca95ca6827",
globals={mission=0x33266a0,player=0x3326468,entities=0x346bf98,avatar=0x3326d20,seater=0x3326d78,collection=0x3326d88,session=0x347cef0,inventory=0x3326738},
layout={entity_unit_map=0xf22ec8,entity_records=0xf32f18},
functions={
['next']={rva=0x63e740,bytes=bytes("405355565741574883ec308b05cf54e4028bfa4c8b3d1e86ce023bd07442458b")},
['previous']={rva=0x63e910,bytes=bytes("48895c2420555657415641574883ec308b05fa52e4024533f68bfa4c8bf93bd0")},
['reserve']={rva=0x6344d0,bytes=bytes("48895c240848896c241848897424205741544155415641574883ec30488b4138")},
['release']={rva=0x6349b0,bytes=bytes("48895c241855565741544155415641574883ec30488b41384c8be98bfa418bf0")},
['authority']={rva=0x635710,bytes=bytes("48895c240848896c241848897424205741544155415641574883ec20418bf145")},
['set_role']={rva=0x63dd10,bytes=bytes("4c8bdc415441554881ece8000000488b05ebe2ff014833c448898424b0000000")},
['restore_seated']={rva=0x63eb10,bytes=bytes("4585c90f847801000053574883ec2848896c2440418bd84889742448418bf933")},
['net_ref']={rva=0xfd9a40,bytes=bytes("4883ec083b0d22ab4a02750c488d05f1aa17014883c408c34c8b153925490245")},
['send']={rva=0xbde430,bytes=bytes("4053555657415641574881ec98000000488b05c9dba5014833c4488984248000")},
['ownership_busy']={rva=0xfde390,bytes=bytes("48895c240848896c2410488974241848897c242041564883ec204c8b31488bd9")},
['active_passenger']={rva=0x63b120,bytes=bytes("48895c241055565741544155415641574881eca0000000488b05d20e00024833")},
['transition_receive']={rva=0x63ecc0,bytes=bytes("48895c2418554883ec20443b054f4fe402418be9458bd04c8bd97507b8ffffff")},
['goto_node']={rva=0x63a670,bytes=bytes("4c8bdc53554881ec98000000488b058d1900024833c44889842480000000488b")},
['role']={rva=0x11957c0,bytes=bytes("ffc983f92c0f87be0100004863c14c8d052ba8e6fe410fb68400d4591901418b")},
['adjacency']={rva=0x11966f0,bytes=bytes("ffc983f92c0f87a00200004c8d05fe98e6fe4863c1418b8480a06919014903c0")},
['route']={rva=0x1196dc0,bytes=bytes("ffc983f92c0f87c40800004c8d152e92e6fe4863c1418b8482987619014903c2")},
['restore_action']={rva=0x119a6b0,bytes=bytes("ffc983f92c0f87d80100004863c1488d0d3b59e6fe8b84819ca819014803c1ff")},
['clear_vehicle_weapon']={rva=0x11a7f80,bytes=bytes("48895c241848896c2420565741544883ec208b410833ff3b0583bc2d02488b35")},
['restore_personal_weapon']={rva=0x11b1070,bytes=bytes("41574883ec308b41084c8bf9448b059d2b2d02413bc00f844101000048895c24")},
['refresh_weapon_context']={rva=0x11b0910,bytes=bytes("40534883ec208b41083b0501332d020f848e0000004c8b05f463170233d24889")},
['remove_avatar_flag']={rva=0x11b11f0,bytes=bytes("4885c90f849101000041564883ec40488b050aae48014833c44889442438f641")},
['seat_action']={rva=0x119b0a0,bytes=bytes("48895c2410488974241848897c24205541564157488bec4883ec70ffc90f2974")},
['avatar_rotation']={rva=0x6ba600,bytes=bytes("41563b151896dc02450fb6f04c8b15a5c0c6020f848a000000458b4a3833c048")},
['equip_current_personal_weapon']={rva=0x11a7900,bytes=bytes("40534883ec208b5108488bd9e88f0b80ff8b5308448bc0ffc8b90100000083f8")},
},engine_functions={
['unit']={rva=0x9d8c0,bytes=bytes("48895c24084889742410574883ec20488b351a2897018bd9488d8ed0000000ff")},
['animation_set_states']={rva=0x201ee0,bytes=bytes("48895c2408574883ec20488bfae8ceb9e9ff488bc8488bd84c8b0041ff90b001")},
['animation_get_states']={rva=0x201f70,bytes=bytes("48895c2408574883ec20488bf98bcae83cb9e9ff488bc8488bd8488b10ff92b0")},
['animation_component']={rva=0x2bd9c0,bytes=bytes("488b8178010000c3cccccccccccccccc488b8158030000488902488bc2c3cccc")},
['animation_event_enqueue']={rva=0x12fd00,bytes=bytes("48895c240848896c24104889742418574883ec20488bf1418be88bca8bdae89d")},
},animation={unit_vtable=0x1676d70,component_offset=0x178,layers=31,
queue={world_offset=0x18,count_offset=0x170038,records_offset=0x10038,stride=0x58,capacity=16384,
end_event=bytes("648eb8da"),entry_events={
[0x29e8fb0c]=true,
[0xb32ac618]=true,
[0x929e2ba1]=true,
[0xa44b4a4]=true,
[0xe86f3c8c]=true,
[0xd3a9222b]=true,
[0xe8344235]=true,
}},states={
front_left={{layer=0,count=124,index=108,hash=bytes("70908c65b58587c2")},{layer=13,count=104,index=64,hash=bytes("748fa5c0c0acbcc7")}},
front_right={{layer=0,count=124,index=112,hash=bytes("3f6c85c24fe14af1")},{layer=13,count=104,index=68,hash=bytes("2bd375776ab53cc1")}},
back_left={{layer=0,count=124,index=106,hash=bytes("718f076960feec38")},{layer=13,count=104,index=62,hash=bytes("4f6d0ff4c3d4a9e7")}},
back_right={{layer=0,count=124,index=110,hash=bytes("3a14a137f69d534f")},{layer=13,count=104,index=66,hash=bytes("c78ac26a45f2855a")}},
frv_gunner={{layer=0,count=124,index=104,hash=bytes("e769413f00ec4334")},{layer=13,count=104,index=60,hash=bytes("2b1c29144f6b5246")}},
tank_top={{layer=0,count=124,index=123,hash=bytes("3d23343383b39bf7")},{layer=13,count=104,index=102,hash=bytes("e67dffbc4cbca3d4")}},
tank_gunner={{layer=0,count=124,index=121,hash=bytes("382c8feedc5204d0")},{layer=13,count=104,index=96,hash=bytes("4dac2faec2ed74d9")}},
}},tables={
m102={rva=0x31b0370,row=8,size=40,transition=26,roles={1,3,3,3,2},restore={0,1,2,3,5}},
m103={rva=0x31b1910,row=8,size=32,transition=27,roles={1,3,3,3},restore={0,1,2,3}},
m104={rva=0x31aa620,row=8,size=24,transition=28,roles={1,3,2},restore={0,1,3}},
bastion={rva=0x31aff20,row=12,size=48,transition=43,roles={1,2,3,3},restore={0,1,2,3}},
maelstrom={rva=0x31ac7e0,row=12,size=48,transition=44,roles={1,2,3,3},restore={0,1,2,3}},
tanker={rva=0x31acef8,row=8,size=16,transition=33,roles={1,2},restore={3,4}},
}}

end)()
local policy=(function()
-- Logical seat names only: native indices must be independently verified.
local M = {}
M.seats = {
    m102 = {'driver', 'front_passenger', 'rear_left', 'rear_right', 'gunner'},
    m103 = {'driver', 'front_passenger', 'rear_left', 'rear_right'},
    m104 = {'driver', 'front_passenger', 'flamer'},
    bastion = {'driver', 'gunner', 'passenger_left', 'passenger_right'},
    maelstrom = {'driver', 'gunner', 'passenger_left', 'passenger_right'},
    tanker = {'driver', 'gunner'},
}
local normal_groups = {
    m102 = {{'driver', 'front_passenger'}, {'rear_left', 'rear_right'}},
    m103 = {{'driver', 'front_passenger'}, {'rear_left', 'rear_right'}},
    m104 = {{'driver', 'front_passenger'}},
    bastion = {{'gunner', 'passenger_left', 'passenger_right'}},
    maelstrom = {{'gunner', 'passenger_left', 'passenger_right'}},
    tanker = {{'driver', 'gunner'}},
}
local function contains(list, item)
    for _, value in ipairs(list or {}) do if item == value then return true end end
    return false
end
function M.check(mode, vehicle, current, target, occupied)
    if mode ~= 'normal' and mode ~= 'enhanced' then return false, 'invalid_mode' end
    local seats = M.seats[vehicle]
    if not seats or not contains(seats, current) or not contains(seats, target) then
        return false, 'invalid_seat'
    end
    if current == target then return false, 'already_seated' end
    -- Unknown occupancy must never be treated as an empty seat.
    if occupied ~= false then return false, occupied == true and 'occupied' or 'unknown_occupancy' end
    if mode == 'enhanced' then return true end
    for _, group in ipairs(normal_groups[vehicle]) do
        if contains(group, current) and contains(group, target) then return true end
    end
    return false, 'normal_restriction'
end
return M

end)()
local config=(function()
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

end)()
local platform=(function()
return function()
 local ffi=require('ffi')
 assert(ffi.abi('64bit'),'Windows x64 required')
 ffi.cdef[[
 void *GetModuleHandleA(const char *);
 uint32_t GetModuleFileNameW(void *,uint16_t *,uint32_t);
 void *GetCurrentProcess(void);
 uint32_t GetCurrentProcessId(void);
 uint64_t GetTickCount64(void);
 int ReadProcessMemory(void *,const void *,void *,size_t,size_t *);
 int WriteProcessMemory(void *,void *,const void *,size_t,size_t *);
 void *GetForegroundWindow(void);
 uint32_t GetWindowThreadProcessId(void *,uint32_t *);
 int16_t GetAsyncKeyState(int);
 typedef struct { uint32_t cbSize; uint32_t flags; void *cursor; int32_t x; int32_t y; } VSSCursorInfo;
 int GetCursorInfo(VSSCursorInfo *);
 void *CreateFileW(const uint16_t *,uint32_t,uint32_t,void *,uint32_t,uint32_t,void *);
 int ReadFile(void *,void *,uint32_t,uint32_t *,void *);
 int CloseHandle(void *);
 int CreateDirectoryA(const char *,void *);
 uint32_t GetFileAttributesA(const char *);
 int32_t BCryptOpenAlgorithmProvider(void **,const uint16_t *,const uint16_t *,uint32_t);
 int32_t BCryptCloseAlgorithmProvider(void *,uint32_t);
 int32_t BCryptCreateHash(void *,void **,void *,uint32_t,const void *,uint32_t,uint32_t);
 int32_t BCryptHashData(void *,const void *,uint32_t,uint32_t);
 int32_t BCryptFinishHash(void *,void *,uint32_t,uint32_t);
 int32_t BCryptDestroyHash(void *);
 ]]
 local k,u,c=ffi.load('kernel32'),ffi.load('user32'),ffi.load('bcrypt')
 local a={ffi=ffi};local process=k.GetCurrentProcess()
 local scratch=ffi.new('uint8_t[32768]');local transferred=ffi.new('size_t[1]')
 function a.config_directory()
  local base=assert(os.getenv('APPDATA'),'APPDATA unavailable')
  assert(base~='','APPDATA is empty')
  local directory=base..'/Arrowhead'
  for _,path in ipairs({directory,directory..'/Helldivers2'}) do
   local attributes=k.GetFileAttributesA(path)
   if attributes==0xffffffff then
    assert(k.CreateDirectoryA(path,nil)~=0,'Cannot create configuration directory: '..path)
   else assert(require('bit').band(attributes,0x10)~=0,'Configuration path is not a directory: '..path) end
  end
  return directory..'/Helldivers2'
 end
 function a.module(name)
  local v=k.GetModuleHandleA(name);if v~=nil then return ffi.cast('uint8_t *',v) end
 end
 function a.read(address,size)
  if not address or size<1 or size>32768 or size%1~=0 then return nil end
  transferred[0]=0
  if k.ReadProcessMemory(process,address,scratch,size,transferred)==0 or tonumber(transferred[0])~=size then return nil end
  return ffi.string(scratch,size)
 end
 function a.pointer(bytes,offset)
  offset=offset or 0;if not bytes or #bytes<offset+8 then return nil end
  local p=ffi.new('uint64_t[1]');ffi.copy(p,bytes:sub(offset+1,offset+8),8)
  local v=tonumber(p[0]);if v<65536 or v>=2^47 then return nil end
  return ffi.cast('uint8_t *',p[0])
 end
 function a.number(p)return tonumber(ffi.cast('uintptr_t',p))end
 function a.now()return tonumber(k.GetTickCount64())/1000 end
 function a.focused()
  local w=u.GetForegroundWindow();if w==nil then return false end
  local p=ffi.new('uint32_t[1]');u.GetWindowThreadProcessId(w,p)
  return p[0]==k.GetCurrentProcessId()
 end
 function a.down(code)return code~=0 and u.GetAsyncKeyState(code)<0 end
 function a.input_allowed()
  if not a.focused() then return false end
  local info=ffi.new('VSSCursorInfo');info.cbSize=ffi.sizeof(info)
  return u.GetCursorInfo(info)~=0 and info.flags==0
 end
 -- Compare-before-write for small validated data fields. No executable code patching.
 function a.replace(address,before,after)
  if #before~=#after or #after>24 or a.read(address,#before)~=before then return false end
  transferred[0]=0
  return k.WriteProcessMemory(process,address,after,#after,transferred)~=0 and tonumber(transferred[0])==#after
 end
 function a.hash_module(handle)
  local wide=ffi.new('uint16_t[32768]');local n=k.GetModuleFileNameW(handle,wide,32768)
  assert(n>0 and n<32768,'Module filename unavailable')
  local file=k.CreateFileW(wide,0x80000000,7,nil,3,0x08000000,nil)
  assert(file~=ffi.cast('void *',-1),'Module file unavailable')
  local algorithm,hash=ffi.new('void *[1]'),ffi.new('void *[1]')
  local ok,value=pcall(function()
   local sha=ffi.new('uint16_t[7]',{83,72,65,50,53,54,0})
   assert(c.BCryptOpenAlgorithmProvider(algorithm,sha,nil,0)==0,'SHA256 provider failed')
   assert(c.BCryptCreateHash(algorithm[0],hash,nil,0,nil,0,0)==0,'SHA256 initialization failed')
   local block,count=ffi.new('uint8_t[262144]'),ffi.new('uint32_t[1]')
   repeat
    assert(k.ReadFile(file,block,262144,count,nil)~=0,'Module read failed')
    if count[0]>0 then assert(c.BCryptHashData(hash[0],block,count[0],0)==0,'SHA256 read failed') end
   until count[0]==0
   local digest=ffi.new('uint8_t[32]');assert(c.BCryptFinishHash(hash[0],digest,32,0)==0,'SHA256 finish failed')
   local hex={};for i=0,31 do hex[#hex+1]=string.format('%02x',digest[i]) end;return table.concat(hex)
  end)
  if hash[0]~=nil then c.BCryptDestroyHash(hash[0]) end
  if algorithm[0]~=nil then c.BCryptCloseAlgorithmProvider(algorithm[0],0) end
  k.CloseHandle(file);if not ok then error(value) end;return value
 end
 return a
end

end)()
local snapshot=(function()
local ffi,bit=require('ffi'),require('bit')
local M={}
local function u32(b,o)
 local a,b1,c,d=b:byte(o+1,o+4);assert(d,'Short integer read');return a+b1*256+c*65536+d*16777216
end
local function i32(b,o)local v=u32(b,o);return v>=2147483648 and v-4294967296 or v end
local function hash(s)return s:gsub('..',function(p)return string.char(tonumber(p,16)) end):reverse() end
M.u32=u32;M.i32=i32
local AVATAR=hash('4d1c334d294dfa97')
M.vehicles={
 [hash('cc21c7ffd3ebefb9')]='m102',
 [hash('e9cd1d0d118886af')]='m102',
 [hash('9b2140378640432e')]='m103',
 [hash('2d85bfe3d8717fe5')]='m104',
 [hash('16474112801385b6')]='bastion',
 [hash('b0c9faf4af8903f9')]='maelstrom',
 [hash('423ff97d57ab04f5')]='tanker',
}
function M.current(api,s)
 for _,g in ipairs(s.guards) do if api.read(g.address,#g.bytes)~=g.bytes then return false end end
 return true
end
function M.capture(api,game,build)
 assert(build and build.source_build==25327279,'Missing validated build profile')
 local s={guards={},reads=0}
 local function get(address,size)
  s.reads=s.reads+1;assert(s.reads<=300,'Read limit')
  local data=api.read(address,size);assert(data and #data==size,'Unreadable state')
  s.guards[#s.guards+1]={address=address,bytes=data};return data
 end
 local function ptr(data,offset)local p=api.pointer(data,offset);assert(p,'Invalid pointer');return p end
 local function global(rva)return ptr(get(game+rva,8))end
 local function lookup(header,key,maxcap)
  local cap,empty,mult=u32(header,8),u32(header,12),u32(header,16)
  if cap==0 then return nil end
  assert(cap<=maxcap and bit.band(cap,cap-1)==0,'Invalid map size')
  local data=ptr(header)
  local start=tonumber(ffi.cast('uint32_t',ffi.new('uint64_t',key)*ffi.new('uint64_t',mult)))
  for j=0,math.min(64,cap)-1 do
   local row=get(data+8*bit.band(start+j,cap-1),8)
   if u32(row,0)==key then local n=u32(row,4);return n~=0xffffffff and n or nil end
   if u32(row,0)==empty then return nil end
  end
  return nil
 end
 local mission=get(global(build.globals.mission),0x44)
 if u32(mission,8)==0 or u32(mission,0x40)<1 or u32(mission,0x40)>7 then return nil,'not_in_mission' end
 local pm=global(build.globals.player);local counts=get(pm+0x84,8)
 assert(u32(counts,0)<=4 and u32(counts,4)<=4,'Unsupported player count')
 if u32(counts,0)==0 or u32(counts,4)==0 then return nil,'no_player' end
 s.player_count=u32(counts,0)
 s.peer_count=u32(get(global(build.globals.session)+0x162d8,4),0)
 assert(s.peer_count<=4,'Unsupported peer count')
 local player=get(ptr(get(pm+0xe8,8)),24)
 if bit.band(player:byte(21),1)==0 then return nil,'no_local_player' end
 local unit=u32(get(pm+0x3a8,4),0)
 if unit==0x7fff then return nil,'no_avatar' end
 local entities=global(build.globals.entities)
 local ei=lookup(get(entities+build.layout.entity_unit_map,20),unit,1048576)
 if not ei then return nil,'no_avatar' end
 assert(ei<262144,'Entity index exceeds bound')
 s.avatar_address=entities+build.layout.entity_records+ei*24
 local avatar=get(s.avatar_address,24)
 if avatar:sub(1,8)~=AVATAR or bit.band(avatar:byte(21),1)==0 then return nil,'not_local_avatar' end
 s.avatar=u32(avatar,8);s.avatar_unit=u32(avatar,12)
 local avatars=global(build.globals.avatar);local ai=lookup(get(avatars+0xf8,20),s.avatar,64)
 if not ai then return nil,'no_avatar_component' end
 local acount=u32(get(avatars+0x6c,4),0)
 assert(acount<=8 and ai<acount,'Avatar index exceeds bound')
 if get(ptr(get(avatars+0x110+ai*8,8)),24)~=avatar then return nil,'avatar_mismatch' end
 -- Read the same permission bit tested by native vehicle input at a7d450.
 local vehicle_input=u32(get(avatars+0x53e88c+ai*0x1238,4),0)
 if bit.band(vehicle_input,0x40000)==0 then return nil,'native_vehicle_input_inactive' end
 s.seaters=global(build.globals.seater)
 local sh=get(s.seaters,0x50);local count=u32(sh,0xc)
 assert(count<=u32(sh,8) and u32(sh,8)<=256,'Invalid seater count')
 local si=lookup(sh:sub(0x21,0x34),s.avatar,1024)
 if not si or si>=count then return nil,'not_seated' end
 s.seater_index=si
 if get(ptr(get(ptr(sh,0x38)+si*8,8)),24)~=avatar then return nil,'seater_mismatch' end
 local states=get(ptr(sh,0x48),count*64)
 s.seater=ptr(sh,0x48)+si*64
 local current=states:sub(si*64+1,(si+1)*64)
 s.seater_bytes=current;s.collection=u32(current,0)
 if s.collection==0 or s.collection==0xffffffff then return nil,'not_seated' end
 s.node=i32(current,0x1c);s.active=current:byte(0x32)==1
 if current:byte(0x31)~=0 or i32(current,0x14)~=s.node or s.node<0 then return nil,'transition_in_progress' end
 if i32(current,0x18)~=-1 or i32(current,0x20)~=-1 then return nil,'transition_pending' end
 s.collections=global(build.globals.collection)
 local ch=get(s.collections,0x58)
 local cc=u32(ch,0xc);assert(cc<=u32(ch,8) and u32(ch,8)<=256,'Invalid collection count')
 local ci=lookup(ch:sub(0x21,0x34),s.collection,1024)
 if not ci or ci>=cc then return nil,'no_vehicle_component' end
 s.collection_index=ci
 s.collection_address=ptr(get(ptr(ch,0x38)+ci*8,8))
 local vehicle=get(s.collection_address,24)
 assert(u32(vehicle,8)==s.collection,'Vehicle identity mismatch')
 local cs=get(ptr(ch,0x48)+ci*100,100)
 s.resource=vehicle:sub(1,8):reverse():gsub('.',function(c)return string.format('%02x',c:byte()) end)
 s.vehicle=M.vehicles[vehicle:sub(1,8)]
 if not s.vehicle then return nil,'unsupported_vehicle resource='..s.resource..' transition='..u32(cs,0) end
 s.profile=assert(build.tables[s.vehicle],'Missing vehicle table')
 s.owned=bit.band(vehicle:byte(21),1)~=0
 s.collection_unit=u32(vehicle,0x10)
 if u32(cs,0)~=s.profile.transition or u32(current,4)~=s.profile.transition then return nil,'transition_profile_mismatch' end
 s.transition=s.profile.transition
 if s.node>=#s.profile.roles or u32(current,8)~=s.profile.roles[s.node+1] then return nil,'seat_role_mismatch' end
 s.mask=u32(get(ptr(ch,0x50)+ci*12,12),0)
 if bit.band(s.mask,bit.lshift(1,s.node))~=0 then return nil,'current_seat_not_reserved' end
 s.occupied={}
 for node=0,#s.profile.roles-1 do s.occupied[node]=bit.band(s.mask,bit.lshift(1,node))==0 end
 for i=0,count-1 do
  local offset=i*64
  if i~=si and u32(states,offset)==s.collection then
   for _,field in ipairs({0x14,0x18,0x1c}) do
    local node=i32(states,offset+field)
    if node>=0 and node<#s.profile.roles then s.occupied[node]=true end
   end
  end
 end
 s.graph={}
 local graph=get(game+s.profile.rva,s.profile.row*#s.profile.roles)
 for node=0,#s.profile.roles-1 do
  local row,terminated={},false
  for j=0,s.profile.row/4-1 do
   local target=i32(graph,node*s.profile.row+j*4)
   if target==-1 then terminated=true;break end
   assert(target>=0 and target<#s.profile.roles,'Unsupported seat adjacency')
   row[#row+1]=target
  end
  assert(terminated,'Unterminated seat adjacency');s.graph[node]=row
 end
 s.identity=avatar:sub(1,20)..vehicle:sub(1,20)
 return s
end
-- The native next/previous helpers walk these lists and the free-seat mask.
function M.predictions(s)
 local function free(node)return bit.band(s.mask,bit.lshift(1,node))~=0 end
 local node,nextseat=s.node,nil;local visited={}
 for _=1,32 do
  if visited[node] then break end;visited[node]=true
  local row=s.graph[node];if not row or not row[1] then break end
  for _,target in ipairs(row) do if free(target) then nextseat=target;break end end
  if nextseat then break end
  node=row[1];if node==s.node then break end
 end
 node=s.node;local previous,done=nil,false;visited={}
 for _=1,32 do
  if visited[node] then break end;visited[node]=true
  local row=s.graph[node];if not row or not row[1] then break end
  local found
  for _,target in ipairs(row) do
   if free(target) then previous=target;found=target;break end
   if target==s.node then done=true;break end
  end
  if done then break end
  node=found or row[1]
 end
 return nextseat,done and previous or nil
end
return M

end)()
local bind_pose=(function()
-- Select only the two vehicle pose layers. All other layers are preserved.
-- IDs/hashes come from this build's avatar state machine, not guessed names.
return function(api,profile)
 local ffi=api.ffi
 local exe=assert(api.module('helldivers2.exe'),'Missing engine module')
 local function bind(name,ctype)
  local p=assert(profile.engine_functions[name])
  assert(api.read(exe+p.rva,#p.bytes)==p.bytes,'Engine signature mismatch: '..name)
  return ffi.cast(ctype,exe+p.rva)
 end
 local unit=bind('unit','void *(*)(uint32_t)')
 local set_states=bind('animation_set_states','void (*)(uint32_t,const int32_t *)')
 local get_states=bind('animation_get_states','void *(*)(int32_t *,uint32_t)')
 local getter=profile.engine_functions.animation_component
 assert(api.read(exe+getter.rva,#getter.bytes)==getter.bytes,'Animation component signature mismatch')
 local enqueue=profile.engine_functions.animation_event_enqueue
 assert(api.read(exe+enqueue.rva,#enqueue.bytes)==enqueue.bytes,'Animation queue signature mismatch')
 local layout=profile.animation
 local targets={m102={'front_left','front_right','back_left','back_right','frv_gunner'},
  m103={'front_left','front_right','back_left','back_right'},
  m104={'front_left','front_right','frv_gunner'},
  bastion={'tank_top','tank_gunner','tank_top','tank_top'},
  maelstrom={'tank_top','tank_gunner','tank_top','tank_top'}}
 local p={}
 local function read(address,n)
  local b=api.read(address,n);assert(b and #b==n,'Unreadable animation state');return b
 end
 local function ptr(address)return assert(api.pointer(read(address,8)),'Invalid animation pointer') end
 local function u32(b,o)
  local a,c,d,e=b:byte(o+1,o+4);assert(e);return a+c*256+d*65536+e*16777216
 end
 local function offset(n)assert(n>=0 and n<0x2000000,'Animation offset exceeds bound');return n end
 function p.check(s)
  assert(targets[s.vehicle],'No direct pose profile')
  local object=unit(s.avatar_unit);assert(object~=nil,'Avatar engine unit expired')
  object=ffi.cast('uint8_t *',object)
  local vtable=ptr(object)
  assert(vtable==exe+layout.unit_vtable,'Unsupported avatar unit class')
  assert(ptr(vtable+0x1b0)==exe+getter.rva,'Animation component accessor changed')
  -- This getter is exactly mov rax,[rcx+178h];ret. Read it without an indirect call.
  local machine=ptr(object+layout.component_offset)
  local resource=ptr(machine+0x28);local header=read(resource,60)
  assert(u32(header,4)==layout.layers,'Avatar animation layer count changed')
  local groups=resource+offset(u32(header,8))
  local group_table=read(groups,4+layout.layers*4)
  assert(u32(group_table,0)==layout.layers,'Invalid animation group table')
  -- Validate bounds and every target state name before the first gameplay change.
  for _,pair in pairs(layout.states) do for _,state in ipairs(pair) do
   local layer=groups+offset(u32(group_table,4+state.layer*4))
   local row=read(layer,12+state.count*4)
   assert(u32(row,8)==state.count,'Avatar animation state count changed')
   local address=layer+offset(u32(row,12+state.index*4))
   assert(read(address,8)==state.hash,'Avatar animation state identity changed')
  end end
  local q=layout.queue;local world=ptr(object+q.world_offset)
  local count=u32(read(world+q.count_offset,4),0)
  assert(count<q.capacity-128,'Animation command queue near capacity')
  s.pose_context={object=object,world=world,start=count}
  return true
 end
 function p.apply(s,target)
  local name=assert(targets[s.vehicle][target+1],'No target pose')
  local context=assert(s.pose_context,'Pose was not validated')
  local q=layout.queue
  assert(ptr(context.object+q.world_offset)==context.world,'Animation world changed')
  local finish=u32(read(context.world+q.count_offset,4),0)
  assert(finish>=context.start and finish<=context.start+128,'Animation command batch changed')
  local skipped=0
  for i=context.start,finish-1 do
   local address=context.world+q.records_offset+i*q.stride
   local row=read(address,q.stride)
   -- Only this avatar's NEW entry events from this synchronous switch batch.
   -- Keep all earlier commands, other units, non-entry events, and queue counts.
   if u32(row,0)==s.avatar_unit and u32(row,0x50)==3 and q.entry_events[u32(row,4)] then
    assert(read(address,q.stride)==row and api.replace(address+4,row:sub(5,8),q.end_event),'Entry event changed')
    skipped=skipped+1
   end
  end
  -- Unit.animation_event queues commands. Setting a pose alone is insufficient:
  -- the queued entry clip would otherwise overwrite it at the next world update.
  -- Its normal completion event has no outgoing link on any selected final pose.
  local values=ffi.new('int32_t[33]')
  for i=0,31 do values[i]=-1 end -- engine leaves these layers untouched
  for _,state in ipairs(layout.states[name]) do values[state.layer]=state.index end
  values[32]=14 -- highest selected layer is 13; no other layer is reset
  set_states(s.avatar_unit,values)
  local actual=ffi.new('int32_t[33]');get_states(actual,s.avatar_unit)
  assert(actual[32]==layout.layers,'Animation layer count changed during switch')
  for _,state in ipairs(layout.states[name]) do
   assert(actual[state.layer]==state.index,'Engine did not apply the requested seat pose')
  end
  return 'pose_layers='..tonumber(actual[0])..','..tonumber(actual[13])..' entry_action_skipped=true entry_events_replaced='..skipped
 end
 return p
end

end)()
local bind_native=(function()
-- ABI recovered from Steam build 25327279. This is an in-game TEST adapter.
-- Native code has no recoverable Lua exception boundary; profile and identity
-- checks must complete before calling it. No arbitrary address is accepted.
return function(api,game,profile,pose_factory,trace)
 local ffi=api.ffi
 local n={}
 local transaction=0
 local function mark(stage)
  if trace then pcall(trace,'direct_stage id='..transaction..' stage='..stage) end
 end
 local function bind(name,ctype)
  local p=assert(profile.functions[name],name)
  assert(api.read(game+p.rva,#p.bytes)==p.bytes,'Native signature mismatch: '..name)
  return ffi.cast(ctype,game+p.rva)
 end
 n.next=bind('next','void (*)(void *,uint32_t)')
 n.previous=bind('previous','void (*)(void *,uint32_t)')
 local reserve=bind('reserve','void (*)(void *,uint32_t,int32_t)')
 local release=bind('release','void (*)(void *,uint32_t,int32_t)')
 local authority=bind('authority','void (*)(void *,uint32_t,int32_t,uint32_t)')
 local set_role=bind('set_role','void (*)(void *,uint32_t,uint32_t)')
 local restore_seated=bind('restore_seated','void (*)(void *,void *,uint32_t,uint32_t,int32_t,bool)')
 local ownership_busy=bind('ownership_busy','bool (*)(void *,uint32_t)')
 local active_passenger=bind('active_passenger','void (*)(void *,uint32_t,bool)')
 local clear_weapon=bind('clear_vehicle_weapon','void (*)(void *,uint32_t)')
 local restore_personal=bind('restore_personal_weapon','void (*)(void *)')
 local equip_personal=bind('equip_current_personal_weapon','void (*)(void *)')
 local refresh_weapon=bind('refresh_weapon_context','void (*)(void *)')
 local remove_flag=bind('remove_avatar_flag','void (*)(void *,uint32_t)')
 local action=bind('seat_action','float (*)(uint32_t,uint32_t,int32_t,int32_t)')
 local rotation=bind('avatar_rotation','void (*)(void *,uint32_t,bool)')
 local pose
 -- The native equip-current helper assumes a live inventory component. Validate
 -- its map, entity identity and selected weapon before any seat mutation.
 local function personal_ready(s)
  local function get(a,n)local b=api.read(a,n);assert(b and #b==n,'Unreadable personal inventory');return b end
  local function ptr(b)local p=api.pointer(b);assert(p,'Invalid personal inventory pointer');return p end
  local function u32(b,o)local a,c,d,e=b:byte(o+1,o+4);return a+c*256+d*65536+e*16777216 end
  local inv=ptr(get(game+profile.globals.inventory,8))
  local h=get(inv+0x28,20);local cap,empty,mult=u32(h,8),u32(h,12),u32(h,16)
  local bit=require('bit')
  assert(cap>0 and cap<=4096 and bit.band(cap,cap-1)==0,'Invalid inventory map')
  local rows=ptr(h)
  local start=tonumber(ffi.cast('uint32_t',ffi.new('uint64_t',s.avatar)*ffi.new('uint64_t',mult)))
  local index
  for j=0,math.min(cap,64)-1 do
   local row=get(rows+8*bit.band(start+j,cap-1),8)
   if u32(row,0)==s.avatar then index=u32(row,4);break end
   if u32(row,0)==empty then break end
  end
  assert(index and index<1024,'Missing personal inventory')
  local owner=ptr(get(ptr(get(inv+0x40,8))+index*8,8))
  assert(owner==s.avatar_address,'Personal inventory identity mismatch')
  local data=get(ptr(get(inv+0x50,8))+index*48,48)
  local slot=u32(data,0x1c);assert(slot<=6,'Invalid personal weapon selection')
  -- Native completion preserves slots 1..4 and falls back to 1 otherwise.
  local offset=({[1]=0,[2]=4,[3]=8,[4]=16})[slot] or 0
  local weapon=u32(data,offset)
  assert(weapon~=0 and weapon~=0xffffffff,'Missing selected personal weapon')
  return true
 end
 local function pose_ready(s)
  if not pose then pose=assert(pose_factory,'Missing pose adapter')(api,profile) end
  return pose.check(s)
 end
 function n.available(s)
  if not s.owned then return false,'vehicle_owned_by_other_peer' end
  -- The first gameplay test must establish local pose/control correctness before
  -- enabling the unverified multiplayer restore protocol. Native group switches
  -- still use the game's normal owner arbitration in either package variant.
  if not profile.direct_solo_only or s.player_count~=1 or s.peer_count>1 then return false,'direct_multiplayer_not_validated' end
  local systems=api.pointer(api.read(game+profile.globals.entities,8))
  if not systems then return false,'missing_engine' end
  -- The native request checks the entity system -> +8 before ownership handoff.
  local engine=api.pointer(api.read(systems+8,8))
  if not engine then return false,'missing_engine' end
  if s.collection_unit~=0x7fff and ownership_busy(engine,s.collection_unit) then
   return false,'vehicle_authority_changing'
  end
  local ok,why=pcall(pose_ready,s)
  if not ok then return false,'direct_pose_unavailable '..tostring(why) end
  return true
 end
 function n.prepare(s)active_passenger(s.seaters,s.avatar,false) end
 function n.direct(s,target)
  assert(type(target)=='number' and target%1==0 and target>=0 and target<#s.profile.roles and target~=s.node and s.occupied[target]==false,'Invalid direct target')
  assert(s.owned and not s.active,'Direct operation requires local vehicle authority')
  assert(profile.direct_solo_only and s.player_count==1 and s.peer_count<=1,'Multiplayer direct restore not validated')
  assert(pose_ready(s))
  if s.profile.roles[target+1]==3 then assert(personal_ready(s)) end
  -- These routines update the replicated seat mask and linked interactables.
  -- They are only called on the owning peer after fresh occupancy checks.
  transaction=transaction+1
  mark('reserve_target')
  reserve(s.collections,s.collection_index,target)
  -- The original switch/exit paths stop a mounted weapon before unbinding it.
  -- Both channels matter: tanks use channel 1 for the coaxial gun, and the
  -- Maelstrom driver uses channel 0 for the smoke launcher.
  mark('stop_old_weapon_0')
  clear_weapon(s.avatar_address,0)
  mark('stop_old_weapon_1')
  clear_weapon(s.avatar_address,1)
  mark('restore_personal_weapon')
  restore_personal(s.avatar_address)
  mark('refresh_weapon_context')
  refresh_weapon(s.avatar_address)
  mark('clear_old_seat_flags')
  if s.vehicle=='maelstrom' then remove_flag(s.avatar_address,44) end
  if (s.vehicle=='m102' or s.vehicle=='m104') and s.profile.roles[s.node+1]==2 then
   rotation(nil,s.avatar,true)
  end
  mark('release_old_seat')
  release(s.collections,s.collection_index,s.node)
  mark('set_new_role')
  set_role(s.seaters,s.seater_index,s.profile.roles[target+1])
  -- FRV late-join restore only runs the final gun attachment action. Its
  -- preceding action configures the gunner camera, holster and body modes.
  mark('prepare_target')
  if s.profile.roles[target+1]==2 then
   if s.vehicle=='m102' then action(s.transition,s.avatar,4,target)
   elseif s.vehicle=='m104' then action(s.transition,s.avatar,2,target) end
  end
  mark('restore_target')
  restore_seated(s.seaters,nil,s.avatar,s.collection,target,false)
  if s.profile.roles[target+1]==3 then
   -- Same sequence as native tank gunner->passenger completion (actions 8/9).
   -- The earlier notification restores visuals only; this restores the current
   -- personal weapon on channel 0, without restoring the old turret/coax.
   mark('equip_current_personal_weapon')
   equip_personal(s.avatar_address)
   restore_personal(s.avatar_address)
  end
  -- Same callback, before another rendered/simulation frame: replace the entry
  -- clip with its final seated state; never run an exit action or clear collection.
  mark('apply_final_pose')
  n.last_detail=pose.apply(s,target)..' old_weapon_channels_cleared=0,1'
  mark('transfer_authority')
  authority(s.collections,s.collection_index,target,s.avatar)
  mark('complete')
  -- Kept for protocol research only. A late-join snapshot alone does not update
  -- remote role/input state. Never send this incomplete sequence in the test.
 end
 return n
end

end)()
local Controller=(function()
return function(policy,snapshot)
 local C={};C.__index=C
 function C.new(mode,keys,api,native,log)
  assert(mode=='normal' or mode=='enhanced')
  local codes={}
  for _,map in pairs(keys) do for _,code in pairs(map) do if code~=0 then codes[code]=true end end end
  local self=setmetatable({mode=mode,keys=keys,api=api,native=native,log=log,codes=codes,down={},cooldown=0},C)
  self:reset();return self
 end
 function C:reset()
  for code in pairs(self.codes) do self.down[code]=self.api.down(code) end
 end
 function C:update(s,reason)
  local focused=self.api.focused() and (not self.api.input_allowed or self.api.input_allowed());local pressed={}
  for code in pairs(self.codes) do
   local down=self.api.down(code)
   if focused and down and not self.down[code] then pressed[code]=true end
   self.down[code]=down
  end
  if not focused then self.pending=nil;self.preparing=nil;return 'not_focused' end
  if self.preparing then
   local p=self.preparing
   if self.api.now()>p.started+6 then self.preparing=nil;return 'prepare_expired' end
   if not s then return 'lowering_personal_weapon' end
   if s.identity~=p.identity then self.preparing=nil;return 'vehicle_changed' end
   if s.active then return 'lowering_personal_weapon' end
   local seat=policy.seats[s.vehicle][p.target+1]
   local current=policy.seats[s.vehicle][s.node+1]
   local allowed,why=policy.check(self.mode,s.vehicle,current,seat,s.occupied[p.target])
   local available,issue=self.native.available(s)
   if not allowed or not available then self.preparing=nil;return why or issue end
   if not self.api.focused() or (self.api.input_allowed and not self.api.input_allowed()) or not snapshot.current(self.api,s) then self.preparing=nil;return 'snapshot_changed' end
   self.preparing=nil;self.pending={identity=s.identity,target=p.target,started=self.api.now()}
   self.log('request direct_solo_test '..s.vehicle..' '..current..' -> '..seat)
   self.native.direct(s,p.target)
   if self.native.last_detail then self.log(self.native.last_detail) end
   return 'requested'
  end
  if self.pending then
   local p=self.pending
   if not s or s.identity~=p.identity then
    if self.api.now()>p.started+6 then self.log('request_expired '..tostring(reason));self.pending=nil end
   elseif s.node==p.target then
    self.log('observed_target vehicle='..s.vehicle..' node='..s.node..' (network/in-game observation still required)')
    self.pending=nil
   elseif self.api.now()>p.started+6 then
    self.log('request_not_completed actual='..s.node..' wanted='..p.target);self.pending=nil
   end
   return 'waiting_for_completion'
  end
  if not s then return reason end
  local target,seat
  for i,name in ipairs(policy.seats[s.vehicle]) do
   if pressed[self.keys[s.vehicle][name]] then
    if target then return 'multiple_seat_keys' end
    target=i-1;seat=name
   end
  end
  if target==nil then return 'ready' end
  if self.api.now()<self.cooldown then return 'cooldown' end
  self.cooldown=self.api.now()+0.35
  local current=policy.seats[s.vehicle][s.node+1]
  local allowed,why=policy.check(self.mode,s.vehicle,current,seat,s.occupied[target])
  if not allowed then self.log('rejected '..why..' '..s.vehicle..' '..current..' -> '..seat);return why end
  local nextseat,previous=snapshot.predictions(s)
  local operation=nextseat==target and 'next' or previous==target and 'previous' or nil
  if not operation and self.mode=='normal' then self.log('no_native_route '..s.vehicle);return 'no_native_route' end
  if not operation then
   local ok,issue=self.native.available(s)
   if not ok then self.log('direct_blocked '..issue);return issue end
  end
  if not self.api.focused() or (self.api.input_allowed and not self.api.input_allowed()) or not snapshot.current(self.api,s) then return 'snapshot_changed' end
  if not operation and s.active then
   self.preparing={identity=s.identity,target=target,started=self.api.now()}
   self.log('lower_personal_weapon_before_switch '..s.vehicle)
   self.native.prepare(s);return 'lowering_personal_weapon'
  end
  self.pending={identity=s.identity,target=target,started=self.api.now()}
  self.log('request '..(operation or 'direct_solo_test')..' '..s.vehicle..' '..current..' -> '..seat)
  if operation then self.native[operation](s.seaters,s.avatar) else self.native.direct(s,target) end
  if not operation and self.native.last_detail then self.log(self.native.last_detail) end
  return 'requested'
 end
 return C
end

end)()(policy,snapshot)
-- Bundler supplies MODE, profile, policy, config, platform, snapshot, bind_native, Controller.
if rawget(_G,'VehicleSeatSwitch') then return end
local state={version='0.2.2-test',mode=MODE,status='starting',experimental=true}
rawset(_G,'VehicleSeatSwitch',state)
local loader=rawget(_G,'CowboyBingusModLoader')
local logfile
local function log(line)
 print('[VehicleSeatSwitch] '..line)
 if logfile then logfile:write(os.date('%Y-%m-%d %H:%M:%S')..' '..line..'\n');logfile:flush() end
end
local previous,previous_shutdown=update,shutdown
local started,frames,api,game,controller=false,0
local unpack_values=unpack
local function pack(...)return {n=select('#',...),...} end
local function initialize()
 assert(loader and loader.api==1 and loader.version>=16,'Bingus Shared Loader v16 / API 1 required')
 logfile=assert(loader.open_log('VehicleSeatSwitch.log'),'Cannot create log')
 log('TEST BUILD '..state.version..' mode='..MODE..'; enhanced fixes require gameplay validation')
 log('loader_runtime='..tostring(loader.version)..' api='..tostring(loader.api)..' supported_build='..profile.source_build)
 assert(profile.enabled,profile.reason or 'Native profile disabled')
 api=platform();game=assert(api.module('game.dll'),'Missing game module')
 local exe=assert(api.module('helldivers2.exe'),'Only supported in helldivers2.exe')
 assert(api.hash_module(game)==profile.game_sha256,'Unsupported game.dll; no changes made')
 assert(api.hash_module(exe)==profile.exe_sha256,'Unsupported game build; no changes made')
 local keys,issues,keypath,origin=config.load(api.config_directory(),loader.log_directory)
 state.config=keypath
 log('key_config '..origin..' path='..keypath)
 for _,issue in ipairs(issues) do log(issue) end
 local native=bind_native(api,game,profile,bind_pose,log)
 controller=Controller.new(MODE,keys,api,native,log)
 state.status='ready';log('Ready; config='..keypath)
 -- Tiny static adjacency tables, never heap/module dumps.
 for name,p in pairs(profile.tables) do
  local data=api.read(game+p.rva,p.size)
  local values={}
  if data then for offset=0,#data-4,4 do values[#values+1]=snapshot.i32(data,offset) end end
  log('seat_adjacency '..name..' '..table.concat(values,','))
 end
end
local last_status,last_snapshot,next_detail=nil,nil,0
local function step()
 frames=frames+1
 if frames<180 then return end
 if not started then started=true;initialize() end
 if not controller then return end
 local ok,s,reason=pcall(snapshot.capture,api,game,profile)
 if not ok then
  reason='waiting_for_valid_state';state.last_snapshot_error=tostring(s);s=nil
  if api.now()>=next_detail then log('snapshot_wait '..state.last_snapshot_error);next_detail=api.now()+10 end
 end
 if s then
  local key=s.identity..s.node..tostring(s.owned)..s.mask..tostring(s.active)
  if key~=last_snapshot then
   log('snapshot vehicle='..s.vehicle..' resource='..s.resource..' transition='..s.transition..' node='..s.node..' mask='..s.mask..' owner='..tostring(s.owned)..' players='..s.player_count..' active='..tostring(s.active)..' provisional_identity='..tostring(s.provisional_identity or false))
   last_snapshot=key
  end
 end
 local status=controller:update(s,reason)
 state.status=status
 if status~=last_status then log('state='..tostring(status));last_status=status end
end
if type(previous)~='function' then state.status='missing_update';return end
update=function(...)
 local result=pack(previous(...))
 if state.status~='disabled_after_error' then
  local ok,err=pcall(step)
  if not ok then state.status='disabled_after_error';log('DISABLED '..tostring(err)) end
 end
 return unpack_values(result,1,result.n)
end
shutdown=function(...)
 if logfile then log('shutdown');logfile:close();logfile=nil end
 if previous_shutdown then return previous_shutdown(...) end
end
