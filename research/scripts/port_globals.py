from reverse import Module, OLD_CAPTURE
from capstone.x86_const import X86_OP_MEM, X86_REG_RIP
from pathlib import Path
import re,json
old,new=Module(root=OLD_CAPTURE),Module()
old.md.detail=True;new.md.detail=True
def matches(addr,length):
 raw=old.read(addr,length);mask=[False]*len(raw)
 for i in old.md.disasm(raw,addr):
  p=i.address-addr
  if i.disp_size and (abs(i.disp)>0x100000 or any(o.type==X86_OP_MEM and o.mem.base==X86_REG_RIP for o in i.operands)):
   for j in range(p+i.disp_offset,p+i.disp_offset+i.disp_size):mask[j]=True
  if i.imm_size and (i.mnemonic.startswith('j') or i.mnemonic=='call'):
   for j in range(p+i.imm_offset,p+i.imm_offset+i.imm_size):mask[j]=True
 rx=b''.join(b'.' if m else re.escape(bytes([b])) for b,m in zip(raw,mask))
 return [m.start()+new.base for m in re.finditer(rx,new.code,re.S)]
if __name__=='__main__':
 result={}
 for name,rva in {'player':0x276c190,'mission':0x276c3d0,'avatar':0x276ca30,'seater':0x276ca88,'collection':0x276ca98,'entities':0x276f0c0}.items():
  found=[]
  for addr,_,f in old.xrefs([rva])[:40]:
   mm=matches(addr,96)
   if len(mm)!=1:continue
   ins=next(new.md.disasm(new.read(mm[0],15),mm[0]))
   target=ins.address+ins.size+ins.disp
   found.append({'old_xref':hex(addr),'new_xref':hex(mm[0]),'global':hex(target)})
   if len(found)>=3:break
  result[name]=found
 for addr in [0x602d20,0x4ab290,0x4aec60]:
  mm=matches(addr,160)
  if len(mm)==1:Path(f'work/reverse/port_{addr:x}.txt').write_text(new.dis(mm[0]))
 result['helpers']={}
 for addr in [0x602d20,0x4ab290,0x4aec60]:result['helpers'][hex(addr)]=[hex(x) for x in matches(addr,160)]
 Path('work/reverse/globals_port.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
