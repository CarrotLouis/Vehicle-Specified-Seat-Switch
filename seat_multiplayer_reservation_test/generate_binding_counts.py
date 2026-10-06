"""Two saved-build witnesses for total vs prefix component count semantics."""
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
old,m=[Module('game.dll',W/'reverse'/('capture-'+b))for b in ('25327279','25480438')]
records={};report=[];reference=None
for name,point in [('binding_manager_add_total',0x53fbe4),('binding_manager_add_prefix',0x53fca4)]:
 start,end=m.function(point)[:2];body=m.read(start,end-start);m.md.detail=True;mask=bytearray(b'\1'*len(body))
 for ins in m.md.disasm(body,start):
  if any(o.type==X86_OP_MEM and o.mem.base==X86_REG_RIP for o in ins.operands):
   i=ins.address-start+ins.disp_offset;mask[i:i+ins.disp_size]=bytes(ins.disp_size)
  if (ins.group(1)or ins.group(2))and ins.operands and ins.operands[0].type==X86_OP_IMM and not start<=ins.operands[0].imm<end:
   i=ins.address-start+ins.imm_offset;mask[i:i+ins.imm_size]=bytes(ins.imm_size)
 chunks=[];i=0
 while i<len(body):
  if not mask[i]:i+=1;continue
  j=i+1
  while j<len(body)and mask[j]:j+=1
  chunks.append({'offset':i,'hex':body[i:j].hex()});i=j
 needle=None
 for c in sorted(chunks,key=lambda x:len(x['hex']),reverse=True):
  b=bytes.fromhex(c['hex'])
  for offset in range(max(1,len(b)-31)):
   key=b[offset:offset+32]
   if len(key)>=8 and all(x.code.count(key)==1 for x in (old,m)):
    needle={'offset':c['offset']+offset,'hex':key.hex()};break
  if needle:break
 # A second manager uses an identical generic initializer body. Its RIP
 # reference distinguishes it from the actual weapon manager; full body,
 # semantic handler and shared root are all required at runtime.
 if not needle:
  c=max(chunks,key=lambda x:len(x['hex']));needle={'offset':c['offset'],'hex':c['hex'][:64]}
 def matches(sample):
  key=bytes.fromhex(needle['hex']);found=[];at=0
  while True:
   at=sample.code.find(key,at)
   if at<0:break
   rva=sample.base+at-needle['offset'];at+=1
   actual=sample.read(rva,len(body))
   if all(actual[c['offset']:c['offset']+len(bytes.fromhex(c['hex']))].hex()==c['hex']for c in chunks):
    ref=rva+point-start
    target=ref+7+int.from_bytes(sample.read(ref+3,4),'little',signed=True)
    clear=0x11a7f80+0x1d
    expected=clear+7+int.from_bytes(sample.read(clear+3,4),'little',signed=True)
    if target==expected:found.append(rva)
  return found
 locations=[]
 for sample in (old,m):
  found=matches(sample);assert len(found)==1,(name,found);locations.append(found[0])
 references=[{'record':'binding_clear_avatar','offset':point-start,'disp':3,'width':4,'size':7,
  'reference':{'offset':0x1d,'disp':3,'width':4,'size':7}}]
 records[name]={'module':'game','hint':start,'length':len(body),'chunks':chunks,'needle':needle,'references':references}
 report.append({'name':name,'rva':start,'length':len(body),'locations':locations,'literal_anchor_hits':m.code.count(bytes.fromhex(needle['hex'])),'unique_after_shared_root_proof':True})
 if name=='binding_manager_add_total':reference=point-start
source='return function(profile,spec)\nlocal records='+lua(records)+'\n'
source+='for name,d in pairs(records)do spec.records[name]=d;spec.core[#spec.core+1]=name;profile.functions[name]={rva=d.hint}end\n'
source+='profile.binding_counts={total=0x18,enabled=0x1c,prefix=0x20,reference_offset='+str(reference)+'}\nreturn profile,spec\nend\n'
(R/'binding_counts_spec.lua').write_bytes(source.encode());(R/'binding-count-evidence.json').write_text(json.dumps(report,indent=2))
print('PASS two saved-build total/prefix initialization witnesses; full body plus semantic shared-root proof',report)
