from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
report=json.loads((R/'package.json').read_text())
zpath=P/'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.23.0.zip'
assert Path(report['file'])==zpath and sha(zpath)==report['sha256'] and zpath.stat().st_size==report['bytes']
with zipfile.ZipFile(zpath)as z:
 assert z.testzip()is None
 manifest=json.loads(z.read('manifest.json').decode('utf-8'))
 assert manifest['Guid']=='f4e73fe9-cf5b-4d3a-8619-e9f7dba79b60'
 assert len(manifest['Options'])==1 and manifest['Options'][0]['Include']==['Diagnostic']
 assert '0.23.0'in manifest['Name'] and '0.23.0'in manifest['Description'] and 'Standalone'in manifest['Description']
 assert '未修复'in manifest['Description'] and 'unresolved'in manifest['Description'] and 'TWO'in manifest['Description']
 bundle=z.read('Source/network_diagnostic.lua')
 # Builder stores canonical LF source in the archive; Windows saves CRLF on
 # disk. Compare decoded source with universal newline handling.
 assert bundle.decode('utf-8')==(R/'bundled.lua').read_text(encoding='utf-8') and b"version='0.23.0'"in bundle
 assert b'multi_peer_cross_switch_enabled=false'in bundle and b'multi_peer_live_validation_pending=true'in bundle
 assert b'local fleet_policy='in bundle and b'local motion_watch='in bundle and b'sync_adapter.fleet=fleet_policy'in bundle
 assert b'adapter.motion=motion_observer'in bundle
 assert b'ownership_loan_only=true'in bundle and b'cross_region_seat_mutation_enabled=false'in bundle
 assert b'adapter=ownership_loan_only(adapter,api,snapshot,trace,emit)'in bundle
 assert b'fall_pose:update'not in bundle
 assert b'local ownership_loan_only='in bundle
 assert b'handoff_property_windows_only=true'in bundle and b'downstream_steering_read_only=true'in bundle
 assert b'pcall(spin_reader,api,game,p,compat)'in bundle and b'pcall(spin.read_vehicle,spin,v)'in bundle
 assert b"if spin and(v.name=='bastion'or v.name=='maelstrom')then"in bundle
 assert b"if handoff and c and (stage~='background' or until_at>0 and now<=until_at)then"in bundle
 for name in ['handoff_reader','spin_reader']:
  body=(R/(name+'.lua')).read_text(encoding='utf-8')
  assert 'api.replace('not in body and 'api.call('not in body and 'api.send('not in body
 assert 'serializer_source'in (R/'handoff_reader.lua').read_text()
 for name in ['fleet_policy','fall_repair','motion_watch','physics_reader','handoff_reader','spin_reader','physics_watch','room_watch','steering_watch','adapter','sender','probe','transaction','ownership_loan_only','entry']:
  target='Source/experiment/entry.lua'if name=='entry'else 'Source/'+name+'.lua'if name!='adapter'and name!='probe'else 'Source/sync_'+name+'.lua'
  assert z.read(target).decode('utf-8').replace('\r\n','\n')==(R/(name+'.lua')).read_text(encoding='utf-8'),target
 for name in ['README_中文.txt','README_English.txt']:
  assert z.read(name)==(R/name).read_bytes()
  body=z.read(name).decode('utf-8');assert '0.23.0'in body and '0.22.1'in body
 archive=[x for x in z.namelist()if x.startswith('Diagnostic/')]
 assert len(archive)==3 and any(x.endswith('.stream')for x in archive)and any(x.endswith('.gpu_resources')for x in archive)
 assert all(x.startswith(('Source/','Diagnostic/'))or x in ('manifest.json','README_中文.txt','README_English.txt')for x in z.namelist())
 assert sha(R/'input_native.c')=='8da7062b9964242d2364c4c851a8230fdd8c144f77b11d2a39b5437cfe57c8ff'
 assert hashlib.sha256(z.read('Source/input/vss_input_priority.dll')).hexdigest()=='2c1c290b4e869fbadd1cba4fdaa8d042731359d497d006287e12395c496e0e1b'
 assert hashlib.sha256(z.read('Source/transport/vss_transport.dll')).hexdigest()=='6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3'
preserved={
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.22.1.zip':'9297f0dd0273316e8a32a77219465945de6c574a82159f3e20dd29bbd8cc8333',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.22.0.zip':'8632cdb222e591b84dd39b884e903ac4aced8212fd8c2377f0f67d5e29c44ede',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.21.0.zip':'34f0bd6af4698443e66d41ef4eb1ebbc1e4ea43643b8d7e6a53a62a551c24779',
 'Vehicle-Specified-Seat-Switch-0.2.4.zip':'0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.3.zip':'c6605c6d5e2f874a8fb1ca55425f1f6db4f74e0f5611b1207004b388f41cca34',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.20.0.zip':'4ed93481c8a9508a155dcc8e75d83f8c94017dbd2fde75ece6bba2a47fcb4e29',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.19.0.zip':'b710e032b90a9d8e237c3ade5073eb6a3f66b578555735ecef90472f61d99568',
}
for name,expected in preserved.items():assert sha(P/'outputs'/name)==expected,name+' changed'
results={'version':'0.23.0','sha256':sha(zpath),'bytes':zpath.stat().st_size,
 'archive_crc':'PASS','bundled_source_and_modules':'PASS','bilingual_manifest_and_docs':'PASS',
 'accepted_input_and_transport_helpers_unchanged':'PASS','seven_prior_packages_unchanged':preserved,
 'ownership_isolation_offline':'PASS','ownership_isolation_live_0210':'VALIDATED',
 'physical_observation_live_0221':'VALIDATED',
 'dynamic_property_offsets_and_native_serializer_source_offline':'PASS',
 'downstream_steering_native_latch_and_smoothing_offline':'PASS',
 'new_handoff_properties_and_steering_live':'PENDING',
 'live_multipeer_validation':'PENDING','moving_hitch':'UNRESOLVED','tank_spin':'UNRESOLVED',
 'next_requested_test':'TWO players only, both host roles; M102 front unchanged; parked / continuous W / coasting once each. Optional natural tank steering only if already available.'}
(R/'artifact-verification.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
