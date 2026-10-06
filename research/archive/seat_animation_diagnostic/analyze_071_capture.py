"""Summarize immutable 0.7.1 runtime observations without touching the game."""
from pathlib import Path
import json,collections
R=Path(__file__).resolve().parent/'capture-20260928-071'
rows=[json.loads(line)for line in (R/'VehicleSeatIntegrated-20260928-132139-37232-322157125.log').read_text().splitlines()]
assert rows[0]['version']=='0.7.1'
native=[r for r in rows if r['event'].startswith('native_')]
assert [r['sequence']for r in native]==list(range(1,len(native)+1))
for operation in (1,2):
 samples=[r for r in rows if r['event']=='animation_watch_sample'and r['operation']==operation]
 applied=next(r for r in samples if r['phase']=='after_pose_apply')
 after=samples[samples.index(applied):]
 target=(106,62)if operation==1 else(112,68)
 assert all((r['states'][0],r['states'][13])==target for r in after)
 assert all(not r['queue_truncated']for r in samples)
 print(operation,len(samples),'written state observations; target vehicle layers stable through end')
failures=[r for r in rows if r['event']in ('animation_watch_gap','read_gap','protocol_gap','integrated_cancelled','integrated_stopped','integrated_incomplete')]
assert not failures
stop=next(r for r in rows if r['event']=='transport_stopped')
assert stop['events']==len(native)and stop['dropped_total']==stop['restore_flags']==0
print(len(rows),'records;',len(native),'native messages; no gaps; both operations completed')
