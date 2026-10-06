"""Generate relocatable code witnesses from two preserved, immutable captures."""
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
from reverse import Module
from capstone.x86 import X86_OP_MEM,X86_REG_RIP,X86_OP_IMM
def lua(v):
 if isinstance(v,str):return json.dumps(v)
 if isinstance(v,bool):return 'true' if v else 'false'
 if isinstance(v,(int,float)):return str(v)
 if isinstance(v,list):return '{'+','.join(map(lua,v))+'}'
 return '{'+','.join('['+lua(k)+']='+lua(x) for k,x in v.items())+'}'
defs=[('action','game',0x118b300,None)]
mods={key:[Module(filename,W/'reverse'/('capture-'+b)) for b in ('25327279','25480438')]
      for key,filename in [('game','game.dll'),('exe','helldivers2.exe')]}
records={};report=[]
for short,module,rva,length in defs:
 name='flamer_'+short;old,m=mods[module];m.md.detail=True
 length=length or m.function(rva)[1]-rva;body=m.read(rva,length);mask=bytearray(b'\1'*length)
 for ins in m.md.disasm(body,rva):
  if any(o.type==X86_OP_MEM and o.mem.base==X86_REG_RIP for o in ins.operands):
   start=ins.address-rva+ins.disp_offset;mask[start:start+ins.disp_size]=bytes(ins.disp_size)
  if (ins.group(1)or ins.group(2))and ins.operands and ins.operands[0].type==X86_OP_IMM:
   if not rva<=ins.operands[0].imm<rva+length:
    start=ins.address-rva+ins.imm_offset;mask[start:start+ins.imm_size]=bytes(ins.imm_size)
 chunks=[];i=0
 while i<length:
  if not mask[i]:i+=1;continue
  j=i+1
  while j<length and mask[j]:j+=1
  chunks.append(dict(offset=i,hex=body[i:j].hex()));i=j
 needle=None
 for c in sorted(chunks,key=lambda c:len(c['hex']),reverse=True):
  data=bytes.fromhex(c['hex'])
  for start in range(max(1,len(data)-31)):
   key=data[start:start+32]
   if len(key)>=8 and all(sample.code.count(key)==1 for sample in (old,m)):
    needle=dict(offset=c['offset']+start,hex=key.hex());break
  if needle:break
 assert needle,(name,'no unique literal anchor')
 locations=[]
 for sample in (old,m):
  key=bytes.fromhex(needle['hex']);assert sample.code.count(key)==1,(name,'ambiguous witness')
  found=sample.base+sample.code.find(key)-needle['offset'];actual=sample.read(found,length)
  assert all(actual[c['offset']:c['offset']+len(bytes.fromhex(c['hex']))].hex()==c['hex'] for c in chunks),(name,hex(found))
  locations.append(found)
 records[name]=dict(module=module,hint=rva,length=length,chunks=chunks,needle=needle)
 report.append(dict(name=name,locations=locations,length=length,unique_in_both_captures=True))
edges=[dict(**{'from':'seat_action'},to='flamer_action',offset=0xf2d,disp=1,width=4,size=5)]
source='return function(profile,spec)\nlocal records='+lua(records)+'\n'
source+='for name,d in pairs(records)do spec.records[name]=d;spec.core[#spec.core+1]=name;local t=d.module=="exe" and profile.engine_functions or profile.functions;t[name]={rva=d.hint}end\n'
source+='for _,edge in ipairs('+lua(edges)+')do spec.edges[#spec.edges+1]=edge end\nreturn profile,spec\nend\n'
(R/'flamer_spec.lua').write_text(source);(R/'flamer-evidence.json').write_text(json.dumps(report,indent=2))
print('PASS M104 action witness in both captures; seat_action dispatch edge')
