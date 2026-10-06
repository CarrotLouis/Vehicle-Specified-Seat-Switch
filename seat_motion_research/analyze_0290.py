"""Freeze 0.29 tank data and report actual bounded capture coverage."""
from pathlib import Path
from collections import Counter
import json,hashlib
R=Path(__file__).resolve().parent;D=R/'capture-20261005-0290'
L=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
names=['VehicleSeatIntegrated-20261005-200113-32636-17571609.log','VehicleSeatIntegratedDiagnostic.log','BingusSharedLoader.log']
D.mkdir(exist_ok=True);files=[]
for name in names:
 path=D/name
 if not path.exists():path.write_bytes((L/name).read_bytes())
 b=path.read_bytes();files.append({'name':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
index=D/'files.json'
if index.exists():assert json.loads(index.read_text())==files
else:index.write_text(json.dumps(files,indent=2))
rows=[json.loads(x)for x in (D/names[0]).read_text(encoding='utf-8').splitlines()if x.strip()]
assert rows[0]['version']=='0.29.0'
counts=Counter(x['event']for x in rows)
req=[x for x in rows if x['event']in ('reservation_request','reservation_local_owner_request')]
ops=[]
for i,x in enumerate(req):
 end=req[i+1]['t']if i+1<len(req)else rows[-1]['t']+1
 done=next((r for r in rows if x['t']<=r['t']<end and r['event']in ('reservation_operation_complete','reservation_local_owner_complete')and r.get('operation')==x['operation']),None)
 ops.append({'request':x,'complete':done,'duration_ms':done['t']-x['t']if done else None})
clears=[x for x in rows if x['event']=='tank_steer_reset_preflight'];windows=[]
for i,x in enumerate(clears):
 end=clears[i+1]['t']if i+1<len(clears)else rows[-1]['t']+1
 after=next((r for r in rows if x['t']<=r['t']<end and r['event']=='tank_steer_reset_returned'),None)
 samples=[r for r in rows if x['t']<=r['t']<end and r['event']=='tank_steer_reset_window']
 windows.append({'preflight':x,'returned':after,'samples':samples})
errors=[x for x in rows if any(w in x['event']for w in ('error','failed','gap','overflow','cancelled'))or x['event']=='reservation_stopped']
friends=[x for x in rows if x['event']=='remote_pose_watch_sample']
transitions=[x for x in rows if x['event']=='remote_pose_transition']
friend_summary={}
for x in friends:
 d=x['data'];a=friend_summary.setdefault(d['avatar'],{'identity':{'unit':d['unit'],'network_unit':d['network_unit']},'samples':0,'rotation_flags':Counter(),'layers':{},'seats':Counter(),'first_t':x['t'],'last_t':x['t']})
 a['samples']+=1;a['last_t']=x['t'];a['rotation_flags'][str(d.get('rotation_flag'))]+=1
 a['seats'][str(d['seat']['current'])]+=1
 for i,value in enumerate(d['states']):a['layers'].setdefault(str(i),Counter())[str(value)]+=1
result={'file':names[0],'start':rows[0],'end':rows[-1],'events':dict(counts),'operations':ops,'tank_windows':windows,
 'friend_summary':friend_summary,'friend_transitions':transitions,'errors':errors}
(D/'analysis.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'version':rows[0]['version'],'end':rows[-1],'operations':len(ops),'completed':sum(bool(x['complete'])for x in ops),'errors':errors,'remote_samples':len(friends),'remote_transitions':len(transitions)},ensure_ascii=False))
for x in ops:print(json.dumps({'op':x['request']['operation'],'t':x['request']['t'],'route':[x['request']['source'],x['request']['target']],'kind':x['request']['event'],'ms':x['duration_ms']},ensure_ascii=False))
for x in windows:
 pre=x['preflight'];after=x['returned'];data=pre['data'];samples=x['samples']
 print(json.dumps({'tank_t':pre['t'],'vehicle':pre['vehicle'],'before':[data['driver_command_steer'],data['input_steer'],data['replicated_steer'],data['replicated_pivot_mode']],
  'after':[after['data'][k]for k in ['input_steer','replicated_steer','replicated_pivot_mode']]if after else None,
  'samples':len(samples),'post_steer':sorted(set(round(r['data']['input_steer'],7)for r in samples)),
  'post_pivot':sorted(set(r['data']['replicated_pivot_mode']for r in samples)),
  'post_active':sorted(set(r['data']['driver_active']for r in samples)),
  'runtime_vectors':{'first':samples[0]['data']['runtime_vector_offset_57c'],'last':samples[-1]['data']['runtime_vector_offset_57c']}if samples else None},ensure_ascii=False))
print(json.dumps({'friend_summary':friend_summary},ensure_ascii=False))
for x in transitions:
 print(json.dumps({'friend_t':x['t'],'avatar':x['avatar'],'seat':[(x.get('seat')or{}).get(k)for k in ['collection','current','role','transitioning']],
  'installer_seat':[(x.get('installer_seat')or{}).get(k)for k in ['current','role']],'owned':x['owned_local']},ensure_ascii=False))
