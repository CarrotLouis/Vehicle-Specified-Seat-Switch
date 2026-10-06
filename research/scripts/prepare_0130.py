from pathlib import Path
import json
W=Path(__file__).resolve().parent;old=W/'seat_input_thread_fix';out=W/'seat_aboard_passenger_test'
report=json.loads((old/'capture-20261001-0121/analysis.json').read_text(encoding='utf-8'))
c=report['counts']
assert c['integrated_operation_complete']==4 and c['integrated_ownership_return_confirmed']==4 and c['input_priority_consumed']==4
assert all(c.get(k,0)==0 for k in ('input_priority_install_failure','input_priority_failed','integrated_cancelled','integrated_stopped','integrated_incomplete','read_gap'))
assert not out.exists();out.mkdir()
for p in old.iterdir():
    if p.is_file() and p.suffix in ('.lua','.py','.txt','.json','.c') and p.name not in ('bundled.lua','check.lua','package.json','docs_thread.py','docs_priority.py'):
        (out/p.name).write_text(p.read_text(encoding='utf-8').replace('seat_input_thread_fix','seat_aboard_passenger_test').replace('0.12.1','0.13.0'),encoding='utf-8')
print('Accepted 0.12.1; isolated 0.13.0 local-owner with remote passenger source created')
