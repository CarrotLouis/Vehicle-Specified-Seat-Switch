from pathlib import Path
from collections import Counter
import json
W=Path(__file__).resolve().parent;old=W/'seat_input_gap_fix'
O=old/'capture-20261001-0111'
e=[json.loads(x)for x in (O/'VehicleSeatIntegrated-20261001-142458-30024-54239109.log').read_text(encoding='utf-8-sig').splitlines()if x.strip()]
c=Counter(x['event']for x in e)
done=[x for x in e if x['event']=='integrated_operation_complete']
assert [x['seat']for x in done]==[4,2,4,3,4,1] and all(x['authority_path']=='borrowed_returned'for x in done)
assert c['integrated_ownership_return_confirmed']==6 and c['sync_weapon_pair_calls_returned']==3
assert not any(c[n]for n in ['integrated_stopped','integrated_cancelled','integrated_incomplete','read_gap'])
assert any(x['event']=='seat_input'and x['reason']=='occupied'and x.get('target')==0 for x in e)
R=W/'seat_fast_settle_test';assert not R.exists();R.mkdir()
for p in old.iterdir():
 if p.is_file()and p.suffix in('.lua','.py','.txt','.json')and p.name not in('bundled.lua','check.lua','package.json','docs.py','docs_fix.py'):
  (R/p.name).write_text(p.read_text(encoding='utf-8').replace('seat_input_gap_fix','seat_fast_settle_test').replace('0.11.1','0.11.2'),encoding='utf-8')
p=R/'probe.lua';s=p.read_text();s=s.replace(' local self={count=0', ' local settle=dynamic and .2 or 3\n local self={count=0')
s=s.replace('self.ready_at=math.max(stable_since+3,cooldown)','self.ready_at=math.max(stable_since+settle,cooldown)').replace('if now-stable_since<3 or now<cooldown then event(', 'if now-stable_since<settle or now<cooldown then event(')
p.write_text(s)
p=R/'entry.lua';s=p.read_text().replace('key_issues=#issues,config_issues=issues,','key_issues=#issues,config_issues=issues,settle_seconds=.2,');p.write_text(s)
# The original 0110 replay remains the intentional failing control, not overwritten.
print('0111 accepted:6completed/6returned,3 personal binds,occupied refusal; isolated0112 dynamic settle=.2s')
