from pathlib import Path
import struct,sys
class Dump:
 def __init__(self,p):
  self.data=Path(p).read_bytes();d=self.data
  assert d[:4]==b'MDMP'
  n,o=struct.unpack_from('<II',d,8)
  self.stream={t:(r,s) for t,s,r in (struct.unpack_from('<III',d,o+i*12) for i in range(n)) if t}
  self.regions=[];r,s=self.stream[5]
  for i in range(struct.unpack_from('<I',d,r)[0]):
   a,n,p=struct.unpack_from('<QII',d,r+4+i*16);self.regions.append((a,n,p))
  self.modules=[];r,s=self.stream[4]
  for i in range(struct.unpack_from('<I',d,r)[0]):
   a,n,_,_,p=struct.unpack_from('<QIIII',d,r+4+i*108);ln=struct.unpack_from('<I',d,p)[0]
   self.modules.append((a,n,d[p+4:p+4+ln].decode('utf-16-le')))
 def read(self,a,n):
  for start,size,p in self.regions:
   if start<=a and a+n<=start+size:return self.data[p+a-start:p+a-start+n]
  return b''
 def symbol(self,a):
  for start,size,p in self.modules:
   if start<=a<start+size:return p.split('\\')[-1]+f'+{a-start:x}'
  return hex(a)
 def context(self,p):
  names=['rax','rcx','rdx','rbx','rsp','rbp','rsi','rdi','r8','r9','r10','r11','r12','r13','r14','r15','rip']
  return dict(zip(names,struct.unpack_from('<17Q',self.data,p+120)))
if __name__=='__main__':
 d=Dump(sys.argv[1]);r,s=d.stream[6];tid=struct.unpack_from('<I',d.data,r)[0];size,p=struct.unpack_from('<II',d.data,r+160);regs=d.context(p)
 print('exception_thread',tid,'registers',{k:d.symbol(v) for k,v in regs.items()})
 r,s=d.stream[3]
 for i in range(struct.unpack_from('<I',d.data,r)[0]):
  row=r+4+i*48;id=struct.unpack_from('<I',d.data,row)[0];size,p=struct.unpack_from('<II',d.data,row+40);reg=d.context(p)
  stack=d.read(reg['rsp'],0x300);frames=[]
  for o in range(0,len(stack)-7,8):
   v=struct.unpack_from('<Q',stack,o)[0];name=d.symbol(v)
   if '+' in name and any(x in name for x in ['helldivers2','game.dll','lua51']):frames.append((hex(o),name))
  if frames or id==tid:print('thread',id,d.symbol(reg['rip']),'stack_scan',frames[:14])
