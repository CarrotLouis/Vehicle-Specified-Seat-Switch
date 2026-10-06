from reverse import Module,OLD_CAPTURE
from capstone.x86_const import X86_OP_MEM,X86_REG_RIP
import re,json
from pathlib import Path
old,new=Module(root=OLD_CAPTURE),Module()
old.md.detail=True
functions={
 'next':0x638090,'previous':0x638260,'reserve':0x62de90,'release':0x62e370,
 'authority':0x62f0c0,'set_role':0x637660,'restore_seated':0x638460,
 'net_ref':0xd3e5d0,'send':0xbcab50,'ownership_busy':0xd42f20,
 'next_free':0x62fdd0,'previous_free':0x62ff50,'owner_switch':0x630d00,
 'role':0xef5490,'route':0xef69b0,'adjacency':0xef6310,
 'restore_action':0xefa1a0,'action':0xefab40,'complete_action':0xefc430,
 'seater_update':0x6334c0,'switch_success':0x637af0,'goto_node':0x633fe0,
 'entity_get':0xd3e8d0,'entity_unit':0xd3e680,'snapshot_send':0x6386f0,
}
result={}
for name,addr in functions.items():
 matches=[];selected=0
 for length in [160,96,48,32,24]:
  raw=old.read(addr,length);mask=[False]*len(raw)
  for i in old.md.disasm(raw,addr):
   p=i.address-addr
   if i.disp_size and (abs(i.disp)>0x100000 or any(o.type==X86_OP_MEM and o.mem.base==X86_REG_RIP for o in i.operands)):
    for j in range(p+i.disp_offset,p+i.disp_offset+i.disp_size):mask[j]=True
   if i.imm_size and (i.mnemonic.startswith('j') or i.mnemonic=='call'):
    for j in range(p+i.imm_offset,p+i.imm_offset+i.imm_size):mask[j]=True
  rx=b''.join(b'.' if masked else re.escape(bytes([byte])) for byte,masked in zip(raw,mask))
  matches=[m.start()+new.base for m in re.finditer(rx,new.code,re.S)]
  if len(matches)==1:selected=length;break
 result[name]={'old':hex(addr),'new':[hex(a) for a in matches],'matched_bytes':selected}
 if len(matches)==1:
  Path('work/reverse/new_'+name+'.txt').write_text(new.dis(matches[0],None if new.function(matches[0]) else 512))
Path('work/reverse/port.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
