from pathlib import Path
import shutil

W=Path(__file__).resolve().parent
old=W/'seat_tank_pose_fix'; R=W/'seat_multi_peer_diagnostic'
assert not R.exists(), 'Do not replace an existing experiment'
R.mkdir()
for p in old.iterdir():
    if not p.is_file() or p.name in {'build-verified.log','artifact-review.json','package.json'}:
        continue
    target=R/p.name
    if p.name.startswith('regression_'):
        shutil.copy2(p,target)
    elif p.suffix in {'.lua','.py','.json','.txt','.md','.c','.h','.S'}:
        target.write_text(p.read_text(encoding='utf-8').replace('seat_tank_pose_fix','seat_multi_peer_diagnostic').replace('0.18.3','0.19.0'),encoding='utf-8')
    else:
        shutil.copy2(p,target)
print('Created isolated 0.19.0 observer workspace; 0.18.3 and production preserved')
