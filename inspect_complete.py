import sys,struct
from pathlib import Path
sys.path.insert(0,'work')
from reverse import Module
m=Module()
for t in [26,27,28,33,43,44]:
 target=struct.unpack('<I',m.read(0x119d2e0+(t-1)*4,4))[0]
 print('complete',t,hex(target),m.dis(target,32))
for label,addr in [('tank_complete',0x1193300),('maelstrom_complete',0x1194860),('mounted_reset',0x832670),('attach',0x119fc60),('seated_restore',0x63eb10),('actor_input',0xa7d700)]:
 Path('work/reverse/new_'+label+'.txt').write_text(m.dis(addr))
print(m.dis(0x1193300))
