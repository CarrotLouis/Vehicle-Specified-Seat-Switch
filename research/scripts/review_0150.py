from pathlib import Path
from collections import Counter
import hashlib,json
W=Path(__file__).resolve().parent
logs=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
out=W/'seat_driver_acquire_test/capture-20261001-0150';out.mkdir(exist_ok=True)
names=['VehicleSeatIntegrated-20261001-211551-21752-78891937.log',
 'VehicleSeatIntegrated-20261001-212008-24424-79149562.log',
 'VehicleSeatIntegrated-20261001-212538-34732-79479687.log',
 'VehicleSeatIntegrated-20261001-212950-10332-79731796.log',
 'VehicleSeatIntegratedDiagnostic.log','BingusSharedLoader.log']
manifest=[];reports=[]
for name in names:
 b=(logs/name).read_bytes();p=out/name
 if p.exists():assert p.read_bytes()==b,'frozen evidence changed'
 else:p.write_bytes(b)
 manifest.append(dict(name=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
 if name not in names[:4]:continue
 rows=[json.loads(x)for x in b.decode('utf-8-sig').splitlines()if x.strip()]
 assert rows[0]['version']=='0.15.0'
 counts=Counter(r['event']for r in rows);inputs=Counter(r.get('reason')for r in rows if r['event']=='seat_input')
 events=[]
 for r in rows:
  if r['event'].startswith('integrated_')or r['event']=='seat_input'or r['event'].startswith('input_priority_')or r['event']in('end','read_gap'):
   selected=dict(r)
   if r['event']=='integrated_state':selected['detail']=json.loads(r['detail'])
   events.append(selected)
 origin=int(name.rsplit('-',1)[-1].removesuffix('.log'));timings=[];last=-1
 for complete in [r for r in rows if r['event']=='integrated_operation_complete']:
  batch=[r for r in rows if last<r['t']<=complete['t']]
  select=next(r for r in batch if r['event']in('integrated_local_authority_selected','integrated_request_attempt'))
  carrier=next((r for r in batch if r['event']=='input_priority_consumed'and r.get('target')==complete['seat']),None)
  first=carrier['input_tick']-origin if carrier else select['t']
  mutation=next(r for r in batch if r['event']=='integrated_switch_attempt')
  pair=next(r for r in batch if r['event']=='sync_pair_calls_returned')
  state=next((r for r in reversed(batch)if r['event']=='integrated_state'),None)
  detail=json.loads(state['detail'])if state else{}
  timings.append(dict(source=select['source'],target=complete['seat'],input_to_submit_ms=select['t']-first,
   input_to_mutation_ms=mutation['t']-first,input_to_sync_return_ms=pair['t']-first,
   authority_path=complete['authority_path'],remote=detail.get('remote_occupants'),ownership=detail.get('ownership')))
  last=complete['t']
 report=dict(name=name,counts=dict(counts),input_reasons=dict(inputs),timings=timings,events=events)
 reports.append(report)
 print(json.dumps(dict(name=name,counts={k:v for k,v in counts.items()if k.startswith('integrated_')or k.startswith('input_priority_')or k in('end','read_gap')},
  input_reasons=dict(inputs),timings=timings,
  other_events=[r for r in events if r['event']in('integrated_cancelled','integrated_stopped','integrated_incomplete','integrated_waiting','end')]),ensure_ascii=False,indent=2))
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
valid=[r for r in reports if r['timings']]
assert len(valid)==2
errors=['integrated_cancelled','integrated_stopped','integrated_incomplete','input_priority_failed','input_priority_discarded','read_gap']
for run,host,count in zip(valid,['P1','P2'],[7,3]):
 assert run['counts']['integrated_operation_complete']==count
 assert run['counts']['integrated_request_attempt']==1 and run['counts']['integrated_acquired']==1 and run['counts']['integrated_driver_authority_retained']==1
 assert all(run['counts'].get(k,0)==0 for k in errors+['integrated_ownership_return_confirmed'])
 assert run['timings'][0]['authority_path']=='acquired_retained'
 assert all(t['authority_path']=='already_local'for t in run['timings'][1:])
 assert all(t['remote'][0]['node']==4 and t['remote'][0]['role']==2 and t['ownership']['owner']=='P1'and t['ownership']['coordinator']==host for t in run['timings'])
 assert all(t['remote']==run['timings'][0]['remote']for t in run['timings'])
 # The accidental exit is an idle interval after operation2 completed.
 if host=='P1':
  completed=[e for e in run['events']if e['event']=='integrated_operation_complete']
  gap=next(e for e in run['events']if e['event']=='integrated_waiting'and e['reason']=='vehicle_not_observed'and completed[1]['t']<e['t']<completed[2]['t'])
  assert not any(e['event']in('integrated_request_attempt','integrated_local_authority_selected')and completed[1]['t']<e['t']<gap['t']for e in run['events'])
 # Genuine original ownerP2 -> local ownerP1, not an already-local shortcut.
 states=[e for e in run['events']if e['event']=='integrated_state']
 request=next(e for e in run['events']if e['event']=='integrated_request_attempt')
 assert any(e['t']<=request['t']and e['detail'].get('seat')==2 and e['detail']['ownership']['owner']=='P2'for e in states)
(out/'analysis.json').write_text(json.dumps(dict(runs=reports,
 accepted=[r['name']for r in valid],excluded=[r['name']for r in reports if not r['timings']],
 no_retest_required=True,occupied_gunner_runtime_refusal_recorded=False,
 user_report='no anomalies; ignore failed-join restart; installer-host accidental exit between completed operations then full route repeated'),ensure_ascii=False,indent=2),encoding='utf-8')
