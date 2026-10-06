"""Run unchanged local identity tests plus the new explicitly remote read entry."""
from pathlib import Path
R=Path(__file__).resolve().parent;B=R.parent/'seat_pose_trace_test'
s=(B/'test_binding_inspect.lua').read_text().replace('work/seat_pose_trace_test/binding_inspect.lua','work/seat_multiplayer_reservation_test/binding_inspect.lua')
s=s.replace("local function rel(rva,op,target)","p.binding_counts={total=0x18,enabled=0x1c,prefix=0x20,reference_offset=0x14};p.functions.binding_manager_add_total={rva=0x600}\nlocal function rel(rva,op,target)")
s=s.replace("rel(0x510,'\\76\\139\\21',0x11010)","rel(0x510,'\\76\\139\\21',0x11010)\nrel(0x614,'\\72\\139\\61',0x11000)")
s=s.replace('u(0x20020,1);q','u(0x20018,1);u(0x2001c,1);u(0x20020,1);q',1)
s+='''
u(0x30000+0xf1aeb8,2);u(0x40008,7);u(0x4000c,0)
u(0x30000+0xf32f20,7);u(0x30000+0xf32f24,9);u(0x30000+0xf32f28,11)
api.replace=function()error('readonly observer wrote')end
api.call=function()error('readonly observer called a game setter')end
a.is_local=false;assert(not pcall(inspector.capture,inspector,a),'sender capture must remain local-only')
out=inspector:observe_remote(a);assert(out.stable and out.rotation_flag==1 and #out.slots==5 and out.reads<100)
-- The real missed case: a remote component lies outside the local processed
-- prefix but within the total array. Its pointer/slots are identity guarded.
u(0x2200c,1);u(0x20018,2);u(0x2001c,1);q(0x23008,0x24000)
for i=0,4 do u(0x251d0+i*0x50,100+i);u(0x251d4+i*0x50,0xffffffff)end
out=inspector:observe_remote(a);assert(out.weapon_index==1 and out.weapon_total==2 and out.weapon_prefix==1)
a.is_local=true;assert(not pcall(inspector.capture,inspector,a));a.is_local=false
u(0x20018,1);assert(not pcall(inspector.observe_remote,inspector,a));u(0x20018,2)
u(0x2001c,3);assert(not pcall(inspector.observe_remote,inspector,a));u(0x2001c,1)
u(0x20020,2);assert(not pcall(inspector.observe_remote,inspector,a));u(0x20020,1)
u(0x2200c,0);u(0x20018,1)
u(0x30000+0xf32f24,10);assert(not pcall(inspector.observe_remote,inspector,a));u(0x30000+0xf32f24,9)
u(0x24010,12);assert(not pcall(inspector.observe_remote,inspector,a));u(0x24010,11)
w(0x26071,'\\2');assert(not pcall(inspector.observe_remote,inspector,a));w(0x26071,'\\1')
a.is_local=true;assert(not pcall(inspector.observe_remote,inspector,a));assert(inspector:capture(a).stable)
print('PASS real remote binding observer: canonical avatar/unit/network identity, rotation flag bounds, local-only sender preflight retained, no writes/calls/sends')
'''
(R/'test_remote_binding.lua').write_bytes(s.encode())
