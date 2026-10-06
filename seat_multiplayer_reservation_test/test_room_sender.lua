-- Actual sender and uint64 FFI signatures; wire delivery is simulated.
local ffi=require('ffi')
local factory=assert(loadfile('work/seat_multiplayer_reservation_test/sender.lua'))()
local game=ffi.cast('uint8_t *',0);local mem,callbacks,calls={},{},{}
local function address(a)return tonumber(ffi.cast('uintptr_t',a))end
local function bytes(typ,n)local b=ffi.new(typ..'[1]',n);return ffi.string(b,ffi.sizeof(b))end
local function peerbytes(v)local b=ffi.new('uint64_t[1]',v);return ffi.string(b,8)end
local selfpeer='selfpeer';local keys={selfpeer,'\16\50\84\118\152\186\220\254','third!!!','fourth!!'}
local target=2
callbacks.snap=ffi.cast('void (*)(uint64_t,uint32_t,uint32_t,int32_t,uint32_t)',function(peer,av,car,t,active)
 assert(av==7 and car==9 and t==target and active==0);calls[#calls+1]={peer=peerbytes(peer),kind='snapshot'}
end)
callbacks.transition=ffi.cast('void (*)(uint64_t,uint32_t,int32_t,int32_t,int32_t,float)',function(peer,av,t,current,action,duration)
 assert(av==7 and t==target and current==target and action==-1 and duration==0);calls[#calls+1]={peer=peerbytes(peer),kind='transition'}
end)
local p={globals={session=0x100},functions={route_dispatch={rva=0x200}}};local spec={records={}}
for name,at in pairs({sync_snapshot_send=address(callbacks.snap),sync_transition_send=address(callbacks.transition),sync_snapshot_adapter=0x700,sync_transition_adapter=0x800,trace_send=0x900})do
 p.functions[name]={rva=at};spec.records[name]={length=1,chunks={}};mem[at]='x'
end
mem[0x209]=bytes('int32_t',0x1000-0x20d);mem[0x1000]=bytes('uint64_t',0x700);mem[0x1008]=bytes('uint64_t',0x800)
mem[0x100]=bytes('uint64_t',0x20000);mem[0x20000+0xb390]=bytes('uint64_t',0x40000);mem[0x40020]=selfpeer
local api={read=function(a,n)local b=mem[address(a)];return b and b:sub(1,n)end,
 pointer=function(b)local v=ffi.new('uint64_t[1]');ffi.copy(v,b,8);return ffi.cast('uint8_t *',v[0])end}
local trace={active=true,health=function()end,registry={
 {name='snapshot',found=true,hash=0xd4f97316,flags={1,1},parameter_count=4,type_indices={256,256,87,106},index=0},
 {name='transition',found=true,hash=0xdcc32107,flags={1,1},parameter_count=5,type_indices={256,87,87,517,518},index=1}}}
local binding={preflight=function()return true end,prepare=function(_,s,peer,t,grant)
 return {check=function()if grant then assert(grant:check())end end,send=function()calls[#calls+1]={peer=peerbytes(peer),kind='binding'}end}
end}
local animation={prepare=function(_,s,peer)
 return {check=function()end,send=function()calls[#calls+1]={peer=peerbytes(peer),kind='animation'}end}
end}
local send=factory(api,game,p,spec,{match=function(b)return b=='x'end},trace,animation,binding,
 assert(loadfile('work/seat_multiplayer_reservation_test/scope.lua'))().layout)
local s={vehicle='m102',transition=26,profile={roles={1,3,3,3,2},row=8},node=1,avatar=7,collection=9,owned=false}
local o={selfpeer=selfpeer,owner=keys[2],coordinator=selfpeer,busy=false,session=game+0x20000,engine=game+0x40000}
local valid=true;local grant={source=1,target=2,check=function()return valid end}
local cases=0
for n=2,4 do for host=1,n do for owner=1,n do
 o.peer_count=n;o.members={};o.owner=keys[owner];o.coordinator=keys[host];s.owned=owner==1;target=2;grant.target=2
 local destinations={};for i=1,n do o.members[keys[i]]=true;if i>1 then destinations[#destinations+1]=keys[i]end end
 mem[0x20000+0x162d8]=bytes('uint32_t',n);mem[0x20000+0x162e0]=table.concat(keys,'',1,n)
 calls={}
 if owner~=1 then assert(send:preflight_all(o,destinations,s,target)and #calls==0)end
 local invoke=send:prepare_all(o,destinations,s,target,owner~=1 and grant or nil)
 invoke(function()end);assert(#calls==(n-1)*4 and not pcall(invoke,function()end))
 for i,peer in ipairs(destinations)do for j,kind in ipairs({'snapshot','transition','binding','animation'})do
  local row=calls[(i-1)*4+j];assert(row.peer==peer and row.kind==kind,'wrong recipient/order')
 end end
 cases=cases+1
 -- Snapshot owner acquired via native reservation, target zero, all observers.
 o.owner=selfpeer;s.owned=true;target=0;grant.target=0;calls={}
 send:prepare_all(o,destinations,s,0,grant)(function()end);assert(#calls==(n-1)*4);cases=cases+1
end end end
target=2;grant.target=2;o.owner=keys[2];s.owned=false
local destinations={keys[2],keys[3],keys[4]}
local before=#calls;assert(not pcall(send.prepare_all,send,o,destinations,s,2)and #calls==before,'foreign owner allowed without grant')
valid=false;assert(not pcall(send.prepare_all,send,o,destinations,s,2,grant));valid=true
local invoke=send:prepare_all(o,destinations,s,2,grant);valid=false
assert(not pcall(invoke,function()end)and #calls==before);valid=true
for _,bad in ipairs({{selfpeer,keys[3],keys[4]},{keys[2],keys[2],keys[4]},{keys[2],keys[3]},{keys[2],keys[3],'unknown!'}})do
 assert(not pcall(send.prepare_all,send,o,bad,s,2,grant)and #calls==before)
end
invoke=send:prepare_all(o,destinations,s,2,grant)
mem[0x20000+0x162e0]=selfpeer..keys[2]..keys[3]..'changed!'
assert(not pcall(invoke,function()end)and #calls==before);mem[0x20000+0x162e0]=table.concat(keys)
-- A mid-send departure cannot resend the already delivered peer or continue.
invoke=send:prepare_all(o,destinations,s,2,grant);calls={}
assert(not pcall(invoke,function(e)if e.event=='sync_fleet_peer_returned'then mem[0x20000+0x162d8]=bytes('uint32_t',3)end end))
assert(#calls==4 and not pcall(invoke,function()end)and #calls==4)
callbacks.snap:free();callbacks.transition:free()
print('PASS '..cases..' real FFI all-member sends, exact high-bit uint64 keys, all host/owner combinations, owner/observer packet order, acquired-driver notifications and zero dry sends; forged/missing grant, self/duplicate/missing peers and in-flight join/leave refusal')
