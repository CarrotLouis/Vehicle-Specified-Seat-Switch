from pathlib import Path
import json

R=Path(__file__).resolve().parent
frozen=R.parent/'seat_aboard_passenger_test/capture-20261001-0130'
out=[]
for run,meta in enumerate(json.loads((frozen/'manifest.json').read_text(encoding='utf-8'))[:2]):
    rows=[json.loads(x) for x in (frozen/meta['name']).read_text(encoding='utf-8').splitlines() if x.strip()]
    for i,row in enumerate(rows):
        if row['event']!='seat_input' or row.get('reason')!='cancelled_by_new_key':
            continue
        previous=rows[:i]
        carrier=next(x for x in reversed(previous) if x['event']=='input_priority_consumed')
        poll=next(x for x in reversed(previous) if x['event']=='seat_input' and x.get('reason')=='waiting_key_release')
        assert 0<=carrier['t']-poll['t']<=250
        assert carrier['source']==poll['source'] and carrier['target']==poll['target']
        out.append(dict(run=meta['name'],host='self' if run==0 else 'friend',poll_ms=poll['t'],carrier_ms=carrier['t'],
                        source=carrier['source'],target=carrier['target'],binding=carrier['binding'],delay_ms=carrier['t']-poll['t']))
assert len(out)==6 and any(x['delay_ms']==31 for x in out)
(R/'input-race-replay.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
lua='return {\n'+''.join(' {'+','.join(k+'='+('"'+v+'"' if isinstance(v,str) else str(v)) for k,v in row.items() if k!='run')+'},\n' for row in out)+'}\n'
(R/'input_race_replay.lua').write_text(lua,encoding='utf-8')
print(f'Frozen six captured poll/GUI cancellations imported ({[r["delay_ms"] for r in out]}ms)')
