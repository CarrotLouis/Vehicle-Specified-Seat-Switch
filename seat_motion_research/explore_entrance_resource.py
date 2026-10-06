from pathlib import Path
import sys, json
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent))
from reverse import Module
m=Module('game.dll',R.parent/'reverse/capture-25480438')
rows=[]
for at,target,f in m.callers([0x50acb0]):
    if not f:continue
    start,end,_=map(lambda x:int(x,16),f)
    if end-start>15000:continue
    text=m.dis(start,end-start)
    if '0x440' in text or '0x448' in text or '0x450' in text:
        rows.append({'at':at,'function':f,'interesting':[line for line in text.splitlines()
          if any(s in line for s in ('0x440','0x448','0x450','0x88','0x50acb0'))]})
        (R/'native-nonowner'/('entrance-resource-'+hex(start)+'.txt')).write_text(text)
(R/'native-nonowner/entrance-resource-refs.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows[:12]))
