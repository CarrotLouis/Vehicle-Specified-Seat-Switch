local ffi=require('ffi')
local factory=assert(loadfile('work/seat_sync_diagnostic/transport.lua'))()
local observer={locate=function()return 0x80 end}
local messages=assert(loadfile('work/seat_transport_diagnostic/messages.lua'))()
local counts={switch_request=4,accepted=3,snapshot=4,transition=5,switch_denied=2,entry_request=3,exit_request=4,entry_denied=2,entering=3,release_request=2,release_retry=2,exit_accepted=4,exit_denied=2,authority_request=2,authority_owned=2}
local route={capture=function()local list={};for h,n in pairs(messages)do list[#list+1]={found=true,hash=h,name=n,parameter_count=counts[n]}end;return {state='observed',callback={matches_dispatch=true,stable=true},messages=list}end}
local function p(n)return ffi.cast('uint8_t *',n)end
local game,exe,services,network,session=p(0x10000000),p(0x20000000),p(0x30000000),p(0x30001000),p(0x40000000)
local profile={globals={session=0x90},engine_functions={route_send_one={rva=0x600},route_send_many={rva=0x700}},functions={route_dispatch={rva=0x500}}}
local mem={}
local function address(x)return tonumber(ffi.cast('uintptr_t',x))end
local function pointer(at,value)local v=ffi.new('uint64_t[1]',address(value));mem[address(at)]=ffi.string(v,8)end
pointer(game+0x80,services);pointer(services+0x38,network);pointer(game+0x90,session)
pointer(network+0x38,exe+0x600);pointer(network+0x40,exe+0x700);pointer(session+0xb3f8,game+0x500)
for _,at in ipairs({exe+0x600,exe+0x700,game+0x500})do mem[address(at)]=string.rep('x',32)end
local api={module=function()return exe end,now=function()return 10 end,describe=function()return {state=4096,protection=4}end,
read=function(at,n)local b=mem[address(at)];return b and b:sub(1,n)end,
pointer=function(b)if not b or #b<8 then return nil end;local v=ffi.new('uint64_t[1]');ffi.copy(v,b,8);return p(v[0])end}
local helper=assert(loadfile('work/seat_transport_diagnostic/helper.lua'))()
local dir=assert(os.getenv('VSS_TRANSPORT_TEST_DIR'));local loader={log_directory=dir}
local events={};local writer={write=function(_,event)events[#events+1]=event end}
local original_load=ffi.load
local real=original_load('work/seat_transport_diagnostic/vss_transport.dll')
-- Factory installs cdefs; first object is never started with the real helper.
factory(api,game,profile,loader,writer,{peers={}},observer,route,messages,helper)
assert(real.VSST_version()==1 and real.VSST_record_size()==256)
assert(real.VSST_start(ffi.new('VSST_Binding[3]'),ffi.new('VSST_Guard[3]'))==-2)
local did_drain=false;local stop_count,install_code,health=0,0,0
local mock={VSST_version=function()return 1 end,VSST_record_size=function()return 256 end,VSST_frequency=function()return 1000 end,
VSST_dropped=function()return 2 end,VSST_health=function()return health end,VSST_stop=function()stop_count=stop_count+1;return 0 end,
VSST_start=function(b,g)assert(b[0].slot==ffi.cast('void **',network+0x38)and g[2].target==session);assert(ffi.string(b[1].head,32)==string.rep('x',32));return install_code end,
VSST_drain=function(b)
 if did_drain then return 0 end;did_drain=true
 for i=0,2 do b[i].kind=i;b[i].message=0xa7ece676;b[i].count=1;b[i].values[0]=123;b[i].types[0]=1;b[i].sizes[0]=4;b[i].valid=1;b[i].peer_count=1;b[i].peer_valid=1;b[i].peers[0]=555;b[i].tick=10000;b[i].sequence=i+1 end
 return 3
end}
ffi.load=function(path)if path:find('VSSTransport-',1,true)then return mock end;return original_load(path)end
local reader={peers={}}
local obj=factory(api,game,profile,loader,writer,reader,observer,route,messages,helper)
obj:start();assert(obj.active and events[1].event=='transport_ready');obj:drain()
assert(events[2].route=='send_one'and events[3].route=='send_many'and events[4].event=='native_receive_dispatch')
assert(events[4].values[1]==123 and events[4].peers[1]=='Q1'and events[5].event=='protocol_gap')
local raw=ffi.new('uint64_t[1]',555);reader.peers[ffi.string(raw,8)]='P1';obj:drain();assert(events[#events].event=='protocol_peer_alias')
-- Preserve distinct handles beyond Lua double precision and alias parameters
-- exactly like envelope peers. Nothing resembling a raw account ID is logged.
local high=ffi.new('uint64_t',0xfedcba98)*ffi.new('uint64_t',4294967296)+ffi.new('uint64_t',0x76543210)
local owner_drain=false
mock.VSST_drain=function(b)
 if owner_drain then return 0 end;owner_drain=true
 for i=0,2 do
  b[i].kind=2;b[i].message=0xe29b4d18;b[i].count=2;b[i].values[0]=101;b[i].values[1]=high+(i%2)
  b[i].types[0]=1;b[i].sizes[0]=4;b[i].types[1]=9;b[i].sizes[1]=8;b[i].valid=i==2 and 1 or 3
  b[i].peer_count=1;b[i].peer_valid=1;b[i].peers[0]=high+(i%2);b[i].tick=10000
 end
 return 3
end
local before=#events;obj:drain()
assert(events[before+1].values[2]=='Q2'and events[before+2].values[2]=='Q3')
assert(events[before+1].peers[1]=='Q2'and events[before+2].peers[1]=='Q3')
assert(events[before+3].values[2]=='unreadable_peer')
health=4;local ok,err=pcall(obj.health,obj);assert(not ok and err:find('transport_bindings_changed_4'));obj:stop('test');assert(not obj.active and stop_count==1)
install_code=102
local failed=factory(api,game,profile,loader,writer,reader,observer,route,messages,helper)
ok,err=pcall(failed.start,failed);assert(not ok and err:find('transport_install_failed_102'));failed:stop('error')
local path=dir..'/VSSTransport-'..helper.sha256..'.dll';local f=assert(io.open(path,'wb'));f:write('tampered');f:close()
local bad=factory(api,game,profile,loader,writer,reader,observer,route,messages,helper)
ok,err=pcall(bad.start,bad);assert(not ok and err:find('helper_file_mismatch'))
ffi.load=original_load
print('PASS actual DLL ABI/outside-game refusal; preflight, exact helper extraction/tamper refusal, three event routes, aliases/loss, health/failure/stop')
