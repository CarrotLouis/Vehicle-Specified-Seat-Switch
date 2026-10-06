from pathlib import Path
import json
W=Path(__file__).resolve().parent;R=W/'seat_aboard_passenger_test/capture-20261001-0130'
manifest=json.loads((R/'manifest.json').read_text());report=[]
for meta in manifest[:2]:
 rows=[json.loads(x) for x in (R/meta['name']).read_text(encoding='utf-8').splitlines() if x.strip()]
 evidence=[]
 for i,x in enumerate(rows):
  if x['event'] not in ('seat_input','integrated_trigger_rejected'):continue
  if x.get('reason') not in ('waiting_key_release','cancelled_by_new_key','friend_must_be_settled_passenger'):continue
  states=[r for r in rows[:i+1] if r['event']=='state' and r.get('data',{}).get('state')=='mission']
  state=states[-1] if states else None
  after=next((r for r in rows[i+1:] if r['event']=='state' and r.get('data',{}).get('state')=='mission'),None)
  def compact(s):
   if not s:return None
   return dict(t=s['t'],avatars=[{k:a[k] for k in ('id','unit','is_local','owned_local','vehicle_input','seat') if k in a} for a in s['data']['avatars']])
  ev=dict(event=x,before=compact(state),after=compact(after))
  evidence.append(ev)
  print(json.dumps(dict(run=meta['name'],**ev),ensure_ascii=False))
 report.append(dict(name=meta['name'],evidence=evidence))
(R/'input-race-evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
