"""Isolated patch; keep every prior source and published package intact."""
from pathlib import Path
import shutil

W = Path(__file__).resolve().parent
old = W / 'seat_physics_motion_test'
new = W / 'seat_physics_layout_fix'
assert not new.exists(), 'Do not overwrite a prepared patch'
new.mkdir()
for source in old.iterdir():
    if not source.is_file():
        continue
    dest = new / source.name
    if source.suffix in ('.lua', '.py', '.md', '.txt', '.json'):
        try:
            text = source.read_text(encoding='utf-8')
        except UnicodeError:
            shutil.copy2(source, dest)
            continue
        dest.write_text(text.replace('seat_physics_motion_test', 'seat_physics_layout_fix'), encoding='utf-8')
    else:
        shutil.copy2(source, dest)
for name in ('entry.lua', 'transport.lua', 'build.py', 'verify_artifact.py'):
    path = new / name
    path.write_text(path.read_text(encoding='utf-8').replace('0.22.0', '0.22.1'), encoding='utf-8')
path = new / 'verify_artifact.py'
text = path.read_text(encoding='utf-8').replace('7fa93305-310a-4d14-9e55-c3020199a706', '469fa4d6-71c6-43e7-8984-ed3e2ecde68d')
text = text.replace("preserved={", "preserved={\n 'Vehicle-Seat-Weapon-Sync-Diagnostic-0.22.0.zip':'8632cdb222e591b84dd39b884e903ac4aced8212fd8c2377f0f67d5e29c44ede',")
text = text.replace("'four_prior_packages_unchanged'", "'six_prior_packages_unchanged'")
path.write_text(text, encoding='utf-8')
print('Prepared isolated 0.22.1 source; previous files unchanged')
