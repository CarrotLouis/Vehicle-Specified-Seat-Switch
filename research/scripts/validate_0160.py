from pathlib import Path
import hashlib,json,zipfile
W=Path(__file__).resolve().parent;R=W/'seat_seated_owner_test';old=W/'seat_driver_acquire_test';P=W.parent
unchanged=['probe.lua','input_gate.lua','dispatcher.lua','transaction.lua','sender.lua','personal.lua','driver.lua','animation_sender.lua','binding_sender.lua','transport.lua','platform.lua','sync_spec.lua','animation_spec.lua','binding_spec.lua']
for name in unchanged:
 expected=(old/name).read_text(encoding='utf-8').replace('seat_driver_acquire_test','seat_seated_owner_test').replace('0.15.0','0.16.0')
 assert (R/name).read_text(encoding='utf-8')==expected,name
for name in ['input_native.c','vss_input_priority.dll']:
 assert (R/name).read_bytes()==(old/name).read_bytes(),name
report=json.loads((R/'package.json').read_text());path=Path(report['file'])
assert hashlib.sha256(path.read_bytes()).hexdigest()==report['sha256']
with zipfile.ZipFile(path)as z:
 assert z.testzip()is None
 manifest=json.loads(z.read('manifest.json'))
 assert manifest['Guid']=='649bec74-f2d5-490d-a6ed-3f3caef67b0b'and len(manifest['Options'])==1
 assert manifest['Options'][0]['Include']==['Diagnostic']and '0.16.0'in manifest['Name']
 assert '暂停0.2.4'in manifest['Description']and 'Disable0.2.4'in manifest['Description']
 assert z.read('Source/network_diagnostic.lua').decode()==(R/'bundled.lua').read_text(encoding='utf-8')
 assert z.read('Source/input/vss_input_priority.dll')==(old/'vss_input_priority.dll').read_bytes()
 for name in ['test_seated_owner.lua','test_driver_acquire.lua','test_remote_gunner.lua','test_observe.lua','prepare_tests.py','docs_seated.py']:
  assert z.read('Source/experiment/'+name)==(R/name).read_bytes(),name
 assert (P/'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.16.0-说明.txt').read_bytes()==z.read('README_中文.txt')
 for name in ['README_中文.txt','README_English.txt']:assert z.read(name)==(R/name).read_bytes()
for name,expected in {
 'Vehicle-Specified-Seat-Switch-0.2.4.zip':'0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.13.1.zip':'13a7f8f07caca31afe6d350a3a019fd4c6f12929ef33e7a487dfd487a27a037e',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.14.0.zip':'97a740e852cab604fe9c823555502653a1f2ea5310e2501b05346cd7f9bc002b',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.15.0.zip':'3a1e50cfdf977b85c4883a7513feff43576c16523d890d3e6bed453b7d709995',
}.items():assert hashlib.sha256((P/'outputs'/name).read_bytes()).hexdigest()==expected,name
log=(R/'build-verified.log').read_text(encoding='utf-8')
for s in ['PASS 136 seated-original-owner cases','PASS 48 vacant-driver acquisition cases','PASS 50 remote-gunner context cases','PASS 56 input-race cases','PASS integrated bundle syntax']:assert s in log,s
assert log.count('PASS 24 real ownership observer vacant-driver cases')==4
assert log.count('PASS 91 real ownership observer seated-original-owner cases')==4
assert 'Traceback'not in log and 'RuntimeError'not in log
fixture=W/'packaging_research/manager-fixture-51d3c3b0-412c-4b2b-b0cb-1452eada568c/result.json'
backend=json.loads(fixture.read_text())
assert backend['sha256']==report['sha256']and backend['bilingual']and backend['payload_hashes_preserved']and backend['purge_empty']
assert not backend['live_profile_changed']and not backend['game_launched']
accepted=json.loads((old/'capture-20261001-0150/analysis.json').read_text(encoding='utf-8'))
assert accepted['no_retest_required']and len(accepted['accepted'])==2 and len(accepted['excluded'])==2
for run in accepted['runs']:
 if run['name']not in accepted['accepted']:continue
 assert run['timings'][0]['authority_path']=='acquired_retained'
 assert run['counts']['integrated_driver_authority_retained']==1
 assert all(t['remote'][0]['node']==4 and t['remote'][0]['role']==2 for t in run['timings'])
 assert all(run['counts'].get(k,0)==0 for k in ['integrated_cancelled','integrated_stopped','integrated_incomplete','input_priority_failed','read_gap','integrated_ownership_return_confirmed'])
report.update(input_binary_and_C_unchanged=True,unchanged_protocol_lifecycle_and_input=unchanged,
 production_024_and_previous_packages_unchanged=True,seated_owner_context_cases=136,seated_owner_observer_cases=91,
 observer_fixture_combinations=4,arsenal_fixture=str(fixture),accepted_0150_runs=2,no_0150_retest_needed=True,
 live_0160_validation='pending; stop for targeted original-owner-front host and guest data')
(R/'artifact-review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
