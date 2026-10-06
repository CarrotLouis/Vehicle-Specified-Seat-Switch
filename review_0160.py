from pathlib import Path
from collections import Counter
import hashlib,json
W=Path(__file__).resolve().parent;logs=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
out=W/'seat_seated_owner_test/capture-20261001-0160';out.mkdir(exist_ok=True)
names=['VehicleSeatIntegrated-20261001-222249-35516-82910781.log','VehicleSeatIntegrated-20261001-223315-35232-83536750.log','VehicleSeatIntegratedDiagnostic.log','BingusSharedLoader.log']
manifest=[];reports=[]
for name in names:
 live=(logs/name).read_bytes();path=out/name
 if path.exists():
  b=path.read_bytes()
  if name in names[:2]:assert b==live,'primary evidence changed'
  # Shared companion logs can be overwritten by later unrelated launches.
  # Keep the originals associated with this capture; never overwrite evidence.
 else:b=live;path.write_bytes(b)
 manifest.append(dict(name=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
 if name not in names[:2]:continue
 rows=[json.loads(x)for x in b.decode('utf-8-sig').splitlines()if x.strip()]
 assert rows[0]['version']=='0.16.0'
 counts=Counter(r['event']for r in rows);inputs=Counter(r.get('reason')for r in rows if r['event']=='seat_input')
 events=[]
 for r in rows:
  if r['event'].startswith('integrated_')or r['event']=='seat_input'or r['event'].startswith('input_priority_')or r['event']in('read_gap','end'):
   e=dict(r)
   if e['event']=='integrated_state':e['detail']=json.loads(e['detail'])
   events.append(e)
 origin=int(name.rsplit('-',1)[-1].removesuffix('.log'));timings=[];last=-1
 for complete in [r for r in rows if r['event']=='integrated_operation_complete']:
  batch=[r for r in rows if last<r['t']<=complete['t']]
  select=next(r for r in batch if r['event']in('integrated_request_attempt','integrated_local_authority_selected'))
  carrier=next((r for r in batch if r['event']=='input_priority_consumed'and r.get('target')==complete['seat']),None)
  first=carrier['input_tick']-origin if carrier else select['t']
  mutation=next(r for r in batch if r['event']=='integrated_switch_attempt');pair=next(r for r in batch if r['event']=='sync_pair_calls_returned')
  states=[json.loads(r['detail'])for r in batch if r['event']=='integrated_state']
  detail=states[-1]if states else{}
  timings.append(dict(source=select['source'],target=complete['seat'],authority_path=complete['authority_path'],
   input_to_submit_ms=select['t']-first,input_to_mutation_ms=mutation['t']-first,input_to_sync_return_ms=pair['t']-first,
   remote=detail.get('remote_occupants'),ownership=detail.get('ownership'),owners_seen=list(dict.fromkeys(s['ownership']['owner']for s in states))))
  last=complete['t']
 reports.append(dict(name=name,counts=dict(counts),input_reasons=dict(inputs),timings=timings,events=events))
 keys=['integrated_operation_complete','integrated_request_attempt','integrated_acquired','integrated_ownership_return_confirmed','integrated_driver_authority_retained','integrated_local_authority_preserved','input_priority_consumed','input_priority_discarded','input_priority_failed','integrated_cancelled','integrated_stopped','integrated_incomplete','read_gap']
 print(json.dumps(dict(name=name,counts={k:counts[k]for k in keys},input_reasons=dict(inputs),timings=timings),ensure_ascii=False,indent=2))
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
for run,host in zip(reports,['P1','P2']):
 assert run['counts']['integrated_operation_complete']==6
 assert run['counts']['integrated_request_attempt']==4 and run['counts']['integrated_acquired']==4
 assert run['counts']['integrated_ownership_return_confirmed']==3 and run['counts']['integrated_driver_authority_retained']==1 and run['counts']['integrated_local_authority_preserved']==2
 assert all(run['counts'].get(k,0)==0 for k in ['integrated_cancelled','integrated_stopped','integrated_incomplete','input_priority_failed','input_priority_discarded','read_gap'])
 assert [t['authority_path']for t in run['timings']]==['borrowed_returned']*3+['acquired_retained']+['already_local']*2
 assert [(t['source'],t['target'])for t in run['timings']]==[(2,4),(4,3),(3,4),(4,0),(0,2),(2,0)]
 assert all(t['remote'][0]['node']==1 and t['remote'][0]['role']==3 and t['remote']==run['timings'][0]['remote']and t['ownership']['coordinator']==host for t in run['timings'])
 assert run['input_reasons']['occupied']>=1
 assert all(e['target']==1 for e in run['events']if e['event']=='seat_input'and e.get('reason')=='occupied')
(out/'analysis.json').write_text(json.dumps(dict(runs=reports,accepted=True,occupied_front_runtime_refusal_recorded=True,user_report='both tests complete without anomalies'),ensure_ascii=False,indent=2),encoding='utf-8')
