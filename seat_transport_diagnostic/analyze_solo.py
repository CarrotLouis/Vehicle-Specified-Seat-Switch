"""Analyze the first successful live transport run without changing any logs."""
from pathlib import Path
import json,collections,hashlib,csv,shutil
R=Path(__file__).resolve().parent;out=R/'solo-20260925-143614';out.mkdir(exist_ok=True)
logs=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
name='VehicleSeatTransport-20260925-143614-32348-67432156.log'
for n in [name,'VehicleSeatTransportDiagnostic.log']:
 if not(out/n).exists():shutil.copyfile(logs/n,out/n)
events=[json.loads(l)for l in(out/name).read_text().splitlines()]
native=[e for e in events if e['event'].startswith('native_')]
states=[e for e in events if e['event']=='state']
assert [e['sequence']for e in native]==list(range(1,len(native)+1))
stop=next(e for e in events if e['event']=='transport_stopped')
assert stop['events']==len(native)==98 and stop['restore_flags']==0 and stop['dropped_total']==0
requests=[e for e in native if e['event']=='native_send'and e['message']=='switch_request']
def complete(e):return e['valid_mask']==(1<<e['argument_count'])-1
def latest(t):return next(s for s in reversed(states)if s['t']<=t)
chains=[]
for i,req in enumerate(requests):
 t,values=req['t'],req['values'];vehicle,avatar,source,direction=values
 end=requests[i+1]['t']if i+1<len(requests)else t+3000
 before=latest(t)['data']
 a=next(a for a in before['avatars']if a['is_local']and a['network_unit']==avatar)
 v=next(v for v in before['vehicles']if v['network_unit']==vehicle)
 assert a['seat']['collection']==v['id']and a['seat']['current']==source
 window=[e for e in native if t<=e['t']<end and e['sequence']>=req['sequence']]
 received=next(e for e in window if e['event']=='native_receive_dispatch'and e['message']=='switch_request'and e['values']==values)
 accepted=next(e for e in window if e['event']=='native_send'and e['message']=='accepted'and e['values'][:2]==values[:2])
 dispatched=next(e for e in window if e['event']=='native_receive_dispatch'and e['message']=='accepted'and e['values']==accepted['values'])
 target=accepted['values'][2]
 after=None
 for state in states:
  if not dispatched['t']<=state['t']<end:continue
  for av in state['data']['avatars']:
   seat=av.get('seat',{})
   if av['is_local']and av.get('network_unit')==avatar and seat.get('collection')==v['id']and seat.get('current')==target and seat.get('transitioning')==0:
    after=state;break
  if after:break
 assert after is not None and all(complete(e)for e in [req,received,accepted,dispatched])
 chains.append(dict(request_ms=t,vehicle_network_id=vehicle,avatar_network_id=avatar,collection_id=v['id'],avatar_id=a['id'],source_seat=source,direction=direction,target_seat=target,
  request_dispatch_ms=received['t'],accept_send_ms=accepted['t'],accept_dispatch_ms=dispatched['t'],settled_ms=after['t'],elapsed_ms=after['t']-t))
with(out/'switch-chains.csv').open('w',newline='')as f:
 writer=csv.DictWriter(f,fieldnames=list(chains[0]));writer.writeheader();writer.writerows(chains)
incomplete=[e for e in native if not complete(e)]
assert len(incomplete)==6 and all(e['message']=='exit_request'and e['event']=='native_receive_dispatch'and e['valid_mask']==7 and e['types']==[1,1,1,0]and e['sizes']==[4,4,4,1]for e in incomplete)
summary=dict(source=name,sha256=hashlib.sha256((out/name).read_bytes()).hexdigest(),events=dict(collections.Counter(e['event']for e in events)),
 native_messages=[dict(event=k[0],message=k[1],count=v)for k,v in collections.Counter((e['event'],e['message'])for e in native).items()],
 matched_switch_chains=len(chains),front=sum(c['source_seat']in [0,1]for c in chains),rear=sum(c['source_seat']in [2,3]for c in chains),
 direction_values=sorted(set(c['direction']for c in chains)),zero_peer_sends=sum(e['event']=='native_send'and e['peer_count']==0 for e in native),
 initial_read_gaps=[e for e in events if e['event']=='read_gap'],incomplete_parameters=incomplete,stop=stop)
(out/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({k:v for k,v in summary.items()if k not in ['incomplete_parameters','native_messages']},indent=2))
