from pathlib import Path
import hashlib,json,zipfile
W=Path(__file__).resolve().parent;P=W.parent;R=W/'seat_multi_vehicle_test';old=W/'seat_outside_owner_test'
unchanged=['probe.lua','personal.lua','platform.lua','transport.lua','animation_watch.lua','inspect.lua','binding_inspect.lua','animation_spec.lua','binding_spec.lua','input_helper.lua']
for name in unchanged:
 expected=(old/name).read_text(encoding='utf-8').replace('seat_outside_owner_test','seat_multi_vehicle_test').replace('0.17.0','0.18.0')
 assert (R/name).read_text(encoding='utf-8')==expected,name
for name in ['input_native.c','vss_input_priority.dll']:
 assert (R/name).read_bytes()==(old/name).read_bytes(),name
# Preserve the existing five code witnesses byte-for-byte; extend with four new
# action bodies and dispatch edges, rather than weakening the original protocol.
prefix=(old/'sync_spec.lua').read_text(encoding='utf-8').split('\nfor name,d',1)[0]
assert prefix.endswith('}') and (R/'sync_spec.lua').read_text(encoding='utf-8').startswith(prefix[:-1]+',')
report=json.loads((R/'package.json').read_text());path=Path(report['file'])
assert hashlib.sha256(path.read_bytes()).hexdigest()==report['sha256']
with zipfile.ZipFile(path)as z:
 assert z.testzip()is None
 manifest=json.loads(z.read('manifest.json'))
 assert manifest['Guid']=='649bec74-f2d5-490d-a6ed-3f3caef67b0b'and len(manifest['Options'])==1
 assert '0.18.0'in manifest['Name']and manifest['Options'][0]['Include']==['Diagnostic']
 assert '暂停0.2.4'in manifest['Description']and 'Disable0.2.4'in manifest['Description']
 assert z.read('Source/network_diagnostic.lua').decode()==(R/'bundled.lua').read_text(encoding='utf-8')
 assert z.read('Source/input/vss_input_priority.dll')==(old/'vss_input_priority.dll').read_bytes()
 for name in ['test_multi_vehicle.lua','test_batch_transaction.lua','test_observe.lua','prepare_tests.py','docs_batch.py','test_vehicle_actions.py','generate_spec.py']:
  assert z.read('Source/experiment/'+name)==(R/name).read_bytes(),name
 for name in ['README_中文.txt','README_English.txt']:assert z.read(name)==(R/name).read_bytes()
 assert (P/'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.0-说明.txt').read_bytes()==z.read('README_中文.txt')
for name,expected in {
 'Vehicle-Specified-Seat-Switch-0.2.4.zip':'0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.16.0.zip':'ebc50c19c0cc3690a7b6ed1c88b6483846a0d9fac34a590b5de802b72bf9243c',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.17.0.zip':'5fc5025dc77dc0149181cc67b6cb5cc92f1ae31d1ff7dd8202b45e3b35fd3876',
}.items():assert hashlib.sha256((P/'outputs'/name).read_bytes()).hexdigest()==expected,name
log=(R/'build-verified.log').read_text(encoding='utf-8')
for marker in ['PASS 359 batched vehicle cases','PASS 372 real batched transaction cases','PASS 8 batched binding FFI cases',
 'PASS 20 real batched sender FFI cases','PASS 140 outside-original-owner cases','PASS 136 seated-original-owner cases',
 'PASS 48 vacant-driver acquisition cases','PASS 50 remote-gunner context cases','PASS 56 input-race cases','PASS integrated bundle syntax']:
 assert log.count(marker)==1,marker
assert log.count('PASS 132 real ownership observer batched-vehicle cases')==4
assert log.count('checked=85')==2 and 'Traceback'not in log and 'RuntimeError'not in log
for build in ['25327279','25480438']:
 actions=json.loads((R/('vehicle-actions-'+build+'.json')).read_text())
 assert len(actions['restores'])==20 and len(actions['prepared'])==2
 assert set(r['vehicle']for r in actions['restores'])=={'m102','m103','m104','bastion','maelstrom'}
fixture=W/'packaging_research/manager-fixture-893f2332-23c5-4c43-8244-151385756dd3/result.json'
backend=json.loads(fixture.read_text())
assert backend['sha256']==report['sha256']and backend['bilingual']and backend['payload_hashes_preserved']and backend['purge_empty']
assert not backend['live_profile_changed']and not backend['game_launched']
accepted=json.loads((old/'capture-20261002-0170/analysis.json').read_text(encoding='utf-8'))
assert accepted['accepted']and len(accepted['runs'])==2 and accepted['remote_gunner_no_entry_animation_observed']
for run in accepted['runs']:
 assert run['counts']['integrated_operation_complete']==6 and run['counts']['integrated_ownership_return_confirmed']==3
 assert run['counts']['integrated_driver_authority_retained']==1 and run['counts']['integrated_local_authority_preserved']==2
 assert all(t['remote'][0]['collection']==0 and t['remote'][0]['role']==0 for t in run['timings'])
report.update(unchanged_lifecycle_input_and_protocol_dependencies=unchanged,input_C_and_binary_unchanged=True,
 production_024_and_0160_0170_unchanged=True,accepted_0170_runs=2,accepted_remote_gunner_no_entry_animation=True,
 batched_context_cases=359,transaction_cases=372,new_observer_cases=132,observer_fixture_combinations=4,
 native_restore_cases_per_build=20,mounted_preparation_cases_per_build=2,interface_witnesses=85,
 arsenal_fixture=str(fixture),live_0180_validation='pending; stop for batched M103/M104/TD220/TD110 two host roles; tanker native optional')
(R/'artifact-review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
