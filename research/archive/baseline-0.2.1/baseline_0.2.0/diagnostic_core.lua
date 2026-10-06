local bit = require('bit')
local M = {}
local function u16(s, p)
    local a,b=s:byte(p+1,p+2); assert(b,'Truncated field'); return a+b*256
end
local function u32(s, p)
    local a,b,c,d=s:byte(p+1,p+4); assert(d,'Truncated field'); return a+b*256+c*65536+d*16777216
end
function M.inspect(read)
    local h=assert(read(0,64),'DOS header unreadable');assert(h:sub(1,2)=='MZ','Not a PE module')
    local pe=u32(h,60);assert(pe>=64 and pe<1048576,'Invalid PE header offset')
    h=assert(read(pe,24),'PE header unreadable');assert(h:sub(1,4)=='PE\0\0','Invalid PE signature')
    assert(u16(h,4)==0x8664,'Expected x64')
    local n,opt=u16(h,6),u16(h,20);assert(n>0 and n<=96 and opt>=64 and opt<=4096,'Invalid PE layout')
    local o=assert(read(pe+24,opt),'Optional header unreadable');assert(u16(o,0)==0x20b,'Expected PE32+')
    local size=u32(o,56);assert(size>=4096 and size<=134217728,'Module too large')
    local table_bytes=assert(read(pe+24+opt,n*40),'Section table unreadable')
    local info={size=size,sections={}}
    for i=0,n-1 do
        local p=i*40
        local name=table_bytes:sub(p+1,p+8):gsub('%z.*',''):gsub('[^%w_.-]','_')
        local length,rva,flags=u32(table_bytes,p+8),u32(table_bytes,p+12),u32(table_bytes,p+36)
        assert(rva+length<=size,'Section outside image')
        local executable=bit.band(flags,0x20000000)~=0
        local readonly=bit.band(flags,0x40000000)~=0 and bit.band(flags,0x80000000)==0
        if length>0 and (executable or readonly) then
            info.sections[#info.sections+1]={index=i+1,name=name,rva=rva,size=length,flags=flags}
        end
    end
    return info
end
function M.describe_api(env)
    local lines,seen={},{}
    local function walk(t,prefix,depth)
        if seen[t] then return end;seen[t]=true
        local keys={}
        for k in next,t do if type(k)=='string' then keys[#keys+1]=k end end
        table.sort(keys)
        for _,k in ipairs(keys) do
            local v=rawget(t,k);local kind=type(v);local path=prefix..k
            -- Names and types only: never serialize global string values/user data.
            lines[#lines+1]=path..'\t'..kind
            if kind=='table' and depth>0 and k~='_G' and k~='package' then walk(v,path..'.',depth-1) end
            if #lines>25000 then return end
        end
    end
    walk(env,'',0)
    for _,name in ipairs({'stingray','Application','Game','Managers','Wwise','Keyboard','Mouse'}) do
        local value=rawget(env,name)
        if type(value)=='table' then seen[value]=nil;walk(value,name..'.',2) end
    end
    return table.concat(lines,'\n')..'\n'
end
return M
