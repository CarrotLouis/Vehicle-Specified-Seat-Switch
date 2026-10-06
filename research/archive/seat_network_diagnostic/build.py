"""Build the read-only multiplayer state recorder, never a multiplayer switcher."""
from pathlib import Path
import hashlib, json, os, struct, subprocess, sys, zipfile
ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent
PROJECT = WORK.parent
sys.path.insert(0, str(WORK / 'BingusSharedLoader/scripts'))
from archive import make_archive, resource_hash, ARCHIVE

def wrapped(name, path):
    return f'local {name}=(function()\n{path.read_text(encoding="utf-8")}\nend)()\n'

for test in ['test_sampler.lua', 'test_recorder.lua', 'test_entry.lua']:
    subprocess.run([sys.executable, str(WORK / 'run_lua.py'), str(ROOT / test)], cwd=PROJECT, check=True)
for order in ['diagnostic-first', 'gameplay-first']:
    env = dict(os.environ, VSS_TEST_ORDER=order)
    env.pop('VSS_EXPECT_OLD_CONFLICT', None)
    subprocess.run([sys.executable, str(WORK / 'run_lua.py'), str(ROOT / 'test_platform_coexistence.lua')], cwd=PROJECT, env=env, check=True)
name = 'mods/vehicle_seat_tools/network_diagnostic'
source = '-- HD2-Addon: ' + name + '\n'
for module in ['profile', 'compat_spec', 'compat', 'module_hash', 'input']:
    source += wrapped(module, WORK / 'seat_switch/src' / (module + '.lua'))
config = (WORK / 'seat_switch/src/config.lua').read_text(encoding='utf-8').split('function M.template()', 1)[0]
assert config.endswith('end\n')
source += 'local config=(function()\n' + config + 'return M\nend)()\n'
for module in ['platform', 'sampler', 'recorder']:
    source += wrapped(module, ROOT / (module + '.lua'))
source += (ROOT / 'entry.lua').read_text(encoding='utf-8')
for banned in ['WriteProcessMemory', 'VirtualProtect', 'SendInput', 'CreateRemoteThread', 'ffi.cast("void (*', "ffi.cast('void (*"]:
    assert banned not in source, banned
assert 'function M.load(' not in source and 'restore_seated(' not in source
(ROOT / 'bundled.lua').write_text(source, encoding='utf-8')
syntax = ROOT / 'check_bundled.lua'
syntax.write_text('assert(loadfile("work/seat_network_diagnostic/bundled.lua")); print("PASS bundled syntax")\n', encoding='utf-8')
subprocess.run([sys.executable, str(WORK / 'run_lua.py'), str(syntax)], cwd=PROJECT, check=True)
data = source.encode('utf-8')
payload = make_archive({resource_hash(name): struct.pack('<II', len(data), 2) + data})
manifest = {'Version': 1, 'Guid': '649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name': 'Vehicle Seat Network Diagnostic / 载具换座联机只读诊断',
 'Description': '0.1.2｜修复与普通版/加强版共存时的光标接口类型冲突。双人联机状态诊断：记录座位过渡、占位掩码与本机控制权。仅需使用者安装。不启用跨区域换座。改用接口特征校验，已核对 build 25327279 / 25480438 样本；需 Loader v16。\n\n0.1.2 | Fixes the shared cursor-API type conflict with Normal/Enhanced. Read-only multiplayer seat/ownership recorder. Install on the observing player only. Does not enable cross-group switching. Uses interface evidence instead of a strict file-hash gate; checked against captures from builds 25327279 and 25480438. Requires Loader v16.',
 'Options': [{'Name': '只读联机诊断 / Read-only network diagnostic',
 'Description': '与正式换座模组普通版一起启用；旧版静态诊断包保持禁用。自动生成独立日志，每次启动保留一份。\n\nUse alongside the Normal seat-switch variant. Keep the old static diagnostic disabled. Each launch creates a separate log.',
 'Include': ['Diagnostic']}]}
files = {'manifest.json': json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf-8'),
 'Diagnostic/' + ARCHIVE: payload, 'Diagnostic/' + ARCHIVE + '.stream': b'', 'Diagnostic/' + ARCHIVE + '.gpu_resources': b'',
 'Source/network_diagnostic.lua': data,
 'README_双人诊断步骤.txt': (ROOT / 'README_双人诊断步骤.txt').read_bytes(),
 'README_English.txt': (ROOT / 'README_English.txt').read_bytes()}
dest = PROJECT / 'outputs/Vehicle-Seat-Network-Diagnostic-0.1.2.zip'
with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
    for n, body in files.items(): z.writestr(n, body)
with zipfile.ZipFile(dest) as z:
    assert z.testzip() is None
    assert z.read('Source/network_diagnostic.lua') == data
print(json.dumps({'file': str(dest), 'bytes': dest.stat().st_size, 'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()}, indent=2))
