import sys,re,struct
from pathlib import Path
sys.path.insert(0,'work');sys.path.insert(0,'work/BingusSharedLoader/scripts')
from reverse import Module
from archive import resource_hash
m=Module();names={}
for f in ['thinhashes.txt','hashes.txt']:
 for line in Path('work/filediver/hashes/'+f).read_text(errors='replace').splitlines():
  if line and not line.startswith('//'):names[resource_hash(line)>>32]=line
for label,addr in [('m102_complete',0x1189380),('m104_complete',0x118bf20),('m104_action',0x118b300),('maelstrom_action',0x1193bf0),('flag_add',0x11b09e0),('gun_target',0x11b52b0),('event',0x119fec0),('anim_state',0x11b53c0),('aim_set',0x11a7ba0),('aim_clear',0x11a7f80),('vehicle_bind_reset',0x11b1070),('actor_input',0xa7d700)]:
 s=m.dis(addr)
 s=re.sub(r'0x[0-9a-f]+',lambda x:x[0]+(' ['+names[int(x[0],16)]+']' if int(x[0],16) in names else ''),s)
 Path('work/reverse/new_'+label+'.txt').write_text(s)
for name in ['m102_action','tank_action','tank_complete','maelstrom_complete']:
 p=Path('work/reverse/new_'+name+'.txt');s=p.read_text();s=re.sub(r'0x[0-9a-f]+',lambda x:x[0]+(' ['+names[int(x[0],16)]+']' if int(x[0],16) in names else ''),s);p.write_text(s)
Path('work/reverse/thin_names.json').write_text(__import__('json').dumps({hex(k):v for k,v in names.items()}))
