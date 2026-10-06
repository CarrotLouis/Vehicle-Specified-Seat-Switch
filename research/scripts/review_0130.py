from pathlib import Path
from collections import Counter
import hashlib,json
W=Path(__file__).resolve().parent
logs=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
out=W/'seat_aboard_passenger_test/capture-20261001-0130';out.mkdir(exist_ok=True)
names=['VehicleSeatIntegrated-20261001-165646-18284-63346859.log','VehicleSeatIntegrated-20261001-170344-32548-63765500.log','VehicleSeatIntegratedDiagnostic.log','BingusSharedLoader.log']
manifest=[]
for name in names:
    data=(logs/name).read_bytes();dest=out/name
    if dest.exists():assert dest.read_bytes()==data,'frozen evidence changed'
    else:dest.write_bytes(data)
    manifest.append(dict(name=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
reports=[]
for name in names[:2]:
    rows=[json.loads(x) for x in (out/name).read_text(encoding='utf-8-sig').splitlines() if x.strip()]
    assert rows[0]['version']=='0.13.0'
    counts=Counter(x['event'] for x in rows)
    selected=[x for x in rows if x['event'].startswith('input_priority_') or x['event']=='seat_input' or x['event'] in ('integrated_operation_complete','integrated_trigger_rejected','integrated_cancelled','integrated_stopped','integrated_incomplete','integrated_request_attempt','integrated_local_authority_selected','integrated_switch_attempt','integrated_preflight_passed','integrated_return_invoked','end')]
    timings=[];last=-1;origin=int(name.rsplit('-',1)[-1].removesuffix('.log'))
    done=[x for x in rows if x['event']=='integrated_operation_complete']
    for complete in done:
        batch=[x for x in rows if last<x['t']<=complete['t']]
        press=next((x for x in batch if x['event']=='seat_input' and x.get('target')==complete['seat'] and x.get('reason') in ('priority_request','waiting_key_release')),None)
        if press:
            tokens=[x for x in batch if x['event']=='input_priority_consumed' and x['target']==press['target'] and x['t']<=press['t']]
            token=tokens[-1] if tokens else None
            milestones={}
            for ev in ('integrated_local_authority_selected','integrated_request_attempt','integrated_switch_attempt','integrated_preflight_passed','sync_snapshot_invoking','sync_pair_calls_returned','integrated_ownership_return_confirmed'):
                r=next((x for x in batch if x['event']==ev and x['t']>=press['t']),None)
                if r:milestones[ev]=r['t']-press['t']
            timings.append(dict(source=press['source'],target=complete['seat'],authority=complete['authority_path'],press=press['t'],input_to_submit_ms=token and press['t']-(token['input_tick']-origin),press_to_complete_ms=complete['t']-press['t'],milestones_ms=milestones))
        last=complete['t']
    states=[]
    for x in rows:
        if x['event']!='integrated_state':continue
        try:d=json.loads(x['detail'])
        except (ValueError,TypeError):continue
        concise={k:d[k] for k in ('seat','local_ready','remote_occupants') if k in d}
        concise['ownership']={k:d['ownership'].get(k) for k in ('coordinator','owner','owned_local')}
        if not states or concise!=states[-1]['data']:states.append(dict(t=x['t'],data=concise))
    report=dict(name=name,counts=dict(counts),events=selected,timings=timings,states=states)
    reports.append(report)
    print(json.dumps(dict(name=name,counts={k:counts[k] for k in ('integrated_operation_complete','integrated_local_authority_preserved','integrated_request_attempt','integrated_ownership_return_confirmed','input_priority_consumed','input_priority_discarded','input_priority_failed','integrated_cancelled','integrated_stopped','integrated_incomplete','read_gap')},timings=timings,events=selected),ensure_ascii=False,indent=2))
(out/'analysis.json').write_text(json.dumps(dict(runs=reports,user_report='both runs pass other steps; gunner to rear-left Ctrl+Z takes about10s after first press, unclear delayed versus missed response'),ensure_ascii=False,indent=2),encoding='utf-8')
