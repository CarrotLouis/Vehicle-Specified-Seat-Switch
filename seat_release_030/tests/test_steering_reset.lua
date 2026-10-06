-- Actual cleanup + actual bounded reader + captured code, explicit memory doubles.
local ffi=require('ffi');local F=assert(loadfile('work/seat_release_030/src/spin_fixture.lua'))()
local scope=assert(loadfile('work/seat_release_030/src/scope.lua'))()
local reset=assert(loadfile('work/seat_release_030/src/steering_reset.lua'))()
local function instance(name,sign)
 local f=F.fixture();local events={};local clock=10;local reads=0
 local original=f.api.read;f.api.read=function(...)reads=reads+1;return original(...)end
 f.api.now=function()return clock end
 f.put(f.inp+16,F.f32(sign));f.put(f.rep+0x58+0x34,F.f32(sign*.75));f.snap.name=name
 local d=name=='bastion'and 43 or 44
 local s={vehicle=name,transition=d,profile={row=12,roles={1,2,3,3}},node=0,owned=true,active=false,
  player_count=1,peer_count=1,collection=f.snap.id,collection_address=ffi.cast('uint8_t *',f.e),collection_unit=f.snap.network_unit,resource=f.snap.resource}
 f.put(f.rep+0x58+0x50,'\1')
 local r=reset(f.api,F.game,F.p,F.compat,F.reader_factory,scope,function(e)events[#events+1]=e end)
 assert(reads==0);assert(r.update==nil,'production must not include a post-exit sampler')
 local out={f=f,r=r,s=s,events=events}
 function out.exit()f.put(f.cmd+48+0x20,F.f32(0));f.put(f.rt+0xd28+0xd18,'\0')end
 function out.tick(t,sample)clock=t;end
 function out.reads()return reads end
 return out
end
local count=0
for _,name in ipairs({'bastion','maelstrom'})do for _,sign in ipairs({-1,0,1})do
 local t=instance(name,sign);local perform=t.r:prepare(t.s);assert(t.f.writes()==0)
 t.exit();local before=t.f.saved();perform();assert(t.f.writes()==3 and not pcall(perform))
 local expected={[t.f.inp+16]=4,[t.f.rep+0x58+0x34]=4,[t.f.rep+0x58+0x50]=1}
 for at,b in pairs(before)do
  local changed=false;for start,len in pairs(expected)do if at>=start and at<start+len then changed=true;assert(t.f.raw(at,1)=='\0')end end
  if not changed then assert(t.f.raw(at,1)==string.char(b),'unrelated control/identity/runtime field changed')end
 end
 assert(t.f.read().input_steer==0 and t.f.read().replicated_steer==0 and t.f.read().replicated_pivot_mode==0)
 t.tick(10);local n=t.reads();t.tick(10.05);assert(t.reads()==n,'window exceeds 10 Hz')
 t.tick(10.11);assert(t.reads()==n);n=t.reads();t.tick(14);t.tick(15);assert(t.reads()==n,'expired window reads')
 assert(t.events[1].event=='tank_steer_reset_preflight'and t.events[2].event=='tank_steer_reset_invoking'and t.events[3].event=='tank_steer_reset_returned')
 count=count+1
end end
local mutations={
 function(t)t.s.owned=false end,function(t)t.s.node=1 end,function(t)t.s.player_count=5;t.s.peer_count=5 end,
 function(t)t.s.active=true end,function(t)t.s.vehicle='m102';t.s.transition=26;t.s.profile={row=8,roles={1,3,3,3,2}}end,
 function(t)t.f.put(t.f.bk+12,F.u32(2))end,function(t)t.f.put(t.f.v+0x34,F.u32(0))end,
 function(t)t.f.put(t.f.d+0x2c,F.u32(0))end,function(t)t.f.put(t.f.rep+0x58+0x4f,'\0')end,
 function(t)t.f.put(t.f.inp+16,F.f32(3))end,function(t)t.f.put(t.f.rep+0x58+0x34,F.f32(3))end,
 function(t)t.f.put(t.f.e+16,F.u32(910))end,
 function(t)t.f.put(t.f.rep+0x58+0x50,'\2')end,
}
for i,change in ipairs(mutations)do local t=instance('bastion',1);change(t);assert(not pcall(t.r.prepare,t.r,t.s),'unsafe cleanup accepted '..i);assert(t.f.writes()==0);count=count+1 end
for _,mode in ipairs({'not_exited','command_not_neutral','storage_move','identity_change','owner_loss','pivot_write_failure','input_write_failure','history_write_failure'})do
 local t=instance('bastion',-1);local perform=t.r:prepare(t.s)
 if mode~='not_exited'then t.exit()end
 if mode=='command_not_neutral'then t.f.put(t.f.cmd+48+0x20,F.f32(-1))end
 if mode=='storage_move'then local dest=t.f.inp+0x100;t.f.allocate(dest,48);t.f.put(dest+16,t.f.raw(t.f.inp+16,16));t.f.put(t.f.v+0x60,F.ptr(dest))end
 if mode=='identity_change'then t.f.put(t.f.e+12,F.u32(100))end
 if mode=='owner_loss'then t.f.put(t.f.e+20,F.u32(0))end
 if mode=='history_write_failure'then t.f.fail_write(t.f.rep+0x58+0x34)end
 if mode=='input_write_failure'then t.f.fail_write(t.f.inp+16)end
 if mode=='pivot_write_failure'then t.f.fail_write(t.f.rep+0x58+0x50)end
 local before=t.f.saved();assert(not pcall(perform),mode);assert(not pcall(perform),'failed cleanup reusable')
 for at,b in pairs(before)do assert(t.f.raw(at,1)==string.char(b),'partial failure did not restore input')end
 assert(t.f.writes()==(mode=='history_write_failure'and 5 or mode=='input_write_failure'and 3 or mode=='pivot_write_failure'and 1 or 0));count=count+1
end
local t=instance('maelstrom',1);local perform=t.r:prepare(t.s);t.exit();perform();local n=t.reads();t.f.snap.owned_local=false;t.tick(10.1);t.tick(10.3);assert(t.reads()==n and t.f.writes()==3,'observer follows opponent ownership')
for n=2,4 do
 local t=instance('maelstrom',1);t.s.player_count=n;t.s.peer_count=n
 local perform=t.r:prepare(t.s);t.exit();perform();assert(t.f.writes()==3);count=count+1
end
print('PASS '..count..' real cleanup/reader cases in '..assert(os.getenv('VSS_CAPTURE'))..'; two four-byte steering stores plus one pivot byte, native-exit prerequisites, scoped ownership, no background sampling and guarded partial rollback; offline physical backend is simulated')
