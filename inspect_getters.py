import sys,struct,re
sys.path.insert(0,'work')
from reverse import Module
m=Module('helldivers2.exe');base=0x7ff7f5df0000
c={}
for r,b in m.sections:
 if r<0x13f5000:continue
 for i in range(0,len(b)-8,8):
  v=struct.unpack_from('<Q',b,i)[0]-base
  if not 0x1000<=v<0x1400000:continue
  code=m.read(v,9)
  if code[:3]==b'\x48\x8b\x81' and code[7]==0xc3 or code[:3]==b'\x48\x8b\x41' and code[4]==0xc3:
   prev=struct.unpack_from('<Q',b,i-8)[0]-base if i>=8 else 0
   nxt=struct.unpack_from('<Q',b,i+8)[0]-base if i+16<len(b) else 0
   if 0x1000<prev<0x1400000 and 0x1000<nxt<0x1400000:c.setdefault(v,[]).append(hex(r+i))
for v,refs in c.items():print(hex(v),m.dis(v,8),refs[:3])

