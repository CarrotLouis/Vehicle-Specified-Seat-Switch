from pathlib import Path
import collections,hashlib,json
W=Path(__file__).resolve().parent;L=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
C=W/'seat_motion_research/capture-20261003-0200';C.mkdir(parents=True,exist_ok=True)
names=['VehicleSeatIntegrated-20261003-222439-36748-255820015.log',
 'VehicleSeatIntegrated-20261003-223418-8524-256399578.log','VehicleSeatIntegratedDiagnostic.log','BingusSharedLoader.log']
files=[];runs=[]
for name in names:
 b=(L/name).read_bytes();dest=C/name
 if dest.exists():assert dest.read_bytes()==b,'Frozen file changed'
 else:dest.write_bytes(b)
 files.append(dict(name=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
 if name in names[2:]:continue
 rows=[json.loads(line)for line in b.decode('utf-8-sig').splitlines()]
 counts=collections.Counter(r['event']for r in rows);assert rows[0]['version']=='0.20.0'
 boundaries=[dict(line=i+1,**r)for i,r in enumerate(rows)if r['event']=='motion_boundary']
 watches=[dict(line=i+1,**r)for i,r in enumerate(rows)if r['event'].startswith('motion_')]
 issues=[dict(line=i+1,**r)for i,r in enumerate(rows)if r['event']in
  ['error','read_gap','room_ownership_gap','motion_boundary_gap','motion_watch_gap','integrated_stopped','integrated_cancelled','integrated_incomplete']]
 room=collections.Counter((r['players'],r['local_peer'],r['coordinator'])for r in rows if r['event']=='room_ownership_sample')
 ops=[];op=None;model=None;request=None
 for i,r in enumerate(rows):
  if r['event']=='integrated_state':model=json.loads(r['detail']).get('vehicle')
  if r['event']=='integrated_request_attempt':request=r
  if r['event']=='integrated_switch_attempt':op=dict(line=i+1,t=r['t'],source=r['source'],target=r['target'],model=model,request=request,events=[])
  if op:
   op['events'].append(r)
   if r['event']=='integrated_operation_complete':op['end']=r['t'];op['authority_path']=r['authority_path'];ops.append(op);op=None
 run=dict(name=name,version=rows[0]['version'],counts=dict(counts),clean_shutdown=rows[-1]['event']=='end',
  room_roles=[dict(players=k[0],local_peer=k[1],coordinator=k[2],samples=v)for k,v in room.items()],
  operations=ops,issues=issues,boundaries=boundaries,motion=watches)
 runs.append(run)
 print(json.dumps(dict(name=name,version=run['version'],clean_shutdown=run['clean_shutdown'],room_roles=run['room_roles'],
  completions=len(ops),routes=collections.Counter(f"{o['model']}:{o['source']}->{o['target']}"for o in ops),
  boundaries=len(boundaries),issues=len(issues),events={k:v for k,v in counts.items()if k.startswith('motion_')},
  unique_commands=[list(x)for x in sorted(set(tuple(r['command_floats_offset_00_to_28'])for r in watches if 'command_floats_offset_00_to_28'in r))]),ensure_ascii=False))
(C/'files.json').write_text(json.dumps(files,indent=2),encoding='utf-8')
(C/'analysis.json').write_text(json.dumps({'user_report':'Both host roles/views agree. Native-range swaps leave speed unaffected. Any cross-region swap (front-rear or mounted) forces actual observed speed to zero. Extra tests near80; release W immediately before swap also instant complete stop, so not a transient displayed speed drop. No seat-specific distinction.','runs':runs},ensure_ascii=True,indent=2),encoding='utf-8')
out=[]
for r in runs:
 out.append(r['name'])
 for b in r['boundaries']:
  out.append(f"{b['t']:7d} {b['source']}->{b['target']} {b['stage']:27s} owner={b['snapshot_owner']} local={b['snapshot_owned_local']} active={b['driver_active']} floats={b['command_floats_offset_00_to_28']} flags={b['command_flags_offset_2c_to_2f']}")
(C/'boundary-summary.txt').write_text('\n'.join(out)+'\n',encoding='utf-8')
