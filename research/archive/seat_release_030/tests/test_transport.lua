local ffi=require('ffi')
local factory=assert(loadfile('work/seat_release_030/src/transport.lua'))()
local helper=assert(loadfile('work/seat_release_030/helper.lua'))()
local messages=assert(loadfile('work/seat_release_030/src/messages.lua'))()
local function ptr(v)return ffi.cast('uint8_t *',v)end
local function address(v)return tonumber(ffi.cast('uintptr_t',v))end
local game,exe,services,network,session=ptr(0x10000000),ptr(0x20000000),ptr(0x30000000),ptr(0x30001000),ptr(0x40000000)
local p={globals={session=0x90},engine_functions={route_send_one={rva=0x600},route_send_many={rva=0x700}},functions={route_dispatch={rva=0x500}}}
local memory={}
local function pointer(a,v)local x=ffi.new('uint64_t[1]',address(v));memory[address(a)]=ffi.string(x,8)end
pointer(game+0x80,services);pointer(services+0x38,network);pointer(game+0x90,session)
pointer(network+0x38,exe+0x600);pointer(network+0x40,exe+0x700);pointer(session+0xb3f8,game+0x500)
for _,a in ipairs({exe+0x600,exe+0x700,game+0x500})do memory[address(a)]=string.rep('x',32)end
local api={module=function()return exe end,now=function()return 10 end,describe=function()return {state=4096,protection=4}end,
 read=function(a,n)local b=memory[address(a)];return b and b:sub(1,n)end,
 pointer=function(b)local x=ffi.new('uint64_t[1]');ffi.copy(x,b,8);return ptr(x[0])end}
local counts={switch_request=4,accepted=3,snapshot=4,transition=5,switch_denied=2,entry_request=3,exit_request=4,entry_denied=2,entering=3,release_request=2,release_retry=2,exit_accepted=4,exit_denied=2,authority_request=2,authority_owned=2}
local route={capture=function()local list={};for hash,name in pairs(messages)do list[#list+1]={found=true,hash=hash,name=name,parameter_count=counts[name]}end;return {state='observed',callback={matches_dispatch=true,stable=true},messages=list}end}
local observer={locate=function()return 0x80 end}
local dir=assert(os.getenv('VSS_TRANSPORT_TEST_DIR'))
local loader={log_directory=dir}
local events={};local writer={closed=false,write=function(_,e)events[#events+1]=e end}
factory(api,game,p,loader,writer,{},observer,route,messages,helper)
local original=ffi.load;local real=original('work/seat_release_030/vss_transport.dll')
assert(real.VSST_version()==4 and real.VSST_record_size()==256)
assert(real.VSST_start(ffi.new('VSST_Binding[3]'),ffi.new('VSST_Guard[3]'))==-2)
local gate,shutdown_count=nil,0
local mock={VSST_version=function()return 4 end,VSST_record_size=function()return 256 end,VSST_frequency=function()return 1000 end,
 VSST_health=function()return 0 end,VSST_dropped=function()return 0 end,
 VSST_start=function(b,g)assert(b[2].slot==ffi.cast('void **',session+0xb3f8)and g[2].target==session);return 0 end,
 VSST_stop=function()return gate and 16 or 0 end,
 VSST_gate_arm=function(c)assert(not gate);gate=ffi.new('VSSR_GateRecord');gate.cookie=c.cookie;gate.peer=c.peer;gate.car=c.car;gate.avatar=c.avatar;gate.source=c.source;gate.target=c.target;gate.status=1;return 0 end,
 VSST_gate_peek=function(out)if not gate then return 0 end;ffi.copy(out,gate,56);return 1 end,
 VSST_gate_finish=function(cookie)assert(gate and gate.cookie==cookie);gate=nil;return 0 end,
 VSST_gate_shutdown=function()shutdown_count=shutdown_count+1;gate=nil end}
ffi.load=function(path)if path:find('VSSTransport-',1,true)then return mock end;return original(path)end
local t=factory(api,game,p,loader,writer,{},observer,route,messages,helper)
t:start();assert(t.active and t.drain==nil,'production must not record/drain protocol events')
local high=ffi.new('uint64_t',0xfedcba98)*ffi.new('uint64_t',4294967296)+ffi.new('uint64_t',0x76543210)
local bytes=ffi.new('uint64_t[1]',high);local key=ffi.string(bytes,8)
local cookie=t:gate_arm(key,4123,4107,1,2);local r=t:gate_peek(cookie)
assert(r.peer_key==key and r.source==1 and r.target==2 and r.status==1)
gate.status=2;gate.chosen=2;r=t:gate_peek(cookie);assert(r.chosen==2);t:gate_finish(cookie)
t:gate_arm(key,4123,4107,1,2);t:stop('error');assert(gate and shutdown_count==0)
t:stop('shutdown');assert(not gate and shutdown_count==1)
local path=dir..'/VSSTransport-'..helper.sha256..'.dll';local f=assert(io.open(path,'wb'));f:write('tampered');f:close()
local bad=factory(api,game,p,loader,writer,{},observer,route,messages,helper)
local ok,err=pcall(bad.start,bad);assert(not ok and err:find('helper_file_mismatch'))
ffi.load=original
print('PASS actual production DLL ABI/outside-game refusal, helper extraction/tamper check, uint64 ACK tuple, pending error-stop retention and shutdown; packet recorder absent')
