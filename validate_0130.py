from pathlib import Path
import hashlib,json,zipfile
W=Path(__file__).resolve().parent;R=W/'seat_aboard_passenger_test';old=W/'seat_input_thread_fix';P=W.parent
unchanged=['input_gate.lua','input_native.c','probe.lua','dispatcher.lua','driver.lua','sender.lua','personal.lua','animation_sender.lua','binding_sender.lua']
for name in unchanged:
    expected=(old/name).read_text(encoding='utf-8').replace('seat_input_thread_fix','seat_aboard_passenger_test').replace('0.12.1','0.13.0')
    assert (R/name).read_text(encoding='utf-8')==expected,name
assert (R/'vss_input_priority.dll').read_bytes()==(old/'vss_input_priority.dll').read_bytes()
report=json.loads((R/'package.json').read_text());path=Path(report['file'])
assert hashlib.sha256(path.read_bytes()).hexdigest()==report['sha256']
with zipfile.ZipFile(path) as z:
    assert z.testzip() is None
    assert z.read('Source/network_diagnostic.lua').decode()==(R/'bundled.lua').read_text(encoding='utf-8')
    assert z.read('Source/input/vss_input_priority.dll')==(old/'vss_input_priority.dll').read_bytes()
    assert z.read('Source/experiment/test_aboard_receiver.py')==(R/'test_aboard_receiver.py').read_bytes()
    assert z.read('Source/experiment/test_aboard_adapter.lua')==(R/'test_aboard_adapter.lua').read_bytes()
    assert (P/'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.13.0-说明.txt').read_bytes()==z.read('README_中文.txt')
assert hashlib.sha256((P/'outputs/Vehicle-Specified-Seat-Switch-0.2.4.zip').read_bytes()).hexdigest()=='0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27'
report.update(input_binary_unchanged=True,core_protocol_and_input_unchanged=unchanged,production_024_unchanged=True)
(R/'artifact-review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
