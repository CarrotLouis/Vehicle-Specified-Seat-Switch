local M=assert(loadfile('work/seat_release_040/src/performance.lua'))()
local spec=assert(loadfile('work/seat_release_040/src/performance_spec.lua'))()
local dir=assert(os.getenv('VSS_CAPTURE'));local changes,reads,writes={},0,0
local function file(name)local f=assert(io.open(dir..'/'..name,'rb'));local b=f:read('*a');f:close();return b end
local sections={{4096,file('game.dll.01_00001000.bin')},{0x2111000,file('game.dll.02_02111000.bin')}}
local api={in_image=function(_,rva,n)return rva>=0 and n>0 and rva+n<0x4000000 end,
 describe=function()return {executable=true,readable=true}end}
function api.read(address,n)
 reads=reads+1
 for _,s in ipairs(sections)do if address>=s[1]and address+n<=s[1]+#s[2]then
  local b=s[2]:sub(address-s[1]+1,address-s[1]+n)
  for at,value in pairs(changes)do if at>=address and at<address+n then local i=at-address;b=b:sub(1,i)..string.char(value)..b:sub(i+2)end end
  return b
 end end
end
local function write(at,from,to)
 if api.read(at,2)~=string.char(from,0xc0)then return false,'fixture_changed',false end
 writes=writes+1;changes[at]=to;return true,nil,true
end
local log={};local function note(s)log[#log+1]=s end
local block=M.new(api,0,spec,write,note)
for i=1,20 do block:update(false)end;assert(reads==0 and writes==0)
block:update(true);assert(block.status=='on'and block.enabled and writes==4)
assert(block.valid(spec.hints[1],true))
local before=reads;for i=1,200 do block:update(true)end;assert(reads==before and writes==4,'no active polling or repeat writes')
block:update(false);assert(block.status=='off'and not block.enabled and writes==8)
assert(block.valid(spec.hints[1],false))
block:update(true);block:close();assert(not block.enabled and writes==16)
print('PASS captured '..os.getenv('VSS_TEST_BUILD')..': four HUD-only checks, helper/graph/advanced proof, ON/OFF/shutdown, no idle or active-frame work')

-- Failed third write rolls back exactly the earlier two, without a partial ON.
changes={};writes=0
local fail_at=spec.hints[1]+spec.sites[3]
local failed=M.new(api,0,spec,function(at,from,to)
 if at==fail_at and to==0x30 then return false,'test_permission_refused',false end
 return write(at,from,to)
end,note)
failed:update(true);assert(failed.status=='unavailable'and not failed.enabled and writes==4)
assert(failed.valid(spec.hints[1],false))
-- A changed callee or a changed branch denies activation, and a surrounding
-- rewrite denies restoration rather than overwriting another mod's code.
changes={};writes=0;block=M.new(api,0,spec,write,note);block:update(true)
changes[spec.hints[1]+10]=0
block:update(false);assert(block.status=='restore_failed'and writes==4)
changes[spec.hints[1]+10]=nil;block:update(false);assert(not block.enabled and writes==8)
print('PASS partial-write rollback and foreign-code-change refusal/recovery')
