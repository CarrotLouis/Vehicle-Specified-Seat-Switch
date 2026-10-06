from pathlib import Path
import hashlib,json,zipfile

W=Path(__file__).resolve().parent;P=W.parent;R=W/'seat_multi_peer_diagnostic';old=W/'seat_tank_pose_fix'
sha=lambda b:hashlib.sha256(b).hexdigest()
runtime=['adapter','observe','probe','sender','transaction','driver','tank_driver','pose','fall_repair',
 'dispatcher','input_gate','personal','inspect','animation_sender','binding_sender','binding_inspect',
 'animation_watch','sync_spec','animation_spec','binding_spec','tank_spec','platform','transport','input_helper']
for name in runtime:
    expected=(old/(name+'.lua')).read_text(encoding='utf-8')
    if name=='transport':expected=expected.replace("version='0.18.3'","version='0.19.0'")
    assert (R/(name+'.lua')).read_text(encoding='utf-8')==expected,name
for name in ['input_native.c','vss_input_priority.dll']:
    assert (R/name).read_bytes()==(old/name).read_bytes(),name
for name in ['room_watch.lua','steering_watch.lua']:
    text=(R/name).read_text(encoding='utf-8')
    for forbidden in ['api.replace(', 'ffi.cast(', ':send(', ':prepare(', 'api.write(']:
        assert forbidden not in text,(name,forbidden)
    assert 'read_only=true' in text
entry=(R/'entry.lua').read_text(encoding='utf-8')
assert 'multi_peer_cross_switch_enabled=false' in entry
assert 'local fleet_owner_reader=authority_observe.new' in entry
assert 'fleet_observer:update(s,probe.pending)' in entry and 'steering_observer:update(s)' in entry
log=(R/'build-verified.log').read_text(encoding='utf-8')
markers=['PASS 312 real control-abort recovery cases','PASS 24 tank-driver personal binding FFI cases',
 'PASS 359 batched vehicle cases','PASS 372 real batched transaction cases','PASS 20 real batched sender FFI cases',
 'PASS 188 recorded pose replays','PASS 80 actual steering input cases','PASS integrated bundle syntax',
 'PASS read-only room watch','PASS read-only steering watch']
for marker in markers:assert log.count(marker)==1,marker
assert log.count('checked=89')==2
assert log.count('PASS 30 real ownership-reader fleet cases')==4
assert 'Traceback'not in log and 'RuntimeError'not in log
report=json.loads((R/'package.json').read_text());path=Path(report['file'])
assert sha(path.read_bytes())==report['sha256']and path.stat().st_size==report['bytes']
with zipfile.ZipFile(path)as z:
    assert z.testzip()is None
    m=json.loads(z.read('manifest.json'))
    assert m['Guid']=='649bec74-f2d5-490d-a6ed-3f3caef67b0b' and len(m['Options'])==1 and m['Options'][0]['Include']==['Diagnostic']
    assert 'Standalone0.19.0'in m['Description']and 'NOT enabled'in m['Description']and '暂停0.2.4'in m['Description']
    for name in runtime+['room_watch','steering_watch']:
        assert z.read('Source/experiment/'+name+'.lua')==(R/(name+'.lua')).read_bytes(),name
    assert z.read('Source/network_diagnostic.lua').decode('utf-8')==(R/'bundled.lua').read_text(encoding='utf-8')
    for name in ['docs_fleet.py','docs_batch.py','repackage_docs.py','prepare_room_tests.py',
                 'test_room_watch.lua','test_steering_watch.lua','test_room_observe.lua']:
        assert z.read('Source/experiment/'+name)==(R/name).read_bytes(),name
    for name in ['README_中文.txt','README_English.txt']:
        assert z.read(name)==(R/name).read_bytes()
    assert z.read('README_中文.txt')==(P/'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.19.0-说明.txt').read_bytes()
preserved={
 'Vehicle-Specified-Seat-Switch-0.2.4.zip':'0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.2.zip':'da9e6746cbd773462f282ae76d316bcd2d62d8f4acaa61e9e19094792e9b9c42',
 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.3.zip':'c6605c6d5e2f874a8fb1ca55425f1f6db4f74e0f5611b1207004b388f41cca34'}
for name,digest in preserved.items():assert sha((P/'outputs'/name).read_bytes())==digest,name
C=W/'seat_multi_peer_research/capture-20261002-0183'
for item in json.loads((C/'files.json').read_text(encoding='utf-8')):
    b=(C/item['name']).read_bytes();assert sha(b)==item['sha256'] and len(b)==item['bytes']
analysis=json.loads((C/'analysis.json').read_text(encoding='utf-8'))
assert analysis['runs'][0]['post_join_input_reasons']['cross_scope_unavailable']==17
assert [sum(r['completed'].values())for r in analysis['runs']]==[8,12,0,12]
fixtures=[f for f in (W/'packaging_research').glob('manager-fixture-*/result.json')if json.loads(f.read_text()).get('sha256')==report['sha256']]
assert fixtures,'Actual Arsenal import/deploy for the final exact ZIP required'
fixture=max(fixtures,key=lambda f:f.stat().st_mtime_ns);manager=json.loads(fixture.read_text())
assert manager['files']==3 and manager['bilingual']and manager['payload_hashes_preserved']and manager['purge_empty']
assert not manager['live_profile_changed']and not manager['game_launched']
report.update(new_modules_read_only=True,accepted_two_player_runtime_unchanged_except_line_endings_and_transport_log_version=runtime,
    production_and_previous_artifacts_preserved=True,all_avatar_fleet_observer_cases=120,
    four_peer_success='offline ownership mapping only; live new capture required',
    multi_peer_cross_switch_enabled=False,tank_spin_fixed=False,bastion_pose_user_accepted_both_hosts=True,
    arsenal_fixture=str(fixture),frozen_evidence=str(C/'analysis.json'))
(R/'artifact-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
