from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;out=R/'analysis-20260927-051';out.mkdir(exist_ok=True)
logs=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
name='VehicleSeatAuthority-20260927-025816-23064-198354531.log'
manifest={}
for n in (name,'VehicleSeatAuthorityDiagnostic.log','VehicleSeatSwitch.log','BingusSharedLoader.log'):
 p=out/n
 if not p.exists():p.write_bytes((logs/n).read_bytes())
 manifest[n]=hashlib.sha256(p.read_bytes()).hexdigest()
es=[json.loads(l)for l in(out/name).read_text().splitlines()]
native=[e for e in es if e['event'].startswith('native_')]
ready=next(e for e in es if e['event']=='transport_ready')
stop=next(e for e in es if e['event']=='transport_stopped')
assert es[0]['version']=='0.5.1'
assert [e['sequence']for e in native]==list(range(1,len(native)+1))
assert all(e['valid_mask']==(1<<e['argument_count'])-1 for e in native)
assert stop['events']==len(native)and stop['dropped_total']==stop['restore_flags']==0
gaps=[e for e in es if e['event']=='read_gap'];assert all(e['t']<ready['t']for e in gaps)
samples=[e for e in es if e['event']=='authority_lookup_sample'];assert len(samples)==6
assert all(e['data']['lookups'][0]==samples[0]['data']['lookups'][0]for e in samples)
result=dict(files=manifest,native_events=len(native),pre_ready_gaps=gaps,samples=samples,
 conclusion='Six stable identical vehicle lookups: bucket_count mislabeled capacity319; bucket242 key307 next367. Bounds must use array length at engine+640, not bucket count at+65c. Native insertion/grow confirms overflow storage beyond bucket region.')
(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(records=len(es),native=len(native),samples=len(samples),sha=manifest[name],first=samples[0]['data']['lookups'][0])))
