"""Reuse immutable baseline tests with explicit new factory/ABI substitutions."""
from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parent;B=W/'seat_pose_trace_test';T=W/'seat_transport_diagnostic'
s=(B/'test_compat.lua').read_text()
s=s.replace("local ffi=require('ffi')", "profile,spec=assert(loadfile('work/seat_reservation_fleet_test/reservation_spec.lua'))()(profile,spec)\nlocal ffi=require('ffi')",1)
s+="\nfor _,name in ipairs({'reservation_entry_send','reservation_release_send','reservation_entrance_node','reservation_accepted_adapter','reservation_interaction_resource','reservation_interaction_update','reservation_mounted_joint_tags','reservation_related_weapon_lookup','reservation_related_weapon_resource'})do assert(p.functions[name]and spec.records[name])end\nprint('PASS nine new reservation witnesses resolved with all existing relationships')\n"
(R/'test_compat.lua').write_text(s)
s=(B/'test_sender.lua').read_text().replace('work/seat_pose_trace_test/sender.lua','work/seat_reservation_fleet_test/sender.lua')
s=s.replace('{prepare=function()return {check=', '{preflight=function()return true end,prepare=function()return {check=')
insert="""
-- New nonowned sender must be justified by the real grant check, never a flag.
s.vehicle='m102';s.transition=26;s.profile=profiles.m102;s.owned=false;s.node=1
o.owner=destination;expected_target=2;calls={}
assert(not pcall(send.prepare,send,o,destination,s,2)and #calls==0)
local valid=true;local checks=0
local grant={source=1,target=2,check=function()checks=checks+1;return valid end}
assert(send:preflight(o,destination,s,2)and #calls==0)
local reserved=send:prepare(o,destination,s,2,grant);valid=false
assert(not pcall(reserved,function()end)and #calls==0);valid=true
send:prepare(o,destination,s,2,grant)(function()end)
assert(table.concat(calls,',')=='snapshot,transition,weapon_pair,animation'and checks>=4)
grant.source=2;local previous=#calls;assert(not pcall(send.prepare,send,o,destination,s,2,grant)and #calls==previous)
print('PASS authentic reservation required before nonowner send, checked again at invocation, exact ordered sync ABI')

-- A real empty-driver grant may legitimately transfer the whole car to the
-- installer. Sending still goes to the exact OTHER peer, with target zero.
s.owned=true;o.owner=selfpeer;grant.source=s.node;grant.target=0;expected_target=0;calls={}
batch:prepare(o,destination,s,0,grant)(function()end)
assert(table.concat(calls,',')=='snapshot,transition,weapon_pair,animation')
valid=false;local before=#calls;assert(not pcall(batch.prepare,batch,o,destination,s,0,grant)and #calls==before);valid=true
s.owned=false;assert(not pcall(batch.prepare,batch,o,destination,s,0,grant)and #calls==before)
print('PASS acquired-driver sync ABI requires actual new owner + valid grant; only own avatar to other peer')
"""
s=s.replace('callbacks.snap:free();callbacks.transition:free()',insert+'\ncallbacks.snap:free();callbacks.transition:free()')
s=s.replace('assert(send:preflight(o,destination,s,2)', 'assert(batch:preflight(o,destination,s,2)')
s=s.replace('send:prepare(o,destination,s,2,grant)', 'batch:prepare(o,destination,s,2,grant)')
(R/'test_sender.lua').write_text(s)
s=(T/'test_transport.lua').read_text().replace('work/seat_transport_diagnostic/transport.lua','work/seat_reservation_fleet_test/transport.lua').replace('work/seat_transport_diagnostic/helper.lua','work/seat_reservation_fleet_test/helper.lua').replace('work/seat_transport_diagnostic/vss_transport.dll','work/seat_reservation_fleet_test/vss_transport.dll').replace('VSST_version()==1','VSST_version()==4').replace('VSST_version=function()return 1 end','VSST_version=function()return 4 end')
insert="""
assert(ffi.sizeof('VSSR_GateRecord')==56 and ffi.sizeof('VSSR_GateConfig')==32)
local gate_,gate_closed=nil,0
mock.VSST_gate_arm=function(config)
 assert(not gate_ and config.source==1 and config.target==2)
 gate_=ffi.new('VSSR_GateRecord');gate_.cookie=config.cookie;gate_.peer=config.peer
 gate_.car=config.car;gate_.avatar=config.avatar;gate_.source=config.source;gate_.target=config.target;gate_.status=1
 return 0
end
mock.VSST_gate_peek=function(out)if not gate_ then return 0 end;ffi.copy(out,gate_,56);return 1 end
mock.VSST_gate_finish=function(cookie)assert(gate_ and gate_.cookie==cookie and gate_.status==2);gate_=nil;return 0 end
mock.VSST_gate_shutdown=function()gate_=nil;gate_closed=gate_closed+1 end
local rawpeer=ffi.new('uint64_t[1]',high);local key=ffi.string(rawpeer,8)
local cookie=obj:gate_arm(key,4123,4107,1,2);local reply=obj:gate_peek(cookie)
assert(reply.peer_key==key and reply.cookie==cookie and reply.source==1 and reply.target==2 and reply.status==1)
gate_.status=2;gate_.chosen=2;gate_.repeats=3;reply=obj:gate_peek(cookie)
assert(reply.chosen==2 and reply.repeats==3 and reply.peer_key==key)
obj:gate_finish(cookie);assert(gate_==nil)
cookie=obj:gate_arm(key,4123,4107,1,2);obj:stop('error');assert(gate_~=nil and gate_closed==0)
obj:stop('shutdown');assert(gate_==nil and gate_closed==1);obj.active=true;stop_count=0
print('PASS real Lua gate adapter layout and uint64 peer preservation; error stop retains gate, actual shutdown clears')
"""
s=s.replace('health=4;local ok,err=',insert+'\nhealth=4;local ok,err=')
(R/'test_transport.lua').write_text(s)
# Life-cycle test runs the exact assembled prefix as well as the raw entry.
# Native engine factories are clearly substituted; the real platform export,
# recorder and new probe constructor remain in use (no live engine/game).
s=(B/'test_entry.lua').read_text().split("-- A failed optional constructor",1)[0]
s=s.replace('work/seat_pose_trace_test/entry.lua','work/seat_reservation_fleet_test/entry.lua')
s=s.replace("io.open('work/seat_reservation_fleet_test/entry.lua')","io.open('work/seat_reservation_fleet_test/entry.lua','rb')")
s=s.replace("local now,started", "local ffi=require('ffi')\nlocal real_platform=assert(loadfile('work/seat_pose_trace_test/platform.lua'))()\nlocal real_probe=assert(loadfile('work/seat_reservation_fleet_test/probe.lua'))()\nlocal now,started")
s=s.replace("local real_probe=assert(loadfile('work/seat_reservation_fleet_test/probe.lua'))()", "local scope=assert(loadfile('work/seat_reservation_fleet_test/scope.lua'))()\nlocal real_probe=assert(loadfile('work/seat_reservation_fleet_test/probe.lua'))()(scope)")
s=s.replace("platform=function()return {now=function()return now end,pid=function()return 1 end,module=function()return 1 end,hash_module=function()return 'unknown'end,input_allowed=function()return false end}end,",
 "platform=function()local a=real_platform(function()return 'unknown'end);assert(a.ffi==ffi and type(a.read)=='function'and type(a.replace)=='function');a.now=function()return now end;a.pid=function()return 1 end;a.module=function()return 1 end;a.input_allowed=function()return false end;return a end,")
