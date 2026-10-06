from pathlib import Path
import hashlib,json,zipfile
W=Path(__file__).resolve().parent;R=W/'seat_remote_gunner_test';old=W/'seat_input_race_fix';P=W.parent
unchanged=['input_gate.lua','dispatcher.lua','probe.lua','transaction.lua','sender.lua','personal.lua','driver.lua','animation_sender.lua','binding_sender.lua','observe.lua','transport.lua','platform.lua']
for name in unchanged:
    expected=(old/name).read_text(encoding='utf-8').replace('seat_input_race_fix','seat_remote_gunner_test').replace('0.13.1','0.14.0')
    assert (R/name).read_text(encoding='utf-8')==expected,name
for name in ['input_native.c','vss_input_priority.dll']:
    assert (R/name).read_bytes()==(old/name).read_bytes(),name
report=json.loads((R/'package.json').read_text());path=Path(report['file'])
assert hashlib.sha256(path.read_bytes()).hexdigest()==report['sha256']
with zipfile.ZipFile(path) as z:
    assert z.testzip() is None
    manifest=json.loads(z.read('manifest.json'))
    assert manifest['Guid']=='649bec74-f2d5-490d-a6ed-3f3caef67b0b' and len(manifest['Options'])==1
    assert manifest['Options'][0]['Include']==['Diagnostic'] and '0.14.0' in manifest['Name']
    assert '暂停0.2.4' in manifest['Description'] and 'Disable gameplay0.2.4' in manifest['Description']
    assert z.read('Source/network_diagnostic.lua').decode()==(R/'bundled.lua').read_text(encoding='utf-8')
    assert z.read('Source/input/vss_input_priority.dll')==(old/'vss_input_priority.dll').read_bytes()
    for name in ['test_remote_gunner.lua','test_aboard_receiver.py','docs_gunner.py']:
        assert z.read('Source/experiment/'+name)==(R/name).read_bytes(),name
    assert (P/'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.14.0-说明.txt').read_bytes()==z.read('README_中文.txt')
    for name in ['README_中文.txt','README_English.txt']:assert z.read(name)==(R/name).read_bytes()
for name,expected in {
    'Vehicle-Specified-Seat-Switch-0.2.4.zip':'0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27',
    'Vehicle-Seat-Weapon-Sync-Diagnostic-0.13.1.zip':'13a7f8f07caca31afe6d350a3a019fd4c6f12929ef33e7a487dfd487a27a037e',
}.items():assert hashlib.sha256((P/'outputs'/name).read_bytes()).hexdigest()==expected,name
log=(R/'build-verified.log').read_text(encoding='utf-8')
assert 'PASS 50 remote-gunner context cases' in log and 'PASS 56 input-race cases' in log and 'Traceback' not in log
for build in ['25327279','25480438']:
    receiver=json.loads((R/('aboard-receiver-'+build+'.json')).read_text())
    gunner=[c for c in receiver['cases'] if c['remote_occupant']==4]
    assert len(receiver['cases'])==38 and len(gunner)==8 and all(c['remote_role']==2 and c['remote_state_unchanged'] and c['remote_entity_unchanged'] for c in gunner)
report.update(input_binary_and_C_unchanged=True,core_protocol_and_input_unchanged=unchanged,production_024_and_previous_0131_unchanged=True,
              remote_gunner_context_cases=50,remote_gunner_actual_receiver_cases_each_build=8,in_game_validation='pending')
(R/'artifact-review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
