local ffi=require('ffi')
local factory=assert(loadfile('work/seat_tank_binding_fix/binding_sender.lua'))()
local cb,calls={},{}
local dest=ffi.new('uint64_t',0x10203040)
cb.send=ffi.cast('void (*)(uint32_t,uint64_t,const void *,uint32_t)',function(hash,peer,ptr,count)
 assert(peer==dest);local a=ffi.cast('struct { uint32_t type; uint32_t size; const void *value; } *',ptr)
 local values={};for i=0,count-1 do assert(a[i].type==1 and a[i].size==4);values[#values+1]=tonumber(ffi.cast('const uint32_t *',a[i].value)[0])end
 calls[#calls+1]={hash=tonumber(hash),values=table.concat(values,',')}
end)
local code_ok,dispatch_ok,types_ok,after,slot2,rotation,selected,identity=true,true,true,false,0,1,90,1
local before_weapon,before_rotation=80,0
local p={functions={}};local spec={records={}}
for i,name in ipairs({'binding_clear_avatar','binding_clear_adapter','binding_clear_dispatch','binding_bind_adapter','binding_bind_dispatch','binding_bind_send','binding_entity_lookup','trace_send'})do
 p.functions[name]={rva=name=='trace_send'and tonumber(ffi.cast('uintptr_t',cb.send))or i};spec.records[name]={length=1,chunks={}}
end
local api={read=function()return code_ok and 'x'or 'y'end}
local inspector={}
function inspector:interface()return {state='observed',clear_dispatch_matches=dispatch_ok,bind_dispatch_matches=dispatch_ok,messages={
 {hash=0x423a4034,found=true,flags={1,1},parameter_count=2,type_indices={256,types_ok and 536 or 1}},
 {hash=0x2671dec5,found=true,flags={1,1},parameter_count=3,type_indices={256,536,256}}}}end
function inspector:entity(id)return {id=id,unit=id+100,network_unit=id+1000,flags=identity}end
function inspector:capture(a)
 assert(a.id==7 and a.unit==107 and a.network_unit==1007 and a.is_local)
 return {stable=true,weapon_component_found=true,rotation_flag=after and rotation or before_rotation,
 slots={{weapon=after and selected or before_weapon},{weapon=slot2},{weapon=0},{weapon=0},{weapon=0}}}
end
local sender=factory(api,ffi.cast('uint8_t *',0),p,spec,{match=function(b)return b=='x'end},inspector,{}, {health=function()end},function()return function()return true,selected end end)
local s={avatar=7,avatar_unit=107,node=4,vehicle='m102',owned=true}
local function prepare()after=false;return sender:prepare(s,dest,1)end
local op=prepare();after=true;op.check();op.send(function()end)
assert(#calls==2 and calls[1].hash==0x423a4034 and calls[1].values=='1007,0'and calls[2].hash==0x2671dec5 and calls[2].values=='1007,0,1090')
assert(not pcall(op.send,function()end)and #calls==2)
op=prepare();after=true;rotation=0;assert(not pcall(op.send,function()end));rotation=1
op=prepare();after=true;selected=91;assert(not pcall(op.send,function()end));selected=90
op=prepare();after=true;identity=3;assert(not pcall(op.send,function()end));identity=1
slot2=42;assert(not pcall(prepare));slot2=0
types_ok=false;assert(not pcall(prepare));types_ok=true
dispatch_ok=false;assert(not pcall(prepare));dispatch_ok=true
code_ok=false;assert(not pcall(prepare));code_ok=true
local none=sender:prepare(s,dest,4);none.check();none.send(function()end);assert(#calls==2)
for _,target in ipairs({2,3})do
 after=false;local rear=sender:prepare(s,dest,target);after=true;rear.check();rear.send(function()end)
 assert(calls[#calls-1].hash==0x423a4034 and calls[#calls-1].values=='1007,0')
 assert(calls[#calls].hash==0x2671dec5 and calls[#calls].values=='1007,0,1090')
end
assert(#calls==6)
for _,target in ipairs({-1,5,2.5})do assert(not pcall(sender.prepare,sender,s,dest,target))end
after=false;local driver=sender:prepare(s,dest,0);after=true;driver.check();driver.send(function()end)
assert(#calls==8 and calls[7].hash==0x423a4034 and calls[8].values=='1007,0,1090')
s.node=0;local none=sender:prepare(s,dest,2);none.check();none.send(function()end);assert(#calls==8)
local profiles=assert(loadfile('work/seat_switch/src/profile.lua'))().tables
local layout=assert(loadfile('work/seat_tank_binding_fix/adapter.lua'))().layout
local batch=factory(api,ffi.cast('uint8_t *',0),p,spec,{match=function(b)return b=='x'end},inspector,{},
 {health=function()end},function()return function()return true,selected end end,layout)
local batch_cases=0
for _,name in ipairs({'m104','bastion','maelstrom'})do
 s.vehicle=name;s.profile=profiles[name];s.transition=s.profile.transition
 local sources=name=='m104'and {2}or name=='maelstrom'and {0,1}or {1}
 for _,source in ipairs(sources)do for target=0,#s.profile.roles-1 do
  if s.profile.roles[target+1]==3 or name=='m104'and target==0 then
   s.node=source;after=false;slot2=name=='m104'and 0 or 81;local before=#calls
   local op=batch:prepare(s,dest,target);after=true;slot2=0;op.check();op.send(function()end)
   local count=name=='m104'and 2 or 3
   assert(#calls-before==count and calls[before+1].values=='1007,0')
   if count==3 then assert(calls[before+2].hash==0x423a4034 and calls[before+2].values=='1007,1')end
   assert(calls[#calls].hash==0x2671dec5 and calls[#calls].values=='1007,0,1090')
   assert(not pcall(op.send,function()end));batch_cases=batch_cases+1
  end
 end end
 -- Native driver/turret restoration must retain its new mounted binding.
 s.node=name=='m104'and 0 or 1;local target=name=='m104'and 2 or 0
 local before=#calls;local none=batch:prepare(s,dest,target);none.check();none.send(function()end);assert(#calls==before)
end
s.vehicle='maelstrom';s.profile=profiles.maelstrom;s.transition=44;s.node=1
after=false;slot2=81;local op=batch:prepare(s,dest,2);after=true;local before=#calls
assert(not pcall(op.send,function()end)and #calls==before,'remaining coax channel must prevent sync')
slot2=0
print('PASS '..batch_cases..' batched binding FFI cases: M104 mounted seat2; tank turret/coax channels0/1; Maelstrom driver-smoke to personal; no clearing new mounted/driver bindings; incomplete coax restore refused')
local driver_cases=0
local old_factory=assert(loadfile('work/seat_tank_binding_fix/regression_0181_binding_sender.lua'))()
local old_batch=old_factory(api,ffi.cast('uint8_t *',0),p,spec,{match=function(b)return b=='x'end},inspector,{},
 {health=function()end},function()return function()return true,selected end end,layout)
for _,target in ipairs({2,3})do
 s.vehicle='bastion';s.profile=profiles.bastion;s.transition=43;s.node=0;after=false;slot2=0
 local before=#calls;local op=old_batch:prepare(s,dest,target);after=true;op.check();op.send(function()end)
 assert(#calls==before,'0.18.1 must reproduce missing Bastion driver-to-passenger weapon synchronization')
end
print('PASS 2 frozen0.18.1 Bastion driver-to-passenger missing-weapon-sync reproductions')
for _,name in ipairs({'bastion','maelstrom'})do for _,target in ipairs({2,3})do
 for _,old in ipairs({0,selected,80})do for _,coax in ipairs({0,81})do
  s.vehicle=name;s.profile=profiles[name];s.transition=s.profile.transition;s.node=0
  before_weapon=old;before_rotation=old==selected and 1 or 0;after=false;slot2=coax
  local before=#calls;local op=batch:prepare(s,dest,target)
  after=true;slot2=0;op.check();op.send(function()end)
  assert(#calls==before+3 and calls[before+1].hash==0x423a4034 and calls[before+1].values=='1007,0')
  assert(calls[before+2].hash==0x423a4034 and calls[before+2].values=='1007,1')
  assert(calls[before+3].hash==0x2671dec5 and calls[before+3].values=='1007,0,1090')
  assert(not pcall(op.send,function()end)and #calls==before+3)
  driver_cases=driver_cases+1
 end end
end end
-- Empty/matching old personal slots are allowed only for verified tank drivers.
s.vehicle='bastion';s.profile=profiles.bastion;s.transition=43;s.node=1
before_weapon=0;before_rotation=0;after=false;slot2=0
assert(not pcall(batch.prepare,batch,s,dest,2))
before_weapon=selected;assert(not pcall(batch.prepare,batch,s,dest,2))
before_weapon=80;local op=batch:prepare(s,dest,2);after=true;selected=91;local before=#calls
assert(not pcall(op.send,function()end)and #calls==before);selected=90
print('PASS '..driver_cases..' tank-driver personal binding FFI cases: both tanks/both passenger seats/empty-same-other old primary/empty-coax secondary; always clear0+clear1+selected-bind0; empty/matching gunner and changed selection refused')
cb.send:free()
print('PASS real FFI clear/bind descriptors, scoped channel0, ordering, identity/selection/schema/code/restore gates, no duplicate or outbound send')
