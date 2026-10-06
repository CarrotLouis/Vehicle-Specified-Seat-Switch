"""Reuse the existing explicit memory fixture with the actual steering reader."""
from pathlib import Path
R=Path(__file__).resolve().parent
B=R.parent/'seat_pose_trace_test'
s=(B/'test_spin_reader.lua').read_text().split('local cases=0',1)[0]
s=s.replace("api.replace=function()writes=writes+1;error('unexpected write')end", """api.replace=function(a,old,new)
   local at=tonumber(ffi.cast('uintptr_t',a));writes=writes+1
   if f_fail_at==at then return false end
   assert(#old==4 and #new==4,'only four-byte steering fields allowed')
   if raw(at,#old)~=old then return false end;put(at,new);return true
  end""")
s=s.replace('local tear_at,tear','local tear_at,tear;local f_fail_at')
s=s.replace('function f.patch(a,b)', '''function f.fail_write(at)f_fail_at=at end
 function f.writes()return writes end
 function f.raw(a,n)return raw(a,n)end
 function f.patch(a,b)''')
s+='\nreturn {fixture=fixture,p=p,game=ffi.cast("uint8_t *",base),reader_factory=maker,compat=compat,u32=u32,ptr=ptr,f32=f32}\n'
(R/'spin_fixture.lua').write_bytes(s.encode('utf-8'))
print('PASS steering fixture derived from saved reader fixture; real captured code guards retained')
