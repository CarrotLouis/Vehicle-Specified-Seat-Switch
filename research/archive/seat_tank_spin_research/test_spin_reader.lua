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
p,spec=assert(loadfile('work/seat_tank_spin_research/spin_spec.lua'))()(p,spec)
local compat=assert(loadfile('work/seat_switch/src/compat.lua'))()
local maker=assert(loadfile('work/seat_tank_spin_research/spin_reader.lua'))()
local function u32(v)local a=ffi.new('uint32_t[1]',v);return ffi.string(a,4)end
local function ptr(v)local a=ffi.new('uint64_t[1]',v);return ffi.string(a,8)end
local function f32(v)local a=ffi.new('float[1]',v);return ffi.string(a,4)end
local function fixture(change_at_start)
 local memory,patches={},{};local writes,calls=0,0;local tear_at,tear
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
 api.replace=function()writes=writes+1;error('unexpected write')end
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
 allocate(v,0x80);allocate(vr,32);allocate(ve,16);allocate(inp,48);allocate(rep,0x58*2)
 put(v+0x30,u32(2)..u32(2));put(v+0x40,ptr(vr)..u32(4)..u32(0xffffffff)..u32(1))
 for i=0,3 do put(vr+i*8,u32(0xffffffff)..u32(0xffffffff))end;put(vr+8,u32(9)..u32(1))
 put(v+0x58,ptr(ve));put(ve+8,ptr(e));put(v+0x60,ptr(inp));put(v+0x78,ptr(rep))
 put(inp+16,f32(-1)..f32(.5)..f32(.25)..string.char(0,1,0,0))
 put(rep+0x58+0x34,f32(-.75)..f32(.5)..f32(.25));put(rep+0x58+0x4f,string.char(1))
 local f={api=api,snap=snap,d=d,dr=dr,de=de,e=e,cmd=cmd,rt=rt,bk=bk,v=v,vr=vr,ve=ve,inp=inp,rep=rep,put=put,allocate=allocate}
 function f.patch(a,b)for i=1,#b do patches[a+i-1]=b:byte(i)end end
 function f.tear_on(a,fn)tear_at=a;tear=fn end
 function f.saved()local out={};for at,x in pairs(memory)do out[at]=x end;return out end
 function f.unchanged(before)for at,x in pairs(before)do assert(memory[at]==x,'unexpected memory mutation')end;assert(writes==0 and calls==0)end
 if change_at_start then change_at_start(f)end
 f.reader=maker(api,ffi.cast('uint8_t *',base),p,compat)
 function f.read()return f.reader:read_vehicle(f.snap)end
 return f
end
local cases=0
for _,sign in ipairs({-1,0,1})do
 local f=fixture();f.put(f.inp+16,f32(sign));f.put(f.cmd+48+0x20,f32(0));f.put(f.cmd+48+0x2c,string.char(0))
 local before=f.saved();local row=f.read();f.unchanged(before)
 assert(row.driver_backend_kind==1 and row.driver_command_steer==0 and row.driver_command_flags_offset_2c_to_2f[1]==0)
 assert(row.input_steer==sign and row.replicated_steer==-.75 and row.driver_active==1 and row.read_count<=100)
 assert(row.input_flags_offset_0c_to_0f[2]==1 and row.driver_in_owned_partition and row.vehicle_in_owned_partition)
 cases=cases+1
end
-- Vehicle remains readable after the local driver has exited and ownership
-- moves to a remote player. This collector makes no write-authority claim.
local f=fixture();f.snap.owned_local=false;f.put(f.e+20,u32(0));f.put(f.d+0x2c,u32(0));f.put(f.v+0x34,u32(0));f.put(f.rt+0xd28+0xd18,string.char(0))
local before=f.saved();local row=f.read();f.unchanged(before)
assert(not row.driver_in_owned_partition and not row.vehicle_in_owned_partition and row.driver_active==0);cases=cases+1
for _,name in ipairs({'m102','m103','m104','bastion','maelstrom'})do
 local f=fixture();f.snap.name=name;local before=f.saved();assert(f.read().driver_backend_kind==1);f.unchanged(before);cases=cases+1
