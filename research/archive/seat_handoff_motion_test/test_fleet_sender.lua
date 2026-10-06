local ffi=require('ffi')
local factory=assert(loadfile('work/seat_handoff_motion_test/sender.lua'))()
local game=ffi.cast('uint8_t *',0);local mem={};local callbacks={};local calls={}
local function address(p)return tonumber(ffi.cast('uintptr_t',p))end
local function word(n)local a=ffi.new('uint64_t[1]',n);return ffi.string(a,8)end
local function dword(n)local a=ffi.new('int32_t[1]',n);return ffi.string(a,4)end
local function raw(v)return ffi.string(ffi.new('uint64_t[1]',v),8)end
local allowed={}
local drop_after_transition=false
local peer=ffi.new('uint64_t[1]');ffi.copy(peer,'\16\50\84\118\152\186\220\254',8)
local destination=ffi.string(peer,8);local expected_target=1
callbacks.snap=ffi.cast('void (*)(uint64_t,uint32_t,uint32_t,int32_t,uint32_t)',function(dest,a,c,t,active)
 assert(allowed[raw(dest)]and a==7 and c==9 and t==expected_target and active==0);calls[#calls+1]='snapshot:'..raw(dest)
end)
callbacks.transition=ffi.cast('void (*)(uint64_t,uint32_t,int32_t,int32_t,int32_t,float)',function(dest,a,t,current,action,duration)
 assert(allowed[raw(dest)]and a==7 and t==expected_target and current==expected_target and action==-1 and duration==0);calls[#calls+1]='transition:'..raw(dest);if drop_after_transition then mem[0x20000+0x162d8]=dword(2)end
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

local others={destination,'\1\2\3\4\5\6\7\128','\16\15\14\13\12\11\10\255'}
local function setup(n)
 calls={};allowed={};o.peer_count=n;o.members={[selfpeer]=true};local raw=selfpeer
 for i=1,n-1 do o.members[others[i]]=true;allowed[others[i]]=true;raw=raw..others[i]end
 mem[0x20000+0x162d8]=dword(n);mem[0x20000+0x162e0]=raw
 local peers={};for i=1,n-1 do peers[i]=others[i]end;return peers
end
local count=0
for n=2,4 do
 local peers=setup(n);local operation=send:prepare_all(o,peers,s,1);assert(#calls==0);operation(function()end)
 assert(#calls==(n-1)*4)
 for i=1,n-1 do local at=(i-1)*4
  assert(calls[at+1]=='snapshot:'..peers[i]and calls[at+2]=='transition:'..peers[i]and
    calls[at+3]=='weapon_pair'and calls[at+4]=='animation')
 end
 assert(not pcall(operation,function()end)and #calls==(n-1)*4);count=count+1
end
for _,change in ipairs({
 function()mem[0x20000+0x162d8]=dword(2)end,
 function()mem[0x20000+0x162e0]=selfpeer..others[2]..others[1]end,
 function()mem[0x40020]='changed!'end,
 function()binding_ok=false end,
})do
 local peers=setup(3);local operation=send:prepare_all(o,peers,s,1);change()
 assert(not pcall(operation,function()end)and #calls==0)
 mem[0x40020]=selfpeer;binding_ok=true;count=count+1
end
for _,peers in ipairs({{others[1],others[1]},{others[1],selfpeer},{others[1],'foreign!'},{others[1]}})do
 setup(3);assert(not pcall(send.prepare_all,send,o,peers,s,1)and #calls==0);count=count+1
end
local peers=setup(3);local operation=send:prepare_all(o,peers,s,1);drop_after_transition=true
assert(not pcall(operation,function()end)and #calls==4)
assert(not pcall(operation,function()end)and #calls==4,'Never repeat a partially delivered fanout');count=count+1
callbacks.snap:free();callbacks.transition:free()
print('PASS '..count..' actual FFI all-peer sender cases: exact high-bit 64-bit peers, per-peer seat/weapon/pose order, no self/broadcast/duplicates, membership/identity/schema guard and no retransmission after partial delivery; no wire acknowledgement claimed')
