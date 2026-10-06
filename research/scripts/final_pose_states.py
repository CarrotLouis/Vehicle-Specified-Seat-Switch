import json
from pathlib import Path
ls=json.loads(Path('work/animation_resources/avatar_states.json').read_text())
for e in ['frv_enter_front_left','frv_enter_front_right','frv_enter_back_left','frv_enter_back_right','frv_enter_boot','tank_enter_top','tank_enter_back']:
 ids=[]
 for li in [0,13]:
  t=sorted({s['transitions'][e]['target'] for s in ls[li]['states'] if e in s['transitions']});assert len(t)==1
  i=t[0]
  if li==13:i=ls[li]['states'][i]['transitions']['action_end']['target']
  ids.append(i)
 print(e,ids,[ls[li]['states'][i]['name'] for li,i in zip([0,13],ids)])
