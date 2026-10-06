from pathlib import Path
import hashlib,json,zipfile

W=Path(__file__).resolve().parent;P=W.parent;R=W/'seat_tank_binding_fix';old=W/'seat_multi_vehicle_fix'
def sha(data):return hashlib.sha256(data).hexdigest()
unchanged=['observe.lua','transaction.lua','sender.lua','driver.lua','animation_sender.lua','dispatcher.lua','input_gate.lua','personal.lua',
 'platform.lua','transport.lua','inspect.lua','binding_inspect.lua','animation_watch.lua','sync_spec.lua','animation_spec.lua','binding_spec.lua','input_helper.lua','entry.lua']
for name in unchanged:
 expected=(old/name).read_text(encoding='utf-8').replace('seat_multi_vehicle_fix','seat_tank_binding_fix').replace('0.18.1','0.18.2')
 assert (R/name).read_text(encoding='utf-8')==expected,name
for name in ['input_native.c','vss_input_priority.dll']:assert (R/name).read_bytes()==(old/name).read_bytes(),name
for name in ['probe.lua','adapter.lua','binding_sender.lua']:assert (R/('regression_0181_'+name)).read_bytes()==(old/name).read_bytes(),name

frozen=R/'capture-20261002-0181';analysis=json.loads((frozen/'analysis.json').read_text(encoding='utf-8'))
for record in analysis['files']:
 data=(frozen/record['name']).read_bytes();assert len(data)==record['bytes']and sha(data)==record['sha256']
boot,host,guest=analysis['runs']
assert boot['host_role']=='excluded_startup_no_operations'and boot['completed']==0
assert host['host_role']=='installer_host'and host['completed']==29 and guest['host_role']=='friend_host'and guest['completed']==39
for run in [host,guest]:
 assert run['clean_shutdown']and run['errors_or_gaps']==0 and run['drops']==0
 assert sum(run['by_model']['m103'].values())==10
 assert sum(run['by_model']['m104'].values())in [10,11]
 assert len(run['bastion_driver_passenger_no_weapon_sync'])==3 and all(not op['weapon_sync']for op in run['bastion_driver_passenger_no_weapon_sync'])
assert host['abort'][-1]['event']=='integrated_aborted_and_returned'and host['abort'][-1]['mutation_started']is False
assert not guest['abort']and guest['native_completed']['tanker']==2 and sum(guest['by_model']['maelstrom'].values())==9

log=(R/'build-verified.log').read_text(encoding='utf-8')
for marker in ['PASS 2 frozen0.18.1 Maelstrom','PASS 312 real control-abort recovery cases',
 'PASS 2 frozen0.18.1 Bastion','PASS 24 tank-driver personal binding FFI cases',
 'PASS 359 batched vehicle cases','PASS 372 real batched transaction cases','PASS 20 real batched sender FFI cases','PASS 8 batched binding FFI cases',
 'PASS 140 outside-original-owner cases','PASS 136 seated-original-owner cases','PASS 48 vacant-driver acquisition cases',
 'PASS 50 remote-gunner context cases','PASS 56 input-race cases','PASS integrated bundle syntax']:
 assert log.count(marker)==1,marker
for marker in ['PASS 512 untracked observer live-state replays','PASS 140 real untracked observer-adapter-probe-keygate-dispatcher-FFI request cases',
 'PASS 6 untracked selection scope refusals','PASS 132 real ownership observer batched-vehicle cases']:assert log.count(marker)==4,marker
assert log.count('checked=85')==2 and 'Traceback'not in log and 'RuntimeError'not in log

report=json.loads((R/'package.json').read_text());path=Path(report['file'])
assert sha(path.read_bytes())==report['sha256']and path.stat().st_size==report['bytes']
with zipfile.ZipFile(path)as z:
 assert z.testzip()is None
 manifest=json.loads(z.read('manifest.json'))
 assert manifest['Guid']=='649bec74-f2d5-490d-a6ed-3f3caef67b0b'and len(manifest['Options'])==1
 assert '0.18.2'in manifest['Name']and manifest['Options'][0]['Include']==['Diagnostic']
 assert '暂停0.2.4'in manifest['Description']and 'Disable0.2.4'in manifest['Description']
 assert z.read('Source/network_diagnostic.lua').decode('utf-8')==(R/'bundled.lua').read_text(encoding='utf-8')
 assert z.read('Source/input/vss_input_priority.dll')==(old/'vss_input_priority.dll').read_bytes()
 for name in ['adapter.lua','probe.lua','binding_sender.lua','regression_0181_adapter.lua','regression_0181_probe.lua','regression_0181_binding_sender.lua',
  'test_binding_sender.lua','test_control_abort.lua','input_race_fixture.lua','test_vehicle_selection.lua','docs_batch.py']:
  assert z.read('Source/experiment/'+name)==(R/name).read_bytes(),name
 for name in ['README_中文.txt','README_English.txt']:assert z.read(name)==(R/name).read_bytes()
 assert (P/'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.2-说明.txt').read_bytes()==z.read('README_中文.txt')
for name,expected in {
 'Vehicle-Specified-Seat-Switch-0.2.4.zip':'0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.17.0.zip':'5fc5025dc77dc0149181cc67b6cb5cc92f1ae31d1ff7dd8202b45e3b35fd3876',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.0.zip':'40059a2fed9477f6b1c8b83e7a695f17b7cb232fc4c2a890f85adbcb0fc1e3c9',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.1.zip':'9a17d5abb741c6847a092b1d279b90f485061da0f044906edcb61f1ddec12685',
}.items():assert sha((P/'outputs'/name).read_bytes())==expected,name
fixture=W/'packaging_research/manager-fixture-f5564ebb-0002-4975-8b0c-facc4d1aeb45/result.json'
manager=json.loads(fixture.read_text())
assert manager['sha256']==report['sha256']and manager['files']==3 and manager['bilingual']and manager['payload_hashes_preserved']and manager['purge_empty']
assert not manager['live_profile_changed']and not manager['game_launched']
report.update(runtime_changes=['adapter control-abort classification/fresh resumability check','probe limited dynamic recovery/new physical press required','tank driver-to-personal weapon replication'],
 unchanged_dependencies=unchanged,input_C_and_binary_unchanged=True,production_024_and_0170_0180_0181_unchanged=True,
 live_0181_evidence=str(frozen/'analysis.json'),live_host_completed=29,live_guest_completed=39,
 control_abort_recovery_cases=312,tank_driver_binding_FFI_cases=24,old_failures_reproduced=True,
 interface_witnesses=85,arsenal_fixture=str(fixture),live_0182_validation='pending; combine Bastion/Maelstrom and optional tanker for both hosts; no full M102/M103/M104 repeat')
(R/'artifact-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
