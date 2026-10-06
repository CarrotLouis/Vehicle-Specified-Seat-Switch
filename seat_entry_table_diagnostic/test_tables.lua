local M=assert(loadfile('work/seat_entry_table_diagnostic/tables.lua'))()
local p=assert(loadfile('work/seat_switch/src/profile.lua'))()
M.extend(p)
local memory,reads={},{}
local function le(n)if n<0 then n=n+4294967296 end;local s='';for _=1,4 do s=s..string.char(n%256);n=math.floor(n/256)end;return s end
for _,r in ipairs(M.ranges)do
 local data=''
 for i=1,r.rows do
  -- Empty lists have their terminator first, with ignored nonzero padding.
  if i==1 then data=data..le(-1)..string.rep(le(999),r.row/4-1)
  else data=data..le((i-1)%r.seats)..string.rep(le(-1),r.row/4-1)end
 end
 memory[p.tables[r.vehicle].rva]=data
end
local api={read=function(a,n)reads[#reads+1]={a=a,n=n};return memory[a]end}
local out=M.capture(api,0,p);assert(out.total_bytes==424 and #out.tables==6 and #reads==12)
for _,t in ipairs(out.tables)do assert(t.hex:sub(1,8)=='ffffffff' and #t.hex==t.rows*t.row*2)end
local base=p.tables.m102.rva;local old=memory[base]
memory[base]=nil;assert(not pcall(M.capture,api,0,p));memory[base]=old
memory[base]=old:sub(1,-2);assert(not pcall(M.capture,api,0,p));memory[base]=old
memory[base]=le(500)..old:sub(5);assert(not pcall(M.capture,api,0,p));memory[base]=old
memory[base]=le(0)..le(0)..old:sub(9);assert(not pcall(M.capture,api,0,p));memory[base]=old
local calls=0;local changing={read=function(a,n)calls=calls+1;return calls==2 and string.rep('\0',n) or memory[a]end}
assert(not pcall(M.capture,changing,0,p))
print('PASS bounded table capture: 424 bytes, stable paired reads, empty rows/padding, missing/short/changing/invalid data rejected')
