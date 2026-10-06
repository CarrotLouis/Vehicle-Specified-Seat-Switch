"""Freeze current three-player 0.30 evidence; classify observations, not claims."""
from pathlib import Path
import json,hashlib,bisect
from collections import Counter
W=Path(__file__).resolve().parent.parent
L=Path('C:/Users/Administrator/AppData/Local/CowboyBingus/Helldivers2/Logs')
D=Path(__file__).resolve().parent/'capture-20261005-0300'
names=['VehicleSeatIntegrated-20261005-223653-33220-26911062.log','VehicleSeatIntegratedDiagnostic.log','BingusSharedLoader.log']
D.mkdir(exist_ok=True);files=[]
for name in names:
 p=D/name
 if not p.exists():p.write_bytes((L/name).read_bytes())
 b=p.read_bytes();files.append({'name':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
idx=D/'files.json'
if idx.exists():assert json.loads(idx.read_text())==files
else:idx.write_text(json.dumps(files,indent=2))
rows=[json.loads(line)for line in(D/names[0]).read_text(encoding='utf-8').splitlines()if line.strip()]
assert rows[0]['version']=='0.30.0'
counts=Counter(r['event']for r in rows)
states=[r for r in rows if r['event']=='state'];st=[r['t']for r in states]
req=[r for r in rows if r['event']in('reservation_request','reservation_local_owner_request')]
ops=[]
for i,r in enumerate(req):
 stop=req[i+1]['t']if i+1<len(req)else rows[-1]['t']+1
 window=[x for x in rows if r['t']<=x['t']<stop]
 complete=next((x for x in window if x['event']in('reservation_operation_complete','reservation_local_owner_complete')and x.get('operation')==r['operation']),None)
 s=states[max(0,bisect.bisect_right(st,r['t'])-1)]['data']
 av=next((a for a in s.get('avatars',[])if a.get('is_local')),None)
 car=next((v for v in s.get('vehicles',[])if av and v['id']==av.get('seat',{}).get('collection')),None)
 sync=[x for x in window if x['event']=='sync_fleet_begin']
 peers=[x for x in window if x['event']=='sync_fleet_peer_returned']
 physics=[x for x in window if x['event']=='reservation_physics_sample']
 ops.append({'request':r,'complete':complete,'duration_ms':complete['t']-r['t']if complete else None,
  'sample_player_count':s.get('player_count'),'vehicle':car,'local_avatar':av,
  'sync':sync,'peer_return_count':len(peers),'installer_host':physics[0].get('installer_is_host')if physics else None})
transitions=[];last=None
for r in states:
 s=r['data'];key=(s.get('state'),s.get('player_count'),s.get('peer_count'),s.get('local_count'))
 if key!=last:transitions.append({'t':r['t'],'state':key[0],'players':key[1],'peers':key[2],'locals':key[3]});last=key
error_events=[r for r in rows if any(x in r['event']for x in('error','failed','gap','overflow','cancelled'))or r['event']=='reservation_stopped']
resets=[r for r in rows if r['event']=='tank_steer_reset_returned']
windows=[r for r in rows if r['event']=='tank_steer_reset_window']
summary={'file':names[0],'start':rows[0],'last':rows[-1],'events':dict(counts),'operations':ops,
 'state_transitions':transitions,'errors':error_events,'tank_resets':resets,'tank_windows':windows,
 'max_players':max((r['data'].get('player_count',0)for r in states),default=0)}
(D/'analysis.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
brief={'files':files,'version':rows[0]['version'],'last_event':rows[-1]['event'],'last_t':rows[-1]['t'],
 'max_players':summary['max_players'],'operations':[{'op':x['request']['operation'],'players':x['sync'][0]['peer_count']if x['sync']else x['sample_player_count'],
 'vehicle':(x['vehicle']or{}).get('name'),'source':x['request']['source'],'target':x['request']['target'],
 'complete':bool(x['complete']),'duration_ms':x['duration_ms'],'destinations':x['sync'][0].get('destinations')if x['sync']else None,
 'peers_returned':x['peer_return_count'],'host':x['installer_host']}for x in ops],
 'transitions':transitions,'error_counts':dict(Counter(r['event']for r in error_events)),
 'errors':[{'t':r.get('t'),'event':r['event'],'reason':r.get('reason')}for r in error_events],
 'tank_resets':len(resets),'tank_window_rows':len(windows),'remote_samples':counts.get('remote_pose_watch_sample',0),
 'input_refusals':[r for r in rows if r['event']=='seat_input'and r.get('reason')in('occupied','network_trigger_refused','cross_scope_unavailable','network_stopped_restart_required')]}
print(json.dumps(brief,indent=2,ensure_ascii=False))
