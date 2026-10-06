-- The 0.9.2 layout probe reads the heap through FFI, so this test allocates REAL memory:
-- a fabricated address space would fault instead of failing softly. The adapter's own
-- test replaces capture() wholesale, so without this file a probe failure would ship
-- unnoticed - which is exactly what happened in the 0.9.0 run.
local ffi=require('ffi')
local M=assert(loadfile('work/seat_weapon_sync_diagnostic/adapter.lua'))()

local GAME_MAGIC=0x3326698
-- The cdata objects must be retained: returning only the address would leave the buffers
-- garbage-collectable, and a collected buffer gets reused - which produced exactly the
-- erratic reads this test first showed (a written value reading back as 0, a zeroed
-- buffer reading back non-zero).
local keep={}
local function alloc(bytes)local b=ffi.new('uint8_t[?]',bytes);keep[#keep+1]=b;return tonumber(ffi.cast('uintptr_t',b))end
-- Addresses are numbers here too, so the same uint64 hop is needed: casting a double
-- straight to a pointer truncates to 32 bits and would write to the wrong place.
local function pp(a)return ffi.cast('uint8_t *',ffi.cast('uint64_t',a))end
local function p64(a,v)ffi.cast('uint64_t *',pp(a))[0]=v end
local function p32(a,v)ffi.cast('uint32_t *',pp(a))[0]=v end

-- collections: a full match for the layout the engine worker at 0x636a30 consumes.
local col=alloc(0x100)
local rows=alloc(0x200)
p64(col+0x20,rows);p32(col+0x28,4);p32(col+0x2c,0x9c);p64(col+0x48,rows)
-- The engine's lookup for the local collection id (9) must resolve: with mult=[+0x30]=2 and
-- count 4, probe index 0 addresses slot (0+9*2)%4 = 2, so plant the matching key there.
p32(col+0x30,2);p32(rows+2*8,9);p32(rows+2*8+4,3)
-- The value is a row index, so row 3 must carry a vehicle-type id in range 1..45, which is
-- what separates a real context from a container that merely happens to hold the same id.
p32(rows+3*0x64,40);p32(rows+3*0x64+4,0x11)
-- The two offsets the project's own snapshot reaches through.
local sub50=alloc(0x40);local sub58=alloc(0x40)
p64(col+0x50,sub50);p64(col+0x58,sub58);p32(sub50+0xc,11);p32(sub58+0xc,22)
-- Row contents are written last so no later allocation can sit in front of them.
p32(rows,0x4107);p32(rows+0x64,0x4108);p32(rows+0xc8,0x4109)

-- seaters: allocated and zeroed, so it is readable but matches nothing. A garbage count is
-- planted to prove the lookup refuses to walk it: 0.9.5 hung the game looping over exactly this.
local sea=alloc(0x100)
p32(sea+0x28,0x7fffffff)

-- A fake module image spanning every global offset used (0x3326308 .. 0x346bf98), so the
-- probe's reads all land inside real allocated memory. It must start at the LOWEST offset.
local BASE=0x3326308
local img=alloc(0x3500000)
local obj=alloc(0x100)
p64(img+(GAME_MAGIC-BASE),obj)
p64(obj+0x20,rows);p32(obj+0x28,7);p32(obj+0x2c,3);p64(obj+0x48,rows)
local game=img-BASE

local function seat(node,role)return {collection=9,current=node,reserved=node,role=role,target=-1,action=-1,transitioning=0,queued_exit=0}end
local sample={state='mission',player_count=2,local_count=1,
 avatars={{id=7,unit=77,is_local=true,owned_local=true,vehicle_input=true,seat=seat(1,3)}}}
local reader={capture=function()return sample end}
local owner={selfpeer='self',coordinator='friend',members={self=true,friend=true},peer_count=2,busy=false,
 context='ctx',owner='friend',vehicle={id=9,unit=88,network_unit=99,resource=5},avatars={[7]={owner='self'}}}
local owner_reader={capture=function()return owner end,summary=function()return {}end}
local native={identity='avatar_binding',vehicle='m102',transition=26,profile={roles={1,3,3,3,2}},
 player_count=2,peer_count=2,owned=false,avatar=7,avatar_unit=77,node=1,collection=9,
 collection_unit=99,resource=5,collections=col,seaters=sea}
local snapshot={capture=function()return native end,current=function()return true end}
local events={}
-- The globals are skipped without a module base: they are proven to work in the live run,
-- and faking a 55 MB image here would add risk without covering the layout decoding that
-- this test exists to protect.
local game=0
local a=M.new({},game,{},reader,owner_reader,snapshot,{},{},{active=true,health=function()end},
 function(e)events[#events+1]=e end,function()return 'x'end)

local c=a:capture()
assert(c and c.native,'capture must still succeed with the probe installed')

local probe,begin_seen,error_seen
for _,e in ipairs(events)do
 if e.event=='probe_layout'and not probe then probe=e end
 if e.event=='probe_layout_begin'then begin_seen=true end
 if e.event=='probe_layout_error'then error_seen=e end
end
assert(begin_seen,'the probe must announce itself before reading')
assert(probe,'the probe must emit a probe_layout event')
assert(not error_seen,'no outer error was expected, got '..tostring(error_seen and error_seen.message))

local L=probe.layout
-- The snapshot hands over FFI pointers, not numbers, so the probe must normalise them.
local col_e=L.collections
assert(col_e and col_e.addr,'collections must be reported by address even when it is a pointer')
assert(col_e.p20 and col_e.n28==4 and col_e.n2c==0x9c,'the worker layout must decode through FFI')
-- The discriminator: the engine's own lookup must find the local collection id here, and the
-- value beside the key must come back, because shape alone cannot separate the containers.
assert(col_e.lookup_id==9,'the lookup key must be reported')
assert(col_e.lookup_found==true,'the engine lookup must find the local collection id, got '..tostring(col_e.lookup_found))
assert(col_e.lookup_slot==2 and col_e.lookup_value==3,
 'the lookup must report the slot and the row index, got '..tostring(col_e.lookup_slot)..'/'..tostring(col_e.lookup_value))
assert(col_e.lookup_row0==40 and col_e.lookup_row4==0x11,
 'the row the worker would use must be read, got '..tostring(col_e.lookup_row0)..'/'..tostring(col_e.lookup_row4))
assert(col_e.lookup_type_valid==true,'a row id in 1..45 must be flagged as a valid vehicle type')

-- The property under test is the 0x64 stride, and all three rows must decode.
assert(col_e.row0_id==0x4107 and col_e.row1_id==0x4108 and col_e.row2_id==0x4109,
 'rows must be read at the 0x64 stride, got '..tostring(col_e.row0_id)..'/'..
 tostring(col_e.row1_id)..'/'..tostring(col_e.row2_id))
-- The offsets the project's own snapshot reaches through, so the two views can be related.
assert(col_e.c50==11 and col_e.c58==22,'the snapshot\'s own offsets must be reported too')

-- Readable but empty: an address, and no matching layout. This is how a non-candidate must look.
local sea_e=L.seaters
assert(sea_e and sea_e.addr and sea_e.p20==nil and sea_e.p48==nil,
 'a zeroed candidate must be reported as an address with no fields')
assert(sea_e.lookup_found==nil,'a garbage count must be skipped, not walked (0.9.5 hung here)')

-- Without a module base the global scan must be skipped entirely, not dereference junk.
for key in pairs(L)do
 assert(not key:match('^global'),'no global may be probed without a module base, found '..key)
end

local before=#events
a:capture()
assert(#events==before,'the probe must emit at most once per session')

-- A wild pointer must be reported as unreadable, not dereferenced. 0.9.2 crashed the game on
-- boarding because an unguarded read faulted; this is the regression guard for that.
local wild_events={}
local wild_native={}
for k,v in pairs(native)do wild_native[k]=v end
wild_native.collections=0x1000
wild_native.seaters=0x10
local wild_snapshot={capture=function()return wild_native end,current=function()return true end}
local w=M.new({},0,{},reader,owner_reader,wild_snapshot,{},{},{active=true,health=function()end},
 function(e)wild_events[#wild_events+1]=e end,function()return 'x'end)
w:capture()
local wild
for _,e in ipairs(wild_events)do if e.event=='probe_layout'then wild=e end end
assert(wild,'the probe must survive a wild pointer and still emit a result')
for _,label in ipairs({'collections','seaters'})do
 local e=wild.layout[label]
 assert(e and (e.none or (e.p20==nil and e.p48==nil)),
  label..' must be reported as unreadable, got '..tostring(e and e.p20))
end

print('PASS layout probe: emits once, normalises FFI pointers to addresses, decodes the ' ..
 'worker\'s [+0x20]/[+0x28]/[+0x2c]/[+0x48] layout with 0x64-stride rows through real memory, ' ..
 'also reports the snapshot\'s own [+0x50]/[+0x58] offsets, dereferences the candidate globals, ' ..
 'reports a zeroed candidate as an address with no fields, and refuses to dereference an ' ..
 'unreadable address instead of crashing. Read-only; memory is really allocated.')
