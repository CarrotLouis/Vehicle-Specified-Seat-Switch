from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;out=R/'analysis-20260927-052';out.mkdir(exist_ok=True)
logs=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
name='VehicleSeatAuthority-20260927-132902-7604-236200562.log'
files={}
for n in (name,'VehicleSeatAuthorityDiagnostic.log','VehicleSeatSwitch.log','BingusSharedLoader.log'):
 p=out/n
 if not p.exists():p.write_bytes((logs/n).read_bytes())
 files[n]=hashlib.sha256(p.read_bytes()).hexdigest()
es=[json.loads(l)for l in(out/name).read_text().splitlines()]
native=[e for e in es if e['event'].startswith('native_')]
stop=next(e for e in es if e['event']=='transport_stopped')
assert es[0]['version']=='0.5.2'
assert [e['sequence']for e in native]==list(range(1,len(native)+1))
assert all(e['valid_mask']==(1<<e['argument_count'])-1 for e in native)
assert stop['events']==len(native)and stop['dropped_total']==stop['restore_flags']==0
probe=[e for e in es if e['event'].startswith('authority_probe_')]
assert not any(e['event'] in ('authority_probe_armed','authority_probe_request_sent')for e in probe)
preflight=[e for e in es if e['event']=='authority_interface_preflight']
summary=dict(files=files,records=len(es),native_count=len(native),gaps=[e for e in es if e['event']=='read_gap'],probe=probe,preflight=preflight,
 conclusion='Ownership map fixed including overflow408/319; next busy check incorrectly keys vehicle.unit instead of network_unit. No active request occurred.')
(out/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
