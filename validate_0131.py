from pathlib import Path
import hashlib,json,zipfile

W=Path(__file__).resolve().parent;R=W/'seat_input_race_fix';old=W/'seat_aboard_passenger_test';P=W.parent
unchanged=['transaction.lua','sender.lua','personal.lua','driver.lua','animation_sender.lua','binding_sender.lua','observe.lua','transport.lua','platform.lua']
for name in unchanged:
    expected=(old/name).read_text(encoding='utf-8').replace('seat_aboard_passenger_test','seat_input_race_fix').replace('0.13.0','0.13.1')
    assert (R/name).read_text(encoding='utf-8')==expected,name
for name in ['input_native.c','vss_input_priority.dll']:
    assert (R/name).read_bytes()==(old/name).read_bytes(),name
report=json.loads((R/'package.json').read_text());path=Path(report['file'])
assert hashlib.sha256(path.read_bytes()).hexdigest()==report['sha256']
with zipfile.ZipFile(path) as z:
    assert z.testzip() is None
    manifest=json.loads(z.read('manifest.json'))
    assert manifest['Guid']=='649bec74-f2d5-490d-a6ed-3f3caef67b0b' and len(manifest['Options'])==1
    assert manifest['Options'][0]['Include']==['Diagnostic'] and '0.13.1' in manifest['Name']
    assert '暂停0.2.4' in manifest['Description'] and 'Disable gameplay0.2.4' in manifest['Description']
    assert z.read('Source/network_diagnostic.lua').decode()==(R/'bundled.lua').read_text(encoding='utf-8')
    assert z.read('Source/input/vss_input_priority.dll')==(old/'vss_input_priority.dll').read_bytes()
    for name in ['test_input_race.lua','input_race_fixture.lua','input_race_replay.lua','input-race-replay.json','docs_race.py']:
        assert z.read('Source/experiment/'+name)==(R/name).read_bytes(),name
    assert 'Source/experiment/docs_thread.py' not in z.namelist()
    assert (P/'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.13.1-说明.txt').read_bytes()==z.read('README_中文.txt')
    for name in ['README_中文.txt','README_English.txt']:
        assert z.read(name)==(R/name).read_bytes()
assert hashlib.sha256((P/'outputs/Vehicle-Specified-Seat-Switch-0.2.4.zip').read_bytes()).hexdigest()=='0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27'
assert hashlib.sha256((P/'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.13.0.zip').read_bytes()).hexdigest()=='860f5a3412c082613d03727629a57b18ff940653a897818761a6341800ebc97c'
replay=json.loads((R/'input-race-replay.json').read_text())
assert len(replay)==6 and sorted(r['delay_ms'] for r in replay)==[16,16,16,31,31,31]
log=(R/'build-verified.log').read_text(encoding='utf-8')
assert 'PASS 56 input-race cases' in log and 'PASS integrated bundle syntax' in log and 'Traceback' not in log
report.update(input_binary_and_C_unchanged=True,core_protocol_unchanged=unchanged,production_024_and_previous_0130_unchanged=True,
              captured_race_cases=6,input_race_regressions=56,in_game_validation='pending')
(R/'artifact-review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
