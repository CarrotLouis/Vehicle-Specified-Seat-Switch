from pathlib import Path
import hashlib, json, zipfile

W=Path(__file__).resolve().parent;P=W.parent
R=W/'seat_multi_vehicle_fix';old=W/'seat_multi_vehicle_test'
def digest(data):return hashlib.sha256(data).hexdigest()
unchanged=['adapter.lua','transaction.lua','sender.lua','driver.lua','binding_sender.lua','animation_sender.lua',
 'dispatcher.lua','input_gate.lua','probe.lua','personal.lua','platform.lua','transport.lua','inspect.lua',
 'binding_inspect.lua','animation_watch.lua','entry.lua','sync_spec.lua','animation_spec.lua','binding_spec.lua','input_helper.lua']
def normalized(name):return (old/name).read_text(encoding='utf-8').replace('seat_multi_vehicle_test','seat_multi_vehicle_fix').replace('0.18.0','0.18.1')
for name in unchanged:assert (R/name).read_text(encoding='utf-8')==normalized(name),name
expected=normalized('observe.lua').replace('local M={}\n',
 '--TEMP--',1)
expected=expected.replace('--TEMP--',"local M={}\n-- Initial observation has no tracked ticket yet. It must recognize the same\n-- five vehicles as the validated cross-seat adapter, before input can be armed.\nlocal cross_vehicles={m102=true,m103=true,m104=true,bastion=true,maelstrom=true}\n",1)
expected=expected.replace("v.id==a.seat.collection and v.name=='m102'",'v.id==a.seat.collection and cross_vehicles[v.name]',1)
assert (R/'observe.lua').read_text(encoding='utf-8')==expected,'No additional runtime changes permitted'
assert (R/'regression_0180_observe.lua').read_bytes()==(old/'observe.lua').read_bytes()
for name in ['input_native.c','vss_input_priority.dll']:assert (R/name).read_bytes()==(old/name).read_bytes(),name

frozen=R/'capture-20261002-0180'
analysis=json.loads((frozen/'analysis.json').read_text(encoding='utf-8'))
for record in analysis['files']:
 data=(frozen/record['name']).read_bytes();assert len(data)==record['bytes']and digest(data)==record['sha256']
assert analysis['native_completions']==7 and analysis['cross_operation_completions']==0 and analysis['shutdown_clean']
assert analysis['vehicle_samples']==dict(m103=52,m104=51,bastion=94,maelstrom=59)

log=(R/'build-verified.log').read_text(encoding='utf-8')
for marker in ['PASS 512 untracked observer live-state replays','PASS 140 real untracked observer-adapter-probe-keygate-dispatcher-FFI request cases',
 'PASS 6 untracked selection scope refusals','PASS 132 real ownership observer batched-vehicle cases']:
 assert log.count(marker)==4,marker
for marker in ['PASS 359 batched vehicle cases','PASS 372 real batched transaction cases',
 'PASS 20 real batched sender FFI cases','PASS 8 batched binding FFI cases',
 'PASS 140 outside-original-owner cases','PASS 136 seated-original-owner cases',
 'PASS 48 vacant-driver acquisition cases','PASS 50 remote-gunner context cases',
 'PASS 56 input-race cases','PASS integrated bundle syntax']:
 assert log.count(marker)==1,marker
assert log.count('checked=85')==2 and 'Traceback'not in log and 'RuntimeError'not in log

report=json.loads((R/'package.json').read_text());path=Path(report['file'])
assert digest(path.read_bytes())==report['sha256']and path.stat().st_size==report['bytes']
with zipfile.ZipFile(path)as z:
 assert z.testzip()is None
 manifest=json.loads(z.read('manifest.json'))
 assert manifest['Guid']=='649bec74-f2d5-490d-a6ed-3f3caef67b0b'and len(manifest['Options'])==1
 assert '0.18.1'in manifest['Name']and manifest['Options'][0]['Include']==['Diagnostic']
 assert '暂停0.2.4'in manifest['Description']and 'Disable0.2.4'in manifest['Description']
 assert z.read('Source/network_diagnostic.lua').decode('utf-8')==(R/'bundled.lua').read_text(encoding='utf-8')
 assert z.read('Source/input/vss_input_priority.dll')==(old/'vss_input_priority.dll').read_bytes()
 for name in ['observe.lua','regression_0180_observe.lua','test_vehicle_selection.lua','selection_cases.lua','selection_replay.lua','prepare_selection_tests.py',
  'test_multi_vehicle.lua','test_batch_transaction.lua','test_observe.lua','prepare_tests.py','docs_batch.py','test_vehicle_actions.py','generate_spec.py']:
  assert z.read('Source/experiment/'+name)==(R/name).read_bytes(),name
 for name in ['README_中文.txt','README_English.txt']:assert z.read(name)==(R/name).read_bytes()
 assert (P/'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.1-说明.txt').read_bytes()==z.read('README_中文.txt')

for name,expected in {
 'Vehicle-Specified-Seat-Switch-0.2.4.zip':'0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.17.0.zip':'5fc5025dc77dc0149181cc67b6cb5cc92f1ae31d1ff7dd8202b45e3b35fd3876',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.0.zip':'40059a2fed9477f6b1c8b83e7a695f17b7cb232fc4c2a890f85adbcb0fc1e3c9',
}.items():assert digest((P/'outputs'/name).read_bytes())==expected,name
fixture=W/'packaging_research/manager-fixture-fb227265-83f9-4b4e-bd8e-1af9ce60d607/result.json'
manager=json.loads(fixture.read_text())
assert manager['sha256']==report['sha256']and manager['files']==3 and manager['bilingual']and manager['payload_hashes_preserved']and manager['purge_empty']
assert not manager['live_profile_changed']and not manager['game_launched']
report.update(runtime_fix='Only initial untracked observation recognizes all five explicitly supported models; unchanged transactional guards/protocol/input.',
 unchanged_dependencies=unchanged,input_C_and_binary_unchanged=True,production_024_and_0170_0180_unchanged=True,
 failed_0180_frozen=str(frozen/'analysis.json'),recorded_vehicle_samples=256,old_failure_reproduced=True,
 untracked_state_replays=512,real_untracked_key_to_FFI_requests=140,selection_scope_refusals=6,fixture_combinations=4,
 batched_context_cases=359,transaction_cases=372,interface_witnesses=85,arsenal_fixture=str(fixture),
 live_0181_validation='pending; request batched four-model two-host-role test; no repeat of accepted M102')
(R/'artifact-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
