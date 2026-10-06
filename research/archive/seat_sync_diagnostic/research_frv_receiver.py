"""Explore actual FRV receiver and action=-1 branches offline; no live game."""
from pathlib import Path
R=Path(__file__).resolve().parent
src=(R.parent/'tankseatkit_research/test_receiver_candidates.py').read_text()
src=src.replace("R=Path(__file__).resolve().parent", "R=Path(__file__).resolve().parent")
src=src.replace('for layout in (43,44):','for layout in (26,):')
src=src.replace('((0,1),(1,0))','((1,2),(2,1))')
src=src.replace('source+1','3').replace('target+1','3')
src=src.replace('stubs={0x5a3020,','stubs={0x1738230,0x5a3020,') # FRV diagnostic logging; no gameplay action stub added.
src=src.replace('def hook(vm,address,size,user):',"stubs.add(0x1188005+struct.unpack('<i',v.mod.read(0x1188001,4))[0])\ndef hook(vm,address,size,user):")
src=src.replace('results=[]',"history=[]\nvm.hook_add(UC_HOOK_CODE,lambda vm,a,n,u: (history.append(a),history.pop(0) if len(history)>35 else None))\nresults=[]")
src=src.replace("out=R/'capture-20260927'/('receiver-candidates-'+BUILD+'.json')","out=R/('frv-receiver-'+BUILD+'.json')")
src=src.replace("'tank receiver counterexamples/candidate; no rendering/network claim'","'FRV passenger receiver; no rendering/network claim'")
try:exec(compile(src,str(R/'frv_receiver_generated.py'),'exec'))
except Exception:
 rip=vm.reg_read(UC_X86_REG_RIP)
 print('Stopped at',hex(rip),'calls',calls)
 for a in history:
  if a>0x1000:
   for ins in v.mod.md.disasm(v.mod.read(a,15),a):print(hex(ins.address),ins.mnemonic,ins.op_str);break
 for ins in v.mod.md.disasm(v.mod.read(rip-24,80),rip-24):print(hex(ins.address),ins.mnemonic,ins.op_str)
 raise
