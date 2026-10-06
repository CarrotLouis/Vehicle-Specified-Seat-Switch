"""Read named resource headers/config only from local game archives."""
from pathlib import Path
import sys,struct,json
W=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from archive import resource_hash
source=(W/'extract_lua.py').read_text()
ns={'__file__':str(W/'extract_lua.py')}
exec(source[:source.index('records=[]')],ns)
names=['core/performance_hud/performance_hud','content/performance_hud','content/input']
wanted={resource_hash(n):n for n in names};typ=resource_hash('config')
rows=[]
for ar in ns['archives']:
    if '.'in ar[0]:continue
    h=ns['read_archive'](ar,0,72)
    if h[:4]!=b'\x11\0\0\xf0':continue
    nt,nf=struct.unpack_from('<II',h,4)
    table=ns['read_archive'](ar,72+nt*32,nf*80)
    for i in range(nf):
        fields=struct.unpack_from('<7Q6I',table,i*80)
        name,kind,offset=fields[:3];length=fields[7]
        if name in wanted and kind==typ:
            p=Path(__file__).parent/(wanted[name].replace('/','-')+'.config.bin')
            p.write_bytes(ns['read_archive'](ar,offset,length))
            rows.append({'name':wanted[name],'archive':ar[0],'bytes':length,'file':p.name})
print(json.dumps(rows,indent=2))
