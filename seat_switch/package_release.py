"""Repackage the verified 0.2.3 payload with release documentation only."""
from pathlib import Path
import hashlib, json, zipfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent.parent / 'outputs'
KIT = OUT / 'Vehicle-Specified-Seat-Switch-0.2.3-Publishing'
KIT.mkdir(exist_ok=True)
original = OUT / 'Vehicle-Specified-Seat-Switch-0.2.3-test.zip'
with zipfile.ZipFile(original) as z:
    files = {n: z.read(n) for n in z.namelist()}

manifest = json.loads(files['manifest.json'])
manifest['Name'] = 'Vehicle Specified Seat Switch / 载具换座'
manifest['Description'] = (
    '0.2.3｜车内快捷换座，支持三型 FRV、Bastion、Maelstrom 和任务油罐车。'
    '支持自定义键盘、鼠标与组合键；不切换到已占用座位。依赖 Bingus Shared Loader v16。'
    '普通版支持单人/联机；加强版跨区域换座仅在单人模式生效。详细按键见 ZIP 内指南。\n\n'
    '0.2.3 | Switch seats without leaving your vehicle. Supports three FRVs, Bastion, Maelstrom and the mission fuel tanker. '
    'Custom keyboard, mouse and modifier bindings; occupied seats are excluded. Requires Bingus Shared Loader v16. '
    'Normal supports solo and multiplayer; Enhanced cross-group switching works ONLY in solo play. See the key guides in the ZIP.'
)
option = manifest['Options'][0]
option['Name'] = '选择版本 / Select variant'
option['Description'] = '选择一个版本，默认普通版。更换版本后重新部署并重启游戏。 / Choose one variant. Normal is the default. Redeploy and restart after changing variants.'
option['SubOptions'][0].update(
    Name='普通版 / Normal',
    Description='单人及联机可用。M-102/M-103 前排与后排各自组内换座；M-104 前排换座；两型坦克炮位与左右乘员位互换；油罐车驾驶位与炮位互换。\n\nSolo and multiplayer. M-102/M-103: switch within the front pair or rear pair. M-104: front pair only. Both tanks: gunner and passenger group. Fuel tanker: driver and gunner.'
)
option['SubOptions'][1].update(
    Name='加强版 / Enhanced',
    Description='加强功能仅在单人模式生效：增加驾驶、乘员和武器位之间的车内跨区域换座，需载具由本机控制。联机时仅保留普通版范围。已知问题：坦克按住转向时离开驾驶位可能持续自旋；建议先松开转向，发生后重回驾驶位操控。\n\nEnhanced cross-group switching works ONLY in solo play, with a locally controlled vehicle. Switch between driver, passenger and weapon stations without exiting. Multiplayer retains Normal restrictions. Known issue: leaving a tank driver seat while steering may leave steering active. Release steering first; re-enter and operate the driver seat if it occurs.'
)
files['manifest.json'] = json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf-8')
files.pop('README_使用与测试.txt', None)
for name in ['README_中文.txt', 'README_English.txt', 'KEYS_English.txt']:
    files[name] = (ROOT / 'release_docs' / name).read_bytes()
files['KEYS_按键清单.txt'] = (ROOT / 'KEYS_按键清单.txt').read_text(encoding='utf-8').replace('0.2.3-test', '0.2.3').encode('utf-8')
files['Source/NOTICE.txt'] = files['Source/NOTICE.txt'].replace(b'0.2.3-test', b'0.2.3')
dest = OUT / 'Vehicle-Specified-Seat-Switch-0.2.3.zip'
with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, data in files.items():
        z.writestr(name, data)
with zipfile.ZipFile(original) as old, zipfile.ZipFile(dest) as new:
    assert new.testzip() is None
    unchanged = [n for n in old.namelist() if n.startswith(('Normal/', 'Enhanced/', 'Source/')) and n != 'Source/NOTICE.txt']
    for name in unchanged:
        assert new.read(name) == old.read(name), name
    for v in [manifest['Name'], manifest['Description'], option['Description']] + [s['Name'] + s['Description'] for s in option['SubOptions']]:
        assert '测试' not in v and '-test' not in v
report = {'package': dest.name, 'sha256': hashlib.sha256(dest.read_bytes()).hexdigest(), 'byte_identical_gameplay_and_ini_files': unchanged, 'changes': 'Manifest and release documentation only; no gameplay or existing INI edits.'}
(KIT / 'Package-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
