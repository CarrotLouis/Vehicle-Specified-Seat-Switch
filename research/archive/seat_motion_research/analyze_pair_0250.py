"""Freeze both PCs. Missing driver telemetry is a collection failure, not zero."""
from pathlib import Path
import collections
import hashlib
import json
import math
import shutil

R = Path(__file__).resolve().parent
W = R.parent
C = R / 'capture-20261004-0250-paired'
LOCAL = Path(r'C:/Users/Administrator/AppData/Local/CowboyBingus/Helldivers2/Logs')
FRIEND = Path(r'E:/下载/QQ Download')
F = [
    ('driver', FRIEND/'VehicleSeatDriverObserver-20261004-215606-8568-209812546.log'),
    ('driver_status', FRIEND/'VehicleSeatDriverObserverDiagnostic.log'),
    ('driver_loader', FRIEND/'BingusSharedLoader.log'),
    ('installer', LOCAL/'VehicleSeatIntegrated-20261004-215650-42712-340550968.log'),
    ('installer_status', LOCAL/'VehicleSeatIntegratedDiagnostic.log'),
    ('installer_loader', LOCAL/'BingusSharedLoader.log'),
]
C.mkdir(exist_ok=True)
if (C/'files.json').exists():
    files = json.loads((C/'files.json').read_text(encoding='utf-8'))
    for f in files:
        data = (C/f['stored']).read_bytes()
        assert len(data)==f['bytes'] and hashlib.sha256(data).hexdigest()==f['sha256'], 'immutable evidence changed'
else:
    files = []
    for role, src in F:
        data = src.read_bytes()
        directory = C/('friend' if role.startswith('driver') else 'installer')
        directory.mkdir(exist_ok=True)
        dest = directory/src.name
        if dest.exists():
            assert dest.read_bytes()==data, 'immutable evidence changed'
        else:
            shutil.copyfile(src, dest)
        files.append(dict(role=role,name=src.name,stored=str(dest.relative_to(C)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))

def local_m102_driver(r):
    # On-foot seat.current is also zero; require a real matching collection.
    d = r['data']
    for a in d['avatars']:
        s = a.get('seat', {})
        if not (a.get('is_local') and s.get('current')==0 and s.get('collection',0)!=0 and s.get('transitioning')==0):
            continue
        if any(v['id']==s['collection'] and v.get('name')=='m102' and v.get('seat_count')==5
               and v.get('transition_type')==26 for v in d['vehicles']):
            return True
    return False
result = {}
for role in ['driver','installer']:
    f = next(x for x in files if x['role']==role)
    rows = [json.loads(s) for s in (C/f['stored']).read_text(encoding='utf-8-sig').splitlines() if s.strip()]
    counts = dict(collections.Counter(r['event']for r in rows))
    result[role] = dict(start=rows[0],end=rows[-1],events=counts,
                        gaps=[r for r in rows if r['event'].endswith('_gap')])
    if role=='driver':
        result[role]['physical_motion_usable']=False
        result[role]['reason']='Physical reader receives read-only platform without api.ffi; first driver update failed, before arming native observer.'
        assert counts.get('driver_physics_sample',0)==0 and counts.get('native_motion_api_call',0)==0
        result[role]['occupied_state_samples']=[r for r in rows if r['event']=='state'and local_m102_driver(r)]
    else:
        origin=int(Path(f['name']).stem.rsplit('-',1)[1])
        ops=[];current=None
        for r in rows:
            if r['event']=='integrated_request_attempt':
                current=dict(number=r['number'],request_t=r['t'],events=[],physical_samples=[],native_calls=[])
                ops.append(current)
            if current:
                if r['event'].startswith('integrated_')or r['event']=='ownership_loan_only_verified':current['events'].append(r)
                if r['event']=='physics_motion_sample':current['physical_samples'].append(r)
                if r['event']=='native_motion_api_call':
                    call=dict(r,call_t=r['native_tick']-origin);current['native_calls'].append(call)
        for op in ops:
            b=next(s for s in op['physical_samples']if s['stage']=='before_authority_return')
            a=next(s for s in op['physical_samples']if s['stage']=='first_observed_authority_return')
            fresh=next(s for s in op['physical_samples']if s['t_sample_ms']>=a['t_sample_ms']and 'handoff_properties'in s and
                       s['handoff_properties']['properties']['motion_peer']['component']['hex']==s['handoff_properties']['engine_owner_hex'])
            h=fresh['handoff_properties'];lv=h['properties']['linear_velocity']['component']['values']
            op['summary']=dict(before_speed=b['native_speed'],first_return_speed=a['native_speed'],fresh_driver_rep_velocity=lv,
                fresh_driver_rep_speed=math.sqrt(sum(x*x for x in lv)),native_call_kinds=dict(collections.Counter(c['kind']for c in op['native_calls'])),
                suspect_collision=op['number']==1,condition='held_W'if op['number']<3 else'coast',
                user_reports_stop=True,driver_physics_not_observed=True)
            assert sum(e['event']=='integrated_loan_operation_complete'for e in op['events'])==1
        result[role]['operations']=ops
        result[role]['physical_motion_usable']=True
        print('INSTALLER',json.dumps([dict(number=o['number'],**o['summary'])for o in ops],ensure_ascii=False))
    print(role,counts)
result['boundary']={
    'first_trial':'User suspected obstacle collision; exclude from causal proof.',
    'remaining_trials':'Repeat held-W and coast confirmed stopped by user; installer process observed only.',
    'friend_logs':'State/loader/startup readable, but no driver physical/API observations. Never treat missing values as speed zero.',
    'root_cause_scope':'Diagnostic integration failure confirmed; gameplay slowdown cause still not established in driver process.',
}
(C/'files.json').write_text(json.dumps(files,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(C/'analysis.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS both originals frozen; driver capture failure explicitly classified, installer three returns complete')
