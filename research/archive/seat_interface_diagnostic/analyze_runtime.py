from pathlib import Path
import sys,json,collections,re,shutil
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W))
from reverse import Module
from capstone.x86 import X86_OP_MEM,X86_OP_REG
out=R/'session-20260925-041449';out.mkdir(exist_ok=True)
logs=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
name='VehicleSeatInterface-20260925-041449-11868-30147140.log'
for n in [name,'VehicleSeatInterfaceDiagnostic.log']:
 if not(out/n).exists():shutil.copyfile(logs/n,out/n)
events=[json.loads(l)for l in(out/name).read_text().splitlines()]
rows=[x for x in events if x['event']=='interface_snapshot']
assert len(rows)==10 and all(x['state']=='observed'for x in rows)
summary={'rounds':len(rows),'end':events[-1],'slots':[]}
for i in range(2):
 slots=[r['slots'][i]for r in rows]
 identities={(s['target']['module'],s['target']['rva'],s['head_hex'],s['storage']['rva'])for s in slots}
 assert len(identities)==1
 module,rva,head,storage=next(iter(identities));comparisons=[]
 for build in ['25327279','25480438']:
  m=Module(module,W/'reverse'/('capture-'+build));same=m.read(rva,64).hex()==head
  assert same
  (out/(build+'-'+slots[0]['name']+'.txt')).write_text(m.dis(rva))
  comparisons.append({'build':build,'head_matches':same,'function':m.function(rva)})
 summary['slots'].append(dict(name=slots[0]['name'],module=module,rva=rva,storage=storage,
  writable_all=all(s['storage']['writable']for s in slots),comparisons=comparisons))
m=Module(root=W/'reverse/capture-25480438');m.md.detail=True
# Short straight-line register data-flow from each root load. Findings are candidates,
# not complete control-flow proofs; review the original function before any use.
found=[]
for addr,_,fn in m.xrefs([0x3326308]):
 taint={};net=False
 for j,ins in enumerate(m.md.disasm(m.read(addr,112),addr)):
  ops=ins.operands
  if j==0:
   if ins.mnemonic!='mov' or ops[0].type!=X86_OP_REG:break
   taint[ops[0].reg]='services';continue
  if ins.mnemonic in ['call','jmp']:
   if len(ops)==1 and ops[0].type==X86_OP_MEM and taint.get(ops[0].mem.base)=='network':
    found.append(dict(reference=addr,call=ins.address,slot=ops[0].mem.disp,function=fn))
   break
  if ins.mnemonic=='ret'or ins.group(1):break
  value=None
  if ins.mnemonic=='mov' and len(ops)==2 and ops[0].type==X86_OP_REG:
   if ops[1].type==X86_OP_REG:value=taint.get(ops[1].reg)
   elif ops[1].type==X86_OP_MEM and not ops[1].mem.index and taint.get(ops[1].mem.base)=='services' and ops[1].mem.disp==0x38:value='network'
  for reg in ins.regs_access()[1]:taint.pop(reg,None)
  if value:taint[ops[0].reg]=value
(out/'network-api-calls.json').write_text(json.dumps(found,indent=2))
(out/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
print('NETWORK API CALLS',len(found))
for f in found:
 if f['slot']not in [0,8,16,56,64]:print(hex(f['call']),'slot',hex(f['slot']),'function',hex(f['function'][0])if f['function']else 'leaf')
