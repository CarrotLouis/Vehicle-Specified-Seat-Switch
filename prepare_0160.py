from pathlib import Path
import json
W=Path(__file__).resolve().parent;old=W/'seat_driver_acquire_test';out=W/'seat_seated_owner_test'
accepted=json.loads((old/'capture-20261001-0150/analysis.json').read_text(encoding='utf-8'))
assert accepted['no_retest_required']and len(accepted['accepted'])==2
assert not out.exists();out.mkdir()
for p in old.iterdir():
 if p.is_file()and p.suffix in('.lua','.py','.txt','.c')and p.name not in('bundled.lua','check.lua','input_helper.lua','docs_driver.py'):
  (out/p.name).write_text(p.read_text(encoding='utf-8').replace('seat_driver_acquire_test','seat_seated_owner_test').replace('0.15.0','0.16.0'),encoding='utf-8')
for name in('input_native.c','vss_input_priority.dll'):(out/name).write_bytes((old/name).read_bytes())
print('Accepted0.15.0 both real acquisitions; isolated0.16.0 seated-original-owner source created')
