from pathlib import Path
import json
W = Path(__file__).resolve().parent
old = W/'seat_outside_owner_test'
out = W/'seat_multi_vehicle_test'
accepted = json.loads((old/'capture-20261002-0170/analysis.json').read_text(encoding='utf-8'))
assert accepted['accepted'] and len(accepted['runs']) == 2
assert not out.exists()
out.mkdir()
for p in old.iterdir():
    if p.is_file() and p.suffix in ('.lua','.py','.txt','.c') and p.name not in ('bundled.lua','check.lua','input_helper.lua','docs_outside.py'):
        (out/p.name).write_text(p.read_text(encoding='utf-8').replace('seat_outside_owner_test','seat_multi_vehicle_test').replace('0.17.0','0.18.0'), encoding='utf-8')
for name in ('input_native.c','vss_input_priority.dll','input_helper.lua'):
    (out/name).write_bytes((old/name).read_bytes())
print('Accepted 0.17.0 both roles; isolated 0.18.0 batched vehicle source created')
