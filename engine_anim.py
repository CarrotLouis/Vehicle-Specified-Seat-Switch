import sys,re
sys.path.insert(0,'work')
from reverse import Module
m=Module('helldivers2.exe')
for r,b in m.sections:
 for x in re.finditer(rb'[ -~]{6,}',b):
  if re.search(rb'animation_(set|state|time)|set_animation|animation_event|animation_layer',x[0],re.I):print(hex(r+x.start()),x[0][:300].decode())
