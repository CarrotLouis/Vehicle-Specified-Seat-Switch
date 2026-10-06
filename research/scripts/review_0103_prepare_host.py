from pathlib import Path
from collections import Counter
import json,hashlib
W=Path(__file__).resolve().parent
out=W/'seat_flamer_weapon_diagnostic/capture-20260930-0103';out.mkdir(exist_ok=True)
logs=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
names=['VehicleSeatIntegrated-20260930-185118-42548-514736359.log','VehicleSeatIntegratedDiagnostic.log','VehicleSeatSwitch.log','BingusSharedLoader.log']
manifest=[]
for name in names:
 b=(logs/name).read_bytes();(out/name).write_bytes(b);manifest.append(dict(name=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
events=[json.loads(x)for x in (out/names[0]).read_text(encoding='utf-8-sig').splitlines()if x.strip()]
counts=Counter(e['event']for e in events)
assert next(e for e in events if e['event']=='start')['version']=='0.10.3'
assert [e['seat']for e in events if e['event']=='integrated_operation_complete']==[2,1]
assert counts['integrated_ownership_return_confirmed']==2 and counts['sync_weapon_pair_calls_returned']==1
assert not any(counts[k]for k in ('integrated_cancelled','integrated_stopped','integrated_incomplete','integrated_aborted_and_returned','read_gap'))
important=[e for e in events if e['event'] in ('start','end','integrated_operation_complete','integrated_ownership_return_confirmed','sync_weapon_clear_invoking','sync_personal_bind_invoking')]
(out/'analysis.json').write_text(json.dumps(dict(counts=counts,important=important,user_observation='M104 guest passenger-flamer roundtrip passed without anomalies; unmodded friend host/driver.'),ensure_ascii=False,indent=2))
print(json.dumps(dict(counts=counts),indent=2))
ds=Path(r'E:\Document\deepseek-harness\default-workspace\vss-project\outputs\DEEPSEEK_NETWORK_GUARD_INVENTORY_20260930.md')
d=W/'deepseek_review_20260930/network_guards';d.mkdir(exist_ok=True);b=ds.read_bytes();(d/ds.name).write_bytes(b)
(d/'manifest.json').write_text(json.dumps(dict(source=str(ds),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()),indent=2))
R=W/'seat_host_weapon_diagnostic';assert not R.exists();R.mkdir()
for p in (W/'seat_rear_weapon_diagnostic').iterdir():
 if p.is_file()and p.suffix in ('.lua','.py','.txt')and p.name not in ('bundled.lua','check.lua'):
  s=p.read_text(encoding='utf-8').replace('seat_rear_weapon_diagnostic','seat_host_weapon_diagnostic').replace('0.10.2','0.10.4')
  (R/p.name).write_text(s,encoding='utf-8')
print('0103 accepted; DS guard inventory frozen; isolated0104 created')
