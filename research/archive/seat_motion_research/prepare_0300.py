"""Fork accepted 0.29 without changing prior sources, packages or installs."""
from pathlib import Path
import shutil
W=Path(__file__).resolve().parent.parent;A=W/'seat_tank_exit_refinement_test';R=W/'seat_multiplayer_reservation_test'
assert not R.exists();R.mkdir()
skip={'package.json','tests-passed.json','artifact-verification.json','bundled.lua','entry.lua','assembly-origins.json'}
for f in A.iterdir():
 if not f.is_file()or f.name in skip:continue
 if f.suffix in('.lua','.py','.c','.S','.h','.dll','.exe','.json'):
  out=R/f.name
  if f.suffix in('.lua','.py','.c','.S','.h'):
   s=f.read_text().replace('seat_tank_exit_refinement_test','seat_multiplayer_reservation_test').replace('0.29.0','0.30.0')
   out.write_bytes(s.encode())
  else:shutil.copyfile(f,out)
(R/'adapter.lua').write_bytes((W/'seat_pose_trace_test/adapter.lua').read_bytes())
print('Created separate 0.30 sources, unchanged prior packages and native ABI4 helper')
