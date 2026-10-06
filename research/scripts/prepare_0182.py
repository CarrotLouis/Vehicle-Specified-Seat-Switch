from pathlib import Path
import collections,hashlib,json,shutil

W=Path(__file__).resolve().parent;old=W/'seat_multi_vehicle_fix';R=W/'seat_tank_binding_fix'
assert not R.exists(),'Preserve an existing repair workspace'
R.mkdir()
for p in old.iterdir():
 if not p.is_file()or p.name in {'build-verified.log','artifact-review.json','package.json'}:continue
 target=R/p.name
 if p.suffix in {'.lua','.py','.json','.txt','.md','.c','.h','.S'}and p.name!='regression_0180_observe.lua':
  target.write_text(p.read_text(encoding='utf-8').replace('seat_multi_vehicle_fix','seat_tank_binding_fix').replace('0.18.1','0.18.2'),encoding='utf-8')
 else:shutil.copy2(p,target)
live=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
capture=R/'capture-20261002-0181';capture.mkdir()
names=['VehicleSeatIntegrated-20261002-145416-36360-142397562.log',
 'VehicleSeatIntegrated-20261002-150025-28924-142766531.log',
 'VehicleSeatIntegrated-20261002-152029-31712-143970046.log',
 'VehicleSeatIntegratedDiagnostic.log','BingusSharedLoader.log']
files=[];runs=[]
for name in names:
 data=(live/name).read_bytes();(capture/name).write_bytes(data)
 files.append(dict(name=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
 if not name.startswith('VehicleSeatIntegrated-'):continue
 rows=[json.loads(line)for line in data.decode('utf-8-sig').splitlines()]
 assert rows[0]['version']=='0.18.1'
 current=None;op=None;models=collections.defaultdict(collections.Counter);driver_personal=[];abort=[];native=collections.Counter()
 local=coordinator=None;sample_vehicle=None
 for row in rows:
  e=row['event']
  if e=='state':
   a=next((a for a in row['data']['avatars']if a['is_local']),{})
   collection=(a.get('seat')or{}).get('collection')
   sample_vehicle=next((v['name']for v in row['data']['vehicles']if v['id']==collection),None)
  elif e=='seat_input'and row['reason']=='native_complete':native[sample_vehicle]+=1
  elif e=='integrated_state':
   detail=json.loads(row['detail']);current=detail['vehicle'];local=detail['ownership']['local_peer'];coordinator=detail['ownership']['coordinator']
  elif e=='integrated_switch_attempt':op=dict(t=row['t'],vehicle=current,source=row['source'],target=row['target'],weapon_sync=[])
  elif op and e in {'sync_weapon_clear_invoking','sync_personal_bind_invoking'}:op['weapon_sync'].append(dict(event=e,channel=row.get('channel')))
  elif e=='integrated_operation_complete':
   models[current][row['authority_path']]+=1
   if op and current=='bastion'and op['source']==0 and op['target']in [2,3]:driver_personal.append(op)
   op=None
  elif e in {'integrated_cancelled','integrated_aborted_and_returned','integrated_ownership_return_confirmed'}and row.get('cancelled',e!='integrated_ownership_return_confirmed'):abort.append(row)
 counts=collections.Counter(row['event']for row in rows)
 runs.append(dict(name=name,host_role=('installer_host'if coordinator==local else 'friend_host')if counts['integrated_operation_complete']else 'excluded_startup_no_operations',
  completed=counts['integrated_operation_complete'],by_model={k:dict(v)for k,v in models.items()},native_completed=dict(native),
  bastion_driver_passenger_no_weapon_sync=driver_personal,abort=abort,clean_shutdown=rows[-1].get('event')=='end',
  errors_or_gaps=counts['read_gap'],drops=sum(row.get('dropped_total',0)for row in rows if row['event']=='transport_stopped')))
assert [r['completed']for r in runs]==[0,29,39]
assert len(runs[1]['abort'])==3 and runs[1]['abort'][-1]['mutation_started']is False
assert not runs[2]['abort']and runs[2]['native_completed']['tanker']==2
assert all(len(r['bastion_driver_passenger_no_weapon_sync'])==3 for r in runs[1:])
analysis=dict(files=files,runs=runs,user_report='Both host roles: M103/M104 fine; installer-host Maelstrom/tanker input unavailable after safe abort; friend-host Bastion driver->passenger personal weapon invisible until switching weapon; otherwise no anomaly.',
 accepted=['M103 both roles','M104 both roles','Maelstrom friend-host seat/control routes with driver binding regression pending','tanker friend-host native routes'],
 issues=['Pre-mutation control-key abort returns confirmed ownership but globally stops all mod seat inputs.',
 'Bastion driver->passenger skips personal weapon channel replication; six observed transitions send no binding messages.'])
(capture/'analysis.json').write_text(json.dumps(analysis,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(files=files,runs=[{k:v for k,v in r.items()if k not in ['abort','bastion_driver_passenger_no_weapon_sync']}for r in runs]),ensure_ascii=False,indent=2))
