"""Relocatable native driver-exit witnesses and named animation-resource checks."""
from pathlib import Path
import sys,json,struct
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
from reverse import Module
from capstone.x86 import X86_OP_MEM,X86_REG_RIP,X86_OP_IMM

def lua(v):
 if isinstance(v,str):return json.dumps(v)
 if isinstance(v,bool):return 'true' if v else 'false'
 if isinstance(v,(int,float)):return str(v)
 if isinstance(v,list):return '{'+','.join(map(lua,v))+'}'
 return '{'+','.join('['+lua(k)+']='+lua(x) for k,x in v.items())+'}'

mods=[Module('game.dll',W/'reverse'/('capture-'+b))for b in ['25327279','25480438']]
defs={'tank_driver_active':0x6fe480,'tank_driver_context':0x6fea30,
      'tank_driver_animation':0x7056f0,'tank_driver_scale':0x5b8790}
records={};report=[];edges=[]
for name,rva in defs.items():
 m=mods[1];m.md.detail=True;length=m.function(rva)[1]-rva
 body=m.read(rva,length);mask=bytearray(b'\1'*length)
 for ins in m.md.disasm(body,rva):
  if any(o.type==X86_OP_MEM and o.mem.base==X86_REG_RIP for o in ins.operands):
   off=ins.address-rva+ins.disp_offset;mask[off:off+ins.disp_size]=bytes(ins.disp_size)
  if (ins.group(1)or ins.group(2))and ins.operands and ins.operands[0].type==X86_OP_IMM:
   target=ins.operands[0].imm
   if not rva<=target<rva+length:
    off=ins.address-rva+ins.imm_offset;mask[off:off+ins.imm_size]=bytes(ins.imm_size)
   for other,at in defs.items():
    if target==at:edges.append(dict(**{'from':name},to=other,offset=ins.address-rva,disp=ins.imm_offset,width=ins.imm_size,size=ins.size))
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
   if len(key)>=8 and all(m.code.count(key)==1 for m in mods):needle=dict(offset=c['offset']+start,hex=key.hex());break
  if needle:break
 assert needle,(name,'no unique anchor')
 found=[]
 for m in mods:
  key=bytes.fromhex(needle['hex']);assert m.code.count(key)==1
  at=m.base+m.code.find(key)-needle['offset'];actual=m.read(at,length)
  assert all(actual[c['offset']:c['offset']+len(bytes.fromhex(c['hex']))].hex()==c['hex'] for c in chunks)
  found.append(at)
 records[name]=dict(module='game',hint=rva,length=length,chunks=chunks,needle=needle)
 report.append(dict(name=name,locations=found,length=length,unique_in_both_captures=True))
for source,at in [('sync_bastion_action',0x1192be3),('sync_maelstrom_action',0x1194137)]:
 start=0x11926d0 if 'bastion' in source else 0x1193bf0
 for m in mods:
  assert m.read(at-3,3)==bytes.fromhex('4533c0') # r8d=false in the native driver-exit branch
  assert m.read(at,1)==b'\xe8' and at+5+struct.unpack('<i',m.read(at+1,4))[0]==defs['tank_driver_active']
 edges.append(dict(**{'from':source},to='tank_driver_active',offset=at-start,disp=1,width=4,size=5))

resource=W/'animation_resources/4d1c334d294dfa97.state_machine.main'
b=resource.read_bytes();layers=json.loads((resource.parent/'avatar_states.json').read_text())
groups=struct.unpack_from('<I',b,8)[0];assert struct.unpack_from('<I',b,groups)[0]==31
layer=groups+struct.unpack_from('<I',b,groups+4+8*4)[0]
assert struct.unpack_from('<I',b,layer+8)[0]==332
states=[]
for index,name in [(0,'action/Action_Empty'),(237,'action/Fall'),(238,'action/Fall_Aim')]:
 assert layers[8]['states'][index]['name']==name
 state=layer+struct.unpack_from('<I',b,layer+12+index*4)[0]
 states.append(dict(layer=8,count=332,index=index,hash_hex=b[state:state+8].hex(),name=name))
event='0x1e84c4c3'
assert all(s['transitions'][event]['target']==0 for s in layers[8]['states'])
assert all(event not in s['transitions']for i in [0,13]for s in layers[i]['states'])
affected={str(i):[j for j,s in enumerate(l['states'])if event in s['transitions']]for i,l in enumerate(layers)}
affected={i:v for i,v in affected.items()if v}
assert set(affected)=={'7','8','17'} and len(affected['7'])==len(affected['17'])==1
assert 3 not in affected['7'] and 18 not in affected['17']
source='return function(profile,spec)\nlocal records='+lua(records)+'\n'
source+='for name,d in pairs(records)do spec.records[name]=d;spec.core[#spec.core+1]=name;profile.functions[name]={rva=d.hint}end\n'
source+='for _,e in ipairs('+lua(edges)+')do spec.edges[#spec.edges+1]=e end\n'
source+='spec.globals.driver[#spec.globals.driver+1]={record="tank_driver_active",offset=0x29,disp=3,width=4,size=7}\n'
source+='local function bytes(hex)return hex:gsub("..",function(x)return string.char(tonumber(x,16))end)end\n'
source+='profile.animation.bastion_fall={event=0x1e84c4c3,states='+lua(states)+'}\n'
source+='for _,s in ipairs(profile.animation.bastion_fall.states)do s.hash=bytes(s.hash_hex)end\nreturn profile,spec\nend\n'
(R/'tank_spec.lua').write_text(source)
(R/'tank-native-evidence.json').write_text(json.dumps(dict(witnesses=report,edges=edges,fall_states=states,event=event,affected_layers=affected,
 boundary='Native driver-exit false call confirmed in both captures. Resource transition verified; actual visuals and remote delivery remain unverified.'),indent=2))
print('PASS four driver-exit witnesses, native false-argument edges in both captures, named fall states and event seat-layer preservation')
