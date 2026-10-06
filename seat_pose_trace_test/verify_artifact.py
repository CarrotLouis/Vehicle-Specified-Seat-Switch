from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pack=P/'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.24.0.zip'
report=json.loads((R/'package.json').read_text(encoding='utf-8'))
assert sha(pack)==report['sha256'] and pack.stat().st_size==report['bytes']
with zipfile.ZipFile(pack)as z:
 assert z.testzip()is None
 manifest=json.loads(z.read('manifest.json').decode('utf-8'))
 assert manifest['Guid']=='9a2a3557-5cc1-4f95-9797-8c00c9a86478'
 assert len(manifest['Options'])==1 and manifest['Options'][0]['Include']==['Diagnostic']
 assert '0.24.0'in manifest['Name']and'Standalone'in manifest['Description']and'未修复'in manifest['Description']
 body=z.read('Source/network_diagnostic.lua').decode('utf-8')
 assert body==(R/'bundled.lua').read_text(encoding='utf-8')
 for key in ["version='0.24.0'",'native_motion_call_observation=true','body_flags_read_only=true',
  'ownership_loan_only=true','cross_region_seat_mutation_enabled=false','multi_peer_cross_switch_enabled=false',
  'pose_calls:arm(c.owner.vehicle,c,t,data)','motion_tools={pose_trace=pose_trace']:
  assert key in body,key
 for name in ['pose_trace','body_flags_reader','motion_helper','physics_reader','handoff_reader','spin_reader',
  'physics_watch','steering_watch','ownership_loan_only']:
  assert z.read('Source/'+name+'.lua').decode('utf-8')==(R/(name+'.lua')).read_text(encoding='utf-8')
 for name in ['README_中文.txt','README_English.txt']:
  assert z.read(name)==(R/name).read_bytes()
 for folder,file,expected in [
  ('input','vss_input_priority.dll','2c1c290b4e869fbadd1cba4fdaa8d042731359d497d006287e12395c496e0e1b'),
  ('transport','vss_transport.dll','6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3'),
  ('motion','vss_motion_trace.dll','72f9102952776c995cbd82f9fe9524a45271658a17f11bd32856f403b5611aec')]:
  assert hashlib.sha256(z.read('Source/'+folder+'/'+file)).hexdigest()==expected
 archive=[n for n in z.namelist()if n.startswith('Diagnostic/')];assert len(archive)==3
 assert not any(n.startswith('Diagnostic/')and n.endswith('.dll')for n in z.namelist())
preserved={
 'Vehicle-Specified-Seat-Switch-0.2.4.zip':'0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.3.zip':'c6605c6d5e2f874a8fb1ca55425f1f6db4f74e0f5611b1207004b388f41cca34',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.19.0.zip':'b710e032b90a9d8e237c3ade5073eb6a3f66b578555735ecef90472f61d99568',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.20.0.zip':'4ed93481c8a9508a155dcc8e75d83f8c94017dbd2fde75ece6bba2a47fcb4e29',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.21.0.zip':'34f0bd6af4698443e66d41ef4eb1ebbc1e4ea43643b8d7e6a53a62a551c24779',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.22.0.zip':'8632cdb222e591b84dd39b884e903ac4aced8212fd8c2377f0f67d5e29c44ede',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.22.1.zip':'9297f0dd0273316e8a32a77219465945de6c574a82159f3e20dd29bbd8cc8333',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.23.0.zip':'3393b51088a97af1eeab7514b220ccc2a92da211c2430b51d22f8a1db5edfb2b'}
for name,expected in preserved.items():assert sha(P/'outputs'/name)==expected,name
old=W/'seat_handoff_motion_test'
for name in ['adapter','probe','transaction','sender','ownership_loan_only','input_gate','tank_driver','spin_reader','handoff_reader','physics_reader']:
 before=(old/(name+'.lua')).read_text(encoding='utf-8')
 after=(R/(name+'.lua')).read_text(encoding='utf-8')
 assert after==before.replace('seat_handoff_motion_test','seat_pose_trace_test').replace('0.23.0','0.24.0'),name
fixture=(W/'packaging_research/test_standalone_package.cjs').read_text(encoding='utf-8')
assert fixture.count("assert(pack.readAsText('README_中文.txt').includes('暂停0.2.4')); ")==0
fixture=fixture.replace("assert(pack.readAsText('README_中文.txt').includes('暂停0.2.4'));",
 "assert(/(?:暂停|停用)0\\.2\\.4/.test(pack.readAsText('README_中文.txt')));")
assert '停用' in fixture
(W/'packaging_research/test_pose_package.cjs').write_text(fixture,encoding='utf-8')
out=dict(version='0.24.0',sha256=sha(pack),bytes=pack.stat().st_size,archive_crc='PASS',source_modules_docs='PASS',
 unchanged_eight_packages=preserved,old_loan_input_transport_unchanged='PASS',two_capture_native_contracts='PASS',
 new_observer_live='PENDING',moving_stop='UNRESOLVED',tank_spin='UNRESOLVED',multi_peer_live='PENDING')
(R/'artifact-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('PASS final ZIP CRC/source/docs/three payload files, new helper hash, unchanged loan/switch/helpers/eight prior ZIPs')
