"""Correlate natural seat snapshots with state; no live-process access."""
from pathlib import Path
import json,collections,hashlib,shutil
R=Path(__file__).resolve().parent;out=R/'late-join-20260925';out.mkdir(exist_ok=True)
logs=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
names=['VehicleSeatTransport-20260925-171638-22072-77056515.log','VehicleSeatTransport-20260925-172940-36044-77838328.log']
summary=[]
for name in names:
 p=out/name
 if not p.exists():shutil.copyfile(logs/name,p)
 es=[json.loads(l)for l in p.read_text().splitlines()];native=[e for e in es if e['event'].startswith('native_')]
 assert es[0]['version']=='0.4.1'
 assert [e['sequence']for e in native]==list(range(1,len(native)+1))
 assert all(e['valid_mask']==(1<<e['argument_count'])-1 for e in native)
 stop=next(e for e in es if e['event']=='transport_stopped')
 assert stop['reason']=='shutdown'and stop['restore_flags']==0 and stop['dropped_total']==0 and stop['events']==len(native)
 states=[e for e in es if e['event']=='state'];snaps=[]
 for e in native:
  if e['message']!='snapshot':continue
  # Snapshot wire order is AVATAR, COLLECTION, seat, active-passenger bool.
  # Entry/accepted messages use the opposite order for the first two fields.
  avatar,vehicle,seat,active=e['values'];sent=e['event']=='native_send'
  candidates=[s for s in states if (0<=e['t']-s['t']<2100 if sent else 0<=s['t']-e['t']<2100)]
  if sent:candidates.reverse()
  match=None
  for s in candidates:
   a=next((a for a in s['data']['avatars']if a['network_unit']==avatar),None)
   v=next((v for v in s['data']['vehicles']if v['network_unit']==vehicle),None)
   if a and v and a['seat']['collection']==v['id']and a['seat']['current']==seat:
    match=dict(t=s['t'],avatar=a,vehicle=v);break
  assert match is not None,(name,e)
  snaps.append(dict(event=e,state=match))
 summary.append(dict(source=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),events=dict(collections.Counter(e['event']for e in es)),
  messages=[dict(event=k[0],message=k[1],count=v)for k,v in collections.Counter((e['event'],e['message'])for e in native).items()],
  snapshots=snaps,stop=stop,aliases=[e for e in es if e['event']=='protocol_peer_alias']))
for n in ['VehicleSeatSwitch.log','BingusSharedLoader.log','VehicleSeatTransportDiagnostic.log']:
 if not(out/n).exists():shutil.copyfile(logs/n,out/n)
(out/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps([dict(source=s['source'],sha256=s['sha256'],native=s['stop']['events'],snapshots=[dict(direction=x['event']['event'],values=x['event']['values'],observed_role=x['state']['avatar']['seat']['role'],observed_free_mask=x['state']['vehicle']['free_mask'])for x in s['snapshots']])for s in summary],indent=2))
