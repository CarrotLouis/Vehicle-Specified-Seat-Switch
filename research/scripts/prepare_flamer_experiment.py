"""Create isolated M104 diagnostic from the accepted two-step 0.10.1 workflow."""
from pathlib import Path
W=Path(__file__).resolve().parent;src=W/'seat_weapon_clear_diagnostic';R=W/'seat_flamer_weapon_diagnostic'
assert not (R/'package.json').exists(),'Do not overwrite a built experiment'
R.mkdir(exist_ok=True)
for p in src.iterdir():
 if p.is_file()and p.suffix in ('.lua','.py','.txt')and p.name not in ('bundled.lua','check.lua','analyze_success.py'):
  s=p.read_text(encoding='utf-8').replace('seat_weapon_clear_diagnostic','seat_flamer_weapon_diagnostic').replace('0.10.1','0.10.3')
  (R/p.name).write_text(s,encoding='utf-8')
def edit(name,pairs):
 p=R/name;s=p.read_text(encoding='utf-8')
 for old,new in pairs:
  assert old in s,(name,old)
  s=s.replace(old,new)
 p.write_text(s,encoding='utf-8')
edit('adapter.lua',[("'m102'","'m104'"),('s.transition~=26','s.transition~=28'),('#s.profile.roles~=5','#s.profile.roles~=3'),('M102_only','M104_only'),('source~=4','source~=2'),('source==4','source==2'),('5-source','3-source'),('5-c.seat','3-c.seat')])
edit('probe.lua',[('self.count==0 and 1 or 4','self.count==0 and 1 or 2'),('5-source','3-source')])
edit('observe.lua',[("v.name=='m102'","v.name=='m104'"),('seat.current==4','seat.current==2')])
edit('transaction.lua',[('M102 passenger1 <-> gunner4','M104 passenger1 <-> flamer2'),("'m102'","'m104'"),('s.transition==26','s.transition==28'),('s.node==4','s.node==2'),('target==4','target==2'),('action(s.transition,s.avatar,4,target)','action(s.transition,s.avatar,2,target)')])
edit('binding_sender.lua',[('M102 gunner','M104 flamer'),('target==4','target==2'),('s.node==4','s.node==2'),("'m102'","'m104'")])
edit('animation_sender.lua',[('target==4','target==2'),('snapshot restores attachments (action5)','snapshot restores attachments (action3)')])
edit('sender.lua',[("'m102'","'m104'"),('target==4','target==2')])
edit('entry.lua',[('guest_M102_front_passenger_gunner','guest_M104_front_passenger_flamer')])
edit('test_adapter.lua',[("c.native.vehicle='m104'","c.native.vehicle='m102'"),('c.native.transition=28','c.native.transition=26'),("vehicle='m102',transition=26","vehicle='m104',transition=28"),('roles={1,3,3,3,2}','roles={1,3,2}'),('[4]=','[2]='),('c.seat=4','c.seat=2'),('c.native.node=4','c.native.node=2'),('seat(4,2)','seat(2,2)')])
edit('test_probe.lua',[('5-x.seat','3-x.seat')])
edit('test_transaction.lua',[("'m102'","'m104'"),('transition=26','transition=28'),('roles={1,3,3,3,2}','roles={1,3,2}'),('target==4','target==2'),('source==4','source==2'),('a[1]==26','a[1]==28'),('a[3]==4 and a[4]==4','a[3]==2 and a[4]==2'),('[4]=','[2]='),('source=4','source=2'),('target=4','target=2'),('s.node=4','s.node=2'),('tx,s,4','tx,s,2')])
edit('test_sender.lua',[("'m102'","'m104'")])
edit('test_binding_sender.lua',[("'m102'","'m104'"),('node=4','node=2'),('s,dest,4','s,dest,2')])
edit('test_animation_sender.lua',[('s,dest[0],4','s,dest[0],2')])
edit('prepare_tests.py',[('for layout in (26,):','for layout in (28,):'),('((1,4),(4,1))','((1,2),(2,1))'),('source==4','source==2'),('target==4','target==2'),('{1,4}','{1,2}'),('node==4','node==2'),("s+='''","s=s.replace(\"name='m102'\",\"name='m104'\")\ns+='''")])
# One additional full relocatable witness for the M104-specific action dispatcher.
s=(R/'generate_animation_spec.py').read_text()
a=s.index('defs=[');b=s.index('\nmods=',a)
s=s[:a]+"defs=[('action','game',0x118b300,None)]"+s[b:]
s=s.replace("name='anim_'+short","name='flamer_'+short")
a=s.index('edges=[');b=s.index("\nsource=",a)
s=s[:a]+"edges=[dict(**{'from':'seat_action'},to='flamer_action',offset=0xf2d,disp=1,width=4,size=5)]"+s[b:]
s=s.replace("R/'animation_spec.lua'","R/'flamer_spec.lua'").replace("R/'evidence.json'","R/'flamer-evidence.json'").replace('PASS four animation witnesses in both captures; sender/index/receiver edges','PASS M104 action witness in both captures; seat_action dispatch edge')
(R/'generate_flamer_spec.py').write_text(s)
edit('test_compat.lua',[("local ffi=require('ffi')","profile,spec=assert(loadfile('work/seat_flamer_weapon_diagnostic/flamer_spec.lua'))()(profile,spec)\nlocal ffi=require('ffi')")])
edit('build.py',[("('binding_spec',R/'binding_spec.lua')","('binding_spec',R/'binding_spec.lua'),('flamer_spec',R/'flamer_spec.lua')"),("R/'test_binding_native.py']","R/'test_binding_native.py',R/'test_flamer_dispatch.py']")])
print('Created isolated 0103 M104 two-step experiment')

