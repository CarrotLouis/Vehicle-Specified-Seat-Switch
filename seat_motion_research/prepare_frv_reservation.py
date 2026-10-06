"""Create an isolated FRV extension; preserve the accepted 0.26.0 inputs."""
from pathlib import Path
import shutil
W=Path(__file__).resolve().parent.parent;A=W/'seat_reservation_test';B=W/'seat_reservation_frv_test'
assert not B.exists(),'preserve existing candidate'
B.mkdir()
omit={'package.json','artifact-verification.json','tests-passed.json','verify_artifact.py','bundled.lua','assembly-origins.json'}
for p in A.iterdir():
 if p.is_file()and p.name not in omit and p.suffix not in ('.exe','.dll'):
  data=p.read_bytes()
  if p.suffix in ('.lua','.py','.c','.h','.S','.txt','.json'):
   data=data.decode('utf-8').replace('work/seat_reservation_test/','work/seat_reservation_frv_test/').replace('0.26.0','0.27.0').encode()
  (B/p.name).write_bytes(data)
s=(B/'native.c').read_text().replace('VSST_version(void){return 2;}','VSST_version(void){return 3;}');(B/'native.c').write_text(s)
s=(B/'gate.c').read_text().replace('c->source>3','c->source>4').replace('c->target>3','c->target>4');(B/'gate.c').write_text(s)
s=(B/'transport.lua').read_text().replace('VSST_version()==2','VSST_version()==3');(B/'transport.lua').write_text(s)
s=(B/'prepare_tests.py').read_text().replace('VSST_version()==2','VSST_version()==3').replace("return 2 end'","return 3 end'")
# The original transport test starts from ABI1; its mock must become ABI3.
s=s.replace("'VSST_version()==3').replace('VSST_version=function()return 1 end','VSST_version=function()return 2 end')",
            "'VSST_version()==3').replace('VSST_version=function()return 1 end','VSST_version=function()return 3 end')")
(B/'prepare_tests.py').write_text(s)
s=(B/'test_gate.c').read_text().replace('c.target=4;assert(VSST_gate_arm(&c)==-1);',
 'c.target=4;assert(VSST_gate_arm(&c)==0);values[2]=4;receive(222,0x2e986f01,3);assert(VSST_gate_peek(&r)==1&&r.status==2&&r.chosen==4);assert(VSST_gate_finish(c.cookie)==0);c.source=4;c.target=1;assert(VSST_gate_arm(&c)==0);values[2]=1;receive(222,0x2e986f01,3);assert(VSST_gate_peek(&r)==1&&r.status==2&&r.source==4);assert(VSST_gate_finish(c.cookie)==0);c.target=5;assert(VSST_gate_arm(&c)==-1);')
(B/'test_gate.c').write_text(s)
s=(B/'generate_spec.py').read_text().replace("('interaction_update','game',0x9770a0,0x2be)]",
 "('interaction_update','game',0x9770a0,0x2be),('mounted_joint_tags','game',0x119a2a0,0x404),('related_weapon_lookup','game',0x5a8870,0xf4),('related_weapon_resource','game',0x5106d0,None)]")
s=s.replace('PASS six reservation witnesses','PASS nine reservation witnesses')
(B/'generate_spec.py').write_text(s)
print('PASS isolated0.27 FRV candidate; accepted0.26 source/binary/archive unchanged')
