"""Verify the final 0.27.0 archive, frozen evidence and isolated Arsenal result."""
from pathlib import Path
import ast
import hashlib
import json
import struct
import sys
import zipfile

W = Path(__file__).resolve().parent
P = W.parent
R = W / 'seat_reservation_frv_test'
sys.path.insert(0, str(W / 'BingusSharedLoader/scripts'))
from archive import resource_hash, TYPE


def sha(data):
    return hashlib.sha256(data).hexdigest()


report = json.loads((R / 'package.json').read_text())
pack = Path(report['file'])
assert pack.stat().st_size == report['bytes']
assert sha(pack.read_bytes()) == report['sha256']
passed = json.loads((R / 'tests-passed.json').read_text())
native = json.loads((R / 'native-build.json').read_text())
with zipfile.ZipFile(pack) as z:
    assert z.testzip() is None
    manifest = json.loads(z.read('manifest.json'))
    assert manifest['Guid'] == 'fd87d6b4-bd61-4ebd-b0f7-36ef885cc027'
    assert len(manifest['Options']) == 1
    assert manifest['Options'][0]['Include'] == ['Diagnostic']
    runtime = z.read('Source/network_diagnostic.lua')
    assert runtime == (R / 'bundled.lua').read_bytes()
    assert b'\r' not in runtime
    assert sha(runtime) == passed['bundled_sha256'] == report['runtime_sha256']
    assert runtime.endswith(z.read('Source/entry.lua'))
    for name in z.namelist():
        if name.startswith('Source/experiment/') and not name.endswith('/'):
            assert z.read(name) == (R / Path(name).name).read_bytes(), name
    for name, origin in json.loads(z.read('Source/origins.json')).items():
        actual = (P / origin['path']).read_text(encoding='utf-8').encode()
        assert sha(actual) == origin['sha256'], name
        assert z.read('Source/' + name + '.lua') == actual, name
    for name in ['scope', 'entrance', 'probe', 'motion_watch', 'mounted_reader']:
        assert z.read('Source/reservation_' + name + '.lua') == (R / (name + '.lua')).read_text().encode()
    for name in ['physics_reader', 'handoff_reader']:
        assert z.read('Source/' + name + '.lua') == (W / 'seat_pose_trace_test' / (name + '.lua')).read_text().encode()
    for name in ['README_中文.txt', 'README_English.txt']:
        assert z.read(name) == (R / name).read_bytes()
    assert (P / 'outputs/Vehicle-Seat-Reservation-FRV-Test-0.27.0-说明.txt').read_bytes() == z.read('README_中文.txt')
    dll = z.read('Source/experiment/vss_transport.dll')
    assert len(dll) == native['bytes']
    assert sha(dll) == native['sha256'] == report['helper_sha256'] == passed['native_sha256']
    helper = z.read('Source/helper.lua').decode()
    assert dll.hex() in helper and sha(dll) in helper
    for name in ['input_native.c', 'test_input_native.c', 'test_input_thread.c',
                 'build_input_native.py', 'input-native-build.json', 'vss_input_priority.dll']:
        assert z.read('Source/input/' + name) == (W / 'seat_pose_trace_test' / name).read_bytes(), name
    deployed = [name for name in z.namelist() if name.startswith('Diagnostic/')]
    assert len(deployed) == 3
    payload = z.read(next(name for name in deployed if name.endswith('patch_0')))
    assert struct.unpack_from('<III', payload) == (0xf0000011, 1, 1)
    row = struct.unpack_from('<7Q6I', payload, 104)
    assert row[0] == resource_hash('mods/vehicle_seat_tools/network_diagnostic')
    assert row[1] == TYPE
    blob = payload[row[2]:row[2] + row[7]]
    assert struct.unpack_from('<II', blob) == (len(runtime), 2)
    assert blob[8:] == runtime
    assert all(z.read(name) == b'' for name in deployed if name != next(n for n in deployed if n.endswith('patch_0')))
    assert b"io.open(base..'/Arrowhead/Helldivers2/VehicleSeatSwitch.ini','rb')" in runtime
    assert b'function M.load(' not in runtime and b'function M.template(' not in runtime
    entry = z.read('Source/entry.lua')
    assert b'ownership_loan_only(' not in entry
    assert b'probe=reservation_tools.probe.new(' in entry
    assert b"physical_motion_scope='m102_only'" in entry
    assert b'VSST_version()==3' in runtime
    own = z.read('Source/transaction.lua')
    for forbidden in [b"bind('reserve'", b"bind('release'", b"bind('authority", b'.owned=true']:
        assert forbidden not in own, forbidden

tree = ast.parse((W / 'verify_driver_fix_artifact.py').read_text())
preserved = next(ast.literal_eval(node.value) for node in tree.body
                 if isinstance(node, ast.Assign) and any(
                     isinstance(target, ast.Name) and target.id == 'preserved'
                     for target in node.targets))
preserved['Vehicle-Seat-Driver-Observer-0.25.1.zip'] = 'd48066f2c973f95d425f1ed3e1b351cff308bec5ca456a3bf2cdb666a727a285'
preserved['Vehicle-Seat-Reservation-Test-0.26.0.zip'] = 'eef42991a0f813fd5c4b3654b9a836933b57fa7fbffee0d925d4e4effe0d091c'
assert len(preserved) == 12
for name, digest in preserved.items():
    assert sha((P / 'outputs' / name).read_bytes()) == digest, name

frozen = {}
for capture in ['capture-20261004-0251-paired', 'capture-20261005-0260']:
    directory = W / 'seat_motion_research' / capture
    entries = json.loads((directory / 'files.json').read_text())
    for entry in entries:
        data = (directory / entry.get('stored', entry['name'])).read_bytes()
        assert len(data) == entry['bytes'] and sha(data) == entry['sha256'], entry['name']
    frozen[capture] = len(entries)

manager = Path(sys.argv[1]).resolve()
assert manager.is_relative_to(W / 'packaging_research')
check = json.loads(manager.read_text())
assert check['sha256'] == report['sha256'] and check['files'] == 3
assert check['payload_hashes_preserved'] and check['bilingual'] and check['purge_empty']
assert not check['live_profile_changed'] and not check['game_launched']
result = {'version': '0.27.0', **report, 'crc': 'PASS', 'exact_lua_resource': 'PASS',
          'every_archived_source': 'PASS', 'two_captured_builds_121_contracts': 'PASS',
          'native_abi3_and_grant_gate': 'PASS', 'twelve_previous_archives_unchanged': preserved,
          'frozen_files_unchanged': frozen, 'arsenal_fixture': str(manager),
          'arsenal_import_deploy_bilingual_purge': 'PASS', 'live_profile_changed': False,
          'game_launched': False, 'tank_spin': 'UNRESOLVED',
          'new_driver_tank_tanker_3_4_routes': 'EXCLUDED', 'expanded_frv_live_validation': 'PENDING'}
(R / 'artifact-verification.json').write_text(json.dumps(result, indent=2))
print('PASS exact archive/source/runtime/DLL/CRC; 12 preserved ZIPs; 11 frozen files; isolated Arsenal import/deploy/purge')
