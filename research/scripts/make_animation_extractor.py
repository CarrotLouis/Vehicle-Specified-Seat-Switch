from pathlib import Path
p=Path('work/extract_lua.py').read_text();p=p[:p.index('records=[]')];p=p.replace("/'lua_resources'","/'animation_resources'")
p+='''
sys.path.insert(0,str(Path(__file__).parent/'BingusSharedLoader/scripts'))
from archive import resource_hash
records=[];seen=set();count=0
state_type=resource_hash('state_machine')
for ar in archives:
 if '.' in ar[0]:continue
 h=read_archive(ar,0,72)
 if h[:4]!=bytes.fromhex('110000f0'):continue
 nt,nf=struct.unpack_from('<II',h,4)
 table=read_archive(ar,72+32*nt,nf*80)
 for i in range(nf):
  fields=struct.unpack_from('<7Q6I',table,i*80);nh,th,off=fields[:3];sz=fields[7]
  if th!=state_type or nh in seen:continue
  seen.add(nh);count+=1
  b=read_archive(ar,off,sz)
  if struct.pack('<I',0xe86f3c8c) not in b:continue
  path=OUT/(f'{nh:016x}.state_machine.main');path.write_bytes(b)
  records.append(dict(archive=ar[0],name=f'{nh:016x}',size=sz));print(records[-1],flush=True)
(OUT/'index.json').write_text(json.dumps(records,indent=2));print('Done',count,len(records))
'''
Path('work/extract_animation.py').write_text(p)
