"""Archive and summarize the user-authorized 0.6.0 test, without changing live logs."""
from pathlib import Path
import hashlib,json,collections,datetime
R=Path(__file__).resolve().parent
DEST=R/'capture-20260928';DEST.mkdir(exist_ok=True)
LIVE=Path.home()/'AppData/Local/CowboyBingus/Helldivers2/Logs'
names=['VehicleSeatSync-20260927-235915-22820-274012984.log','VehicleSeatSync-20260928-000346-13720-274284765.log','VehicleSeatSyncDiagnostic.log']
manifest=[]
for name in names:
 data=(LIVE/name).read_bytes();target=DEST/name
 if target.exists():assert target.read_bytes()==data,'frozen capture differs'
 else:target.write_bytes(data)
 manifest.append(dict(name=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
results=[]
for item in manifest[:2]:
 rows=[dict(json.loads(line),line=i)for i,line in enumerate((DEST/item['name']).read_text(encoding='utf-8').splitlines(),1)]
 select=lambda name:[e for e in rows if e['event']==name]
 native=[e for e in rows if e['event']in('native_send','native_receive_dispatch')]
 seq=[e['sequence']for e in native]
 attempts=select('sync_probe_operation_attempt');operations=[]
 for attempt in attempts:
  lo=attempt['t'];target=attempt['target']
  window=[e for e in rows if lo<=e.get('t',-1)<=lo+1500]
  calls=[e for e in window if e['event']=='native_send'and e['message']in('snapshot','transition')]
  local_observed=[e for e in window if e['event']=='sync_probe_local_target_observed'and e['seat']==target]
  pre=[e for e in window if e['event']=='sync_preflight_passed']
  assert len(calls)==2 and [e['message']for e in calls]==['snapshot','transition']
  assert calls[0]['values'][2:]==[target,0]and calls[1]['values'][1:]==[target,target,0xffffffff,0]
  assert calls[0]['values'][0]==calls[1]['values'][0]
  assert all(e['route']=='send_one'and e['peers']==['P2']and e['peer_count']==1 and e['peer_valid_mask']==1 and e['valid_mask']==(1<<e['argument_count'])-1 for e in calls)
  assert len(local_observed)==1 and len(pre)==1
  ownership=pre[0]['ownership'];assert ownership['owner']==ownership['local_peer']=='P1'and ownership['coordinator']=='P2'and ownership['busy']==False
  operations.append(dict(attempt=attempt,ownership=ownership,native_messages=calls,local_observed=local_observed[0],pose=[e for e in window if e['event']=='sync_local_calls_returned'],
   entry_exit_events=[e for e in window if e['event']in('native_send','native_receive_dispatch')and e['message']in('entry_request','entering','exit_request','exit_accepted')]))
 result=dict(file=item['name'],events=len(rows),counts=dict(collections.Counter(e['event']for e in rows)),native_count=len(native),
  sequence_contiguous=seq==list(range(1,len(seq)+1)),operations=operations,
  errors=[e for e in rows if e['event']in('read_gap','size_limit','sync_probe_stopped','transport_install_failure','native_trace_drop')],
  transport_stop=select('transport_stopped'),end=select('end'),start=select('start'),
  selected_native=[e for e in native if e['message']in('entry_request','exit_request','exit_accepted','authority_owned','snapshot','transition')])
 results.append(result)
(DEST/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(DEST/'analysis.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
for r in results:
 print(json.dumps({k:r[k]for k in ['file','events','native_count','sequence_contiguous','errors','transport_stop','end']},ensure_ascii=False))
 for op in r['operations']:print(json.dumps(op,ensure_ascii=False))
