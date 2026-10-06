import json
from pathlib import Path
ls=json.loads(Path('work/animation_resources/avatar_states.json').read_text())
events=['frv_enter_front_left','frv_enter_front_right','frv_enter_back_left','frv_enter_back_right','frv_enter_boot','tank_enter_top','tank_enter_back','frv_switch','tank_switch']
for li,l in enumerate(ls):
 all_targets={e:sorted({s['transitions'][e]['target'] for s in l['states'] if e in s['transitions']}) for e in events}
 if not any(all_targets.values()):continue
 print('LAYER',li,'default',l['default'])
 print({k:v for k,v in all_targets.items() if v})
 for i in sorted({x for xs in all_targets.values() for x in xs}):
  s=l['states'][i];print('STATE',i,s['name'],'loop',s['loop'],'end',s['end_event'],'anim',s['animations'][:1])
  print(' LINKS',{e:v for e,v in s['transitions'].items() if e in events+['0x0','finished','animation_end','animation_finished','end'] or v['type']==1})
