"""Immutable game/engine captures only; no live process or game query."""
from pathlib import Path
import json,sys,re
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
from reverse import Module
out=R/'native-motion';out.mkdir(exist_ok=True)
results={}
query=rb'(velocity|kinematic|set_dynamic|is_dynamic|set_sleep|set_awake)'
for name in ['game.dll','helldivers2.exe']:
 m=Module(name,W/'reverse/capture-25480438')
 rx=re.compile(query,re.I)
 strings=[(base+hit.start(),hit.group().decode('ascii'))for base,data in m.sections
  for hit in re.finditer(rb'[ -~]{5,}',data)if rx.search(hit.group())]
 refs=m.xrefs(a for a,s in strings)
 results[name]={'strings':[{'rva':hex(a),'text':s}for a,s in strings],
  'refs':[{'at':hex(a),'string':hex(t),'function':hex(f[0])if f else None}for a,t,f in refs]}
 starts={f[0]for a,t,f in refs if f}
 for a in starts:(out/(name+'-'+hex(a)+'.txt')).write_text(m.dis(a),encoding='utf-8')
 print(name,len(strings),'strings',len(refs),'references',len(starts),'functions')
 for a,s in strings:
  ff=sorted({f[0]for at,t,f in refs if t==a and f})
  if ff:print(hex(a),s,[hex(f)for f in ff])
 if name=='game.dll':
  for target in [0x3326668]:
   refs=m.xrefs([target]);print('DRIVER_GLOBAL',[{'at':hex(a),'fn':hex(f[0])if f else None}for a,t,f in refs])
   for a,t,f in refs:
    if f:(out/(name+'-'+hex(f[0])+'.txt')).write_text(m.dis(f[0]),encoding='utf-8')
  for target in [0x6fe480,0x635710]:print('CALLERS',hex(target),m.callers([target]))
  for target in [0x8bbc50,0xbf1b70,0x6fe480,0x7056f0]:
   (out/(name+'-'+hex(target)+'.txt')).write_text(m.dis(target),encoding='utf-8')
 else:
  for target in [0x29c840,0x29bcf0,0x298a00]:
   (out/(name+'-'+hex(target)+'.txt')).write_text(m.dis(target),encoding='utf-8')
(out/'strings.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
