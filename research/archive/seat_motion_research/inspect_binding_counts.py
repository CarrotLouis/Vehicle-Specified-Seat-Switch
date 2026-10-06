"""Inspect exact native weapon/rotation manager uses in the saved build."""
from pathlib import Path
import os,sys
W=Path(__file__).resolve().parent.parent
os.environ['VSS_CAPTURE']=str(W/'reverse/capture-25480438');sys.path.insert(0,str(W))
from emulate_seats import StaticVM
m=StaticVM().mod;m.md.detail=True
for rva,length in [(18513792,368),(0x6ba600,181),(0x117bf60,512)]:
 text='\n'.join(f'{i.address:08x}: {i.mnemonic:8} {i.op_str}'for i in m.md.disasm(m.read(rva,length),rva))
 (W/'seat_motion_research'/f'binding-counts-{rva:x}.txt').write_text(text)
 print(text)
