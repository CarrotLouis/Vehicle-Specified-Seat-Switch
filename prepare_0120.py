from pathlib import Path
import json
W=Path(__file__).resolve().parent
old=W/'seat_fast_settle_test';out=W/'seat_input_priority_test'
report=json.loads((old/'capture-20261001-0112/analysis.json').read_text(encoding='utf-8'))
c=report['counts'];assert c['integrated_operation_complete']==12 and c['integrated_ownership_return_confirmed']==6
assert not any(c.get(k,0) for k in ['integrated_cancelled','integrated_stopped','read_gap','integrated_incomplete'])
assert not out.exists();out.mkdir()
for p in old.iterdir():
    if p.is_file() and p.suffix in ('.lua','.py','.txt','.json') and p.name not in ('bundled.lua','check.lua','package.json','docs_fast.py'):
        (out/p.name).write_text(p.read_text(encoding='utf-8').replace('seat_fast_settle_test','seat_input_priority_test').replace('0.11.2','0.12.0'),encoding='utf-8')
print('Accepted 0.11.2; isolated 0.12.0 input priority source created')
