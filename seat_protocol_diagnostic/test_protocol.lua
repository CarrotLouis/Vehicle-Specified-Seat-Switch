local ffi=require('ffi')
local factory=assert(loadfile('work/seat_protocol_diagnostic/protocol.lua'))()
local helper=assert(loadfile('work/seat_protocol_diagnostic/helper.lua'))()
local points=assert(loadfile('work/seat_protocol_diagnostic/trace_points.lua'))()
local messages=assert(loadfile('work/seat_protocol_diagnostic/messages.lua'))()
local dir=assert(os.getenv('VSS_PROTOCOL_TEST_DIR'))
local p={functions={}};for _,v in ipairs(points)do p.functions['trace_'..v.name]={rva=v.rva,bytes=v.hex:gsub('..',function(h)return string.char(tonumber(h,16))end)}end
local api={now=function()return 50 end,read=function(address)for _,d in pairs(p.functions)do if address==ffi.cast('uint8_t *',0x10000000)+d.rva then return d.bytes end end end}
local writer={events={},write=function(self,e)self.events[#self.events+1]=e;return true end}
local bytes=ffi.new('uint64_t[1]',0x123456)
local reader={peers={[ffi.string(bytes,8)]='P1'}}
local trace=factory(api,ffi.cast('uint8_t *',0x10000000),p,{log_directory=dir},writer,reader,points,messages,helper)
-- Validate the actual DLL's exported ABI in this separate offline process.
local real_load=ffi.load
local real=real_load('work/seat_protocol_diagnostic/vss_protocol.dll')
assert(real.VSSP_version()==2 and real.VSSP_record_size()==192 and real.VSSP_frequency()>0)
assert(real.VSSP_start(ffi.new('void *[8]'),ffi.new('uint8_t[256]'),8)==-2,'must refuse outside game')
local drains,stops=0,0
local fake={VSSP_version=function()return 2 end,VSSP_record_size=function()return 192 end,VSSP_frequency=function()return 10000000 end,
 VSSP_start=function(targets,expected,n)assert(n==8 and targets[0]~=nil and ffi.string(expected,32)==p.functions.trace_send.bytes);return 0 end,
 VSSP_dropped=function()return 2 end,VSSP_stop=function()stops=stops+1;return 0 end}
function fake.VSSP_drain(out,n)
 drains=drains+1;if drains>1 then return 0 end
 for i=0,1 do out[i].sequence=i+1;out[i].tick=49900+i;out[i].qpc=4990000+i;out[i].peer=0x123456;out[i].count=4;out[i].valid=15 end
 out[0].kind=0;out[0].message=0xa7ece676;out[0].values[0]=11
 out[1].kind=4;out[1].values[3]=0xaabbcc01
 return 2
end
ffi.load=function(path)assert(path:find(helper.sha256,1,true));return fake end
trace:start();trace:drain();trace:stop('test')
assert(stops==1 and trace.seen==2)
assert(writer.events[1].event=='protocol_ready')
assert(writer.events[2].event=='native_send' and writer.events[2].message=='switch_request' and writer.events[2].peer=='P1')
assert(writer.events[3].name=='restore' and writer.events[3].values[4]==1)
assert(writer.events[4].event=='protocol_gap' and writer.events[4].dropped_total==2)
assert(writer.events[5].event=='protocol_stopped')
fake.VSSP_start=function()return 310 end
fake.VSSP_failure=function(out)
 out[0].stage=1;out[0].win32_error=5;out[0].hook_index=0;out[0].enabling=1
 out[0].patch_address=0x10001000;out[0].region_base=0x10000000;out[0].region_size=4096;out[0].protection=32
 return 1
end
local failed=factory(api,ffi.cast('uint8_t *',0x10000000),p,{log_directory=dir},writer,reader,points,messages,helper)
local ok,why=pcall(failed.start,failed)
assert(not ok and tostring(why):find('protocol_install_failed_310_win32_5_hook_send'))
assert(writer.events[6].event=='protocol_install_failure' and writer.events[6].patch_rva==4096 and writer.events[6].win32_error==5)
failed:stop('error')
local path=dir..'/VSSProtocol-'..helper.sha256..'.dll'
local f=assert(io.open(path,'wb'));f:write('tampered');f:close()
local other=factory(api,ffi.cast('uint8_t *',0x10000000),p,{log_directory=dir},writer,reader,points,messages,helper)
ok,why=pcall(other.start,other);assert(not ok and tostring(why):find('helper_file_mismatch'))
ffi.load=real_load
print('PASS protocol adapter: actual DLL ABI/outside-game refusal, verified extraction, event decoding, aliases, bool masking, gaps, stop, cached-DLL tamper refusal')
