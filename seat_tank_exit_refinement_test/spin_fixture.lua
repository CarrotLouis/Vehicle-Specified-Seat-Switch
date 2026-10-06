-- Real frozen function witnesses, synthetic maps; never attaches to the game.
local ffi,bit=require('ffi'),require('bit')
local root=assert(os.getenv('VSS_CAPTURE'))
local function file(name)local f=assert(io.open(root..'/'..name,'rb'));local b=f:read('*a');f:close();return b end
local base,modules=0x10000000,{}
for fn,hex in file('capture.txt'):gmatch('([^%s]+%.%d+_([%da-f]+)%.bin) name=')do
 if fn:sub(1,8)=='game.dll'then modules[#modules+1]={base+tonumber(hex,16),file(fn)}end
end
local function code(a,n)for _,r in ipairs(modules)do if a>=r[1]and a+n<=r[1]+#r[2]then return r[2]:sub(a-r[1]+1,a-r[1]+n)end end end
local p={functions={tank_driver_active={rva=0x6fe480,bytes=assert(code(base+0x6fe480,897))}},driver={global=0x3326668}}
local spec={records={},core={},edges={}}
p,spec=assert(loadfile('work/seat_pose_trace_test/spin_spec.lua'))()(p,spec)
local compat=assert(loadfile('work/seat_switch/src/compat.lua'))()
local maker=assert(loadfile('work/seat_tank_exit_refinement_test/spin_reader.lua'))()
local function u32(v)local a=ffi.new('uint32_t[1]',v);return ffi.string(a,4)end
local function ptr(v)local a=ffi.new('uint64_t[1]',v);return ffi.string(a,8)end
local function f32(v)local a=ffi.new('float[1]',v);return ffi.string(a,4)end
local function fixture(change_at_start)
 local memory,patches={},{};local writes,calls=0,0;local tear_at,tear;local f_fail_at
 local function allocate(a,n)for i=0,n-1 do memory[a+i]=0 end end
 local function put(a,b)for i=1,#b do memory[a+i-1]=b:byte(i)end end
 local function raw(a,n)
  local out={};local exists=true
  for i=0,n-1 do if memory[a+i]==nil then exists=false;break end;out[#out+1]=string.char(memory[a+i])end
  local b=exists and table.concat(out)or code(a,n);if not b then return nil end
  if next(patches)then out={};for i=0,n-1 do out[#out+1]=string.char(patches[a+i]or b:byte(i+1))end;b=table.concat(out)end
  return b
 end
 local api={ffi=ffi}
 function api.read(a,n)
  local at=tonumber(ffi.cast('uintptr_t',a));local b=raw(at,n)
  if at==tear_at then tear_at=nil;tear()end;return b
 end
 function api.pointer(b,o)
  o=o or 0;if not b or #b<o+8 then return nil end
  local a=ffi.new('uint64_t[1]');ffi.copy(a,b:sub(o+1,o+8),8)
  if a[0]<65536 or a[0]>=2^47 then return nil end;return ffi.cast('uint8_t *',a[0])
 end
 api.replace=function(a,old,new)
   local at=tonumber(ffi.cast('uintptr_t',a));writes=writes+1
   if f_fail_at==at then return false end
   assert(#old==#new and (#old==4 or #old==1),'only steering fields/pivot byte allowed')
   if raw(at,#old)~=old then return false end;put(at,new);return true
  end
 api.call=function()calls=calls+1;error('unexpected game call')end
 local d,dr,de,e,cmd,rt,bk=0x20000000,0x20001000,0x20002000,0x20003000,0x20004000,0x20005000,0x20008000
 local v,vr,ve,inp,rep=0x21000000,0x21001000,0x21002000,0x21003000,0x21004000
 local snap={name='bastion',id=9,unit=99,network_unit=909,resource='16474112801385b6',owned_local=true}
 local resource=(snap.resource:gsub('..',function(x)return string.char(tonumber(x,16))end)):reverse()
 allocate(base+0x3326668,8);put(base+0x3326668,ptr(d));allocate(base+0x3326458,8);put(base+0x3326458,ptr(v))
 allocate(d,0x80);allocate(dr,32);allocate(de,16);allocate(e,24);allocate(cmd,96);allocate(rt,0xd28*2);allocate(bk,16)
 put(d+0x24,u32(2)..u32(2)..u32(2));put(d+0x38,ptr(dr)..u32(4)..u32(0xffffffff)..u32(1))
 for i=0,3 do put(dr+i*8,u32(0xffffffff)..u32(0xffffffff))end;put(dr+8,u32(9)..u32(1))
 put(d+0x50,ptr(de));put(de+8,ptr(e));put(e,resource..u32(9)..u32(99)..u32(909)..u32(1))
 put(d+0x58,ptr(cmd));put(d+0x60,ptr(bk));put(d+0x68,ptr(rt))
 put(bk+8,u32(1)..u32(1));put(cmd+48+0x18,f32(.5)..f32(.25)..f32(-1))
 put(cmd+48+0x2c,string.char(1,0,0,1));put(rt+0xd28+0xd18,string.char(1))
 allocate(v,0x80);allocate(vr,32);allocate(ve,16);allocate(inp,48);allocate(rep,0x58*2);local vrt=0x21005000;allocate(vrt,0x670*2);put(v+0x70,ptr(vrt))
 put(v+0x30,u32(2)..u32(2));put(v+0x40,ptr(vr)..u32(4)..u32(0xffffffff)..u32(1))
 for i=0,3 do put(vr+i*8,u32(0xffffffff)..u32(0xffffffff))end;put(vr+8,u32(9)..u32(1))
 put(v+0x58,ptr(ve));put(ve+8,ptr(e));put(v+0x60,ptr(inp));put(v+0x78,ptr(rep))
 put(inp+16,f32(-1)..f32(.5)..f32(.25)..string.char(0,1,0,0))
 put(rep+0x58+0x34,f32(-.75)..f32(.5)..f32(.25));put(rep+0x58+0x4f,string.char(1))
 local f={api=api,snap=snap,d=d,dr=dr,de=de,e=e,cmd=cmd,rt=rt,bk=bk,v=v,vr=vr,ve=ve,inp=inp,rep=rep,put=put,allocate=allocate}
 function f.fail_write(at)f_fail_at=at end
 function f.writes()return writes end
 function f.raw(a,n)return raw(a,n)end
 function f.patch(a,b)for i=1,#b do patches[a+i-1]=b:byte(i)end end
 function f.tear_on(a,fn)tear_at=a;tear=fn end
 function f.saved()local out={};for at,x in pairs(memory)do out[at]=x end;return out end
 function f.unchanged(before)for at,x in pairs(before)do assert(memory[at]==x,'unexpected memory mutation')end;assert(writes==0 and calls==0)end
 if change_at_start then change_at_start(f)end
 f.reader=maker(api,ffi.cast('uint8_t *',base),p,compat)
 function f.read()return f.reader:read_vehicle(f.snap)end
 return f
end

return {fixture=fixture,p=p,game=ffi.cast("uint8_t *",base),reader_factory=maker,compat=compat,u32=u32,ptr=ptr,f32=f32}
