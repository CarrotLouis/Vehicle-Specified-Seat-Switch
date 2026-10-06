from pathlib import Path
import shutil

W=Path(__file__).resolve().parent
source=W/'seat_handoff_motion_test'
target=W/'seat_pose_trace_test'
assert not target.exists(), 'preserve an existing working copy'
target.mkdir()
exclude={'bundled.lua','package.json','artifact-review.json','artifact-verification.json',
         'finalize_package.py','verify_artifact.py'}
for path in source.iterdir():
    if not path.is_file() or path.name in exclude or path.suffix in ('.log','.txt'):
        continue
    dest=target/path.name
    if path.suffix in ('.py','.lua') and path.name!='input_helper.lua':
        text=path.read_text(encoding='utf-8').replace('seat_handoff_motion_test','seat_pose_trace_test')
        text=text.replace('0.23.0','0.24.0')
        dest.write_text(text,encoding='utf-8')
    else:
        shutil.copyfile(path,dest)
print('Created isolated 0.24.0 copy; no old source/ZIP/live game changes')
