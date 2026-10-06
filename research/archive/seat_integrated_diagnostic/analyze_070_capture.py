from pathlib import Path
import json,hashlib,collections
R=Path(__file__).resolve().parent;D=R/'capture-20260928-070';D.mkdir(exist_ok=True)
L=Path.home()/'AppData/Local/CowboyBingus/Helldivers2/Logs'
name='VehicleSeatIntegrated-20260928-004555-804-276813296.log';manifest=[]
for n in (name,'VehicleSeatIntegratedDiagnostic.log'):
 data=(L/n).read_bytes();p=D/n
 if p.exists():assert p.read_bytes()==data
 else:p.write_bytes(data)
 manifest.append(dict(name=n,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
rows=[dict(json.loads(line),line=i)for i,line in enumerate((D/name).read_text().splitlines(),1)]
native=[e for e in rows if e['event'].startswith('native_')]
assert [e['sequence']for e in native]==list(range(1,len(native)+1))
assert all(e['valid_mask']==(1<<e['argument_count'])-1 for e in native)
operations=[]
for e in rows:
 if e['event']=='integrated_request_attempt':
  complete=next(x for x in rows if x['event']=='integrated_operation_complete'and x['t']>e['t'])
  window=[x for x in rows if e['t']<=x['t']<=complete['t']+1000]
  operations.append(dict(request=e,complete=complete,detail=[x for x in window if x['event']!='state'and x['event']!='authority_interface_preflight']))
assert len(operations)==2
stop=next(e for e in rows if e['event']=='transport_stopped')
assert stop['events']==len(native)and stop['dropped_total']==stop['restore_flags']==0
summary=dict(manifest=manifest,records=len(rows),native_count=len(native),operations=operations,
 failures=[e for e in rows if e['event']in('read_gap','protocol_gap','integrated_cancelled','integrated_stopped','integrated_incomplete')],stop=stop,
 user_observation='Both players saw entry animation; otherwise expected. Third trigger did nothing (two-operation limit).')
(D/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:summary[k]for k in ('records','native_count','failures','stop')},ensure_ascii=False))
for op in operations:
 for e in op['detail']:
  if e['event']!='integrated_state':print(json.dumps(e,ensure_ascii=False))
