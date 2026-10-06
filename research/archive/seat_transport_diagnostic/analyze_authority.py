"""Freeze and correlate the user's 0.4.3 normal-operation capture."""
from pathlib import Path
import collections, hashlib, json, shutil
R=Path(__file__).resolve().parent;OUT=R/'authority-20260926';OUT.mkdir(exist_ok=True)
LOGS=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
NAME='VehicleSeatTransport-20260926-131328-20056-148866031.log'
p=OUT/NAME
if not p.exists():shutil.copyfile(LOGS/NAME,p)
es=[json.loads(l) for l in p.read_text().splitlines()]
assert es[0]['version']=='0.4.3'
native=[e for e in es if e['event'].startswith('native_')]
assert [e['sequence'] for e in native]==list(range(1,len(native)+1))
assert all(e['valid_mask']==(1<<e['argument_count'])-1 for e in native)
ready=next(e for e in es if e['event']=='transport_ready')
stop=next(e for e in es if e['event']=='transport_stopped')
assert stop['events']==len(native) and stop['dropped_total']==stop['restore_flags']==0 and stop['reason']=='shutdown'
assert len(ready['registry'])==15 and all(r['found'] for r in ready['registry'])
registry={r['name']:r for r in ready['registry']}
assert registry['authority_request']['index']==525 and registry['authority_owned']['index']==575
assert all(registry[n]['type_indices']==[107,91] for n in ['authority_request','authority_owned'])
gaps=[e for e in es if e['event']=='read_gap']
assert all(e['t']<ready['t'] for e in gaps),'Post-install gap needs individual review'
states=[e for e in es if e['event']=='state']
aliases=[e for e in es if e['event']=='protocol_peer_alias']
windows=[]
for e in native:
    if not e['message'].startswith('authority'):continue
    windows.append(dict(event=e,states=[s for s in states if abs(s['t']-e['t'])<2200],
                        adjacent_messages=[x for x in native if abs(x['t']-e['t'])<250]))
summary=dict(source=NAME,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),ready=ready,stop=stop,
             read_gaps=gaps,aliases=aliases,authority_windows=windows,
             messages=[dict(direction=k[0],message=k[1],count=v) for k,v in collections.Counter((e['event'],e['message'])for e in native).items()])
(OUT/'summary.json').write_text(json.dumps(summary,indent=2))
for name in ['VehicleSeatTransportDiagnostic.log','VehicleSeatSwitch.log','BingusSharedLoader.log']:
    if not(OUT/name).exists():shutil.copyfile(LOGS/name,OUT/name)
print(json.dumps(dict(sha256=summary['sha256'],events=len(native),gaps=gaps,aliases=aliases)))
for e in native:
    print(e['t'],e['sequence'],e['event'],e['message'],e['values'],e['peers'],hex(e.get('caller_rva',0)))
last=None
for s in states:
    if not s['data']['vehicles']:continue
    key=dict(avatars=[dict(net=a['network_unit'],local=a['is_local'],seat=a['seat']['current'],collection=a['seat']['collection'],role=a['seat']['role'],reserved=a['seat']['reserved']) for a in s['data']['avatars']],vehicles=s['data']['vehicles'])
    if key!=last:
        print('STATE',s['t'],json.dumps(key));last=key
