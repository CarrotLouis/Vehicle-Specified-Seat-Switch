"""Run unchanged local identity tests plus the new explicitly remote read entry."""
from pathlib import Path
R=Path(__file__).resolve().parent;B=R.parent/'seat_pose_trace_test'
s=(B/'test_binding_inspect.lua').read_text().replace('work/seat_pose_trace_test/binding_inspect.lua','work/seat_tank_exit_refinement_test/binding_inspect.lua')
s+='''
u(0x30000+0xf1aeb8,2);u(0x40008,7);u(0x4000c,0)
u(0x30000+0xf32f20,7);u(0x30000+0xf32f24,9);u(0x30000+0xf32f28,11)
api.replace=function()error('readonly observer wrote')end
api.call=function()error('readonly observer called a game setter')end
a.is_local=false;assert(not pcall(inspector.capture,inspector,a),'sender capture must remain local-only')
out=inspector:observe_remote(a);assert(out.stable and out.rotation_flag==1 and #out.slots==5 and out.reads<100)
u(0x30000+0xf32f24,10);assert(not pcall(inspector.observe_remote,inspector,a));u(0x30000+0xf32f24,9)
u(0x24010,12);assert(not pcall(inspector.observe_remote,inspector,a));u(0x24010,11)
w(0x26071,'\\2');assert(not pcall(inspector.observe_remote,inspector,a));w(0x26071,'\\1')
a.is_local=true;assert(not pcall(inspector.observe_remote,inspector,a));assert(inspector:capture(a).stable)
print('PASS real remote binding observer: canonical avatar/unit/network identity, rotation flag bounds, local-only sender preflight retained, no writes/calls/sends')
'''
(R/'test_remote_binding.lua').write_bytes(s.encode())
