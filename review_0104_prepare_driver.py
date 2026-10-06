from pathlib import Path
from collections import Counter
import json,hashlib
W=Path(__file__).resolve().parent;out=W/'seat_host_weapon_diagnostic/capture-20260930-0104';out.mkdir(exist_ok=True)
L=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
names=['VehicleSeatIntegrated-20260930-190732-47496-515709906.log','VehicleSeatIntegratedDiagnostic.log','VehicleSeatSwitch.log','BingusSharedLoader.log'];manifest=[]
for name in names:
 b=(L/name).read_bytes();(out/name).write_bytes(b);manifest.append(dict(name=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
ev=[json.loads(x)for x in (out/names[0]).read_text(encoding='utf-8-sig').splitlines()if x.strip()];counts=Counter(e['event']for e in ev)
complete=[e for e in ev if e['event']=='integrated_operation_complete'];assert [e['seat']for e in complete]==[4,2,4,3,4,1]
assert all(e['authority_path']=='borrowed_returned'for e in complete)and counts['integrated_ownership_return_confirmed']==6
assert not any(counts[e]for e in ['integrated_cancelled','integrated_stopped','integrated_incomplete','read_gap','integrated_local_authority_selected'])
assert next(e for e in ev if e['event']=='start')['version']=='0.10.4'
imp=[e for e in ev if e['event'] in ['start','end','integrated_operation_complete','sync_weapon_clear_invoking','sync_personal_bind_invoking','integrated_ownership_return_confirmed']]
(out/'analysis.json').write_text(json.dumps(dict(counts=counts,important=imp,user_observation='Installer-host M102 six-step roundtrip passed, friend unmodded driver; all operations borrowed_returned. Already-local path not exercised.'),ensure_ascii=False,indent=2))
print(json.dumps(dict(counts=counts,paths=[e['authority_path']for e in complete]),indent=2))
d=W/'deepseek_review_20260930/input_integration';d.mkdir(exist_ok=True)
src=Path(r'E:\Document\deepseek-harness\default-workspace\vss-project\outputs\DEEPSEEK_INPUT_INTEGRATION_INVENTORY_20260930.md');b=src.read_bytes();(d/src.name).write_bytes(b)
(d/'manifest.json').write_text(json.dumps(dict(source=str(src),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()),indent=2))
R=W/'seat_driver_weapon_diagnostic';assert not R.exists();R.mkdir()
for p in (W/'seat_host_weapon_diagnostic').iterdir():
 if p.is_file()and p.suffix in ('.lua','.py','.txt')and p.name not in ('bundled.lua','check.lua'):
  (R/p.name).write_text(p.read_text(encoding='utf-8').replace('seat_host_weapon_diagnostic','seat_driver_weapon_diagnostic').replace('0.10.4','0.10.5'),encoding='utf-8')
s=(W/'seat_switch/src/driver.lua').read_text().replace("s.owned and s.player_count==1 and s.peer_count<=1 and s.profile.roles[s.node+1]==1","s.owned and s.vehicle=='m102'and s.player_count==2 and s.peer_count==2 and s.node==0 and s.profile.roles[s.node+1]==1").replace('local solo driver','local M102 two-player driver')
(R/'driver.lua').write_text(s)
s=(W/'seat_switch/tests/test_driver.lua').read_text().replace('work/seat_switch/src/driver.lua','work/seat_driver_weapon_diagnostic/driver.lua').replace('owned=true,player_count=1,peer_count=1,profile=profile.tables.bastion','owned=true,vehicle="m102",player_count=2,peer_count=2,profile=profile.tables.m102').replace("s.player_count=2;assert(not pcall(d.prepare,s) and writes==count,'Online must refuse');s.player_count=1","s.player_count=3;assert(not pcall(d.prepare,s) and writes==count,'Three players must refuse');s.player_count=2")
(R/'test_driver.lua').write_text(s)
print('0104 accepted as borrowed path only; isolated0105 created')
