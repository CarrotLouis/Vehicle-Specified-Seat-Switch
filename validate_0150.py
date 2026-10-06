from pathlib import Path
import hashlib,json,zipfile
W=Path(__file__).resolve().parent;R=W/'seat_driver_acquire_test';old=W/'seat_remote_gunner_test';P=W.parent
unchanged=['input_gate.lua','dispatcher.lua','transaction.lua','sender.lua','personal.lua','driver.lua','animation_sender.lua','binding_sender.lua','transport.lua','platform.lua','sync_spec.lua','animation_spec.lua','binding_spec.lua']
for name in unchanged:
 expected=(old/name).read_text(encoding='utf-8').replace('seat_remote_gunner_test','seat_driver_acquire_test').replace('0.14.0','0.15.0')
 assert (R/name).read_text(encoding='utf-8')==expected,name
for name in ['input_native.c','vss_input_priority.dll']:
 assert (R/name).read_bytes()==(old/name).read_bytes(),name
report=json.loads((R/'package.json').read_text());path=Path(report['file'])
assert hashlib.sha256(path.read_bytes()).hexdigest()==report['sha256']
with zipfile.ZipFile(path)as z:
 assert z.testzip()is None
 manifest=json.loads(z.read('manifest.json'))
 assert manifest['Guid']=='649bec74-f2d5-490d-a6ed-3f3caef67b0b'and len(manifest['Options'])==1
 assert manifest['Options'][0]['Include']==['Diagnostic']and '0.15.0'in manifest['Name']
 assert '暂停0.2.4'in manifest['Description']and 'Disable0.2.4'in manifest['Description']
 assert z.read('Source/network_diagnostic.lua').decode()==(R/'bundled.lua').read_text(encoding='utf-8')
 assert z.read('Source/input/vss_input_priority.dll')==(old/'vss_input_priority.dll').read_bytes()
 for name in ['test_driver_acquire.lua','test_remote_gunner.lua','test_observe.lua','prepare_tests.py','docs_driver.py']:
  assert z.read('Source/experiment/'+name)==(R/name).read_bytes(),name
 assert (P/'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.15.0-说明.txt').read_bytes()==z.read('README_中文.txt')
 for name in ['README_中文.txt','README_English.txt']:assert z.read(name)==(R/name).read_bytes()
for name,expected in {
 'Vehicle-Specified-Seat-Switch-0.2.4.zip':'0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.13.1.zip':'13a7f8f07caca31afe6d350a3a019fd4c6f12929ef33e7a487dfd487a27a037e',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.14.0.zip':'97a740e852cab604fe9c823555502653a1f2ea5310e2501b05346cd7f9bc002b',
}.items():assert hashlib.sha256((P/'outputs'/name).read_bytes()).hexdigest()==expected,name
log=(R/'build-verified.log').read_text(encoding='utf-8')
for s in ['PASS 48 vacant-driver acquisition cases','PASS 50 remote-gunner context cases','PASS 56 input-race cases','PASS integrated bundle syntax']:assert s in log,s
assert log.count('PASS 24 real ownership observer vacant-driver cases')==4
assert 'Traceback'not in log and 'RuntimeError'not in log
fixture=W/'packaging_research/manager-fixture-7e788efb-1d60-41b4-ba57-da082987ac9d/result.json'
backend=json.loads(fixture.read_text())
assert backend['sha256']==report['sha256']and backend['bilingual']and backend['payload_hashes_preserved']and backend['purge_empty']
assert not backend['live_profile_changed']and not backend['game_launched']
accepted=json.loads((old/'capture-20261001-0140/analysis.json').read_text(encoding='utf-8'))
for run in accepted['runs']:
 assert run['counts']['integrated_operation_complete']==4 and run['counts']['integrated_local_authority_preserved']==4
 assert all(t['authority_path']=='already_local'and t['remote'][0]['node']==4 and t['remote'][0]['role']==2 for t in run['timings'])
 assert run['input_reasons']=={'priority_request':4}
report.update(input_binary_and_C_unchanged=True,unchanged_protocol_and_input=unchanged,
 production_024_and_previous_packages_unchanged=True,acquisition_cases=48,observer_cases=24,
 observer_fixture_combinations=4,arsenal_fixture=str(fixture),accepted_0140_runs=2,
 live_0150_validation='pending; stop for targeted host and guest data')
(R/'artifact-review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
