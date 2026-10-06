import json
from pathlib import Path
ls=json.loads(Path('work/animation_resources/avatar_states.json').read_text())
for li,i in [(13,39),(13,42),(13,98)]:
 s=ls[li]['states'][i]
 print(li,i, {k:v for k,v in s['transitions'].items() if any(w in k for w in ['end','idle','action','vehicle','mounted'])})
for li,l in enumerate(ls):
 targets=sorted({s['transitions']['action_end']['target'] for s in l['states'] if 'action_end' in s['transitions']})
 if targets:print('action_end',li,targets)
