local r=assert(loadfile('work/seat_network_diagnostic/recorder.lua'))()
local lines,closed,flushed={},0,0
local f={write=function(self,line)lines[#lines+1]=line;return self end,flush=function()flushed=flushed+1;return true end,close=function()closed=closed+1;return true end}
local w=r.new(f,10,2000)
assert(r.encode({a='a"\n\\',b={},c=true})=='{"a":"a\\"\\u000a\\\\","b":[],"c":true}')
w:sample({a=1},10,1);w:sample({a=1},10.2,2);assert(#lines==1)
w:sample({a=1},12.1,3);assert(#lines==2 and flushed==1)
w:sample({a=2},12.2,4);assert(#lines==3)
w:close(13,'shutdown');assert(closed==1);w:close(14,'again');assert(closed==1)
local limited=r.new(f,0,20);limited:write({event='too_large'},0);assert(limited.closed and lines[#lines]:find('size_limit'))
local bad=r.new({write=function()return nil end},0);assert(not pcall(bad.write,bad,{a=1},0))
print('PASS recorder: valid escaping/arrays, changed states, heartbeat, flush, size limit, shutdown and disk-write failure')
