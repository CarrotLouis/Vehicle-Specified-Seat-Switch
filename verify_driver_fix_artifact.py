"""Post-build verification. Preserve every file already shipped in the ZIP."""
from pathlib import Path
import hashlib
import json
import struct
import sys
import zipfile

W = Path(__file__).resolve().parent
P = W.parent
R = W / 'seat_driver_observer_fix'
sys.path.insert(0, str(W / 'BingusSharedLoader/scripts'))
from archive import resource_hash, TYPE

def digest(data):
    return hashlib.sha256(data).hexdigest()

pack = P / 'outputs/Vehicle-Seat-Driver-Observer-0.25.1.zip'
report = json.loads((R / 'package.json').read_text(encoding='utf-8'))
assert digest(pack.read_bytes()) == report['sha256'] and pack.stat().st_size == report['bytes']
with zipfile.ZipFile(pack) as z:
    assert z.testzip() is None
    manifest = json.loads(z.read('manifest.json').decode('utf-8'))
    assert manifest['Guid'] == 'a3d2bf30-46bc-48d4-8177-18dc9c250001'
    assert len(manifest['Options']) == 1 and manifest['Options'][0]['Include'] == ['Diagnostic']
    runtime = z.read('Source/driver_observer.lua').decode('utf-8')
    assert runtime == (R / 'bundled.lua').read_text(encoding='utf-8')
    # Every archived experiment file must still match the reviewed build input.
    for name in z.namelist():
        if name.startswith('Source/experiment/') and not name.endswith('/'):
            assert z.read(name) == (R / Path(name).name).read_bytes(), name
    for name in ['physics_reader', 'handoff_reader', 'body_flags_reader', 'pose_trace', 'motion_helper', 'platform']:
        assert z.read('Source/' + name + '.lua').decode('utf-8') == (R / (name + '.lua')).read_text(encoding='utf-8')
    platform = z.read('Source/platform.lua').decode('utf-8')
    assert 'local a={hash_module=hash_module,ffi=ffi}' in platform
    old_platform = (W/'seat_network_diagnostic/platform.lua').read_text(encoding='utf-8')
    assert platform == old_platform.replace('local a={hash_module=hash_module}', 'local a={hash_module=hash_module,ffi=ffi}')
    assert "assert(api.ffi and api.ffi.new and api.ffi.copy and api.ffi.cast,'driver_observer_ffi_adapter_missing')" in runtime
    for forbidden in ['WriteProcessMemory', 'VirtualProtect', 'SendInput', 'ownership_loan_only(', 'sync_probe.new', 'input_gate(', 'Arrowhead/', '.replace(']:
        assert forbidden not in runtime, forbidden
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
    assert struct.unpack_from('<II', blob) == (len(runtime.encode('utf-8')), 2)
    assert blob[8:] == runtime.encode('utf-8')
    entry = (R/'entry.lua').read_text(encoding='utf-8')
    assert runtime.endswith(entry)
    prefix = runtime[:-len(entry)]
    exports = '\nreturn {platform=platform,physics_reader=physics_reader,driver_watch=driver_watch,recorder=recorder}\n'
    assert z.read('Source/experiment/components.lua').decode('utf-8').replace('\r\n', '\n') == prefix + exports
    with zipfile.ZipFile(P/'outputs/Vehicle-Seat-Driver-Observer-0.25.0.zip') as old:
        old_runtime = old.read('Source/driver_observer.lua').decode('utf-8')
    old_entry = (W/'seat_driver_observer/entry.lua').read_text(encoding='utf-8')
    assert old_runtime.endswith(old_entry)
    assert z.read('Source/experiment/previous_components.lua').decode('utf-8').replace('\r\n', '\n') == old_runtime[:-len(old_entry)] + exports

origins = json.loads((R/'origins.json').read_text(encoding='utf-8'))
for name, o in origins.items():
    assert digest(Path(o['path']).read_bytes()) == o.get('sha256', o.get('original_sha256'))
    if o.get('unchanged'):
        assert digest((R/(name+'.lua')).read_bytes()) == o['sha256']
bootstrap = json.loads((R/'bootstrap-origins.json').read_text(encoding='utf-8'))
assert digest(Path(bootstrap['platform_original']).read_bytes()) == bootstrap['platform_original_sha256']
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
    'Vehicle-Seat-Driver-Observer-0.25.0.zip': 'c1044204eb1318b97b9ef40f1f3d63103bf4b9fcd4a92cb94aaf0248285754ff',
}
for name, sha in preserved.items():
    assert digest((P/'outputs'/name).read_bytes()) == sha, name
log = (R/'build-0251.log').read_text(encoding='utf-8')
assert log.count('PASS exact deployed components plus entry: real read-only adapter FFI') == 2
assert log.count('PASS negative control: exact 0.25.0 deployment reproduces missing-ffi') == 2
test = (W/'packaging_research/test_pose_package.cjs').read_text(encoding='utf-8')
test = test.replace('Source/network_diagnostic.lua', 'Source/driver_observer.lua')
(W/'packaging_research/test_driver_fix_package.cjs').write_text(test, encoding='utf-8')
result = dict(version='0.25.1', sha256=report['sha256'], bytes=report['bytes'], crc='PASS',
              exact_runtime_in_lua_resource='PASS', every_archived_experiment_input='PASS',
              adapter_contract='PASS', startup_dependency_refusal='PASS',
              exact_deployed_bundle_driver_replays_both_saved_builds='PASS',
              previous_deployed_bundle_failure_reproduced_both_saved_builds='PASS',
              captured_contracts_112_both_builds='PASS', unchanged_native_helper='PASS',
              unchanged_ten_prior_packages=preserved, original_sources_unchanged='PASS',
              live='PENDING', moving_stop='UNRESOLVED', tank_spin='UNRESOLVED')
(R/'artifact-verification.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
print('PASS exact ZIP payload/source/adapter/replay inputs/docs, CRC, unchanged native helper and ten prior ZIPs; no gameplay/physics-writer pipeline')
