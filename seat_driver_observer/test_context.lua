local ffi=require('ffi');local make=assert(loadfile('work/seat_driver_observer/context.lua'))()
local game,exe,session,engine,vt=0x10000000,0x20000000,0x30000000,0x30001000,0x20008000
local memory={};local count=0;local fault
local function put(a,b)memory[a]=b end
local function packed(kind,v)local b=ffi.new(kind..'[1]',v);return ffi.string(b,ffi.sizeof(b))end
local function raw(a,n)for at,b in pairs(memory)do if a>=at and a+n<=at+#b then return b:sub(a-at+1,a-at+n)end end end
local api={module=function()return exe end,pointer=function(b)local q=ffi.new('uint64_t[1]');ffi.copy(q,b,8);return tonumber(q[0])end}
function api.read(a,n)count=count+1;if fault then fault(a,n,count)end;return raw(a,n)end
local p={globals={session=0x5000},engine_functions={authority_constructor={rva=0x1000}}}
local function setup()
 memory={};count=0;fault=nil
 put(game+0x5000,packed('uint64_t',session));put(session+0xb390,packed('uint64_t',engine))
 put(engine,packed('uint64_t',vt));local at=exe+0x1012
 put(at,'\72\141\5'..packed('int32_t',vt-(at+7)))
 put(vt+0x68,packed('uint64_t',exe+0x2000));put(exe+0x2000,'\72\139\65\32\195')
 put(vt+0x98,packed('uint64_t',exe+0x3000));put(exe+0x3000,'\72\139\129\48\1\0\0\195')
 put(engine+0x20,'DRIVER12');put(engine+0x130,'HOST1234');put(engine+0x60e4,'EPCH')
 put(session+0xb398,'DRIVER12');put(session+0xb3a8,'HOST1234')
end
local s={state='mission',player_count=2,peer_count=2,local_count=1,mission_value=123};local v={name='m102'}
setup();local x=make(api,game,p);local o=x:read(s,v)
assert(o.engine==engine and o.session==session and o.selfpeer=='DRIVER12'and o.coordinator=='HOST1234')
assert(count==23 and o.read_count==23 and o.local_peer_hex=='4452495645523132')
for _,bad in ipairs({
 function()put(engine,packed('uint64_t',vt+8))end,
 function()put(exe+0x1012,'bad????')end,
 function()put(exe+0x2000,'wrong')end,
 function()put(exe+0x3000,'wrong!!!')end,
 function()put(session+0xb398,'NOTSAME!')end,
 function()put(engine+0x20,string.rep('\0',8))end,
 function()fault=function(a,n,k)if k==14 then put(engine+0x60e4,'NEXT')end end end,
})do setup();bad();assert(not pcall(x.read,x,s,v))end
s.player_count=3;setup();assert(not pcall(x.read,x,s,v)and count==0)
print('PASS read-only session context: 23 bounded reads, actual constructor/leaf identities, 7 mismatched/raced guards, room barrier, no authority calls')
