from pathlib import Path
import collections,json,hashlib
W=Path(__file__).resolve().parent;R=W/'seat_tank_binding_fix/capture-20261002-0182';out=W/'seat_tank_pose_fix'
runs=[];states={}
for name,role in [('VehicleSeatIntegrated-20261002-163416-4988-148396796.log','installer_host'),('VehicleSeatIntegrated-20261002-164406-31476-148987750.log','friend_host')]:
 data=(R/name).read_bytes();rows=[json.loads(l)for l in data.decode('utf-8-sig').splitlines()]
 assert rows[0]['version']=='0.18.2' and rows[-1]['event']=='end'
 counts=collections.Counter(r['event']for r in rows);model=None;op=None;completed=collections.Counter();overlay=collections.defaultdict(collections.Counter);binding=[]
 for row in rows:
  if row['event']=='integrated_state':model=json.loads(row['detail'])['vehicle']
  if row['event']=='integrated_switch_attempt':op={'vehicle':model,'source':row['source'],'target':row['target'],'messages':[]}
  if row['event']=='integrated_operation_complete':completed[model]+=1
  if row['event']=='animation_watch_sample':
   key=(model,tuple(row['states']));states.setdefault(key,{'vehicle':model,'values':row['states'],'occurrences':0})['occurrences']+=1
   overlay[model][row['states'][8]]+=1
  if row['event'] in {'sync_weapon_clear_invoking','sync_personal_bind_invoking'} and op:
   op['messages'].append({'event':row['event'],'channel':row.get('channel'),'rotation_flag':(row.get('after')or{}).get('rotation_flag')})
  if row['event']=='integrated_operation_complete' and op:
   if op['source']==0 and op['target']in [2,3]:binding.append(op)
   op=None
 runs.append(dict(name=name,role=role,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),completed=dict(completed),
  read_gaps=counts['read_gap'],drops=sum(r.get('dropped_total',0)for r in rows if r['event']=='transport_stopped'),
  animation_gaps=counts['animation_watch_gap'],recovered_input_aborts=counts['integrated_input_abort_recovered'],
  overlay_by_vehicle={k:{str(a):b for a,b in v.items()}for k,v in overlay.items()},driver_passenger_bindings=binding,clean_shutdown=True))
assert [sum(r['completed'].values())for r in runs]==[14,20]
assert all(r['read_gaps']==r['animation_gaps']==r['drops']==0 for r in runs)
assert set(runs[0]['overlay_by_vehicle']['bastion'])=={'0'}
assert set(runs[1]['overlay_by_vehicle']['bastion'])=={'237','238'}
assert all(set(r['overlay_by_vehicle']['maelstrom'])=={'0'}for r in runs)
analysis={'runs':runs,'user_report':'Installer host: no anomaly. Guest Bastion passengers aim/shoot but body stays facing forward in both views. Maelstrom and other tested behavior normal. User now authorizes trying held-steering driver-exit fix.',
 'conclusion':'Weapon replication and input-abort recovery observed. Guest Bastion has a unique Fall/Fall_Aim overlay. This is a repair candidate, not proven visual root cause. Native tank exit disables driver state; prior direct transaction omitted that call. Runtime steering state was not captured by 0.18.2.',
 'remaining':'Bastion guest aim; held A/D tank exit; 3/4-peer contexts; solo Enhanced integration and final selectable release.'}
(R/'analysis.json').write_text(json.dumps(analysis,ensure_ascii=False,indent=2),encoding='utf-8')
fixtures=list(states.values())
(out/'captured-pose-cases.json').write_text(json.dumps(fixtures,indent=2))
lua='return {'+','.join('{vehicle='+json.dumps(s['vehicle'])+',occurrences='+str(s['occurrences'])+',values={'+','.join(map(str,s['values']))+'}}'for s in fixtures)+'}\n'
(out/'captured_pose_cases.lua').write_text(lua)
print(json.dumps({'runs':[{k:v for k,v in r.items()if k!='driver_passenger_bindings'}for r in runs],'unique_poses':len(fixtures)},ensure_ascii=False,indent=2))
