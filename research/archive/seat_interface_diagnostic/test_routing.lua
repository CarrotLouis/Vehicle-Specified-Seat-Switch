local ffi=require('ffi')
local M=assert(loadfile('work/seat_interface_diagnostic/routing.lua'))()
local base,exe=0x10000000,0x20000000
local root,session_global=0x4000,0x5000
local send,decode,setup,dispatcher=0x1000,0x2000,0x3000,0x6000
local session,network,registry,rows=0x30000000,0x31000000,0x32000000,0x33000000
local mem={};local mutate,mutate_types=false,false;local counts={};local types_at=0x34000000
local function le(n)local v=ffi.new('uint32_t[1]',n);return ffi.string(v,4)end
local function ptr(n)local v=ffi.new('uint64_t[1]',n);return ffi.string(v,8)end
local function reference(b,at,target,op)mem[b+at]=op..le(target-at-7)end
reference(exe,send+0x2d,root,'\72\139\61');reference(exe,decode+0x2a,root,'\72\139\53')
reference(base,setup+0x14,session_global,'\72\139\53');reference(base,setup+0x13c,dispatcher,'\72\141\5')
mem[base+session_global]=ptr(session);mem[session+0xb3f8]=ptr(base+dispatcher)
mem[exe+root]=ptr(network);mem[network]=ptr(registry);mem[registry+0x88]=le(3);mem[registry+0x90]=ptr(rows)
for i,h in ipairs({10,20,30})do
 local b=le(h)..'\1\0'..string.rep('\0',74)..le(0)..string.rep('\0',20)
 assert(#b==0x68);mem[rows+(i-1)*0x68]=b
end
local api={module=function()return exe end,in_image=function()return true end,
 pointer=function(b,o)local v=ffi.new('uint64_t[1]');ffi.copy(v,b:sub((o or 0)+1,(o or 0)+8),8);return v[0]~=0 and tonumber(v[0])or nil end,
 describe=function()return {writable=true,state=4096}end}
function api.read(a,n)
 counts[a]=(counts[a]or 0)+1
 if mutate and a==registry+0x88 and counts[a]>1 then return le(4)end
 if mutate_types and a==types_at and counts[a]>1 then return le(8)..le(9)end
 local b=mem[a];return b and #b>=n and b:sub(1,n)or nil
end
local p={engine_functions={route_send_many={rva=send},route_decode={rva=decode}},functions={route_setup={rva=setup},route_dispatch={rva=dispatcher}},globals={session=session_global}}
local reader=M.new(api,base,p,{[10]='one',[30]='three',[40]='absent'})
local s=reader:capture();assert(s.state=='observed' and s.callback.matches_dispatch and s.callback.stable)
assert(s.messages[1].index==0 and s.messages[2].index==2 and not s.messages[3].found)
local function put(b,o,x)return b:sub(1,o)..x..b:sub(o+#x+1)end
mem[rows]=put(put(mem[rows],0x50,le(2)),0x58,ptr(types_at));mem[types_at]=le(7)..le(9)
s=reader:capture();assert(s.messages[1].parameter_count==2 and s.messages[1].type_indices[1]==7 and s.messages[1].type_indices[2]==9)
counts={};mutate_types=true;s=reader:capture();assert(s.state=='registry_changed_during_read');mutate_types=false
mem[session+0xb3f8]=ptr(base+dispatcher+16);s=reader:capture();assert(not s.callback.matches_dispatch)
mutate=true;counts={};s=reader:capture();assert(s.state=='registry_changed_during_read' and #s.messages==0)
mutate=false;mem[registry+0x88]=le(8193);s=reader:capture();assert(s.state=='invalid_registry_layout')
mem[exe+root]=nil;s=reader:capture();assert(s.state=='network_state_unavailable')
reference(exe,decode+0x2a,root+8,'\72\139\53')
local ok,why=pcall(M.new,api,base,p,{});assert(not ok and why:find('inconsistent_registry_root'))
print('PASS routing reader: selected/absent messages, callback mismatch, registry mutation/bounds, unavailable root, conflicting witnesses')
