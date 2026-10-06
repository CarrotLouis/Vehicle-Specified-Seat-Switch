from pathlib import Path
import shutil

W=Path(__file__).resolve().parent
old=W/'seat_tank_binding_fix'; R=W/'seat_tank_pose_fix'
assert not R.exists(), 'Do not replace existing experiment'
R.mkdir()
for p in old.iterdir():
    if not p.is_file() or p.name in {'build-verified.log','artifact-review.json','package.json'}: continue
    target=R/p.name
    if p.name.startswith('regression_'):
        shutil.copy2(p,target)
    elif p.suffix in {'.lua','.py','.json','.txt','.md','.c','.h','.S'}:
        target.write_text(p.read_text(encoding='utf-8').replace('seat_tank_binding_fix','seat_tank_pose_fix').replace('0.18.2','0.18.3'),encoding='utf-8')
    else: shutil.copy2(p,target)
for name in ['animation_sender','adapter','dispatcher','transaction']:
    shutil.copy2(old/(name+'.lua'),R/('regression_0182_'+name+'.lua'))
shutil.copy2(W/'seat_switch/src/pose.lua',R/'pose.lua')
shutil.copy2(W/'seat_switch/src/pose.lua',R/'regression_0182_pose.lua')
print('Created isolated 0.18.3 workspace; prior artifacts and production unchanged')
