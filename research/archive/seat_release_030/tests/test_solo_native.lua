local ffi=require('ffi')
local factory=assert(loadfile('work/seat_release_030/solo_native.lua'))()
local scope=assert(loadfile('work/seat_release_030/src/scope.lua'))()
local profile=assert(loadfile('work/seat_release_030/src/profile.lua'))()
local game=ffi.cast('uint8_t *',0)
local function address(v)return tonumber(ffi.cast('uintptr_t',v))end
local systems,engine=ffi.cast('uint8_t *',0x20000000),ffi.cast('uint8_t *',0x21000000)
local busy,lowered,executed,checked=false,0,0,0
local cb={}
cb.busy=ffi.cast('bool (*)(void *,uint32_t)',function(e,u)assert(e==engine and u==9);return busy end)
cb.active=ffi.cast('void (*)(void *,uint32_t,bool)',function(m,a,v)assert(m==systems and a==7 and v==false);lowered=lowered+1 end)
local p={functions={ownership_busy={rva=address(cb.busy),bytes='x'},active_passenger={rva=address(cb.active),bytes='x'}},globals={entities=0x100}}
local api={ffi=ffi,read=function(a,n)
 if address(a)==0x100 then return 'systems' elseif a==systems+8 then return 'engine' else return 'x'end
end,pointer=function(b)if b=='systems'then return systems elseif b=='engine'then return engine end end}
local pose_ok=true
local pose=function()return {check=function()checked=checked+1;assert(pose_ok);return true end}end
local owned={prepare=function(_,s,t)assert(scope.direction(s,t)and s.owned and not s.active and s.player_count==1 and s.peer_count==1);return function()executed=executed+1 end end}
local n=factory(api,game,p,{next=function()end,previous=function()end},owned,pose,scope)
local s={vehicle='m102',transition=26,profile=profile.tables.m102,node=1,owned=true,active=false,player_count=1,peer_count=1,collection_unit=9,seaters=systems,avatar=7}
assert(n.available(s));n.direct(s,4);assert(executed==1)
s.active=true;n.prepare(s);assert(lowered==1 and not pcall(n.direct,s,4));s.active=false
for _,mutation in ipairs({function()s.owned=false end,function()s.player_count=2;s.peer_count=2 end,function()s.peer_count=0 end,
 function()s.transition=25 end,function()busy=true end,function()pose_ok=false end})do
 mutation();local before=executed;assert(not n.available(s));assert(not pcall(n.direct,s,4));assert(executed==before)
 s.owned=true;s.player_count=1;s.peer_count=1;s.transition=26;busy=false;pose_ok=true
end
assert(checked>0);for _,v in pairs(cb)do v:free()end
print('PASS actual solo availability/lowering FFI signatures, transaction routing and ownership/member/schema/busy/pose refusal guards; engine behavior simulated')
