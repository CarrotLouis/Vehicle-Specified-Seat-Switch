from pathlib import Path
from collections import Counter
import json, hashlib
W=Path(__file__).resolve().parent
out=W/'seat_driver_weapon_diagnostic/capture-20260930-0105'
ev=[json.loads(s) for s in (out/'VehicleSeatIntegrated-20260930-192915-34072-517013062.log').read_text(encoding='utf-8-sig').splitlines() if s.strip()]
c=Counter(x['event'] for x in ev)
complete=[x for x in ev if x['event']=='integrated_operation_complete']
assert [x['seat'] for x in complete]==[4,0,2,0,3,0]
assert all(x['authority_path']=='already_local' for x in complete)
assert c['integrated_local_authority_preserved']==6 and c['sync_weapon_pair_calls_returned']==1
assert sum(x['event']=='integrated_local_stage' and x['stage']=='neutralize_own_driver_commands' for x in ev)==3
assert not any(c[n] for n in ['read_gap','integrated_cancelled','integrated_stopped','integrated_incomplete','integrated_request_attempt','integrated_return_invoked'])
rejected=[x for x in ev if x['event']=='integrated_trigger_rejected']
assert all(x['reason']=='settle_or_cooldown' for x in rejected)
note='Installer-host M102, friend outside: six already-local operations passed per logs and user. Native driver/front-passenger roundtrip 19:32:27–19:32:30 occurred after step2 completion19:32:23 and before step3 start19:32:39. No pending operation overlapped; no retest needed. Some presses <20s apart; three settle/cooldown rejections, no extra mutations. Host-only, two-player scope; no claim about guest-driver or three/four players.'
(out/'analysis.json').write_text(json.dumps(dict(counts=c,complete=complete,rejected=rejected,conclusion=note),ensure_ascii=False,indent=2),encoding='utf-8')
d=W/'deepseek_review_20260930/chord_overlap';d.mkdir(exist_ok=True)
src=Path(r'E:\Document\deepseek-harness\default-workspace\vss-project\outputs\DEEPSEEK_CHORD_OVERLAP_CASES_20260930.md');b=src.read_bytes()
(d/src.name).write_bytes(b)
(d/'manifest.json').write_text(json.dumps(dict(source=str(src),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()),indent=2))
(d/'REVIEW.md').write_text('''# Primary review
The 12 code values/overlap results agree with config.lua (verified by test_review.lua). Side-specific modifiers reject both sides held, as DS correctly says.
Correction: overlap=false for different primary keys does NOT mean they cannot fire in the same poll. F2+F5 or both mouse side keys can have simultaneous rising edges. A dispatcher must reject multiple seat targets independently of parse-time overlap detection.
Standalone CTRL example needs CTRL first, then SHIFT, then HOME; SHIFT-first example needs SHIFT, then CTRL, then HOME. Extra modifiers suppress the standalone binding on later edges.
Existing test_input.lua already explicitly asserts standalone CTRL vs CTRL+1 and LSHIFT vs CTRL+SHIFT+MOUSE4 overlaps. The report's broad missing-coverage wording is not evidence of absent tests. Specific HOME examples were not covered and are checked separately here.
No DS code imported; report remains raw. 0105 is now accepted for installer-host M102 already-local driver routes, not all runtime cases.
''',encoding='utf-8')
print(note)
