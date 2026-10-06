from pathlib import Path
from collections import Counter
import json,hashlib
W=Path(__file__).resolve().parent;old=W/'seat_configurable_network_test';out=old/'capture-20261001-0110'
name='VehicleSeatIntegrated-20261001-135022-22620-52163453.log'
e=[json.loads(s)for s in(out/name).read_text(encoding='utf-8-sig').splitlines()if s.strip()]
complete=[x for x in e if x['event']=='integrated_operation_complete']
assert [x['seat']for x in complete]==[4,1,2,0,3,1,2,1]
assert [x['authority_path']for x in complete]==['already_local']*6+['borrowed_returned']*2
keys=[x for x in e if x['event']=='seat_input'and x.get('target')==4 and x['t']>480000]
assert len(keys)==17
assert not any(x['event']=='integrated_request_attempt'and x['target']==4 for x in e)
bad=[]
for k in keys:
 changed=[]
 for x in e:
  if k['t']<x['t']<=k['t']+1800 and x['event']=='state':
   for a in x['data'].get('avatars',[]):
    if a['is_local']and a.get('seat',{}).get('action')in(15,16,17,19,20,21):
     changed.append(dict(t=x['t'],seat=a['seat']))
 if changed:bad.append(dict(key=k,lean=changed[:5]))
assert bad
report=dict(main=name,counts=Counter(x['event']for x in e),complete=complete,gunner_key_requests=len(keys),failed_gunner_authority_requests=0,
 root_cause='CTRL+MOUSE2 raises same-seat lean17/21 (front15/19); snapshot returns transition_in_progress/pending and dispatcher unconditionally erases queued target. No gunner authority request or mutation was issued.',examples=bad[:2],
 scope='User confirms one installer-host run only; other archived launches are not promoted to visually verified host/guest success.')
(out/'analysis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
d=W/'deepseek_review_20261001/unified_input';d.mkdir(parents=True,exist_ok=True)
p=Path(r'E:\Document\deepseek-harness\default-workspace\vss-project\outputs\DEEPSEEK_UNIFIED_INPUT_BOUNDARIES_20261001.md');b=p.read_bytes()
(d/p.name).write_bytes(b);(d/'manifest.json').write_text(json.dumps(dict(source=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()),indent=2))
(d/'REVIEW.md').write_text('''# Final DS report review
20 directed routes/counts are correct; scopes agree broadly. Corrections: key162 is LCTRL, not RCTRL; counting mock keywords is not substitute coverage; tests use engine/RPC substitutes. README Chinese is valid UTF8 in primary (verified), DS encoding failure does not show source corruption. Owner is independent of coordinator/host; latest user confirms installer-host only. Complete() sets cooldown=now+10 explicitly. No static report finding explains actual lean gap: primary log review establishes dispatcher erases queue when native snapshot is briefly nil.
User explicitly ended DeepSeek delegation on2026-10-01. Do not generate or send more DS tasks. Report preserved as raw and reviewed; no DS code merged.
''',encoding='utf-8')
R=W/'seat_input_gap_fix';assert not R.exists();R.mkdir()
for p in old.iterdir():
 if p.is_file()and p.suffix in('.lua','.py','.txt')and p.name not in('bundled.lua','check.lua'):
  (R/p.name).write_text(p.read_text(encoding='utf-8').replace('seat_configurable_network_test','seat_input_gap_fix').replace('0.11.0','0.11.1'),encoding='utf-8')
print(json.dumps(dict(complete_targets=[x['seat']for x in complete],gunner_key_requests=len(keys),matching_lean_examples=len(bad),new=str(R)),ensure_ascii=False))
