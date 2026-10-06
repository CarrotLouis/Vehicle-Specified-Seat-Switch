from pathlib import Path
from collections import Counter
import hashlib,json
W=Path(__file__).resolve().parent
logs=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
out=W/'seat_input_thread_fix/capture-20261001-0121';out.mkdir(exist_ok=True)
names=['VehicleSeatIntegrated-20261001-162104-32752-61205578.log','VehicleSeatIntegratedDiagnostic.log','BingusSharedLoader.log']
manifest=[]
for name in names:
    data=(logs/name).read_bytes();dest=out/name
    if dest.exists():assert dest.read_bytes()==data,'frozen evidence changed'
    else:dest.write_bytes(data)
    manifest.append(dict(name=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
rows=[json.loads(x) for x in (out/names[0]).read_text(encoding='utf-8-sig').splitlines() if x.strip()]
assert rows[0]['version']=='0.12.1'
counts=Counter(x['event'] for x in rows)
done=[x for x in rows if x['event']=='integrated_operation_complete']
clock_origin=int(names[0].rsplit('-',1)[-1].removesuffix('.log'))
timings=[];last=-1
for complete in done:
    batch=[x for x in rows if last<x['t']<=complete['t']]
    press=next((x for x in reversed(batch) if x['event']=='seat_input' and x.get('reason') in ('priority_request','waiting_key_release')),None)
    if press:
        token=next((x for x in reversed(batch) if x['event']=='input_priority_consumed' and x['target']==press['target'] and x['t']<=press['t']),None)
        after=[x for x in batch if x['t']>=press['t']]
        milestones={}
        for name in ['integrated_request_attempt','integrated_local_authority_selected','integrated_acquired','integrated_switch_attempt','sync_snapshot_invoking','sync_pair_calls_returned','integrated_return_invoked','integrated_ownership_return_confirmed']:
            r=next((x for x in after if x['event']==name),None)
            if r:milestones[name]=r['t']-press['t']
        timings.append(dict(source=press['source'],target=complete['seat'],authority=complete['authority_path'],press=press['t'],input_tick=token and token['input_tick'],input_to_submit_ms=token and press['t']-(token['input_tick']-clock_origin),consumed_to_submit_ms=token and press['t']-token['t'],press_to_complete_ms=complete['t']-press['t'],milestones_ms=milestones))
    last=complete['t']
interesting=[x for x in rows if x['event'].startswith('input_priority_') or x['event']=='seat_input' or x['event'] in ('integrated_operation_complete','integrated_cancelled','integrated_stopped','integrated_incomplete','end')]
ownership=[]
for r in rows:
    if r['event']!='integrated_state':continue
    try:o=json.loads(r['detail'])['ownership'];v={k:o[k] for k in ['coordinator','self','owner'] if k in o}
    except (ValueError,KeyError,TypeError):continue
    if v and v not in ownership:ownership.append(v)
report=dict(counts=dict(counts),complete=done,timings=timings,identity=ownership,events=interesting,files=manifest,user_report='hold and tap pass, gunner switch practically immediate, test passed')
(out/'analysis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(counts={k:counts[k] for k in ['input_priority_install_pending','input_priority_ready','input_priority_consumed','input_priority_discarded','input_priority_failed','input_priority_install_failure','integrated_operation_complete','integrated_ownership_return_confirmed','sync_weapon_pair_calls_returned','integrated_cancelled','integrated_stopped','integrated_incomplete','read_gap']},timings=timings,events=interesting,identity=ownership),ensure_ascii=False,indent=2))
