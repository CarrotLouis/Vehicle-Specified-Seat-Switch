-- Real filesystem test isolated under this workspace, never the user's config.
local config=assert(loadfile('work/seat_switch/src/config.lua'))()
local api=assert(loadfile('work/seat_switch/src/platform.lua'))()()
local base='work/seat_switch/tests/fixture_entry'
local old_getenv=os.getenv
os.getenv=function(name)assert(name=='APPDATA');return base end
local directory=api.config_directory()
os.getenv=old_getenv
assert(directory==base..'/Arrowhead/Helldivers2')
local path=directory..'/VehicleSeatSwitch.ini'
local legacy=base..'/VehicleSeatSwitch.ini'
local function write(p,t)local f=assert(io.open(p,'wb'));assert(f:write(t));f:close() end
local function read(p)local f=assert(io.open(p,'rb'));local t=f:read('*a');f:close();return t end
os.remove(path);os.remove(legacy)
local keys,issues,p,origin=config.load(directory,base)
assert(p==path and origin=='created_defaults' and #issues==0)
assert(keys.m102.driver==112 and keys.m102.gunner==116)
local custom='; preserved comment\r\n[m102]\r\ndriver=NUMPAD1\r\nfront_passenger=NUMPAD2\r\n'
write(legacy,custom);os.remove(path)
keys,issues,p,origin=config.load(directory,base)
assert(origin=='migrated_legacy' and #issues==0 and read(path)==custom and read(legacy)==custom)
assert(keys.m102.driver==97 and keys.m102.front_passenger==98)
write(path,'[m102]\ndriver=F8\n');write(legacy,'[m102]\ndriver=F9\n')
keys,issues,p,origin=config.load(directory,base)
assert(origin=='existing' and keys.m102.driver==119 and read(path)=='[m102]\ndriver=F8\n')
assert(config.key('NUMPAD0')==96 and config.key('NUMPAD9')==105 and config.key('F24')==135)
assert(config.key('NUMPAD10')==nil and config.key('F25')==nil)
os.remove(path);os.remove(legacy)
print('PASS: actual config directory creation, first-run defaults, exact legacy migration, existing APPDATA config precedence, preserved originals and numpad key names. Workspace only.')
