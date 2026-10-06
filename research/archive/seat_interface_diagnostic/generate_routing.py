"""Generate normalized evidence from preserved code, never a live process."""
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
from reverse import Module
from capstone.x86 import X86_OP_MEM,X86_REG_RIP,X86_OP_IMM
def lua(v):
 if isinstance(v,str):return json.dumps(v)
 if isinstance(v,bool):return 'true'if v else'false'
 if isinstance(v,(int,float)):return str(v)
 if isinstance(v,list):return '{'+','.join(map(lua,v))+'}'
 return '{'+','.join('['+lua(k)+']='+lua(x)for k,x in v.items())+'}'
defs=[('route_send_one','exe',0x3502c0,None),('route_send_many','exe',0x34ff40,None),
 ('route_decode','exe',0x34f810,None),('route_registry_lookup','exe',0x173ae0,None),
 ('route_setup','game',0x134d470,None),('route_dispatch','game',0xbc2d10,17)]
records={};report=[]
for name,module,rva,length in defs:
 mods=[Module('game.dll'if module=='game'else'helldivers2.exe',W/'reverse'/('capture-'+build))for build in ['25327279','25480438']]
 m=mods[-1];m.md.detail=True
 if length is None:length=m.function(rva)[1]-rva
 b=m.read(rva,length);mask=bytearray(b'\x01'*length)
 for ins in m.md.disasm(b,rva):
  if any(o.type==X86_OP_MEM and o.mem.base==X86_REG_RIP for o in ins.operands):
   a=ins.address-rva+ins.disp_offset;mask[a:a+ins.disp_size]=bytes(ins.disp_size)
  if (ins.group(1)or ins.group(2))and ins.operands and ins.operands[0].type==X86_OP_IMM:
   if not rva<=ins.operands[0].imm<rva+length:
    a=ins.address-rva+ins.imm_offset;mask[a:a+ins.imm_size]=bytes(ins.imm_size)
 chunks=[];i=0
 while i<length:
  if not mask[i]:i+=1;continue
  j=i+1
  while j<length and mask[j]:j+=1
  chunks.append(dict(offset=i,hex=b[i:j].hex()));i=j
 needle=max(chunks,key=lambda c:len(c['hex']));needle=dict(offset=needle['offset'],hex=needle['hex'][:64])
 locations=[]
 for sample in mods:
  key=bytes.fromhex(needle['hex']);assert sample.code.count(key)==1,(name,'ambiguous needle')
  found=sample.base+sample.code.find(key)-needle['offset'];locations.append(found)
  actual=sample.read(found,length);assert all(actual[c['offset']:c['offset']+len(bytes.fromhex(c['hex']))].hex()==c['hex']for c in chunks),(name,hex(found))
 records[name]=dict(module=module,hint=rva,length=length,chunks=chunks,needle=needle)
 report.append(dict(name=name,module=module,rva=rva,length=length,masked_bytes=mask.count(0),both_builds_match=True,build_rvas=locations))
source='return function(profile,spec)\nlocal records='+lua(records)+'\n'
source+='for name,d in pairs(records)do spec.records[name]=d;spec.core[#spec.core+1]=name;local t=d.module=="exe" and profile.engine_functions or profile.functions;t[name]={rva=d.hint}end\n'
source+='for _,edge in ipairs('+lua([dict(from_='route_send_one',to='route_send_many',offset=0x1c,disp=1,width=4,size=5),dict(from_='route_send_many',to='route_registry_lookup',offset=0x48,disp=1,width=4,size=5)]).replace('["from_"]','["from"]')+')do spec.edges[#spec.edges+1]=edge end\nreturn profile,spec\nend\n'
(R/'routing_spec.lua').write_text(source)
(R/'routing-evidence.json').write_text(json.dumps(report,indent=2))
print('PASS six routing proofs: both preserved builds match, unique anchors, relocatable references masked')
