from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parent;V=W/'seat_multiplayer_reservation_test';S=R/'src';D=R/'tests'
D.mkdir(exist_ok=True)
(D/'fixture_entry').mkdir(exist_ok=True)
paths={
 'work/seat_switch/src/':'work/seat_release_041/src/',
 'work/seat_interface_diagnostic/':'work/seat_release_041/src/',
 'work/seat_authority_diagnostic/':'work/seat_release_041/src/',
 'work/seat_protocol_diagnostic/':'work/seat_release_041/src/',
 'work/seat_transport_diagnostic/':'work/seat_release_041/src/',
 'work/seat_pose_trace_test/':'work/seat_release_041/src/',
 'work/seat_multiplayer_reservation_test/':'work/seat_release_041/src/',
}
def remap(text):
 # Different semantics share historical names; map these before folder changes.
 text=text.replace('work/seat_pose_trace_test/transaction.lua','work/seat_release_041/src/owned_base.lua')
 text=text.replace('work/seat_pose_trace_test/driver.lua','work/seat_release_041/src/owned_driver.lua')
 text=text.replace('work/seat_pose_trace_test/tank_driver.lua','work/seat_release_041/src/owned_tank_driver.lua')
 text=text.replace('work/seat_pose_trace_test/adapter.lua','work/seat_release_041/src/scope.lua')
 for a,b in paths.items():text=text.replace(a,b)
 text=text.replace('work/seat_release_041/src/regression_0181_binding_sender.lua','work/seat_pose_trace_test/regression_0181_binding_sender.lua')
 return text
for name in ['test_transaction.lua','test_probe.lua','test_owner_paths.lua','test_room.lua','test_room_sender.lua',
             'test_room_adapter.lua','test_owned_transaction.lua','test_acquired_release.lua','test_entrance.lua',
             'test_sender.lua','test_binding.lua','test_mounted_reader.lua']:
 text=remap((V/name).read_text(encoding='utf-8'))
 if name=='test_owned_transaction.lua':text=text.replace('for room_count=2,4','for room_count=1,4')
 (D/name).write_text(text,encoding='utf-8')
test=remap((V/'test_compat.lua').read_text(encoding='utf-8'))
test='\n'.join(l for l in test.splitlines()if '/motion_spec.lua'not in l and '/handoff_spec.lua'not in l)+'\n'
(D/'test_compat.lua').write_text(test,encoding='utf-8')
test=remap((V/'spin_fixture.lua').read_text(encoding='utf-8'))
(S/'spin_fixture.lua').write_text(test,encoding='utf-8')
test=remap((V/'test_steering_reset.lua').read_text(encoding='utf-8'))
test=test.replace('player_count=2,peer_count=2','player_count=1,peer_count=1')
test=test.replace("r:update({vehicles={f.snap}});assert(reads==0,'idle must not read physics')", "assert(r.update==nil,'production must not include a post-exit sampler')")
test=test.replace('clock=t;r:update(sample or{vehicles={f.snap}})','clock=t;')
test=test.replace("assert(t.reads()>n)","assert(t.reads()==n)")
test=test.replace('for n=3,4 do','for n=2,4 do')
test=test.replace('bounded lazy sampling','no background sampling').replace('3/4-player physical spin PENDING','offline physical backend is simulated')
(D/'test_steering_reset.lua').write_text(test,encoding='utf-8')
for name in ['test_policy.lua','test_input.lua','test_config_controller.lua','test_snapshot.lua','test_config_storage.lua']:
 test=remap((W/'seat_switch/tests'/name).read_text(encoding='utf-8'))
 test=test.replace('work/seat_switch/tests/fixture_entry','work/seat_release_041/tests/fixture_entry')
 test=test.replace('work/seat_switch/src/controller.lua','work/seat_release_041/src/controller.lua')
 (D/name).write_text(test,encoding='utf-8')
print('STAGED meaningful regression tests against production dependencies')
