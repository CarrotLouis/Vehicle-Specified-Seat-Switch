from pathlib import Path
from collections import Counter
import json,hashlib,shutil
R=Path(__file__).resolve().parent
logs=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
src=logs/'VehicleSeatBinding-20260930-023922-15800.log'
out=R/'capture-20260930-0100';out.mkdir(exist_ok=True)
manifest=[]
for p in (src,logs/'VehicleSeatBindingDiagnostic.log'):
 data=p.read_bytes();(out/p.name).write_bytes(data);manifest.append(dict(name=p.name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
events=[json.loads(x)for x in src.read_text(encoding='utf-8-sig').splitlines() if x.strip()]
counts=Counter(e['event']for e in events)
interfaces=[e for e in events if e['event']=='binding_interface']
samples=[e for e in events if e['event']=='binding_sample']
compact=[]
for e in samples:
 d=e.get('data',{});compact.append(dict(t=e['t'],ok=e['ok'],reason=e.get('reason'),seat=d.get('seat'),slots=d.get('slots'),rotation=d.get('rotation_flag')))
report=dict(counts=dict(counts),interfaces=len(interfaces),all_interfaces_valid=all(e['ok'] and e['data']['clear_dispatch_matches'] and e['data']['state']=='observed' for e in interfaces),first_interface=interfaces[0],samples=compact,end=events[-1])
(out/'analysis.json').write_text(json.dumps(report,indent=2))
print(json.dumps(dict(counts=dict(counts),interfaces_valid=report['all_interfaces_valid'],all_samples_valid=all(e['ok']for e in samples),schemas=interfaces[0]['data']['messages'],end=events[-1]),ensure_ascii=False,indent=2))
