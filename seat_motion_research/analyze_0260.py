"""Freeze/classify the three installer starts; never infer remote W input."""
from pathlib import Path
from collections import Counter
import json,hashlib,math
R=Path(__file__).resolve().parent;D=R/'capture-20261005-0260'
L=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
names=['VehicleSeatIntegrated-20261005-132047-38676-395988187.log',
 'VehicleSeatIntegrated-20261005-132703-33836-396364046.log',
 'VehicleSeatIntegrated-20261005-134052-44572-397193140.log',
 'VehicleSeatIntegratedDiagnostic.log','BingusSharedLoader.log']
D.mkdir(exist_ok=True)
files=[]
for name in names:
 p=D/name
 if not p.exists():p.write_bytes((L/name).read_bytes())
 b=p.read_bytes();files.append({'name':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
if not (D/'files.json').exists():(D/'files.json').write_text(json.dumps(files,indent=2))
else:assert json.loads((D/'files.json').read_text())==files
summary=[]
def norm(v):return math.sqrt(sum(x*x for x in v))if isinstance(v,list)and len(v)==3 else None
for name in names[:3]:
 rows=[json.loads(x)for x in (D/name).read_text(encoding='utf-8').splitlines()if x.strip()]
 counts=Counter(x['event']for x in rows)
 states=[x for x in rows if x['event']=='state']
 requests=[x for x in rows if x['event']=='reservation_request']
 completes=[x for x in rows if x['event']=='reservation_operation_complete']
 stage_names={'reservation_entrance_mapping','reservation_request','reservation_owner_accepted',
 'reservation_waiting_owner_reservation_mask','reserved_local_stage','reserved_local_calls_returned',
 'sync_snapshot_invoking','sync_transition_invoking','sync_pair_calls_returned','reservation_operation_complete',
 'reservation_stopped','reservation_cancelled','reservation_owner_denied','seat_input','protocol_gap','transport_stopped',
 'input_priority_failed','input_priority_consumed','input_priority_discarded','end'}
 stages=[x for x in rows if x['event']in stage_names]
 physics=[x for x in rows if x['event']=='reservation_physics_sample']
 owner_reads=[x for x in rows if x['event']=='authority_interface_preflight']
 packets=[x for x in rows if x['event']in ('native_send','native_receive_dispatch')]
 operations=[]
 for i,req in enumerate(requests):
  end=next((x for x in completes if x['operation']==req['operation']),None)
  cutoff=requests[i+1]['t']if i+1<len(requests)else req['t']+5000
  events=[x for x in stages if req['t']<=x['t']<cutoff]
  samples=[x for x in physics if req['t']<=x['t']<cutoff]
  owner_samples=sorted(set((x.get('owner'),x.get('owner_serial'))for x in samples))
  wire=[{k:x.get(k)for k in ('t','event','message','values','peers','native_tick','caller_rva')}for x in packets if req['t']-5<=x['t']<cutoff]
  own_states=[]
  for state in states:
   if req['t']-250<=state['t']<=req['t']+5000:
    local=next((a for a in state['data']['avatars']if a['is_local']),None)
    if local:
     seat=local['seat'];item={'t':state['t'],'node':seat['current'],'reserved':seat['reserved'],'role':seat['role'],
      'action':seat['action'],'target':seat['target'],'transitioning':seat['transitioning'],
      'free_mask':next((v['free_mask']for v in state['data']['vehicles']if v['id']==seat['collection']),None)}
     own_states.append(item)
  operations.append({'request':req,'complete':end,'duration_ms':end['t']-req['t']if end else None,
   'stages':events,'owners_in_window':owner_samples,'physics':samples,'wire':wire,'own_states':own_states})
 item={'name':name,'version':rows[0].get('version'),'start':rows[0],'end':rows[-1],
  'events':dict(counts),'room_states':len(states),'operations':operations,
  'owner_reads':owner_reads,'classification':'two completed actual swaps'if len(completes)==2 else 'startup-only; no actual seat request'}
 summary.append(item)
main=summary[-1]
assert main['version']=='0.26.0'and len(main['operations'])==2
assert [(o['request']['source'],o['request']['target'])for o in main['operations']]==[(1,2),(2,1)]
for o in main['operations']:
 assert o['complete']and o['complete']['old_slot_released']and o['complete']['chassis_authority_unchanged']
 assert not any(x['message']in ('authority_request','authority_owned')for x in o['wire'])
 assert len(o['owners_in_window'])==1
 assert any(x['node']==o['request']['target']and x['reserved']==x['node']and x['role']==3 for x in o['own_states'])
for bad in ['reservation_stopped','reservation_cancelled','reservation_owner_denied','protocol_gap','reservation_physics_gap','reservation_property_gap','input_priority_failed']:
 assert main['events'].get(bad,0)==0,bad
(D/'analysis.json').write_text(json.dumps(summary,indent=2))
for s in summary:
 print(json.dumps({'name':s['name'],'classification':s['classification'],'end':s['end'],'events':s['events']},ensure_ascii=False))
for o in main['operations']:
 print(json.dumps({'operation':o['request']['operation'],'source':o['request']['source'],'target':o['request']['target'],
  'duration_ms':o['duration_ms'],'owners':o['owners_in_window'],'stages':o['stages'],'wire':o['wire'],
  'physics_keys':list(o['physics'][0])if o['physics']else []},ensure_ascii=False))
print('PASS two real grants/targets/source releases; driver authority unchanged; no new control-input assumption')
