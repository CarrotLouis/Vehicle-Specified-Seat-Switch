"""Read-only archive and validation of the actual 0.5.3 ownership round trip."""
from pathlib import Path
import json,hashlib,collections
R=Path(__file__).resolve().parent;D=R/'analysis-20260928-053';D.mkdir(exist_ok=True)
L=Path.home()/'AppData/Local/CowboyBingus/Helldivers2/Logs'
name='VehicleSeatAuthority-20260928-001556-14684-275014781.log'
manifest=[]
for n in (name,'VehicleSeatAuthorityDiagnostic.log','VehicleSeatSwitch.log','BingusSharedLoader.log'):
 src=L/n
 if not src.exists():continue
 dst=D/n
 if not dst.exists():dst.write_bytes(src.read_bytes())
 data=dst.read_bytes();manifest.append(dict(name=n,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
es=[dict(json.loads(line),line=i)for i,line in enumerate((D/name).read_text(encoding='utf-8').splitlines(),1)]
native=[e for e in es if e['event']in('native_send','native_receive_dispatch')]
assert es[0]['version']=='0.5.3'
assert [e['sequence']for e in native]==list(range(1,len(native)+1))
assert all(e['valid_mask']==(1<<e['argument_count'])-1 for e in native)
stop=next(e for e in es if e['event']=='transport_stopped')
assert stop['events']==len(native)and stop['dropped_total']==stop['restore_flags']==0
probe=[e for e in es if e['event'].startswith('authority_probe_')]
def one(event):
 items=[e for e in es if e['event']==event];assert len(items)==1,(event,len(items));return items[0]
request=one('authority_probe_request_sent');acquired=one('authority_probe_acquired');returned=one('authority_probe_return_sent');complete=one('authority_probe_complete')
assert request['owner']==complete['owner']==request['coordinator']=='P2'
assert acquired['owner']==returned['owner']==request['local_peer']=='P1'
assert not request['owned_local']and acquired['owned_local']and not complete['owned_local']
assert request['t']<acquired['t']==returned['t']<complete['t']
active=[e for e in native if request['t']<=e['t']<=complete['t']]
states=[e for e in es if e['event']=='state'and request['t']-1000<=e['t']<=complete['t']+30000]
seat_states=[]
for e in states:
 for a in e['data']['avatars']:
  if a['seat'].get('collection')==750:
   seat_states.append(dict(t=e['t'],local_player=a['is_local'],seat=a['seat']['current'],role=a['seat']['role'],target=a['seat']['target'],reserved=a['seat']['reserved']))
   assert a['seat']['current']==(1 if a['is_local']else 0)
   assert a['seat']['role']==(3 if a['is_local']else 1)
assert not any(e['message']in('entry_request','exit_request','switch_request','snapshot','transition')for e in active)
summary=dict(manifest=manifest,records=len(es),native_count=len(native),native=native,probe=probe,
 gaps=[e for e in es if e['event']=='read_gap'],transport_stop=stop,
 events=dict(collections.Counter(e['event']for e in es)),
 request_to_acquire_ms=acquired['t']-request['t'],return_call_to_stable_complete_ms=complete['t']-returned['t'],
 active_native=active,seat_states=seat_states,
 failures=[e for e in probe if any(x in e['event']for x in ['failed','incomplete','timeout','rejected'])])
assert not summary['failures']
(D/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:summary[k]for k in ['records','native_count','gaps','request_to_acquire_ms','return_call_to_stable_complete_ms','failures','transport_stop']},ensure_ascii=False))
for e in probe:
 if e['event']!='authority_probe_waiting':print(json.dumps(e,ensure_ascii=False))
for e in active:print(json.dumps(e,ensure_ascii=False))
