"""Explore native empty-seat selection using preserved entry tables only."""
from pathlib import Path
import os,json,struct,sys
R=Path(__file__).resolve().parent;W=R.parent
os.environ['VSS_CAPTURE']=str(W/'reverse/capture-25480438');sys.path.insert(0,str(W))
from emulate_seats import StaticVM
v=StaticVM();u=v.vm
def w(a,f,*x):u.mem_write(a,struct.pack(f,*x))
data=json.loads((W/'seat_transport_diagnostic/reservation-20260925/entry-tables.json').read_text())
for row in data['tables']:u.mem_write(row['rva'],bytes.fromhex(row['hex']))
manager,info,mask=0x10010000,0x10011000,0x10012000
w(manager+0x48,'<Q',info);w(manager+0x50,'<Q',mask)
result=[]
for row in data['tables']:
 layout=row['transition'];seats=row['seat_count'];n=row['rows'];w(info,'<I',layout)
 cases=[]
 for current in range(n):
  for target in range(seats):
   w(mask,'<I',1<<target)
   selected=v.run(0x636430,manager,0,current,0xffffffff)&0xffffffff
   if selected==target:cases.append([current,target])
 aliases={}
 for target in range(seats):
  good=[]
  for current in range(seats,n):
   valid=True
   for occupied in range(1<<seats):
    if occupied & (1<<target):continue
    w(mask,'<I',((1<<n)-1)^occupied)
    selected=v.run(0x636430,manager,0,current,0xffffffff)&0xffffffff
    if selected!=target:valid=False;break
   if valid:good.append(current)
  aliases[target]=good
 result.append({'vehicle':row['vehicle'],'transition':layout,'seats':seats,'rows':n,'one_free_target_routes':cases,'exact_target_free_entry_aliases':aliases})
(R/'request-routes.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
