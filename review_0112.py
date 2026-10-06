from pathlib import Path
from collections import Counter
import hashlib,json

W=Path(__file__).resolve().parent
logs=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
out=W/'seat_fast_settle_test/capture-20261001-0112'
out.mkdir(exist_ok=True)
names=['VehicleSeatIntegrated-20261001-145040-32368-55781109.log',
       'VehicleSeatIntegrated-20261001-145239-19832-55900312.log',
       'VehicleSeatIntegratedDiagnostic.log','BingusSharedLoader.log']
manifest=[]
for name in names:
    source=logs/name
    if not source.exists():continue
    b=source.read_bytes();dest=out/name
    if dest.exists():assert dest.read_bytes()==b,'frozen log changed'
    else:dest.write_bytes(b)
    manifest.append(dict(name=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
e=[json.loads(x) for x in (out/names[1]).read_text(encoding='utf-8-sig').splitlines() if x.strip()]
counts=Counter(x['event'] for x in e)
done=[x for x in e if x['event']=='integrated_operation_complete']
times=[];last=-1
for complete in done:
    batch=[x for x in e if last<x['t']<=complete['t']]
    press=next((x for x in reversed(batch) if x['event']=='seat_input' and x.get('reason')=='waiting_key_release'),None)
    if press:
        after=[x for x in batch if x['t']>=press['t']]
        milestones={}
        for name in ['lean_transition_finished','integrated_request_attempt','integrated_local_authority_selected','integrated_acquired','integrated_switch_attempt','integrated_preflight_passed','sync_snapshot_invoking','sync_pair_calls_returned','integrated_return_invoked','integrated_ownership_return_confirmed']:
            row=next((x for x in after if x['event']==name or x['event']=='seat_input' and x.get('reason')==name),None)
            if row:milestones[name]=row['t']-press['t']
        times.append(dict(source=press['source'],target=complete['seat'],authority=complete['authority_path'],press=press['t'],press_to_complete_ms=complete['t']-press['t'],milestones_ms=milestones))
    last=complete['t']
owners=[x for x in e if x['event']=='integrated_state']
identity=[]
for x in owners:
    try:o=json.loads(x['detail'])['ownership'];v={k:o[k] for k in ['coordinator','self','owner'] if k in o}
    except (ValueError,KeyError,TypeError):continue
    if v and v not in identity:identity.append(v)
report=dict(counts=dict(counts),complete=done,timings=times,identity=identity,user='0.11.2 test passed basically; gunner still ~2s and native lean first; user requires suppression and lowest practical latency')
(out/'analysis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(counts={k:counts[k] for k in ['integrated_operation_complete','integrated_local_authority_preserved','integrated_request_attempt','integrated_ownership_return_confirmed','sync_weapon_pair_calls_returned','read_gap','integrated_stopped','integrated_cancelled','integrated_incomplete']},targets=[(x['seat'],x['authority_path']) for x in done],timings=times,identity=identity),ensure_ascii=False,indent=2))
