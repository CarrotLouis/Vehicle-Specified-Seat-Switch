from pathlib import Path
from collections import Counter
import hashlib,json
W=Path(__file__).resolve().parent
logs=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
out=W/'seat_remote_gunner_test/capture-20261001-0140';out.mkdir(exist_ok=True)
names=['VehicleSeatIntegrated-20261001-201856-32648-75476906.log','VehicleSeatIntegrated-20261001-202450-22172-75831718.log','VehicleSeatIntegratedDiagnostic.log','BingusSharedLoader.log']
manifest=[]
for name in names:
    b=(logs/name).read_bytes();p=out/name
    if p.exists():assert p.read_bytes()==b,'frozen evidence changed'
    else:p.write_bytes(b)
    manifest.append(dict(name=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
reports=[]
for name in names[:2]:
    rows=[json.loads(x) for x in (out/name).read_text(encoding='utf-8-sig').splitlines() if x.strip()]
    assert rows[0]['version']=='0.14.0'
    counts=Counter(r['event'] for r in rows);inputs=Counter(r.get('reason') for r in rows if r['event']=='seat_input')
    origin=int(name.rsplit('-',1)[-1].removesuffix('.log'));timings=[];last=-1
    for complete in [r for r in rows if r['event']=='integrated_operation_complete']:
        batch=[r for r in rows if last<r['t']<=complete['t']]
        select=next(r for r in batch if r['event']=='integrated_local_authority_selected')
        trigger=next((r for r in batch if r['event']=='seat_input' and r.get('target')==complete['seat'] and r.get('reason') in ('priority_request','waiting_key_release')),None)
        carrier=next((r for r in batch if r['event']=='input_priority_consumed' and r.get('target')==complete['seat']),None)
        mutation=next(r for r in batch if r['event']=='integrated_switch_attempt');pair=next(r for r in batch if r['event']=='sync_pair_calls_returned')
        first=carrier['input_tick']-origin if carrier else trigger['t'] if trigger else select['t']
        state=next((r for r in reversed(batch) if r['event']=='integrated_state'),None)
        detail=json.loads(state['detail']) if state else {}
        timings.append(dict(source=select['source'],target=complete['seat'],input_to_submit_ms=select['t']-first,input_to_mutation_ms=mutation['t']-first,input_to_sync_return_ms=pair['t']-first,authority_path=complete['authority_path'],remote=detail.get('remote_occupants'),ownership=detail.get('ownership')))
        last=complete['t']
    selected=[r for r in rows if r['event']=='seat_input' or r['event'].startswith('input_priority_') or r['event'] in ('integrated_operation_complete','integrated_trigger_rejected','integrated_stopped','end')]
    report=dict(name=name,counts=dict(counts),input_reasons=dict(inputs),timings=timings,events=selected)
    reports.append(report)
    keys=['integrated_operation_complete','integrated_local_authority_preserved','integrated_request_attempt','integrated_ownership_return_confirmed','input_priority_consumed','input_priority_discarded','input_priority_failed','integrated_cancelled','integrated_stopped','integrated_incomplete','read_gap']
    print(json.dumps(dict(name=name,counts={k:counts[k] for k in keys},input_reasons=dict(inputs),timings=timings),ensure_ascii=False,indent=2))
(out/'analysis.json').write_text(json.dumps(dict(runs=reports,user_report='test completed without anomalies'),ensure_ascii=False,indent=2),encoding='utf-8')
