"""Preserve and correlate the completed two-role capture; no live process access."""
from pathlib import Path
import json,collections,hashlib,csv,shutil,bisect,sys
name=sys.argv[1]if len(sys.argv)>1 else 'VehicleSeatTransport-20260925-150918-11080-69416500.log'
assert Path(name).name==name and name.startswith('VehicleSeatTransport-')and name.endswith('.log')
R=Path(__file__).resolve().parent;out=R/('multiplayer-'+'-'.join(name.split('-')[1:3]));out.mkdir(exist_ok=True)
logs=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
for n in [name,'VehicleSeatTransportDiagnostic.log']:
 if not(out/n).exists():shutil.copyfile(logs/n,out/n)
events=[json.loads(l)for l in(out/name).read_text().splitlines()]
native=[e for e in events if e['event'].startswith('native_')]
states=[e for e in events if e['event']=='state'];times=[e['t']for e in states]
assert [e['sequence']for e in native]==list(range(1,len(native)+1))
stop=next(e for e in events if e['event']=='transport_stopped')
assert stop['events']==len(native)and stop['dropped_total']==stop['restore_flags']==0
missions=[];active=None
for s in states:
 if s['data']['state']=='mission':
  if active is None:active={'start':s['t'],'states':[]};missions.append(active)
  active['states'].append(s);active['last']=s['t']
 else:
  if active is not None:active['end']=s['t']
  active=None
if active:active['end']=events[-1]['t']
assert len(missions)==2
def complete(e):return e['valid_mask']==(1<<e['argument_count'])-1
def latest(t):return states[bisect.bisect_right(times,t)-1]
chains=[];rounds=[];occupied_keys=[]
for m,role in zip(missions,['user_host','friend_host']):
 ns=[e for e in native if m['start']<=e['t']<m['end']]
 reqs=[e for e in ns if e['event']=='native_send'and e['message']=='switch_request']
 ownership=[];previous={}
 for s in m['states']:
  for v in s['data']['vehicles']:
   if previous.get(v['network_unit'])!=v['owned_local']:
    ownership.append(dict(t=s['t'],vehicle=v['network_unit'],owned_local=v['owned_local']))
   previous[v['network_unit']]=v['owned_local']
 for i,r in enumerate(reqs):
  t=r['t'];vehicle,avatar,source,direction=r['values'];end=reqs[i+1]['t']if i+1<len(reqs)else min(t+3000,m['end'])
  before=latest(t)['data'];a=next(a for a in before['avatars']if a['is_local']and a['network_unit']==avatar)
  v=next(v for v in before['vehicles']if v['network_unit']==vehicle)
  assert a['seat']['collection']==v['id']and a['seat']['current']==source and complete(r)
  window=[e for e in ns if t<=e['t']<end and e['sequence']>=r['sequence']]
  rx=next((e for e in window if e['event']=='native_receive_dispatch'and e['message']=='switch_request'and e['values']==r['values']),None)
  txaccept=next((e for e in window if e['event']=='native_send'and e['message']=='accepted'and e['values'][:2]==r['values'][:2]),None)
  accept=next(e for e in window if e['event']=='native_receive_dispatch'and e['message']=='accepted'and e['values'][:2]==r['values'][:2])
  assert complete(accept);target=accept['values'][2];after=None
  for s in m['states']:
   if not accept['t']<=s['t']<end:continue
   av=next((a for a in s['data']['avatars']if a['is_local']and a['network_unit']==avatar),None)
   if av and av['seat']['collection']==v['id']and av['seat']['current']==target and av['seat']['transitioning']==0:
    after=s;break
  # Native timestamps and sampled states share milliseconds but are collected
  # separately. A fast next request can precede a sampled settled frame.
  # Keep the gap visible instead of stretching the pairing window.
  chains.append(dict(round=role,t=t,sequence=r['sequence'],vehicle=vehicle,avatar=avatar,source=source,target=target,direction=direction,
   sampled_owned_local=v['owned_local'],send_peer='|'.join(r['peers']),request_receive=rx is not None,accepted_send=txaccept is not None,
   accepted_from='|'.join(accept['peers']),accepted_ms=accept['t'],settled_ms=after['t']if after else None,elapsed_ms=after['t']-t if after else None))
 # Default numbered seat intents use profile-seat ordering for M102 only.
 for e in events:
  if e['event']!='configured_seat_key'or not m['start']<=e['t']<m['end']:continue
  d=latest(e['t'])['data'];a=next((a for a in d['avatars']if a['is_local']),None)
  if not a:continue
  v=next((v for v in d['vehicles']if v['id']==a['seat']['collection']and v['name']=='m102'),None)
  if not v:continue
  occupied_keys.append(dict(round=role,t=e['t'],key_event=e,source=a['seat']['current'],vehicle=v['network_unit'],free_mask=v['free_mask'],avatars=d['avatars']))
 rounds.append(dict(role=role,start=m['start'],end=m['end'],local_network_ids=sorted({a['network_unit']for s in m['states']for a in s['data']['avatars']if a['is_local']}),
  messages=[dict(event=k[0],message=k[1],count=v)for k,v in collections.Counter((e['event'],e['message'])for e in ns).items()],
  switches=len(reqs),ownership=ownership))
incomplete=[e for e in native if not complete(e)]
assert all(e['message']=='exit_request'and e['event']=='native_receive_dispatch'and e['valid_mask']==7 and e['sizes']==[4,4,4,1]for e in incomplete)
with(out/'switch-chains.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=list(chains[0]));w.writeheader();w.writerows(chains)
(out/'key-context.json').write_text(json.dumps(occupied_keys,indent=2))
summary=dict(source=name,sha256=hashlib.sha256((out/name).read_bytes()).hexdigest(),start=events[0],stop=stop,event_counts=dict(collections.Counter(e['event']for e in events)),rounds=rounds,
 incomplete_bool_records=len(incomplete),matched_chains=len(chains),settled_samples=sum(c['settled_ms']is not None for c in chains),routing_counts=[dict(round=k[0],owned_local=k[1],request_receive=k[2],accepted_send=k[3],count=v)for k,v in collections.Counter((c['round'],c['sampled_owned_local'],c['request_receive'],c['accepted_send'])for c in chains).items()])
(out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
