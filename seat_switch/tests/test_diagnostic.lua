local ffi=require('ffi')
local core=assert(loadfile('work/seat_switch/src/diagnostic_core.lua'))()
local data=ffi.new('uint8_t[12288]')
local function s(offset,bytes)ffi.copy(data+offset,bytes,#bytes)end
local function u16(offset,value)s(offset,string.char(value%256,math.floor(value/256)%256))end
local function u32(offset,value)
    local b={};for i=1,4 do b[i]=string.char(value%256);value=math.floor(value/256)end;s(offset,table.concat(b))
end
s(0,'MZ');u32(60,128);s(128,'PE\0\0');u16(132,0x8664);u16(134,2);u16(148,240)
u16(152,0x20b);u32(152+56,12288)
local st=152+240
s(st,'.text');u32(st+8,16);u32(st+12,4096);u32(st+36,0x60000020)
s(st+40,'.data');u32(st+48,16);u32(st+52,8192);u32(st+76,0xc0000040)
s(4096,'CODE-ONLY-TEST!!');s(8192,'PRIVATE-DATA!!!!')
local function read(offset,size)return ffi.string(data+offset,size)end
local parsed=core.inspect(read)
assert(parsed.size==12288 and #parsed.sections==1 and parsed.sections[1].rva==4096)
u32(st+8,20000);assert(not pcall(core.inspect,read));u32(st+8,16)
assert(not pcall(core.inspect,function()return nil end))
local api=core.describe_api({secret='TOP_SECRET_VALUE',stingray={Vehicle={swap=function()end},token='PRIVATE'}})
assert(api:find('stingray.Vehicle.swap\tfunction',1,true))
assert(not api:find('TOP_SECRET_VALUE',1,true) and not api:find('PRIVATE',1,true))

local function run_scenario(name,interrupt,original_fails)
    local dir='work/seat_switch/tests/fixture_'..name
    -- Directories are created by the Python build harness.
    local kernel={}
    function kernel.GetModuleHandleA()return ffi.cast('void *',data)end
    function kernel.GetModuleFileNameA(_,out)
        local path='C:\\Game\\helldivers2.exe';ffi.copy(out,path,#path);return #path
    end
    function kernel.GetCurrentProcess()return ffi.cast('void *',1)end
    function kernel.CreateDirectoryA()return 1 end
    function kernel.GetLastError()return 183 end
    function kernel.ReadProcessMemory(_,address,out,size,count)
        local offset=tonumber(ffi.cast('const uint8_t *',address)-data)
        assert(offset>=0 and offset+size<=12288,'Unexpected memory request')
        ffi.copy(out,address,size);count[0]=size;return 1
    end
    local saved_load=ffi.load
    ffi.load=function(library)assert(library=='kernel32');return kernel end
    local updates,stopped=0,0
    local env={core=core,module_hash=function()return string.rep('a',64)end,stingray={},CowboyBingusModLoader={api=1,version=16,log_directory=dir}}
    env.CowboyBingusModLoader.open_log=function()return assert(io.open(dir..'/status.log','w'))end
    env.update=function(...)
        updates=updates+1
        if original_fails then error('ORIGINAL_ERROR')end
        return ...
    end
    env.shutdown=function(...)stopped=stopped+1;return ... end
    env._G=env;setmetatable(env,{__index=_G})
    local entry=assert(loadfile('work/seat_switch/src/diagnostic_entry.lua'));setfenv(entry,env);entry()
    assert(not env.HD2VehicleSeatDiagnostic.status:find('unavailable'),env.HD2VehicleSeatDiagnostic.status)
    local registered=env.update;entry();assert(env.update==registered,'Duplicate installation')
    if original_fails then
        local ok,message=pcall(env.update,1);assert(not ok and message:find('ORIGINAL_ERROR'))
        assert(env.HD2VehicleSeatDiagnostic.status:find('original_update_failed'))
    elseif interrupt then
        env.update(1);assert(env.shutdown(8)==8);assert(stopped==1)
        assert(env.HD2VehicleSeatDiagnostic.status:find('stopped_before_complete'))
    else
        for i=1,185 do local a,b,c=env.update(0.016,nil,7);assert(a==0.016 and b==nil and c==7)end
        assert(updates==185 and env.HD2VehicleSeatDiagnostic.status:match('^complete;'))
        local capture=assert(io.open(dir..'/VehicleSeatDiagnostic/aaaaaaaaaaaa/capture.txt','rb'))
        local details=capture:read('*a');capture:close()
        assert(details:find('file_sha256='..string.rep('a',64),1,true))
        assert(details:find('base=0x',1,true) and not details:find('cdata',1,true))
        assert(tonumber(details:match('base=0x(%x+)'),16)==tonumber(ffi.cast('uintptr_t',data)),'Address formatting truncated')
        for _,module in ipairs({'game.dll','helldivers2.exe'}) do
            local file=assert(io.open(dir..'/VehicleSeatDiagnostic/aaaaaaaaaaaa/'..module..'.01_00001000.bin','rb'))
            assert(file:read('*a')=='CODE-ONLY-TEST!!');file:close()
        end
        assert(env.shutdown(5)==5 and stopped==1)
    end
    ffi.load=saved_load
end
run_scenario('complete',false,false)
run_scenario('interrupt',true,false)
run_scenario('failure',false,true)
print('PASS: PE bounds, writable-data exclusion, API value privacy, bounded capture, callback forwarding, duplicate guard, interrupted/error cleanup.')
