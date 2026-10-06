"""Execute real owner/authority/relation lookup instructions with explicit asset/backend doubles."""
from pathlib import Path
import os,sys,json,struct
R=Path(__file__).resolve().parent;W=R.parent
s=(W/'seat_motion_research/test_reservation_native.py').read_text()
s=s.replace('recent = deque(maxlen=16)','recent = deque(maxlen=16)\nchild_mode=False\nCHILD_ID,CHILD_NET=80,6001\nCHILD=0x100a0000;REL=0x100a1000;RELROWS=0x100a2000;RELOBJS=0x100a3000;RELGUNS=0x100a4000;GUNSPEC=0x100a5000')
s=s.replace('assert cx in (0, CAR_ID, AVATAR_ID)', 'assert cx in (0, CAR_ID, AVATAR_ID, CHILD_ID)')
s=s.replace('ret(CAR if cx == CAR_ID else AVATAR if cx == AVATAR_ID else 0)', 'ret(CAR if cx == CAR_ID else AVATAR if cx == AVATAR_ID else CHILD if cx==CHILD_ID else 0)')
s=s.replace('elif at == 0x5a8870:', 'elif at==0x5106d0:\n        assert cx==CAR;ret(GUNSPEC)\n    elif at == 0x5a8870 and not child_mode:')
s=s.replace('assert cx in (CAR_ID, AVATAR_ID)','assert cx in (CAR_ID, AVATAR_ID, CHILD_ID)')
s=s.replace('ret(1 if cx == CAR_ID else 2)', 'ret(1 if cx == CAR_ID else CHILD_NET if cx==CHILD_ID else 2)')
# Keep immutable helper test definitions and run the baseline under these
# declared doubles; all later mounted cases execute 5a8870 itself.
exec(compile(s,str(R/'test_linked_native.py'),'exec'))
child_mode=True
global_(0x5a8898,3,7,REL)
map_(REL,0x20,RELROWS,CAR_ID)
w(REL+0x38,'<Q',RELOBJS);w(RELOBJS,'<Q',CAR)
w(REL+0x48,'<Q',RELGUNS);w(RELGUNS,'<6I',CHILD_ID,0,0,0,0,0)
w(GUNSPEC+0x10,'<I',0x12345678)
w(CHILD+8,'<4I',CHILD_ID,0x80001234,CHILD_NET,1)
extra=[]
for transition,count,source,mount in [(26,5,1,4),(28,3,1,2)]:
 table=v.run(0x119a2a0,transition,mount);w(table,'<5I',0x12345678,0,0,0,0)
 for owned_child in [1,0]:
  setup(transition,((1<<count)-1)&~1&~(1<<source));w(CHILD+0x14,'<I',owned_child)
  # First matching synthetic entrance must choose the validated mounted role.
  entries=[]
  for entrance in range(count):
   setup(transition,((1<<count)-1)&~1&~(1<<source));event=execute_entry(entrance)
   if any(x['event']=='accepted'and x['chosen']==mount for x in event):entries.append(event)
  assert entries
  for event in entries:
   authority=[x for x in event if x['event'].startswith('authority_')]
   assert authority and all(x['unit']==CHILD_NET and x['peer']==hex(INSTALLER_PEER)for x in authority),'only mounted child transferred/requested; never chassis'
   extra.append({'transition':transition,'child_owned_by_owner':bool(owned_child),'events':event})
driver_cases=[]
for transition,count,source in [(26,5,1),(27,4,1),(28,3,1),(43,4,2),(44,4,2)]:
 found=[]
 for entrance in range(count):
  setup(transition,((1<<count)-1)&~(1<<source));event=execute_entry(entrance)
  if any(x['event']=='accepted'and x['chosen']==0 for x in event):
   # fd9af0's explicit fixture returns ownership handle 1 for the car;
   # this is NOT the 4123 wire NET reference used by the entry adapter.
   car_authority=[x for x in event if x['event'].startswith('authority_')and x['unit']==1]
   assert car_authority and all(x['peer']==hex(INSTALLER_PEER)for x in car_authority),('genuine empty driver transfers car to installer',transition,entrance,event)
   assert not read(FREE,'<I')[0]&(1<<source),'own previous reservation remains until acquired-owner release'
   found.append({'entrance':entrance,'events':event})
 assert found,('no native driver selection',transition)
 driver_cases.append({'transition':transition,'source':source,'car_authority_handle_double':1,'synthetic_asset_tables':True,'cases':found})
out=R/('linked-native-'+BUILD+'.json')
out.write_text(json.dumps({'build':BUILD,'boundary':__doc__,'cases':extra,'driver_cases':driver_cases},indent=2))
print('PASS',BUILD,'real mounted authority + related lookup for M102/M104, transfer/request only exact child net ref; chassis excluded')
print('PASS',BUILD,'five actual native empty-driver selection/authority branches; car transferred only to authentic installer; source reservation retained; asset/engine/network doubles')
