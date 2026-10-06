local ffi=require('ffi')
local factory=assert(loadfile('work/seat_rear_weapon_diagnostic/binding_sender.lua'))()
local cb,calls={},{}
local dest=ffi.new('uint64_t',0x10203040)
cb.send=ffi.cast('void (*)(uint32_t,uint64_t,const void *,uint32_t)',function(hash,peer,ptr,count)
 assert(peer==dest);local a=ffi.cast('struct { uint32_t type; uint32_t size; const void *value; } *',ptr)
 local values={};for i=0,count-1 do assert(a[i].type==1 and a[i].size==4);values[#values+1]=tonumber(ffi.cast('const uint32_t *',a[i].value)[0])end
 calls[#calls+1]={hash=tonumber(hash),values=table.concat(values,',')}
end)
local code_ok,dispatch_ok,types_ok,after,slot2,rotation,selected,identity=true,true,true,false,0,1,90,1
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
 return {stable=true,weapon_component_found=true,rotation_flag=after and rotation or 0,
 slots={{weapon=after and selected or 80},{weapon=slot2},{weapon=0},{weapon=0},{weapon=0}}}
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
for _,target in ipairs({0,5,2.5})do assert(not pcall(sender.prepare,sender,s,dest,target))end
cb.send:free()
print('PASS real FFI clear/bind descriptors, scoped channel0, ordering, identity/selection/schema/code/restore gates, no duplicate or outbound send')