end
local failures={
 function(f)f.snap.name='unknown'end,
 function(f)f.snap.unit=100 end,
 function(f)f.snap.network_unit=910 end,
 function(f)f.snap.resource='b0c9faf4af8903f9'end,
 function(f)f.snap.owned_local=false end,
 function(f)f.put(base+0x3326668,ptr(0))end,
 function(f)f.put(base+0x3326458,ptr(0))end,
 function(f)f.put(f.d+0x40,u32(3))end,
 function(f)f.put(f.v+0x48,u32(0))end,
 function(f)f.put(f.v+0x48,u32(32768))end,
 function(f)f.put(f.dr+8,u32(0xffffffff))end,
 function(f)f.put(f.vr+8,u32(0xffffffff))end,
 function(f)f.put(f.dr+12,u32(2))end,
 function(f)f.put(f.vr+12,u32(2))end,
 function(f)f.put(f.d+0x24,u32(0))end,
 function(f)f.put(f.d+0x28,u32(3))end,
 function(f)f.put(f.d+0x2c,u32(3))end,
 function(f)f.put(f.v+0x30,u32(0))end,
 function(f)f.put(f.v+0x34,u32(3))end,
 function(f)f.put(f.d+0x60,ptr(0))end,
 function(f)f.put(f.bk+12,u32(4))end,
 function(f)f.put(f.cmd+48,f32(0/0))end,
 function(f)f.put(f.cmd+48+0x20,f32(math.huge))end,
 function(f)f.put(f.inp+16,f32(0/0))end,
 function(f)f.put(f.inp+20,f32(math.huge))end,
 function(f)f.put(f.rep+0x58+0x34,f32(-math.huge))end,
 function(f)f.put(f.rt+0xd28+0xd18,string.char(7))end,
 function(f)f.put(f.rep+0x58+0x4f,string.char(2))end,
 function(f)f.put(f.ve+8,ptr(f.e+8))end,
 function(f)f.patch(base+p.functions.spin_driver_export.rva+0x93,'\0')end,
 function(f)f.patch(base+p.functions.spin_driver_export.rva+0x378+3,u32(0))end,
 function(f)f.patch(base+p.functions.tank_driver_active.rva+0x29+3,u32(0))end,
 function(f)
  f.allocate(f.dr,512);f.put(f.d+0x40,u32(64))
  for i=0,63 do f.put(f.dr+i*8,u32(100+i)..u32(1))end
 end,
}
for i,change in ipairs(failures)do
 local f=fixture();change(f);local before=f.saved();local ok,reason=pcall(f.read)
 assert(not ok,'accepted failure case '..i);f.unchanged(before);cases=cases+1
end
local f=fixture();local fired=false
f.tear_on(f.inp+16,function()fired=true;f.put(f.e+12,u32(100))end)
local ok,reason=pcall(f.read);assert(fired and not ok and tostring(reason):find('spin_identity_changed_during_read',1,true));cases=cases+1
-- Unmasked native code corruption refuses even before sampling.
for name,d in pairs(p.spin.records)do
 local chunk=d.chunks[1];local at=base+p.functions[name].rva+chunk.offset
 local original=assert(code(at,1)):byte(1)
 assert(not pcall(fixture,function(f)f.patch(at,string.char(bit.bxor(original,1)))end));cases=cases+1
end
assert(not pcall(fixture,function(f)f.patch(base+p.functions.tank_driver_active.rva,'\0')end));cases=cases+1
print('PASS '..cases..' steering reader cases with frozen code in '..root..'; bounded identities/maps/backend/input/replica guards, natural ownership loss, inactive command retaining steer, structural race, code rejection; no writes or game calls; physical spin unverified')
