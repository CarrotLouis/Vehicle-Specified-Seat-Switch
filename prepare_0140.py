from pathlib import Path
import json
W=Path(__file__).resolve().parent;old=W/'seat_input_race_fix';out=W/'seat_remote_gunner_test'
accepted=json.loads((old/'capture-20261001-0131/analysis.json').read_text(encoding='utf-8'))
assert len(accepted['runs'])==2
for r in accepted['runs']:
    assert r['counts']['integrated_operation_complete']==5 and r['counts']['integrated_local_authority_preserved']==5
    assert r['input_reasons'].get('cancelled_by_new_key',0)==0
    assert all(r['counts'].get(k,0)==0 for k in ('integrated_stopped','integrated_cancelled','integrated_incomplete','input_priority_failed','read_gap'))
assert not out.exists();out.mkdir()
for p in old.iterdir():
    if p.is_file() and p.suffix in ('.lua','.py','.txt','.c') and p.name not in ('bundled.lua','check.lua','input_helper.lua','docs_race.py'):
        (out/p.name).write_text(p.read_text(encoding='utf-8').replace('seat_input_race_fix','seat_remote_gunner_test').replace('0.13.1','0.14.0'),encoding='utf-8')
for name in ('input_native.c','vss_input_priority.dll'):(out/name).write_bytes((old/name).read_bytes())
print('Accepted0.13.1 input; isolated0.14.0 remote-gunner context created')
