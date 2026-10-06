from pathlib import Path
import hashlib,json,zipfile
W=Path(__file__).resolve().parent;R=W/'seat_outside_owner_test';old=W/'seat_seated_owner_test';P=W.parent
unchanged=['probe.lua','input_gate.lua','dispatcher.lua','transaction.lua','sender.lua','personal.lua','driver.lua','animation_sender.lua','binding_sender.lua','transport.lua','platform.lua','sync_spec.lua','animation_spec.lua','binding_spec.lua']
for name in unchanged:
 expected=(old/name).read_text(encoding='utf-8').replace('seat_seated_owner_test','seat_outside_owner_test').replace('0.16.0','0.17.0')
 assert (R/name).read_text(encoding='utf-8')==expected,name
for name in ['input_native.c','vss_input_priority.dll']:
 assert (R/name).read_bytes()==(old/name).read_bytes(),name
report=json.loads((R/'package.json').read_text());path=Path(report['file'])
assert hashlib.sha256(path.read_bytes()).hexdigest()==report['sha256']
with zipfile.ZipFile(path)as z:
 assert z.testzip()is None
 manifest=json.loads(z.read('manifest.json'))
 assert manifest['Guid']=='649bec74-f2d5-490d-a6ed-3f3caef67b0b'and len(manifest['Options'])==1
 assert manifest['Options'][0]['Include']==['Diagnostic']and '0.17.0'in manifest['Name']
 assert '暂停0.2.4'in manifest['Description']and 'Disable0.2.4'in manifest['Description']
 assert z.read('Source/network_diagnostic.lua').decode()==(R/'bundled.lua').read_text(encoding='utf-8')
 assert z.read('Source/input/vss_input_priority.dll')==(old/'vss_input_priority.dll').read_bytes()
 for name in ['test_outside_owner.lua','test_seated_owner.lua','test_driver_acquire.lua','test_observe.lua','prepare_tests.py','docs_outside.py']:
  assert z.read('Source/experiment/'+name)==(R/name).read_bytes(),name
 assert (P/'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.17.0-说明.txt').read_bytes()==z.read('README_中文.txt')
 for name in ['README_中文.txt','README_English.txt']:assert z.read(name)==(R/name).read_bytes()
for name,expected in {
 'Vehicle-Specified-Seat-Switch-0.2.4.zip':'0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.14.0.zip':'97a740e852cab604fe9c823555502653a1f2ea5310e2501b05346cd7f9bc002b',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.15.0.zip':'3a1e50cfdf977b85c4883a7513feff43576c16523d890d3e6bed453b7d709995',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.16.0.zip':'ebc50c19c0cc3690a7b6ed1c88b6483846a0d9fac34a590b5de802b72bf9243c',
}.items():assert hashlib.sha256((P/'outputs'/name).read_bytes()).hexdigest()==expected,name
log=(R/'build-verified.log').read_text(encoding='utf-8')
for s in ['PASS 140 outside-original-owner cases','PASS 136 seated-original-owner cases','PASS 48 vacant-driver acquisition cases','PASS 50 remote-gunner context cases','PASS 56 input-race cases','PASS integrated bundle syntax']:assert s in log,s
for n,kind in [(24,'vacant-driver'),(91,'seated-original-owner'),(89,'outside-original-owner')]:
 assert log.count(f'PASS {n} real ownership observer {kind} cases')==4
assert 'Traceback'not in log and 'RuntimeError'not in log
fixture=W/'packaging_research/manager-fixture-f199cb62-0795-406c-aa88-bbb5a72bc6cc/result.json'
backend=json.loads(fixture.read_text())
assert backend['sha256']==report['sha256']and backend['bilingual']and backend['payload_hashes_preserved']and backend['purge_empty']
assert not backend['live_profile_changed']and not backend['game_launched']
accepted=json.loads((old/'capture-20261001-0160/analysis.json').read_text(encoding='utf-8'))
assert accepted['accepted']and accepted['occupied_front_runtime_refusal_recorded']and len(accepted['runs'])==2
for run in accepted['runs']:
 assert run['counts']['integrated_operation_complete']==6 and run['counts']['integrated_ownership_return_confirmed']==3
 assert run['counts']['integrated_driver_authority_retained']==1 and run['counts']['integrated_local_authority_preserved']==2
 assert [t['authority_path']for t in run['timings']]==['borrowed_returned']*3+['acquired_retained']+['already_local']*2
 assert all(run['counts'].get(k,0)==0 for k in ['integrated_cancelled','integrated_stopped','integrated_incomplete','input_priority_failed','read_gap'])
foot=json.loads((old/'capture-20261001-0160/outside-avatar-states.json').read_text(encoding='utf-8'))
assert len(foot)==2
expected=dict(collection=0,transition_type=0,role=0,entry_role=0,entrance=-1,current=0,reserved=0,target=-1,action=-1,transitioning=0,queued_exit=0)
for sample in foot:
 a=sample['avatar'];assert a['is_local']==False and a['owned_local']==False and a['vehicle_input']==False
 assert all(a['seat'][k]==v for k,v in expected.items())
report.update(input_binary_and_C_unchanged=True,unchanged_protocol_lifecycle_and_input=unchanged,
 production_024_and_previous_packages_unchanged=True,outside_owner_context_cases=140,outside_owner_observer_cases=89,
 observer_fixture_combinations=4,arsenal_fixture=str(fixture),accepted_0160_runs=2,
 captured_remote_completed_exit_states=2,live_0170_validation='pending; stop for original-owner-outside host and guest data')
(R/'artifact-review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