s=s.replace("sync_adapter={new=function()return {}end}","sync_adapter={new=function()return {capture=function()return nil,'not_in_mission'end}end}")
s=s.replace("local previous_update=env.update", """env.reservation_tools={probe=real_probe,scope=scope,mounted_reader=function(a)assert(a.ffi==ffi);return {}end,entrance=function(a)assert(a.ffi==ffi);return {}end,motion_watch=function()return {update=function()end}end}
local previous_update=env.update
local previous_shutdown=env.shutdown
""")
s=s.replace('VehicleSeatNetworkDiagnostic=nil;env.update=previous_update','VehicleSeatNetworkDiagnostic=nil;env.update=previous_update;env.shutdown=previous_shutdown')
s+="""
-- Run the EXACT shipped module prefix, then substitute only external backends
-- at the entry boundary. This exercises actual grouping/local names/wiring.
enhanced=true
local f=assert(io.open('work/seat_reservation_fleet_test/bundled.lua','rb'));local bundle=f:read('*a');f:close()
assert(bundle:sub(-#source)==source,'entry must be exact bundle suffix')
local substitutions={'snapshot','bind_native','seat_dispatcher','platform','compat','config','input','authority_observe','transaction','sender','sync_adapter','sampler','pages','routing','transport','input_gate','animation_watch','animation_inspect','animation_sender','binding_inspect','binding_sender','motion_tools','reservation_tools'}
local bridge='\\n'
for _,name in ipairs(substitutions)do bridge=bridge..name..'=__fixture.'..name..'\\n'end
env.__fixture=env
source=bundle:sub(1,#bundle-#source)..bridge..source
restart();tick(601);assert(VehicleSeatNetworkDiagnostic.transport_ready and VehicleSeatNetworkDiagnostic.version=='0.28.0')
assert(env.shutdown()=='shutdown_forwarded')
print('PASS exact shipped bundle prefix/new factory grouping, real platform.ffi and real probe constructor; ship lifecycle and original returns')
"""
s=s.replace('motion_watch=function()return {update=function()end}end}', '''motion_watch=function()return {update=function()end}end,
 owned_transaction=function(a)assert(a.ffi==ffi);return {}end,release_acquired=function(a)assert(a.ffi==ffi);return {}end,
 steering_reset=assert(loadfile('work/seat_reservation_fleet_test/steering_reset.lua'))(),spin_reader=function()error('must not poll idle')end}''')
(R/'test_entry.lua').write_text(s)
print('PASS prepared new compatibility/sender/transport/entry tests with declared engine fixture boundaries')
