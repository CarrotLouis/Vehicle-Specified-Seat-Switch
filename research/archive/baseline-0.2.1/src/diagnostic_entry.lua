-- DIAGNOSTIC ONLY. No seat changes, process writes, input injection, hooks or network.
-- The builder prepends local core = (...) from diagnostic_core.lua.
if rawget(_G,'HD2VehicleSeatDiagnostic') then return end
local state={version='0.1.1',status='starting'}
rawset(_G,'HD2VehicleSeatDiagnostic',state)
local loader=rawget(_G,'CowboyBingusModLoader')
local function report(message)
    state.status=message
    print('[VehicleSeatDiagnostic] '..message)
    if loader and type(loader.open_log)=='function' then
        pcall(function()
            local f=loader.open_log('VehicleSeatDiagnostic.log')
            if f then f:write('Diagnostic only; gameplay mod not implemented.\n'..message..'\n');f:close() end
        end)
    end
end
local initialized,why=pcall(function()
    assert(loader and loader.api==1 and loader.version>=16,'Requires Bingus Shared Loader v15+ / API 1')
    assert(type(stingray)=='table' and type(update)=='function','Game startup unavailable')
    local ffi=require('ffi')
    assert(ffi.abi('64bit'),'Expected x64')
    ffi.cdef [[
        void *GetModuleHandleA(const char *name);
        uint32_t GetModuleFileNameA(void *module,char *path,uint32_t capacity);
        void *GetCurrentProcess(void);
        int ReadProcessMemory(void *process,const void *address,void *buffer,size_t size,size_t *read);
        int CreateDirectoryA(const char *path,void *security);
        uint32_t GetLastError(void);
    ]]
    local kernel=ffi.load('kernel32')
    local path=ffi.new('char[32768]')
    local length=kernel.GetModuleFileNameA(nil,path,32768)
    assert(length>0 and length<32768,'Cannot identify host')
    assert(ffi.string(path,length):lower():match('[\\/]helldivers2%.exe$'),'Only runs inside helldivers2.exe')
    report('Preparing local diagnostic capture')
    assert(type(loader.log_directory)=='string','Shared log directory unavailable')
    local root=loader.log_directory..'/VehicleSeatDiagnostic'
    assert(kernel.CreateDirectoryA(root,nil)~=0 or kernel.GetLastError()==183,'Cannot create diagnostic folder')
    local game_hash_ok,game_digest=pcall(module_hash,kernel.GetModuleHandleA('game.dll'))
    local suffix=game_hash_ok and game_digest:sub(1,12) or os.date('%Y%m%d-%H%M%S')
    local directory=root..'/'..suffix
    assert(kernel.CreateDirectoryA(directory,nil)~=0 or kernel.GetLastError()==183,'Cannot create build diagnostic folder')
    state.directory=directory
    local function write_text(name,value)
        local f=assert(io.open(directory..'/'..name,'wb'));assert(f:write(value));assert(f:close())
    end
    write_text('lua-api.txt',core.describe_api(_G))
    local process=kernel.GetCurrentProcess()
    local buffer,count=ffi.new('uint8_t[65536]'),ffi.new('size_t[1]')
    local function read(base,offset,size)
        assert(size>0 and size<=65536,'Read bound exceeded')
        local pointer=ffi.cast('const uint8_t *',base)+offset
        count[0]=0
        if kernel.ReadProcessMemory(process,pointer,buffer,size,count)==0 or tonumber(count[0])~=size then return nil end
        return ffi.string(buffer,size)
    end
    local jobs,notes={}, {'Vehicle Seat Diagnostic 0.1.1', 'Local executable/static module sections only.',
        'No whole-process/heap dump. No gameplay state changes. Unreadable pages are zero-filled and recorded.'}
    for _,module_name in ipairs({'game.dll','helldivers2.exe'}) do
        local base=kernel.GetModuleHandleA(module_name)
        assert(base~=nil,'Missing module '..module_name)
        local info=core.inspect(function(offset,size)return read(base,offset,size)end)
        -- The game replaces cdata tostring; numeric formatting retains the address.
        notes[#notes+1]=module_name..' base='..string.format('0x%x',tonumber(ffi.cast('uintptr_t',base)))..' image_size='..info.size
        local hash_ok,digest=game_hash_ok,game_digest
        if module_name~='game.dll' then hash_ok,digest=pcall(module_hash,base) end
        notes[#notes+1]=module_name..' file_sha256='..(hash_ok and digest or ('unavailable: '..tostring(digest)))
        local headers=read(base,0,4096)
        if headers then write_text(module_name..'.headers.bin',headers) end
        for _,section in ipairs(info.sections) do
            local name=module_name..'.'..string.format('%02d_%08x',section.index,section.rva)..'.bin'
            jobs[#jobs+1]={base=base,section=section,name=name,done=0}
            notes[#notes+1]=string.format('%s name=%s rva=0x%x size=%d flags=0x%x',name,section.name,section.rva,section.size,section.flags)
        end
    end
    assert(#jobs>0,'No module sections available')
    local details=assert(io.open(directory..'/capture.txt','wb'))
    assert(details:write(table.concat(notes,'\n')..'\nstatus=capturing\n'));details:flush()
    local previous,previous_shutdown=update,shutdown
    local index,frame=1,0
    local active,output=true,nil
    local function cleanup(status)
        active=false
        if output then pcall(output.close,output);output=nil end
        if details then pcall(details.write,details,'status='..status..'\n');pcall(details.close,details);details=nil end
        report(status..'; output='..directory)
    end
    local function step()
        frame=frame+1
        -- Let startup finish. At most 64 KiB of module reads/writes per update.
        if frame<180 then return end
        local job=jobs[index]
        if not job then cleanup('complete');return end
        if not output then output=assert(io.open(directory..'/'..job.name,'wb')) end
        local n=math.min(65536,job.section.size-job.done)
        local offset=job.section.rva+job.done
        local bytes=read(job.base,offset,n)
        if not bytes then
            local pages={}
            for page=0,n-1,4096 do
                local count_bytes=math.min(4096,n-page)
                local part=read(job.base,offset+page,count_bytes)
                if not part then
                    details:write(string.format('unreadable %s rva=0x%x size=%d\n',job.name,offset+page,count_bytes))
                    part=string.rep('\0',count_bytes)
                end
                pages[#pages+1]=part
            end
            bytes=table.concat(pages)
        end
        assert(output:write(bytes));job.done=job.done+n
        if job.done==job.section.size then assert(output:close());output=nil;index=index+1 end
    end
    local function after(ok,...)
        if not ok then if active then cleanup('original_update_failed') end;error((...),0) end
        if active then local passed,error_text=pcall(step);if not passed then cleanup('capture_failed: '..tostring(error_text)) end end
        return ...
    end
    update=function(...)return after(pcall(previous,...))end
    shutdown=function(...)
        if active then cleanup('stopped_before_complete') end
        if previous_shutdown then return previous_shutdown(...) end
    end
    report('Capturing after startup. Wait 60 seconds on the ship; output='..directory)
end)
if not initialized then report('unavailable: '..tostring(why)) end
