local ffi=require('ffi')
local make=assert(loadfile('work/seat_pose_trace_test/pose_trace.lua'))()
local calls,events,now,memory={}, {},0,{}
local game,exe,A=0x10000000,0x20000000,0x20008000
local function put(a,b)memory[a]=b end
local function pointer(n)local p=ffi.new('uint64_t[1]',n);return ffi.string(p,8)end
local function read(a,n)for at,b in pairs(memory)do if a>=at and a+n<=at+#b then return b:sub(a-at+1,a-at+n)end end end
local p={pose_watch={records={pose_actor_set={module='exe',length=32,chunks={}},pose_velocity_set={module='exe',length=32,chunks={}},pose_remote_tick={module='game',length=0x11dd,chunks={}}}},
 functions={motion_vehicle_velocity={rva=0x1000},pose_remote_tick={rva=0x713f50}},
 engine_functions={pose_actor_set={rva=0x2000},pose_velocity_set={rva=0x3000},motion_actor_velocity={rva=0x4000}},
 motion={refs={velocity_api={record='motion_vehicle_velocity',offset=0,disp=3,size=7,opcode_hex='4c8b0d'}}}}
local global=game+0x5000
local dis=ffi.new('int32_t[1]',global-(game+0x1000+7))
put(game+0x1000,string.char(0x4c,0x8b,0x0d)..ffi.string(dis,4));put(global,pointer(A))
put(A+0x70,pointer(exe+0x2000));put(A+0xa0,pointer(exe+0x3000));put(A+0xa8,pointer(exe+0x4000))
put(exe+0x2000,string.rep('P',32));put(exe+0x3000,string.rep('V',32));put(game+0x713f50,string.rep('R',0x11dd))
local api={read=read,now=function()return now end,module=function()return exe end,
 pointer=function(b)if not b or #b<8 then return nil end;local n=ffi.new('uint64_t[1]');ffi.copy(n,b,8);return tonumber(n[0])end,
 in_image=function(_,a,n)return a>=0 and a+n<0x100000 end,
 describe=function()return {state=4096,protection=4,region_remaining=4096}end}
local rows,health,armcode,startcode={},0,0,0
local lib={VSSM_version=function()return 1 end,VSSM_record_size=function()return 128 end,VSSM_frequency=function()return 1000 end,VSSM_dropped=function()return 0 end,
 VSSM_start=function(bindings,guards)
  calls[#calls+1]='start';assert(tonumber(ffi.cast('uintptr_t',bindings[0].slot))==A+0x70)
  assert(tonumber(ffi.cast('uintptr_t',guards[0].slot))==global);return startcode
 end,VSSM_health=function()calls[#calls+1]='health';return health end,
 VSSM_arm=function(handle,epoch,ms)calls[#calls+1]='arm';assert(handle==0xa0001234 and ms==2000 and epoch>0);return armcode end,
 VSSM_disarm=function()calls[#calls+1]='disarm';return 0 end,VSSM_stop=function()calls[#calls+1]='stop';return 0 end,
 VSSM_drain=function(out,max)
  calls[#calls+1]='drain';assert(max==256);for i,r in ipairs(rows)do for k,v in pairs(r)do
   if k=='values'then for j,x in ipairs(v)do out[i-1].values[j-1]=x end else out[i-1][k]=v end
  end end;local n=#rows;rows={};return n
 end}
local function emit(e)events[#events+1]=e end
local function new()calls={};events={};return make(api,game,p,{match=function(b)return b~=nil end},{},{sha256='fixture'},emit,lib)end
local v={name='m102',id=12,unit=34};local c={seat=1,sample={player_count=2}};local t={loan_only=true}
local body={collection=12,unit=34,actor_handle=0xa0001234}
local x=new();x:update();assert(#calls==0);x:arm(v,c,t,body);assert(calls[1]=='start'and x.epoch==1)
rows={{kind=0,valid=1,actor=body.actor_handle,caller_module=1,caller=p.functions.pose_remote_tick.rva+0x487,epoch=1,
 tick=100,sequence=1,values={1,0,0,0,0,1,0,0,0,0,1,0,12,23,34,1}},
 {kind=1,valid=3,actor=body.actor_handle,caller_module=1,caller=0x714c21,epoch=1,tick=101,sequence=2,values={4,5,6,0,0,0,.8}}}
x:update();assert(x.seen==2)
local a,b=events[#events-1],events[#events]
assert(a.native_path=='vehicle_remote_first_sample_pose'and a.matrix[13]==12 and a.call_completion_not_observed)
assert(b.linear_velocity[1]==4 and math.abs(b.angular_velocity[3]-.8)<.00001)
now=3;x:update();assert(not x.needs_drain and x.until_at==0)
local count=#calls;x:update();x:update();assert(#calls==count,'idle observer must not call library')
x:arm(v,c,t,body);assert(x.epoch==2);x:close('test');assert(calls[#calls]=='stop')
for _,change in ipairs({function()v.name='m103'end,function()c.seat=0 end,function()c.sample.player_count=3 end,
 function()t.loan_only=false end,function()body.unit=99 end})do
 v.name='m102';c.seat=1;c.sample.player_count=2;t.loan_only=true;body.unit=34
 x=new();change();assert(not pcall(x.arm,x,v,c,t,body));assert(#calls==0)
end
v.name='m102';c.seat=1;c.sample.player_count=2;t.loan_only=true;body.unit=34
x=new();health=1;assert(not pcall(x.arm,x,v,c,t,body)and x.failed);health=0
x=new();armcode=-1;assert(not pcall(x.arm,x,v,c,t,body)and x.failed);armcode=0
x=new();startcode=101;assert(not pcall(x.arm,x,v,c,t,body)and x.failed);startcode=0
x=new();x:arm(v,c,t,body);health=1;x:update();assert(x.failed and calls[#calls]=='drain');health=0
print('PASS motion-call Lua actual slot/ABI construction, no idle C calls, windows/epochs, argument mapping, 5 scope barriers, init/arm/post-request failure isolation')
