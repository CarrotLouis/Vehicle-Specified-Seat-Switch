"""Freeze actual 0.28.0 result and correlate tank-input rows with seat switches."""
from pathlib import Path
from collections import Counter
import hashlib,json
R=Path(__file__).resolve().parent;D=R/'capture-20261005-0280'
L=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
names=['VehicleSeatIntegrated-20261005-170430-34600-6968156.log','VehicleSeatIntegratedDiagnostic.log','BingusSharedLoader.log']
D.mkdir(exist_ok=True);files=[]
for name in names:
 path=D/name
 if not path.exists():path.write_bytes((L/name).read_bytes())
 data=path.read_bytes();files.append({'name':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
index=D/'files.json'
if index.exists():assert json.loads(index.read_text())==files
else:index.write_text(json.dumps(files,indent=2))
rows=[json.loads(line)for line in (D/names[0]).read_text(encoding='utf-8').splitlines()if line.strip()]
assert rows[0]['version']=='0.28.0';counts=Counter(x['event']for x in rows)
requests=[x for x in rows if x['event']in ('reservation_request','reservation_local_owner_request')]
states=[x for x in rows if x['event']=='state'];ops=[]
for i,request in enumerate(requests):
 limit=requests[i+1]['t']if i+1<len(requests)else rows[-1]['t']+1
 completion=next((x for x in rows if request['t']<=x['t']<limit and x['event']in ('reservation_operation_complete','reservation_local_owner_complete')and x['operation']==request['operation']),None)
 context=next((x for x in reversed(states)if x['t']<=request['t']),{})
 data=context.get('data',{});avatar=next((x for x in data.get('avatars',[])if x.get('is_local')),{});seat=avatar.get('seat',{})
 car=next((x for x in data.get('vehicles',[])if x['id']==seat.get('collection')),{})
 # Preparation can precede the published request by one frame. Use the
 # actual native-exit boundary for these rows rather than a 5 ms guess.
 preflight=next((x for x in reversed(rows)if x['t']<=request['t'] and x['event']=='tank_steer_reset_preflight'),None)
 preflight_start=preflight['t']if preflight and request['t']-preflight['t']<=50 and request['source']==0 else request['t']
 next_preflight=next((x for x in rows if x['t']>request['t'] and x['event']=='tank_steer_reset_preflight' and x['t']<limit),None)
 end=next_preflight['t']if next_preflight else limit
 related=[x for x in rows if preflight_start<=x['t']<end and(x['event'].startswith('tank_')or x['event'].startswith('reservation_')or x['event'].startswith('integrated_local_'))]
 ops.append({'request':request,'complete':completion,'duration_ms':completion['t']-request['t']if completion else None,
  'car':car,'avatars':data.get('avatars',[]),'events':related})
errors=[x for x in rows if any(w in x['event']for w in ('error','failed','stopped','gap','overflow','cancelled'))and x['event']not in ('input_priority_stopped','transport_stopped')]
result={'name':names[0],'start':rows[0],'end':rows[-1],'events':dict(counts),'operations':ops,'errors':errors}
(D/'analysis.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'version':rows[0]['version'],'requests':len(ops),'completed':sum(bool(x['complete'])for x in ops),'errors':errors},ensure_ascii=False))
for op in ops:
 print(json.dumps({'op':op['request']['operation'],'t':op['request']['t'],'vehicle':op['car'].get('name'),'car':op['car'].get('id'),
  'mode':op['request']['event'],'route':[op['request']['source'],op['request']['target']],'duration_ms':op['duration_ms']},ensure_ascii=False))
def brief(row):
 d=row.get('data',{})
 return {'t':row['t'],'event':row['event'],'vehicle':row.get('vehicle'),'car':row.get('collection'),
  'values':{k:d.get(k)for k in ('driver_active','driver_command_steer','driver_command_flags_offset_2c_to_2f','input_steer','replicated_steer','input_throttle','input_brake')},
  'command_hex':d.get('driver_command_hex')}
for op in ops:
 tank=[x for x in op['events']if x['event'].startswith('tank_steer_reset')]
 if not tank:continue
 window=[x for x in tank if x['event']=='tank_steer_reset_window']
 records=[{k:brief(x)[k]for k in ('t','event','values')}for x in tank if x['event']in ('tank_steer_reset_preflight','tank_steer_reset_returned')]
 if window:records.append({k:brief(window[-1])[k]for k in ('t','event','values')})
 print(json.dumps({'tank_op':op['request']['operation'],'records':records,'window_samples':len(window),
  'steer_range':[min(x['data']['input_steer']for x in window),max(x['data']['input_steer']for x in window)]if window else None},ensure_ascii=False))
