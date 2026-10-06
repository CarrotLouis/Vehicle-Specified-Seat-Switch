"""Bounded static branch constants and actual Maelstrom avatar transitions."""
from pathlib import Path
import json,os,sys,struct
R=Path(__file__).resolve().parent;W=R.parent
os.environ['VSS_CAPTURE']=str(W/'reverse/capture-25480438')
sys.path.insert(0,str(W))
from emulate_seats import StaticVM
m=StaticVM().mod;m.md.detail=True
for rva in [0x71562c,0x715651,0x71574e,0x71575c,0x715784,0x715795,0x7157be,0x7157cb,0x7157fc,0x715814]:
 i=next(m.md.disasm(m.read(rva,15),rva));at=i.address+i.size+i.disp
 print(hex(rva),i.mnemonic,i.op_str,'constant',hex(at),struct.unpack('<f',m.read(at,4))[0])
rows=[json.loads(x)for x in (R/'capture-20261005-0280/VehicleSeatIntegrated-20261005-170430-34600-6968156.log').read_text(encoding='utf-8').splitlines()]
last={}
for x in rows:
 if x['event']!='state' or x['t']<1350000:continue
 d=x.get('data',{});cars={v['id']:v for v in d.get('vehicles',[])if v.get('name')=='maelstrom'}
 for a in d.get('avatars',[]):
  seat=a.get('seat')or{};key=(seat.get('collection'),seat.get('current'),seat.get('role'),seat.get('transitioning'))
  if last.get(a['id'])!=key:
   if seat.get('collection') in cars or(last.get(a['id'])or(None,))[0]==911:
    c=cars.get(seat.get('collection'))or{}
    print(json.dumps({'t':x['t'],'avatar':a['id'],'local':a['is_local'],'seat':key,'action':seat.get('action'),
     'car_owned':c.get('owned_local'),'flags':[a.get('input_flags_low'),a.get('input_flags_high')],'vehicle_input':a.get('vehicle_input')},ensure_ascii=False))
   last[a['id']]=key
