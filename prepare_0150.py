from pathlib import Path
import json
W=Path(__file__).resolve().parent;old=W/'seat_remote_gunner_test';out=W/'seat_driver_acquire_test'
accepted=json.loads((old/'capture-20261001-0140/analysis.json').read_text(encoding='utf-8'))
assert len(accepted['runs'])==2
for r in accepted['runs']:
    assert r['counts']['integrated_operation_complete']==4 and r['counts']['integrated_local_authority_preserved']==4
    assert all(r['counts'].get(k,0)==0 for k in ('integrated_stopped','integrated_cancelled','integrated_incomplete','input_priority_failed','read_gap'))
    assert all(t['remote'][0]['node']==4 and t['remote'][0]['role']==2 for t in r['timings'])
assert not out.exists();out.mkdir()
for p in old.iterdir():
    if p.is_file() and p.suffix in ('.lua','.py','.txt','.c') and p.name not in ('bundled.lua','check.lua','input_helper.lua','docs_gunner.py'):
        (out/p.name).write_text(p.read_text(encoding='utf-8').replace('seat_remote_gunner_test','seat_driver_acquire_test').replace('0.14.0','0.15.0'),encoding='utf-8')
for name in ('input_native.c','vss_input_priority.dll'):(out/name).write_bytes((old/name).read_bytes())
print('Accepted0.14.0; isolated0.15.0 vacant-driver acquisition source created')
