from pathlib import Path
import hashlib,json,zipfile
W=Path(__file__).resolve().parent;P=W.parent;R=W/'seat_tank_pose_fix';old=W/'seat_tank_binding_fix'
def sha(b):return hashlib.sha256(b).hexdigest()
unchanged=['observe.lua','sender.lua','driver.lua','input_gate.lua','personal.lua','probe.lua',
 'platform.lua','transport.lua','binding_inspect.lua','binding_sender.lua','animation_watch.lua',
 'sync_spec.lua','animation_spec.lua','binding_spec.lua','input_helper.lua']
for name in unchanged:
 expected=(old/name).read_text(encoding='utf-8').replace('seat_tank_binding_fix','seat_tank_pose_fix').replace('0.18.2','0.18.3')
 assert (R/name).read_text(encoding='utf-8')==expected,name
for name in ['input_native.c','vss_input_priority.dll']:assert (R/name).read_bytes()==(old/name).read_bytes(),name
for name in ['animation_sender','adapter','dispatcher','transaction']:
 assert (R/('regression_0182_'+name+'.lua')).read_bytes()==(old/(name+'.lua')).read_bytes()
assert (R/'regression_0182_pose.lua').read_bytes()==(W/'seat_switch/src/pose.lua').read_bytes()
capture=old/'capture-20261002-0182';files=json.loads((capture/'files.json').read_text(encoding='utf-8'))
# The initial freeze stores a list (or its enclosing files property).
if isinstance(files,dict):files=files['files']
for f in files:
 b=(capture/f['name']).read_bytes();assert sha(b)==f['sha256']and len(b)==f['bytes']
analysis=json.loads((capture/'analysis.json').read_text(encoding='utf-8'))
assert [sum(r['completed'].values())for r in analysis['runs']]==[14,20]
log=(R/'build-verified.log').read_text(encoding='utf-8')
markers=['PASS 312 real control-abort recovery cases','PASS 24 tank-driver personal binding FFI cases',
 'PASS 359 batched vehicle cases','PASS 372 real batched transaction cases','PASS 20 real batched sender FFI cases','PASS 8 batched binding FFI cases',
 'PASS 188 recorded pose replays','PASS 80 actual steering input cases','PASS tank native-exit FFI','PASS integrated bundle syntax',
 'PASS 140 outside-original-owner cases','PASS 136 seated-original-owner cases','PASS 48 vacant-driver acquisition cases','PASS 50 remote-gunner context cases','PASS 56 input-race cases']
for marker in markers:assert log.count(marker)==1,marker
assert log.count('checked=89')==2 and 'Traceback'not in log and 'RuntimeError'not in log
assert log.count('actual tank exit/completion false/true arguments')==2
report=json.loads((R/'package.json').read_text());path=Path(report['file'])
assert sha(path.read_bytes())==report['sha256']and path.stat().st_size==report['bytes']
with zipfile.ZipFile(path)as z:
 assert z.testzip()is None
 manifest=json.loads(z.read('manifest.json'))
 assert manifest['Guid']=='649bec74-f2d5-490d-a6ed-3f3caef67b0b'and len(manifest['Options'])==1
 assert '0.18.3'in manifest['Name']and manifest['Options'][0]['Include']==['Diagnostic']
 assert '暂停0.2.4'in manifest['Description']and 'Standalone0.18.3'in manifest['Description']
 assert z.read('Source/network_diagnostic.lua').decode('utf-8')==(R/'bundled.lua').read_text(encoding='utf-8')
 assert z.read('Source/input/vss_input_priority.dll')==(old/'vss_input_priority.dll').read_bytes()
 for name in ['adapter.lua','transaction.lua','dispatcher.lua','animation_sender.lua','inspect.lua','pose.lua',
  'fall_repair.lua','tank_driver.lua','tank_spec.lua','test_tank_native.py','test_tank_driver.lua','test_tank_pose.lua',
  'test_tank_steering.lua','docs_tank.py','test_batch_transaction.lua']:
  assert z.read('Source/experiment/'+name)==(R/name).read_bytes(),name
 assert z.read('Source/pose.lua')==(R/'pose.lua').read_bytes()
 for name in ['README_中文.txt','README_English.txt']:assert z.read(name)==(R/name).read_bytes()
 assert (P/'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.3-说明.txt').read_bytes()==z.read('README_中文.txt')
for name,expected in {
 'Vehicle-Specified-Seat-Switch-0.2.4.zip':'0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.17.0.zip':'5fc5025dc77dc0149181cc67b6cb5cc92f1ae31d1ff7dd8202b45e3b35fd3876',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.0.zip':'40059a2fed9477f6b1c8b83e7a695f17b7cb232fc4c2a890f85adbcb0fc1e3c9',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.1.zip':'9a17d5abb741c6847a092b1d279b90f485061da0f044906edcb61f1ddec12685',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.2.zip':'da9e6746cbd773462f282ae76d316bcd2d62d8f4acaa61e9e19094792e9b9c42',
}.items():assert sha((P/'outputs'/name).read_bytes())==expected,name
fixtures=[f for f in (W/'packaging_research').glob('manager-fixture-*/result.json')if json.loads(f.read_text()).get('sha256')==report['sha256']]
assert fixtures,'A real Arsenal fixture for this exact ZIP is required'
fixture=max(fixtures,key=lambda f:f.stat().st_mtime_ns)
manager=json.loads(fixture.read_text())
assert manager['sha256']==report['sha256']and manager['files']==3 and manager['bilingual']and manager['payload_hashes_preserved']and manager['purge_empty']
assert not manager['live_profile_changed']and not manager['game_launched']
report.update(runtime_changes=['named/conditional own Bastion Fall/Fall_Aim layer reset; preserves seated/lean layers',
 'existing native animation RPC for Bastion passenger overlay; native-route own-avatar recovery',
 'verified canonical native driver-exit cleanup for installer-controlled tanks',
 'held A/D exception only for validated local two-player tank driver exits'],
 unchanged_dependencies=unchanged,production_and_old_packages_unchanged=True,input_C_and_binary_unchanged=True,
 live_0182_evidence=str(capture/'analysis.json'),live_host_completed=14,live_guest_completed=20,
 recorded_pose_replays=188,matching_fall_cases=44,steering_input_cases=80,interface_witnesses=89,
 arsenal_fixture=str(fixture),live_0183_validation='pending; combined Bastion aiming and both tanks held-steering exit/friend takeover; both hosts; no full FRV/tanker repeat')
(R/'artifact-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
