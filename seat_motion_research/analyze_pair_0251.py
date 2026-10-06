"""Freeze the new paired coast run; never invent values from missing events."""
from pathlib import Path
import collections
import hashlib
import json
import shutil

R = Path(__file__).resolve().parent
C = R/'capture-20261004-0251-paired'
LOCAL = Path(r'C:/Users/Administrator/AppData/Local/CowboyBingus/Helldivers2/Logs')
FRIEND = Path(r'E:/下载/QQ Download')
F = [
    ('driver', FRIEND/'VehicleSeatDriverObserver-20261004-223837-28260-212363218.log'),
    ('driver_status', FRIEND/'VehicleSeatDriverObserverDiagnostic.log'),
    ('driver_loader', FRIEND/'BingusSharedLoader.log'),
    ('installer', LOCAL/'VehicleSeatIntegrated-20261004-223819-41344-343039875.log'),
    ('installer_status', LOCAL/'VehicleSeatIntegratedDiagnostic.log'),
    ('installer_loader', LOCAL/'BingusSharedLoader.log'),
]
C.mkdir(exist_ok=True)
if (C/'files.json').exists():
    files = json.loads((C/'files.json').read_text(encoding='utf-8'))
    for f in files:
        b = (C/f['stored']).read_bytes()
        assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256']
else:
    files = []
    for role, src in F:
        b = src.read_bytes()
        directory = C/('friend' if role.startswith('driver') else 'installer')
        directory.mkdir(exist_ok=True)
        dst = directory/src.name
        if dst.exists():
            assert dst.read_bytes()==b, 'immutable evidence changed'
        else:
            shutil.copyfile(src, dst)
        files.append(dict(role=role, name=src.name, stored=str(dst.relative_to(C)),
                          bytes=len(b), sha256=hashlib.sha256(b).hexdigest()))
    (C/'files.json').write_text(json.dumps(files,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
result = {}
for role in ['driver','installer']:
    f = next(x for x in files if x['role']==role)
    rows = [json.loads(s) for s in (C/f['stored']).read_text(encoding='utf-8-sig').splitlines() if s.strip()]
    counts = dict(collections.Counter(r['event'] for r in rows))
    result[role] = dict(start=rows[0],end=rows[-1],events=counts,
                        gaps=[r for r in rows if r['event'].endswith('_gap')])
    print(role.upper(), 'bytes', f['bytes'], 'SHA256', f['sha256'])
    print('COUNTS', json.dumps(counts))
    print('START', json.dumps(rows[0],ensure_ascii=False)[:4200])
    print('END', json.dumps(rows[-1],ensure_ascii=False)[:1800])
    for event in ['driver_watch_started','driver_authority_observed_change','driver_physics_sample',
                  'pose_call_ready','native_motion_api_call','integrated_request_attempt',
                  'integrated_return_invoked','integrated_ownership_return_confirmed','pose_call_stopped']:
        selected = [r for r in rows if r['event']==event]
        for r in (selected[:1] if event in ['driver_physics_sample','native_motion_api_call'] else selected[:5]):
            print(event,json.dumps(r,ensure_ascii=False)[:6800])
    if result[role]['gaps']:
        print('GAPS',json.dumps(result[role]['gaps'],ensure_ascii=False)[:3200])
(C/'summary.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS immutable paired originals frozen; data availability must be assessed before causal claims')
