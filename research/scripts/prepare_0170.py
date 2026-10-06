from pathlib import Path
import json
W=Path(__file__).resolve().parent;old=W/'seat_seated_owner_test';out=W/'seat_outside_owner_test'
accepted=json.loads((old/'capture-20261001-0160/analysis.json').read_text(encoding='utf-8'))
assert accepted['accepted']and len(accepted['runs'])==2
assert not out.exists();out.mkdir()
for p in old.iterdir():
 if p.is_file()and p.suffix in('.lua','.py','.txt','.c')and p.name not in('bundled.lua','check.lua','input_helper.lua','docs_seated.py'):
  (out/p.name).write_text(p.read_text(encoding='utf-8').replace('seat_seated_owner_test','seat_outside_owner_test').replace('0.16.0','0.17.0'),encoding='utf-8')
for name in('input_native.c','vss_input_priority.dll','input_helper.lua'):(out/name).write_bytes((old/name).read_bytes())
print('Accepted0.16.0 both roles, all ownership paths; isolated0.17.0 outside-original-owner source created')
