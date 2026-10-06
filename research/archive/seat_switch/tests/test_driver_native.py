"""Execute captured driver input writer blocks, not a live game."""
import sys,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from emulate_seats import StaticVM
from unicorn.x86_const import *
v=StaticVM();u=v.vm
manager,states=0x10010000,0x10020000
u.mem_write(0x3326668,struct.pack('<Q',manager))
u.mem_write(manager+0x58,struct.pack('<Q',states))
blocks=[(0xa7f946,0xa7f961,UC_X86_REG_XMM8,0x18),
 (0xa7f987,0xa7f9a2,UC_X86_REG_XMM9,0x1c),
 (0xa7f9c8,0xa7f9e8,UC_X86_REG_XMM7,0x20),
 (0xa7fd5f,0xa7fd79,UC_X86_REG_XMM6,0x24),
 (0xa7fd9f,0xa7fdb9,UC_X86_REG_XMM7,0x28)]
for value in [-1.0,0.0,1.0]:
 u.mem_write(states,bytes([0x55])*96)
 for start,end,xmm,offset in blocks:
  u.reg_write(UC_X86_REG_RAX,1);u.reg_write(UC_X86_REG_RSI,manager)
  u.reg_write(xmm,struct.unpack('<I',struct.pack('<f',value))[0])
  u.emu_start(start,end,count=32)
  assert u.reg_read(UC_X86_REG_RIP)==end
  assert struct.unpack('<f',u.mem_read(states+48+offset,4))[0]==value
 assert u.mem_read(states,72)==bytes([0x55])*72
 assert u.mem_read(states+92,4)==bytes([0x55])*4
print('PASS: captured native driver writer blocks independently verify all five command offsets/48-byte stride for negative, neutral and positive input; adjacent state preserved.')
