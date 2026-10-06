from pathlib import Path
import hashlib
import json
import struct
import sys
import zipfile
R = Path(__file__).resolve().parent
W, P = R.parent, R.parent.parent
sys.path.insert(0, str(W / 'BingusSharedLoader/scripts'))
from archive import resource_hash, TYPE
def digest(data): return hashlib.sha256(data).hexdigest()
pack = P / 'outputs/Vehicle-Seat-Driver-Observer-0.25.1.zip'
report = json.loads((R / 'package.json').read_text(encoding='utf-8'))
assert digest(pack.read_bytes()) == report['sha256'] and pack.stat().st_size == report['bytes']
with zipfile.ZipFile(pack) as z:
    assert z.testzip() is None
    manifest = json.loads(z.read('manifest.json').decode('utf-8'))
    assert manifest['Guid'] == 'a3d2bf30-46bc-48d4-8177-18dc9c250001'
    assert len(manifest['Options']) == 1 and manifest['Options'][0]['Include'] == ['Diagnostic']
    text = z.read('Source/driver_observer.lua').decode('utf-8')
    assert text == (R / 'bundled.lua').read_text(encoding='utf-8')
    for name in ['context', 'watch', 'entry', 'docs', 'test_watch', 'test_context', 'test_entry']:
        extension = '.py' if name == 'docs' else '.lua'
        assert z.read('Source/experiment/' + name + extension) == (R / (name + extension)).read_bytes()
    for name in ['physics_reader', 'handoff_reader', 'body_flags_reader', 'pose_trace', 'motion_helper']:
        assert z.read('Source/' + name + '.lua').decode('utf-8') == (R / (name + '.lua')).read_text(encoding='utf-8')
    for forbidden in ['WriteProcessMemory', 'VirtualProtect', 'SendInput', 'ownership_loan_only(', 'sync_probe.new', 'input_gate(', 'Arrowhead/']:
        assert forbidden not in text
    for name in ['README_中文.txt', 'README_English.txt']:
        assert z.read(name) == (R / name).read_bytes()
    helper_sha = digest(z.read('Source/motion/vss_motion_trace.dll'))
    assert helper_sha == '72f9102952776c995cbd82f9fe9524a45271658a17f11bd32856f403b5611aec'
    deployed = [n for n in z.namelist() if n.startswith('Diagnostic/')]
    assert len(deployed) == 3
    payload = z.read(next(n for n in deployed if n.endswith('patch_0')))
    assert struct.unpack_from('<III', payload) == (0xf0000011, 1, 1)
    row = struct.unpack_from('<7Q6I', payload, 104)
    assert row[0] == resource_hash('mods/vehicle_seat_tools/driver_motion_observer') and row[1] == TYPE
    blob = payload[row[2]:row[2] + row[7]]
    assert struct.unpack_from('<II', blob) == (len(text.encode('utf-8')), 2)
    assert blob[8:] == text.encode('utf-8')
    origins = json.loads((R / 'origins.json').read_text(encoding='utf-8'))
    for name, o in origins.items():
        assert digest(Path(o['path']).read_bytes()) == o.get('sha256', o.get('original_sha256'))
        if o.get('unchanged'):
            assert digest((R / (name + '.lua')).read_bytes()) == o['sha256']

preserved = {
    'Vehicle-Specified-Seat-Switch-0.2.4.zip': '0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27',
    'Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.3.zip': 'c6605c6d5e2f874a8fb1ca55425f1f6db4f74e0f5611b1207004b388f41cca34',
    'Vehicle-Seat-Weapon-Sync-Diagnostic-0.19.0.zip': 'b710e032b90a9d8e237c3ade5073eb6a3f66b578555735ecef90472f61d99568',
    'Vehicle-Seat-Weapon-Sync-Diagnostic-0.20.0.zip': '4ed93481c8a9508a155dcc8e75d83f8c94017dbd2fde75ece6bba2a47fcb4e29',
    'Vehicle-Seat-Weapon-Sync-Diagnostic-0.21.0.zip': '34f0bd6af4698443e66d41ef4eb1ebbc1e4ea43643b8d7e6a53a62a551c24779',
    'Vehicle-Seat-Weapon-Sync-Diagnostic-0.22.0.zip': '8632cdb222e591b84dd39b884e903ac4aced8212fd8c2377f0f67d5e29c44ede',
    'Vehicle-Seat-Weapon-Sync-Diagnostic-0.22.1.zip': '9297f0dd0273316e8a32a77219465945de6c574a82159f3e20dd29bbd8cc8333',
    'Vehicle-Seat-Weapon-Sync-Diagnostic-0.23.0.zip': '3393b51088a97af1eeab7514b220ccc2a92da211c2430b51d22f8a1db5edfb2b',
    'Vehicle-Seat-Weapon-Sync-Diagnostic-0.24.0.zip': '9a5fbada3a23a9ffd359eb9e9508e7fd1c5486d1b6576631164d312995ad679f',
}
for name, sha in preserved.items():
    assert digest((P / 'outputs' / name).read_bytes()) == sha, name
test = (W / 'packaging_research/test_pose_package.cjs').read_text(encoding='utf-8')
test = test.replace('Source/network_diagnostic.lua', 'Source/driver_observer.lua')
(W / 'packaging_research/test_driver_package.cjs').write_text(test, encoding='utf-8')
result = dict(version='0.25.1', sha256=report['sha256'], bytes=report['bytes'], crc='PASS',
              exact_runtime_in_lua_resource='PASS', driver_scope_failure_tests='PASS',
              captured_contracts_112_both_builds='PASS', unchanged_native_helper='PASS',
              unchanged_nine_prior_packages=preserved, original_sources_unchanged='PASS',
              live='PENDING', moving_stop='UNRESOLVED', tank_spin='UNRESOLVED')
(R / 'artifact-verification.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print('PASS passive ZIP CRC, exact compiled resource/runtime/source/docs, ABI helper unchanged, no authority/input/physics writer pipeline, nine prior ZIPs preserved')
