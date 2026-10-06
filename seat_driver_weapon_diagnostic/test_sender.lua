local ffi=require('ffi')
local factory=assert(loadfile('work/seat_driver_weapon_diagnostic/sender.lua'))()
local game=ffi.cast('uint8_t *',0);local mem={};local callbacks={};local calls={}
local function address(p)return tonumber(ffi.cast('uintptr_t',p))end
local function word(n)local a=ffi.new('uint64_t[1]',n);return ffi.string(a,8)end
local function dword(n)local a=ffi.new('int32_t[1]',n);return ffi.string(a,4)end
local peer=ffi.new('uint64_t[1]');ffi.copy(peer,'\16\50\84\118\152\186\220\254',8)
local destination=ffi.string(peer,8);local expected_target=1
callbacks.snap=ffi.cast('void (*)(uint64_t,uint32_t,uint32_t,int32_t,uint32_t)',function(dest,a,c,t,active)
 assert(dest==peer[0]and a==7 and c==9 and t==expected_target and active==0);calls[#calls+1]='snapshot'
end)
callbacks.transition=ffi.cast('void (*)(uint64_t,uint32_t,int32_t,int32_t,int32_t,float)',function(dest,a,t,current,action,duration)
 assert(dest==peer[0]and a==7 and t==expected_target and current==expected_target and action==-1 and duration==0);calls[#calls+1]='transition'
end)
local p={globals={session=0x100},functions={route_dispatch={rva=0x200}}}
local spec={records={}}
for name,where in pairs({sync_snapshot_send=address(callbacks.snap),sync_transition_send=address(callbacks.transition),sync_snapshot_adapter=0x700,sync_transition_adapter=0x800,trace_send=0x900})do
 p.functions[name]={rva=where};spec.records[name]={length=1,chunks={}};mem[where]='x'
end
mem[0x209]=dword(0x1000-0x20d);mem[0x1000]=word(0x700);mem[0x1008]=word(0x800)
mem[0x100]=word(0x20000);mem[0x20000+0xb390]=word(0x40000)
local selfpeer='selfpeer';mem[0x40020]=selfpeer
local api={read=function(a,n)local b=mem[address(a)];return b and b:sub(1,n)end,pointer=function(b)if not b then return end;local v=ffi.new('uint64_t[1]');ffi.copy(v,b,8);return ffi.cast('uint8_t *',v[0])end}
local trace={active=true,health=function()end,registry={
 {name='snapshot',found=true,hash=0xd4f97316,flags={1,1},parameter_count=4,type_indices={256,256,87,106},index=0},
 {name='transition',found=true,hash=0xdcc32107,flags={1,1},parameter_count=5,type_indices={256,87,87,517,518},index=1}}}
local o={selfpeer=selfpeer,members={[destination]=true},owner=selfpeer,busy=false,session=game+0x20000,engine=game+0x40000}
local s={vehicle='m102',avatar=7,collection=9}
local binding_ok=true
local send=factory(api,game,p,spec,{match=function(b)return b=='x'end},trace,{prepare=function()return {check=function()end,send=function()calls[#calls+1]='animation'end}end},
 {prepare=function()return {check=function()assert(binding_ok,'binding_not_restored')end,send=function()calls[#calls+1]='weapon_pair'end}end})
local refused=send:prepare(o,destination,s,1);binding_ok=false;assert(not pcall(refused,function()end)and #calls==0);binding_ok=true
local operation=send:prepare(o,destination,s,1);operation(function()end)
assert(table.concat(calls,',')=='snapshot,transition,weapon_pair,animation')
assert(not pcall(operation,function()end)and #calls==4)
local changed=send:prepare(o,destination,s,1)
mem[0x40020]='changed!';assert(not pcall(changed,function()end));assert(#calls==4);mem[0x40020]=selfpeer
assert(not pcall(send.prepare,send,o,selfpeer,s,1))
trace.registry[1].type_indices[1]=1;assert(not pcall(send.prepare,send,o,destination,s,1));trace.registry[1].type_indices[1]=256
mem[0x1000]=word(0x999);assert(not pcall(send.prepare,send,o,destination,s,1));mem[0x1000]=word(0x700)
mem[p.functions.sync_snapshot_send.rva]='y';assert(not pcall(send.prepare,send,o,destination,s,1))
assert(#calls==4)
mem[p.functions.sync_snapshot_send.rva]='x'
for _,target in ipairs({0,2,3,4})do
 expected_target=target;calls={};send:prepare(o,destination,s,target)(function()end)
 assert(table.concat(calls,',')=='snapshot,transition,weapon_pair,animation')
end
callbacks.snap:free();callbacks.transition:free()
print('PASS real FFI sender ABI and exact uint64 peer, ordered messages, changed identity/schema/handler/code refusal')
