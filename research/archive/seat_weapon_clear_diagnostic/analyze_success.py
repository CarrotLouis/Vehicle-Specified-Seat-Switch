from pathlib import Path
from collections import Counter
import json,hashlib
R=Path(__file__).resolve().parent;out=R/'capture-20260930-0101';out.mkdir(exist_ok=True)
L=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
names=['VehicleSeatIntegrated-20260930-131835-5060-494773359.log','VehicleSeatIntegratedDiagnostic.log','VehicleSeatSwitch.log','BingusSharedLoader.log']
manifest=[]
for name in names:
 src=L/name
 if not src.exists():continue
 b=src.read_bytes();(out/name).write_bytes(b);manifest.append(dict(name=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
events=[json.loads(x)for x in (out/names[0]).read_text(encoding='utf-8-sig').splitlines()if x.strip()]
counts=Counter(e['event']for e in events)
important=[e for e in events if e['event'] in ('start','end','integrated_operation_complete','integrated_ownership_return_confirmed','sync_weapon_clear_invoking','sync_personal_bind_invoking','sync_weapon_pair_calls_returned','integrated_cancelled','integrated_aborted_and_returned','integrated_stopped','integrated_incomplete')]
report=dict(counts=dict(counts),important=important,user_observation='User reports test passed, no anomalies; scope guest M102 passenger1-gunner4-passenger1, unmodded friend hosts/drives.')
(out/'analysis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'counts':dict(counts),'milestones':[{k:v for k,v in e.items()if k not in ('before','after','interface','compatibility')}for e in important]},ensure_ascii=False,indent=2))
