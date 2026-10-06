local ffi=require('ffi');local scope=assert(loadfile('work/seat_release_030/src/scope.lua'))()
local factory=assert(loadfile('work/seat_release_030/src/release_acquired.lua'))()
local calls=0;local expected_slot,expected_index=3,12
local callback=ffi.cast('void (*)(void *,uint32_t,int32_t)',function(manager,index,slot)
 assert(manager==ffi.cast('void *',0x420000)and index==expected_index and slot==expected_slot);calls=calls+1
end)
local at=tonumber(ffi.cast('uintptr_t',callback));local code='x'
local p={functions={release={rva=at,bytes='x'}}};local game=ffi.cast('uint8_t *',0)
local api={ffi=ffi,read=function(address,n)assert(tonumber(ffi.cast('uintptr_t',address))==at and n==1);return code end}
local release=factory(api,game,p,scope)
local s={vehicle='bastion',transition=43,profile={row=12,roles={1,2,3,3}},owned=true,node=3,collections=ffi.cast('void *',0x420000),collection_index=12}
local valid=true;local grant={source=3,target=0,check=function()return valid end}
local perform=release:prepare(s,3,grant);perform();assert(calls==1 and not pcall(perform))
perform=release:prepare(s,3,grant);valid=false;assert(not pcall(perform)and calls==1);valid=true
perform=release:prepare(s,3,grant);code='y';assert(not pcall(perform)and calls==1);code='x'
grant.source=2;assert(not pcall(release.prepare,release,s,3,grant));grant.source=3
grant.target=2;assert(not pcall(release.prepare,release,s,3,grant));grant.target=0
s.owned=false;assert(not pcall(release.prepare,release,s,3,grant));s.owned=true
assert(not pcall(release.prepare,release,s,0,grant)and calls==1)
-- Fresh component index after legitimate driver authority acquisition is used.
s.collection_index=47;expected_index=47;release:prepare(s,3,grant)();assert(calls==2)
callback:free()
print('PASS acquired-owner native release ABI; exact OWN old slot/fresh index, real matching grant, changed grant/code, nonowner and repeated-call refusal')
