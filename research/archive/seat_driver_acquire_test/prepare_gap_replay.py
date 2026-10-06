from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent
O=R.parent/'seat_configurable_network_test/capture-20261001-0110'
name='VehicleSeatIntegrated-20261001-135022-22620-52163453.log'
p=O/name;b=p.read_bytes();m=json.loads((O/'manifest.json').read_text())
assert hashlib.sha256(b).hexdigest()==next(x['sha256']for x in m if x['name']==name)
e=[json.loads(x)for x in b.decode('utf-8-sig').splitlines()if x.strip()]
trigger=next(x['t']for x in e if x['event']=='seat_input'and x.get('source')==3 and x.get('target')==4 and x['t']>480000)
rows=[]
for x in e:
 if x['event']=='state'and trigger<=x['t']<=trigger+1800:
  a=next(a for a in x['data']['avatars']if a['is_local']);s=a['seat']
  assert a['id']==438 and s['collection']==580 and s['current']==3 and s['reserved']==3 and s['queued_exit']==0
  rows.append(dict(t=(x['t']-trigger)/1000,current=s['current'],reserved=s['reserved'],target=s['target'],action=s['action'],transitioning=s['transitioning'],active=s['active_passenger']))
assert rows[0]['transitioning']==0 and any(x['action']==17 for x in rows)and any(x['action']==21 for x in rows)
assert rows[-1]['action']==-1 and rows[-1]['active']==0
(R/'lean-replay.json').write_text(json.dumps(dict(source=name,sha256=hashlib.sha256(b).hexdigest(),trigger_ms=trigger,rows=rows),indent=2))
lua='return {\n'+''.join(' {'+','.join(k+'='+str(v)for k,v in x.items())+'},\n'for x in rows)+'}\n'
(R/'lean_replay.lua').write_text(lua)
print('Generated real-log same-seat lean17/21 replay:',len(rows),'samples')
