local ffi=require('ffi')
local factory=assert(loadfile('work/seat_motion_loan_test/animation_sender.lua'))()
local game=ffi.cast('uint8_t *',0);local mem={};local calls=0
local function addr(p)return tonumber(ffi.cast('uintptr_t',p))end
local function words(...)local t={...};return ffi.string(ffi.new('uint32_t[?]',#t,t),#t*4)end
local expected_indices={17}
local dest=ffi.new('uint64_t[1]');ffi.copy(dest,'\16\50\84\118\152\186\220\254',8)
local cb=ffi.cast('void (*)(uint32_t,uint64_t,const void *,uint32_t)',function(hash,peer,args,n)
 assert(hash==0xbde53653 and peer==dest[0] and n==3)
 local rows=ffi.cast('const struct { uint32_t type; uint32_t size; const void *value; } *',args)
 for i=0,2 do assert(rows[i].type==(i==2 and 0 or 1)and rows[i].size==4)
  assert(ffi.cast('const uint32_t *',rows[i].value)[0]==({1007,expected_indices[calls+1],0})[i+1])end
 calls=calls+1
end)
local p={functions={}};local spec={records={}}
for i,name in ipairs({'anim_event_send','anim_event_adapter','anim_event_receive','anim_event_index','trace_send'})do
 local at=name=='trace_send'and addr(cb)or i*1000
 p.functions[name]={rva=at};spec.records[name]={length=1,chunks={}};mem[at]='x'
end
mem[0x10000]=words(0,0,7,123,1007,1)
local api={read=function(a,n)local b=mem[addr(a)];return b and b:sub(1,n)end}
local function result()return {stable=true,dispatch_matches=true,event_count=20,
 routing={messages={{found=true,hash=0xbde53653,flags={1,1},parameter_count=3,type_indices={256,567,106}}}},
 animators={{avatar_found=true,entity_matches=true,network_matches=true}},
 events={{name='action_end',hash=0xdab88e64,found=true,roundtrip=true,index=17}}}end
local x=result();local inspect={capture=function(_,a)assert(a.id==7 and a.unit==123 and a.network_unit==1007);return x end}
local trace={health=function()end};local s={avatar_address=game+0x10000,avatar=7,avatar_unit=123}
local sender=factory(api,game,p,spec,{match=function(b)return b=='x'end},inspect,trace)
local op=sender:prepare(s,dest[0],1);assert(calls==0);op.check();op.send(function()end)
assert(calls==1 and not pcall(op.send,function()end)and calls==1)
local mutations={
 function(x)x.stable=false end,function(x)x.dispatch_matches=false end,
 function(x)x.routing.messages[1].flags[1]=0 end,function(x)x.routing.messages[1].type_indices[2]=999 end,
 function(x)x.routing.messages[1].parameter_count=2 end,function(x)x.animators={}end,
 function(x)x.animators[2]=x.animators[1]end,function(x)x.animators[1].avatar_found=false end,
 function(x)x.animators[1].entity_matches=false end,function(x)x.animators[1].network_matches=false end,
 function(x)x.events[1].found=false end,function(x)x.events[1].roundtrip=false end,
 function(x)x.events[1].index=20 end,function(x)x.events[1].hash=1 end}
for _,change in ipairs(mutations)do x=result();change(x);assert(not pcall(sender.prepare,sender,s,dest[0],1));assert(calls==1)end
x=result();op=sender:prepare(s,dest[0],1);x.events[1].index=18;assert(not pcall(op.check));assert(calls==1)
x=result();mem[0x10000]=words(0,0,8,123,1007,1);assert(not pcall(sender.prepare,sender,s,dest[0],1))
mem[0x10000]=words(0,0,7,123,1007,1);mem[p.functions.anim_event_adapter.rva]='y';assert(not pcall(sender.prepare,sender,s,dest[0],1))
assert(calls==1)
mem[p.functions.anim_event_adapter.rva]='x';x=result();x.events[2]={name='frv_enter_boot',hash=0xe86f3c8c,found=true,roundtrip=true,index=18}
expected_indices={17,18,17};op=sender:prepare(s,dest[0],4);op.check();op.send(function()end);assert(calls==3)
assert(not pcall(op.send,function()end));x.events[2].roundtrip=false;assert(not pcall(sender.prepare,sender,s,dest[0],4));assert(calls==3)
x=result();expected_indices={17,18,17,17,17}
for _,target in ipairs({2,3})do op=sender:prepare(s,dest[0],target);op.check();op.send(function()end)end
assert(calls==5)
expected_indices[6]=17;op=sender:prepare(s,dest[0],0);op.check();op.send(function()end);assert(calls==6)
local profiles=assert(loadfile('work/seat_switch/src/profile.lua'))().tables
local layout=assert(loadfile('work/seat_motion_loan_test/adapter.lua'))().layout
local batch=factory(api,game,p,spec,{match=function(b)return b=='x'end},inspect,trace,layout)
for _,name in ipairs({'m103','m104','bastion','maelstrom'})do
 s.vehicle=name;s.profile=profiles[name];s.transition=s.profile.transition;x=result()
 x.events[2]={name='frv_enter_boot',hash=0xe86f3c8c,found=true,roundtrip=true,index=18}
 x.events[3]={name='clear_fall_overlay',hash=0x1e84c4c3,found=true,roundtrip=true,index=19}
 for target=0,#s.profile.roles-1 do
  local old_calls=calls
  if name=='m104'and target==2 then expected_indices[calls+1]=18;expected_indices[calls+2]=17
  elseif name=='bastion'and target>=2 then expected_indices[calls+1]=17;expected_indices[calls+2]=19
  else expected_indices[calls+1]=17 end
  local op=batch:prepare(s,dest[0],target);op.check();op.send(function()end)
  assert(calls-old_calls==((name=='m104'and target==2 or name=='bastion'and target>=2)and 2 or 1))
 end
end
s.vehicle='bastion';s.profile=profiles.bastion;s.transition=43;s.node=2;x=result()
x.events[2]={name='clear_fall_overlay',hash=0x1e84c4c3,found=true,roundtrip=true,index=19}
expected_indices[calls+1]=19;local old=calls;op=batch:prepare_fall(s,dest[0]);op.check();op.send(function()end)
assert(calls==old+1 and not pcall(op.send,function()end),'native passenger repair sends only the fall event once')
for _,change in ipairs({function()x.events[2].found=false end,function()x.events[2].roundtrip=false end,
 function()x.events[2].index=20 end,function()x.events[2].hash=1 end})do
 x=result();x.events[2]={name='clear_fall_overlay',hash=0x1e84c4c3,found=true,roundtrip=true,index=19};change()
 assert(not pcall(batch.prepare_fall,batch,s,dest[0])and calls==old+1)
end
s.vehicle='maelstrom';s.profile=profiles.maelstrom;s.transition=44
assert(not pcall(batch.prepare_fall,batch,s,dest[0])and calls==old+1)
print('PASS batched animation FFI: Bastion passenger ends old fall overlay; other tanks/FRVs keep prior sequence; native-route repair sends only the existing overlay event, validated dictionary and scope')
cb:free()
print('PASS gunner pose then action_end ordered notifications; missing/mismatched boot event blocks all sends')
print('PASS real FFI animation descriptors, uint64 peer, one-shot send, dynamic index, 14 refusal cases, identity/code/pre-send recheck')
