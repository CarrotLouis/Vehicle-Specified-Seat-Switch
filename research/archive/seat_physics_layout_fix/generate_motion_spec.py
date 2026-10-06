"""Identify native, read-only actor velocity witnesses in both frozen images."""
from pathlib import Path
import sys,json,struct
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
from reverse import Module
from capstone.x86 import X86_OP_MEM,X86_REG_RIP,X86_OP_IMM
mods={name:[Module(name,W/'reverse'/('capture-'+b))for b in ['25327279','25480438']]for name in ['game.dll','helldivers2.exe']}
defs={
 'motion_vehicle_velocity':('game.dll',0x719a20,0x145),
 'motion_resource_profile':('game.dll',0x507a90,0xb2),
 'motion_actor_lookup':('helldivers2.exe',0x799de0,0xbc),
 'motion_actor_resolve':('helldivers2.exe',0x7951b0,0x68),
 'motion_unit_actors':('helldivers2.exe',0x7e1c20,0x369),
 'motion_unit_actor_count':('helldivers2.exe',0x7e10f0,0x78),
 'motion_actor_velocity':('helldivers2.exe',0x799540,0xb0),
 'motion_actor_position':('helldivers2.exe',0x7999a0,0xe9),
}
def lua(v):
 if isinstance(v,str):return json.dumps(v)
 if isinstance(v,bool):return 'true'if v else'false'
 if isinstance(v,(int,float)):return str(v)
 if isinstance(v,list):return '{'+','.join(map(lua,v))+'}'
 return '{'+','.join('['+lua(k)+']='+lua(x)for k,x in v.items())+'}'
records={};edges=[];report=[]
for name,(mod,rva,length)in defs.items():
 ms=mods[mod];m=ms[-1];m.md.detail=True;body=m.read(rva,length);mask=bytearray(b'\1'*length)
 for ins in m.md.disasm(body,rva):
  if any(o.type==X86_OP_MEM and o.mem.base==X86_REG_RIP for o in ins.operands):
   off=ins.address-rva+ins.disp_offset;mask[off:off+ins.disp_size]=bytes(ins.disp_size)
  if(ins.group(1)or ins.group(2))and ins.operands and ins.operands[0].type==X86_OP_IMM:
   target=ins.operands[0].imm
   if not rva<=target<rva+length:
    off=ins.address-rva+ins.imm_offset;mask[off:off+ins.imm_size]=bytes(ins.imm_size)
   for other,(om,at,_)in defs.items():
    if om==mod and target==at:edges.append(dict(**{'from':name},to=other,offset=ins.address-rva,disp=ins.imm_offset,width=ins.imm_size,size=ins.size))
 chunks=[];i=0
 while i<length:
  if not mask[i]:i+=1;continue
  j=i+1
  while j<length and mask[j]:j+=1
  chunks.append(dict(offset=i,hex=body[i:j].hex()));i=j
 needle=None
 for c in sorted(chunks,key=lambda x:len(x['hex']),reverse=True):
  data=bytes.fromhex(c['hex'])
  for off in range(max(1,len(data)-15)):
   key=data[off:off+32]
   if len(key)>=12 and all(x.code.count(key)==1 for x in ms):needle=dict(offset=c['offset']+off,hex=key.hex());break
  if needle:break
 assert needle,(name,'no unique code anchor')
 locations=[]
 for m in ms:
  key=bytes.fromhex(needle['hex']);at=m.base+m.code.find(key)-needle['offset'];actual=m.read(at,length)
  assert all(actual[c['offset']:c['offset']+len(bytes.fromhex(c['hex']))].hex()==c['hex']for c in chunks),(name,at)
  locations.append(at)
 records[name]=dict(module='game'if mod=='game.dll'else'exe',hint=rva,length=length,chunks=chunks,needle=needle)
 report.append(dict(name=name,length=length,locations=locations,unique_in_both=True))
refs={
 'component_manager':dict(record='motion_vehicle_velocity',offset=0x24,disp=3,size=7),
 'lookup_api':dict(record='motion_vehicle_velocity',offset=0xb5,disp=3,size=7),
 'velocity_api':dict(record='motion_vehicle_velocity',offset=0xe2,disp=3,size=7),
 'resource_manager':dict(record='motion_resource_profile',offset=0x17,disp=3,size=7),
 'unit_components':dict(record='motion_unit_actors',offset=0x1a,disp=3,size=7),
 'actor_pools':dict(record='motion_actor_resolve',offset=0x14,disp=3,size=7),
 'physics_worlds':dict(record='motion_actor_velocity',offset=0x36,disp=3,size=7),
}
for key,ref in refs.items():
 mod,rva,_=defs[ref['record']];m=mods[mod][-1];off=rva+ref['offset'];b=m.read(off,ref['size'])
 assert b[:3]in [bytes.fromhex(s)for s in ['488b1d','488b05','4c8b0d','488d0d'] ],(key,b.hex())
 ref['opcode_hex']=b[:3].hex();ref['expected_rva']=off+ref['size']+struct.unpack('<i',b[ref['disp']:ref['disp']+4])[0]
 # Independent body identity, not the seat component key or network id.
 if key=='component_manager':assert ref['expected_rva']==0x3326458
 if key=='physics_worlds':assert ref['expected_rva']==0x27ba8a8
source='return function(profile,spec)\nlocal records='+lua(records)+'\n'
source+='for name,d in pairs(records)do spec.records[name]=d;local group=d.module=="game"and spec.core or spec.engine;group[#group+1]=name;local fs=d.module=="game"and profile.functions or profile.engine_functions;fs[name]={rva=d.hint}end\n'
source+='for _,e in ipairs('+lua(edges)+')do spec.edges[#spec.edges+1]=e end\n'
source+='profile.motion={records=records,refs='+lua(refs)+'}\nreturn profile,spec\nend\n'
(R/'motion_spec.lua').write_text(source,encoding='utf8')
(R/'motion-native-evidence.json').write_text(json.dumps(dict(witnesses=report,edges=edges,refs=refs,boundary='Native actor getter contract, relocation and call edges validated offline. Real physics state and ownership reset phase require in-game observation.'),indent=2),encoding='utf8')
print('PASS eight relocatable motion witnesses and body/actor/API relationships in two frozen captures')
