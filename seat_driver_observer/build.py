"""Passive observer only. Build inside workspace; never install or launch."""
from pathlib import Path
import hashlib
import json
import os
import struct
import subprocess
import sys
import zipfile

R = Path(__file__).resolve().parent
W, P = R.parent, R.parent.parent
OLD = W / 'seat_pose_trace_test'
RELEASE = '0.25.0'
PACK = P / f'outputs/Vehicle-Seat-Driver-Observer-{RELEASE}.zip'
assert not PACK.exists(), 'preserve published diagnostic'


def run(path, env=None):
    subprocess.run([sys.executable, '-X', 'utf8', str(W / 'run_lua.py'), str(path)],
                   cwd=P, env=env, check=True)


subprocess.run([sys.executable, '-X', 'utf8', str(R / 'prepare.py')], check=True)
from docs import save, manifest
save()
for name in ['test_watch', 'test_context', 'test_pose_trace', 'test_entry']:
    run(R / (name + '.lua'))

# Validate identical frozen contracts and reused readers on both saved builds.
compat_test = (OLD / 'test_compat.lua').read_text(encoding='utf-8')
compat_test = compat_test.replace('work/seat_pose_trace_test/', 'work/seat_driver_observer/')
# Notification inspectors are irrelevant to this passive package; their original
# contract remains validated by the compatibility resolver above.
compat_test = compat_test.replace('work/seat_driver_observer/inspect.lua', 'work/seat_pose_trace_test/inspect.lua')
(R / 'test_compat.lua').write_text(compat_test, encoding='utf-8')
for capture in ['25327279', '25480438']:
    env = dict(os.environ, VSS_CAPTURE=str(W / 'reverse' / ('capture-' + capture)), VSS_TEST_BUILD=capture)
    run(R / 'test_compat.lua', env)
    # Read-only physics/property modules are byte-for-byte identical.
    run(OLD / 'test_physics_reader.lua', env)
    run(OLD / 'test_handoff_reader.lua', env)
run(OLD / 'test_body_flags.lua')

N = W / 'seat_network_diagnostic'
G = W / 'seat_switch/src'
I = W / 'seat_interface_diagnostic'
A = W / 'seat_authority_diagnostic'
PROTO = W / 'seat_protocol_diagnostic'
source = '-- HD2-Addon: mods/vehicle_seat_tools/driver_motion_observer\n'
files = {}


def module(name, path):
    global source
    data = path.read_text(encoding='utf-8')
    source += 'local ' + name + '=(function()\n' + data + '\nend)()\n'
    files['Source/' + name + '.lua'] = data.encode('utf-8')


for name in ['profile', 'compat', 'module_hash']:
    module(name, G / (name + '.lua'))
module('compat_spec', PROTO / 'compat_spec.lua')
module('trace_points', PROTO / 'trace_points.lua')
source += "for _,point in ipairs(trace_points)do profile.functions['trace_'..point.name]={rva=point.rva}end\n"
for name, path in [('routing_spec', I / 'routing_spec.lua'), ('authority_spec', A / 'authority_spec.lua')] + [
    (name, R / (name + '.lua')) for name in ['sync_spec', 'animation_spec', 'binding_spec', 'tank_spec',
                                         'motion_spec', 'handoff_spec', 'spin_spec', 'pose_spec']
]:
    module(name, path)
    source += 'profile,compat_spec=' + name + '(profile,compat_spec)\n'
module('platform', N / 'platform.lua')
module('pages', I / 'pages.lua')
module('sampler', N / 'sampler.lua')
module('recorder', N / 'recorder.lua')
for name in ['physics_reader', 'handoff_reader', 'body_flags_reader', 'motion_helper', 'pose_trace']:
    module(name, R / (name + '.lua'))
module('driver_context', R / 'context.lua')
module('driver_watch', R / 'watch.lua')
source += (R / 'entry.lua').read_text(encoding='utf-8')
for forbidden in ['WriteProcessMemory', 'VirtualProtect', 'SendInput', 'authority_observe.new',
                  'ownership_loan_only(', 'sync_probe.new', 'input_gate(', 'Arrowhead/', '.replace(']:
    assert forbidden not in source, forbidden
assert "version='0.25.0'" in source
(R / 'bundled.lua').write_text(source, encoding='utf-8')
(R / 'check.lua').write_text("assert(loadfile('work/seat_driver_observer/bundled.lua'));print('PASS exact passive bundle syntax')\n", encoding='utf-8')
run(R / 'check.lua')

sys.path.insert(0, str(W / 'BingusSharedLoader/scripts'))
from archive import make_archive, resource_hash, ARCHIVE
resource_name = 'mods/vehicle_seat_tools/driver_motion_observer'
data = source.encode('utf-8')
payload = make_archive({resource_hash(resource_name): struct.pack('<II', len(data), 2) + data})
files.update({
    'manifest.json': json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf-8'),
    'Diagnostic/' + ARCHIVE: payload,
    'Diagnostic/' + ARCHIVE + '.stream': b'',
    'Diagnostic/' + ARCHIVE + '.gpu_resources': b'',
    'Source/driver_observer.lua': data,
})
for name in ['README_中文.txt', 'README_English.txt']:
    files[name] = (R / name).read_bytes()
for path in R.iterdir():
    if path.is_file() and path.suffix in ('.lua', '.py', '.json') and path.name not in (
        'bundled.lua', 'package.json', 'artifact-verification.json', 'check.lua'):
        files['Source/experiment/' + path.name] = path.read_bytes()
for name in ['motion_native.c', 'motion_bridge.S', 'test_motion_native.c', 'build_motion_native.py',
             'motion-native-build.json', 'vss_motion_trace.dll']:
    files['Source/motion/' + name] = (OLD / name).read_bytes()
assert hashlib.sha256(files['Source/motion/vss_motion_trace.dll']).hexdigest() == '72f9102952776c995cbd82f9fe9524a45271658a17f11bd32856f403b5611aec'
with zipfile.ZipFile(PACK, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, content in files.items():
        z.writestr(name, content)
with zipfile.ZipFile(PACK) as z:
    assert z.testzip() is None
    assert z.read('Source/driver_observer.lua') == data
report = dict(file=str(PACK), sha256=hashlib.sha256(PACK.read_bytes()).hexdigest(), bytes=PACK.stat().st_size,
              helper_sha256='72f9102952776c995cbd82f9fe9524a45271658a17f11bd32856f403b5611aec',
              resource=resource_name, installer_package='Vehicle-Seat-Weapon-Sync-Diagnostic-0.24.0.zip',
              installer_unchanged=True, live_validation='PENDING')
(R / 'package.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
(P / f'outputs/Vehicle-Seat-Driver-Observer-{RELEASE}-说明.txt').write_bytes((R / 'README_中文.txt').read_bytes())
print(json.dumps(report, indent=2))
