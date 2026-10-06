from pathlib import Path
import collections, hashlib, json, shutil

ROOT=Path(__file__).resolve().parents[1]
SRC=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
DEST=ROOT/'work/seat_motion_research/capture-20261004-0221'
DEST.mkdir(parents=True,exist_ok=True)
names=['VehicleSeatIntegrated-20261004-144356-26884-314577640.log',
       'VehicleSeatIntegratedDiagnostic.log','BingusSharedLoader.log']
files=[]
for name in names:
    data=(SRC/name).read_bytes();dest=DEST/name
    if dest.exists():assert dest.read_bytes()==data,'frozen evidence changed'
    else:shutil.copyfile(SRC/name,dest)
    files.append(dict(name=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
rows=[json.loads(line)for line in(DEST/names[0]).read_text(encoding='utf-8-sig').splitlines()if line.strip()]
operations=[];current=None
for row in rows:
    event=row['event']
    if event=='integrated_request_attempt':
        current={'number':row['number'],'condition':['parked','held_W','coasting'][row['number']-1],
                 'request_t':row['t'],'events':[],'samples':[],'pre_samples':[]}
        operations.append(current)
    if current is not None:
        if event.startswith('integrated_')or event=='ownership_loan_only_verified':current['events'].append(row)
        if event=='physics_motion_sample':current['samples'].append(row)
        if event=='physics_motion_window':current['pre_samples']=row['pre_samples']
motion=[r for r in rows if r['event']=='physics_motion_sample']
gaps=[r for r in rows if r['event']=='physics_motion_gap']
summary={'files':files,'start':rows[0],'end':rows[-1],
         'event_counts':dict(collections.Counter(r['event']for r in rows)),
         'ready':[r for r in rows if r['event']=='physics_motion_ready'],
         'gap_reasons':dict(collections.Counter(r['reason']for r in gaps)),
         'gap_example':gaps[:2],
         'actor_counts':dict(collections.Counter(r['actor_count']for r in motion)),
         'actor_handles':dict(collections.Counter(r['actor_handle']for r in motion)),
         'actor_flags':dict(collections.Counter(hex(r['actor_flags'])for r in motion)),
         'operations':operations,
         'user_observation':'Installer-host round, exactly three prescribed triggers; no new anomalies, deceleration persists. Order parked, held W, coasting. User explicitly confirmed operation 3 actually stopped the vehicle and interrupted coasting; this round is not the older host-coast camera-only exception.'}
for name,data in [('files.json',files),('analysis.json',summary)]:
    (DEST/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items()if k!='operations'},ensure_ascii=False,indent=2))
for op in operations:
    print('\nOPERATION',op['number'],op['condition'])
    for e in op['events']:
        if e['event']!='integrated_state':print(json.dumps(e,ensure_ascii=False))
    print('BOUNDARY SAMPLES')
    for r in op['samples']:
        if r['stage']!='background':print(json.dumps(r,ensure_ascii=False))
    print('PRE/POST POSITION AND VELOCITY')
    samples=op['pre_samples']+op['samples']
    seen=set()
    for r in samples:
        if r['t_sample_ms']in seen:continue
        seen.add(r['t_sample_ms'])
        print(json.dumps({k:r.get(k)for k in ['t','t_sample_ms','stage','phase','owner','owner_serial','native_speed',
              'linear_velocity','angular_velocity','physical_position','position_delta_native_per_second','actor_flags','actor_aux']},ensure_ascii=False))
