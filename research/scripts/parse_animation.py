import sys,json,struct
from pathlib import Path
sys.path.insert(0,'work/BingusSharedLoader/scripts')
from archive import resource_hash
thin=json.loads(Path('work/reverse/thin_names.json').read_text());names={resource_hash(x):x for x in Path('work/filediver/hashes/hashes.txt').read_text().splitlines() if x and not x.startswith('//')}
b=Path('work/animation_resources/4d1c334d294dfa97.state_machine.main').read_bytes()
def ints(o,n):return struct.unpack_from('<'+'I'*n,b,o)
def nam(h):return thin.get(hex(h),hex(h))
base=ints(8,1)[0];n=ints(base,1)[0];layers=[]
for go in ints(base+4,n):
 start=base+go;magic,default,cnt=ints(start,3);states=[]
 for ao in ints(start+12,cnt):
  p=start+ao;raw=ints(p+8,38);nh=struct.unpack_from('<Q',b,p)[0];anim=[names.get(x,f'{x:016x}') for x in struct.unpack_from('<'+'Q'*raw[1],b,p+raw[2])] if raw[2] else []
  events=[struct.unpack_from('<Ii',b,p+raw[9]+8*j) for j in range(raw[8])] if raw[9] else []
  links=[struct.unpack_from('<IfII',b,p+raw[11]+16*j) for j in range(raw[10])] if raw[11] else []
  tr={nam(h):dict(target=links[idx][0],time=links[idx][1],type=links[idx][2]) for h,idx in events if idx>=0}
  states.append(dict(name=names.get(nh,hex(nh)),type=raw[0],loop=bool(raw[6]),animations=anim,transitions=tr,end_event=nam(raw[16])))
 layers.append(dict(default=default,states=states))
Path('work/animation_resources/avatar_states.json').write_text(json.dumps(layers,indent=2))
for li,l in enumerate(layers):
 candidates=[(i,s) for i,s in enumerate(l['states']) if any('frv_' in a or 'tank_' in a or 'lav_' in a for a in s['animations'])]
 print('layer',li,'states',len(l['states']),'vehicle animations',len(candidates))
 for i,s in candidates:
  print(i,s['name'],s['type'],s['loop'],s['animations'][:3],{k:v for k,v in s['transitions'].items() if k in ['frv_switch','tank_switch','0x0']})
