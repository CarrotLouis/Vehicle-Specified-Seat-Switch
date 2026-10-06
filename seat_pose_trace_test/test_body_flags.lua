local ffi=require('ffi');local make=assert(loadfile('work/seat_pose_trace_test/body_flags_reader.lua'))()
local exe,root,vt,array=0x10000000,0x20000000,0x20001000,0x20010000
local memory={};local reads=0;local change
local function put(a,b)memory[a]=b end
local function packed(kind,n)local d=ffi.new(kind..'[1]',n);return ffi.string(d,ffi.sizeof(d))end
local function raw(a,n)for at,b in pairs(memory)do if a>=at and a+n<=at+#b then return b:sub(a-at+1,a-at+n)end end end
local api={module=function()return exe end,pointer=function(b)if not b or #b<8 then return nil end;local d=ffi.new('uint64_t[1]');ffi.copy(d,b,8);return tonumber(d[0])end}
function api.read(a,n)reads=reads+1;if change then change(a,n,reads)end;return raw(a,n)end
local leaf=string.char(0x8b,0xc2,0x25,0xff,0xff,0xff,0,0x48,0x8d,4,0x80,0x48,0xc1,0xe0,5,0x48,3,0x41,0x18,0xc3)
local p={pose_watch={body_lookup_bytes=leaf},engine_functions={motion_actor_velocity={rva=0x1000}},
 motion={refs={physics_worlds={record='motion_actor_velocity',offset=0,disp=3,size=7,opcode_hex='488d0d'}}}}
local global=exe+0x5000;local function setup(flags)
 memory={};reads=0;change=nil
 put(exe+0x1000,string.char(0x48,0x8d,0x0d)..packed('int32_t',global-(exe+0x1000+7)))
 put(global+2*0xb0,packed('uint64_t',root));put(root,packed('uint64_t',vt));put(vt+0x70,packed('uint64_t',exe+0x8000))
 put(exe+0x8000,leaf);put(root+0x18,packed('uint64_t',array)..packed('uint32_t',8));put(array+3*160+0x44,packed('uint32_t',flags))
end
local physical={read_only=true,world=2,physics_body_id=0x1000003,body_api_methods={['112']=0x8000}}
for _,flags in ipairs({0,1,2,3,0x10,0x80000001})do
 setup(flags);local x=make(api,0,p,{});local v=x:read(physical)
 assert(v.flags==flags and v.pose_callback_clears_velocity==(flags%2==0)and v.body_index==3 and reads<=15)
end
for _,fault in ipairs({
 function()put(exe+0x8000,leaf:sub(1,19)..'X')end,
 function()put(root+0x18,packed('uint64_t',array)..packed('uint32_t',3))end,
 function()put(root+0x18,packed('uint64_t',array)..packed('uint32_t',1048577))end,
 function()put(root+0x18,packed('uint64_t',array)..packed('uint32_t',0))end,
 function()put(vt+0x70,packed('uint64_t',exe+0x9999))end,
 function()memory[array+3*160+0x44]=nil end,
 function()change=function(a,n,k)if k==8 then put(root,packed('uint64_t',vt+0x100))end end end,
})do setup(0);local x=make(api,0,p,{});fault();assert(not pcall(x.read,x,physical))end
print('PASS body flags 6 branch values + 7 malformed/raced body/leaf/context barriers, <=15 bounded reads, no game calls or writes')
