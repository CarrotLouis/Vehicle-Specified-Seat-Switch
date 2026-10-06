import sys,struct
sys.path.insert(0,'work')
from reverse import Module
m=Module('helldivers2.exe');base=0x7ff7f5df0000
for r,b in m.sections:
 if r<0x13f5000:continue
 for i in range(0,len(b)-0x1c0,8):
  q=struct.unpack_from('<Q',b,i)[0]-base
  if not 0x13f5000<=q<0x1900000:continue
  raw=m.read(q,24)
  if len(raw)!=24:continue
  sig,off,cons,tr,hr,selfr=struct.unpack('<6I',raw)
  if sig!=1 or selfr!=q:continue
  td=m.read(tr,128)
  if b'Unit' not in td.split(b'\0',1)[0] and b'Unit' not in td[16:].split(b'\0',1)[0]:continue
  vt=r+i+8;getter=struct.unpack_from('<Q',b,i+8+0x1b0)[0]-base
  print(hex(vt),td[16:].split(b'\0',1)[0],hex(getter),m.dis(getter,40))
