from pathlib import Path
import collections,json,struct,sys
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W))
from reverse import Module
m=Module('game.dll',W/'reverse/capture-25480438')
m.md.detail=True
out=R/'native-0190';out.mkdir(exist_ok=True)
for name,addr in [('reserve',0x6344d0),('release',0x6349b0),('restore_seated',0x63eb10),('driver_active',0x6fe480)]:
 text=m.dis(addr);(out/(name+'.txt')).write_text(text)
 ins=list(m.md.disasm(m.read(addr,m.function(addr)[1]-addr),addr))
 print(name,hex(addr),'externalcalls',list(dict.fromkeys(i.op_str for i in ins if i.mnemonic=='call')))
for addr in [0xa7e8ec,0xa7e93f]:
 ins=next(m.md.disasm(m.read(addr,8),addr))
 target=ins.address+ins.size+ins.disp
 b=m.read(target,12)
 print('inhibited_command_default',hex(addr),hex(target),b.hex(),struct.unpack('<3f',b)if len(b)==12 else None)
a=json.loads((R/'capture-20261002-0190/analysis.json').read_text())
for run in a['runs']:
 print('RUN',run['name'])
 print('ROSTER',[(r['t'],r['data']['players'],r['data']['peer_count'])for r in run['rosters']])
 print('OPS',[(o['t'],o['model'],o['source'],o['target'],o['end']-o['t'],o['authority_path'],
  [(e['event'],e['t']-o['t'])for e in o['events']if e['event']in ['integrated_acquired','integrated_return_invoked','integrated_ownership_return_confirmed']])for o in run['operations']])
 print('STEERING')
 groups=[];group=None
 for r in run['steering'].get('steering_watch_sample',[]):
  key=(r['collection'],r['local_seat']['current']if r.get('local_seat')else None,r['driver_active'],tuple(r['held_keys']),tuple(round(x,4)for x in r['command_floats_offset_00_to_28']),tuple(r['command_flags_offset_2c_to_2f']))
  if not group or group['key']!=key:
   group={'first':r['t'],'last':r['t'],'key':key,'count':1};groups.append(group)
  else:group['last']=r['t'];group['count']+=1
 print(json.dumps([g for g in groups if g['count']>=3 or g['key'][1]!=0],ensure_ascii=False))
 print('OWNER_ELSEWHERE',run['peer_car_contexts'][:18])
