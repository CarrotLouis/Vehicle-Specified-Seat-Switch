from pathlib import Path
import collections,hashlib,json

W=Path(__file__).resolve().parent;L=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
C=W/'seat_multi_peer_research/capture-20261002-0190';C.mkdir(parents=True,exist_ok=True)
names=['VehicleSeatIntegrated-20261002-212541-22004-165881968.log',
 'VehicleSeatIntegrated-20261002-214258-22220-166919062.log',
 'VehicleSeatIntegrated-20261002-220039-29104-167979875.log',
 'VehicleSeatIntegratedDiagnostic.log','BingusSharedLoader.log']
files=[];runs=[]
for name in names:
 b=(L/name).read_bytes();dest=C/name
 if dest.exists():assert dest.read_bytes()==b,'Frozen data differs'
 else:dest.write_bytes(b)
 files.append(dict(name=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
 if name in names[3:]:continue
 # 0.19.0 logged the ownership epoch as raw bytes inside context. Preserve
 # undecodable bytes rather than discarding evidence; JSON structure is intact.
 decoded=b.decode('utf-8-sig',errors='surrogateescape')
 rows=[json.loads(l)for l in decoded.splitlines()];counts=collections.Counter(r['event']for r in rows)
 room=[];owners=collections.Counter();pair=collections.Counter();conditions=collections.Counter();ops=[];op=None;model=None
 steering=collections.defaultdict(list);rosters=[];issues=[]
 for i,r in enumerate(rows):
  e=r['event']
  if e=='room_roster':rosters.append(dict(line=i+1,t=r['t'],data=r['data']))
  if e=='integrated_state':model=json.loads(r['detail']).get('vehicle')
  if e=='integrated_switch_attempt':op=dict(line=i+1,t=r['t'],model=model,source=r['source'],target=r['target'],events=[])
  if op:
   op['events'].append(r)
   if e=='integrated_operation_complete':op['end']=r['t'];op['authority_path']=r['authority_path'];ops.append(op);op=None
  if e=='room_ownership_sample':
   own=r['ownership'];v=r['vehicle'];driver=next((a for a in r['avatars']if a.get('seat')and a['seat']['collection']==v['id']and a['seat']['current']==0 and a['seat']['role']==1),None)
   ca=(r['players'],r['local_peer'],r['coordinator']);conditions[ca]+=1
   owners[(r['players'],v['id'],v['name'],own['owner'],driver and driver.get('owner'),v['owned_local'],own['busy'])]+=1
   current_owner=next((a for a in r['avatars']if a.get('owner')==own['owner']),None)
   owner_elsewhere=current_owner and current_owner.get('seat')and current_owner['seat']['collection']not in [0,v['id']]
   key=(r['players'],r['local_peer'],r['coordinator'],v['id'],v['name'],own['owner'],driver and driver.get('owner'),owner_elsewhere or False)
   pair[key]+=1
   if owner_elsewhere or driver and own['owner']!=driver.get('owner'):room.append(dict(line=i+1,**r))
  if e.startswith('steering_watch_'):steering[e].append(dict(line=i+1,**r))
  if e in ['error','read_gap','room_ownership_gap','animation_watch_gap','integrated_stopped','integrated_cancelled','integrated_incomplete','steering_watch_gap']:
   issues.append(dict(line=i+1,**r))
 runs.append(dict(name=name,version=rows[0].get('version'),counts=dict(counts),raw_epoch_invalid_utf8=any(0xDC80<=ord(c)<=0xDCFF for c in decoded),
  clean_shutdown=rows[-1]['event']=='end',rosters=rosters,
  room_roles=[dict(players=k[0],local_peer=k[1],coordinator=k[2],samples=v)for k,v in conditions.items()],
  owner_driver_cases=[dict(players=k[0],collection=k[1],vehicle=k[2],owner=k[3],driver=k[4],owned_local=k[5],busy=k[6],samples=v)for k,v in owners.items()],
  peer_car_contexts=[dict(players=k[0],local_peer=k[1],coordinator=k[2],collection=k[3],vehicle=k[4],owner=k[5],driver=k[6],owner_elsewhere=k[7],samples=v)for k,v in pair.items()],
  distinct_owner_driver_or_owner_elsewhere=room,operations=ops,steering=dict(steering),issues=issues))
(C/'files.json').write_text(json.dumps(files,ensure_ascii=False,indent=2),encoding='utf-8')
(C/'analysis.json').write_text(json.dumps(dict(runs=runs,user_report='First full round installer host; second friend A host. Only three people. Unspecified slips, broadly completed. Two-player cross works, third landing disables and leaving restores immediately. No other visual/control anomaly. Moving remote-driver cross causes chassis abrupt slowdown. Tank spin persists. Minimize new >=3-person tests.'),ensure_ascii=True,indent=2),encoding='utf-8')
for r in runs:
 print(json.dumps(dict(name=r['name'],version=r['version'],end=r['clean_shutdown'],room_roles=r['room_roles'],ops=len(r['operations']),completed=collections.Counter(o['model']for o in r['operations']),
   gaps=len(r['issues']),issue_reasons=collections.Counter(a.get('reason',a['event'])for a in r['issues']),steering_counts={k:len(v)for k,v in r['steering'].items()},
   owner_elsewhere=sum(a['samples']for a in r['peer_car_contexts']if a['owner_elsewhere']),owner_driver_different=sum(a['samples']for a in r['peer_car_contexts']if a['driver']and a['owner']!=a['driver'])),ensure_ascii=False))
