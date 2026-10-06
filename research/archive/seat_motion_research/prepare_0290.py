"""Fork immutable 0.28 source into a separate, reviewable refinement package."""
from pathlib import Path
import shutil
W=Path(__file__).resolve().parent.parent;A=W/'seat_reservation_fleet_test';R=W/'seat_tank_exit_refinement_test'
assert not R.exists(),'new experiment must not overwrite old work'
R.mkdir()
skip={'package.json','tests-passed.json','artifact-verification.json','bundled.lua','entry.lua','assembly-origins.json'}
for f in A.iterdir():
 if not f.is_file() or f.name in skip:continue
 if f.suffix in ('.lua','.py','.json','.c','.S','.h','.dll','.exe'):
  dest=R/f.name
  if f.suffix in ('.lua','.py','.S','.c','.h'):
   s=f.read_text(encoding='utf-8').replace('seat_reservation_fleet_test','seat_tank_exit_refinement_test').replace('0.28.0','0.29.0')
   dest.write_bytes(s.encode('utf-8'))
  else:shutil.copyfile(f,dest)
for name in ['spin_reader','binding_inspect']:
 (R/(name+'.lua')).write_bytes((W/'seat_pose_trace_test'/(name+'.lua')).read_bytes())
print('Created isolated 0.29 sources; old source, archives, native DLL and live installation unchanged')
