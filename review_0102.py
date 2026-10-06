from pathlib import Path
from collections import Counter
import json,hashlib
W=Path(__file__).resolve().parent
out=W/'seat_rear_weapon_diagnostic/capture-20260930-0102';out.mkdir(exist_ok=True)
logs=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
names=['VehicleSeatIntegrated-20260930-134308-13428-496246593.log','VehicleSeatIntegratedDiagnostic.log','VehicleSeatSwitch.log','BingusSharedLoader.log']
manifest=[]
for name in names:
 b=(logs/name).read_bytes();(out/name).write_bytes(b)
 manifest.append(dict(name=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
events=[json.loads(x)for x in (out/names[0]).read_text(encoding='utf-8-sig').splitlines()if x.strip()]
counts=Counter(e['event']for e in events)
important=[e for e in events if e['event'] in ('start','end','integrated_operation_complete','integrated_ownership_return_confirmed','sync_weapon_clear_invoking','sync_personal_bind_invoking','integrated_cancelled','integrated_stopped','integrated_incomplete','integrated_aborted_and_returned')]
assert next(e for e in events if e['event']=='start')['version']=='0.10.2'
assert [e['seat']for e in events if e['event']=='integrated_operation_complete']==[4,2,4,3,4,1]
assert counts['integrated_ownership_return_confirmed']==6 and counts['sync_weapon_pair_calls_returned']==3
assert not any(counts[k]for k in ('integrated_cancelled','integrated_stopped','integrated_incomplete','integrated_aborted_and_returned','read_gap'))
(out/'analysis.json').write_text(json.dumps(dict(counts=counts,important=important,user_observation='Passed without anomalies; guest M102 six-step rear weapon route, two players, friend hosts/drives.'),ensure_ascii=False,indent=2))
print(json.dumps({'counts':counts,'seats':[e['seat']for e in important if e['event']=='integrated_operation_complete']},indent=2))
ds=Path(r'E:\Document\deepseek-harness\default-workspace\vss-project\outputs')
dest=W/'deepseek_review_20260930/native_routes';dest.mkdir(exist_ok=True)
manifest=[]
for name in ['DEEPSEEK_NATIVE_ROUTE_REVIEW_20260930.md','DEEPSEEK_NATIVE_ROUTE_REVIEW_20260930.json','verify_native_routes_20260930.py','verify_native_routes_20260930.json']:
 b=(ds/name).read_bytes();(dest/name).write_bytes(b);manifest.append(dict(name=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('Frozen 0102 success and DS route artifacts')
