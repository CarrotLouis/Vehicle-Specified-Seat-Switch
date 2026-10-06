"""Freeze and index the user-labelled 0.23.0 captures, no live process access."""
from pathlib import Path
import collections, hashlib, json, shutil

ROOT=Path(__file__).resolve().parents[1]
SRC=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
DEST=ROOT/'work/seat_motion_research/capture-20261004-0230'
DEST.mkdir(parents=True,exist_ok=True)
sessions=[
 ('host','VehicleSeatIntegrated-20261004-161830-20256-320251000.log'),
 ('excluded_join_failure','VehicleSeatIntegrated-20261004-162801-40444-320822343.log'),
 ('guest','VehicleSeatIntegrated-20261004-163124-16760-321025062.log')]
files=[]
for role,name in sessions+[('latest_status','VehicleSeatIntegratedDiagnostic.log'),('latest_loader','BingusSharedLoader.log')]:
 data=(SRC/name).read_bytes();target=DEST/name
 if target.exists():assert target.read_bytes()==data,'frozen evidence changed'
 else:shutil.copyfile(SRC/name,target)
 files.append(dict(role=role,name=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))

reports={}
for role,name in sessions:
 rows=[json.loads(line)for line in(DEST/name).read_text(encoding='utf-8-sig').splitlines()if line.strip()]
 assert rows[0]['event']=='start'and rows[0]['version']=='0.23.0'
 operations=[];current=None
 for row in rows:
  event=row['event']
  if event=='integrated_request_attempt':
   current=dict(number=row['number'],request_t=row['t'],events=[],samples=[],pre_samples=[])
   operations.append(current)
  if current is not None:
   if event.startswith('integrated_')or event=='ownership_loan_only_verified':current['events'].append(row)
   if event=='physics_motion_sample':current['samples'].append(row)
   if event=='physics_motion_window':current['pre_samples']=row['pre_samples']
 motions=[r for r in rows if r['event']=='physics_motion_sample']
 steering=[r for r in rows if r['event']=='steering_watch_sample']
 gaps=[r for r in rows if r['event'].endswith('_gap')]
 report=dict(name=name,role=role,start=rows[0],end=rows[-1],event_counts=dict(collections.Counter(r['event']for r in rows)),
  actor_counts=dict(collections.Counter(r['actor_count']for r in motions)),
  gap_reasons=dict(collections.Counter(r.get('reason','unspecified')for r in gaps)),gap_examples=gaps[:3],
  handoff_samples=sum('handoff_properties'in r for r in motions),spin_samples=sum('spin'in r for r in steering),
  spin_gap_reasons=dict(collections.Counter(r['spin_gap']for r in steering if 'spin_gap'in r)),
  steering_samples=steering,operations=operations)
 reports[role]=report
 compact={k:v for k,v in report.items()if k not in('operations','steering_samples','gap_examples')}
 print(json.dumps(compact,ensure_ascii=False,indent=2))
 for op in operations:
  bounds=[{k:r.get(k)for k in('t','stage','native_speed','owner','owner_serial','physical_position','linear_velocity','angular_velocity')}
          for r in op['samples']if r['stage']!='background']
  print('OP',role,op['number'],json.dumps(bounds,ensure_ascii=False))
 if gaps:print('GAP EXAMPLES',json.dumps(gaps[:2],ensure_ascii=False))
 if report['handoff_samples']:
  print('PROPERTY EXAMPLE',json.dumps(next(r['handoff_properties']for r in motions if 'handoff_properties'in r),ensure_ascii=False))
 if report['spin_samples']:
  print('SPIN EXAMPLE',json.dumps(next(r for r in steering if 'spin'in r),ensure_ascii=False))

reports['user_observation']={
 'host':'First launch installer host. Four released-W trials: first only camera deceleration/hitch with apparently unaffected motion; second/third stopped; fourth retained a small speed. Other prescribed steps completed.',
 'excluded':'Second launch could not join friend; ignore for feature/motion conclusions.',
 'guest':'Third launch friend host; every trigger reported speed to zero.',
 'tank':'User performed requested natural tank steering/exit at end of each valid test; model/cause not assumed from statement.'}
(DEST/'files.json').write_text(json.dumps(files,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(DEST/'analysis.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
