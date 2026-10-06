"""Offline execution of pure static game lookup routines; never attaches to a process."""
from reverse import Module
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64
from unicorn.x86_const import *
import struct,json
from pathlib import Path

class StaticVM:
    def __init__(self):
        self.mod=Module()
        self.vm=Uc(UC_ARCH_X86,UC_MODE_64)
        self.vm.mem_map(0,0x5000000)
        for r,b in self.mod.sections:self.vm.mem_write(r,b)
        self.vm.mem_map(0x10000000,0x100000)
        self.vm.mem_map(0x20000000,0x1000)
        self.vm.mem_write(0x20000000,b'\xcc')
    def run(self,addr,*args):
        for reg in (UC_X86_REG_RAX,UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9,UC_X86_REG_R10,UC_X86_REG_R11):
            self.vm.reg_write(reg,0)
        for reg,arg in zip((UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9),args):self.vm.reg_write(reg,arg)
        self.vm.reg_write(UC_X86_REG_RSP,0x10080008)
        self.vm.mem_write(0x10080008,struct.pack('<Q',0x20000000))
        self.vm.emu_start(addr,0x20000000,count=10000)
        assert self.vm.reg_read(UC_X86_REG_RIP)==0x20000000
        return self.vm.reg_read(UC_X86_REG_RAX)

def disk_read(rva,n):
    p=Path(r'F:\SteamLibrary\steamapps\common\Helldivers 2\data\game\game.dll')
    if not p.exists():p=Path(r'F:\SteamLibrary\steamapps\common\Helldivers 2\bin\game.dll')
    data=p.read_bytes();pe=struct.unpack_from('<I',data,0x3c)[0]
    ns=struct.unpack_from('<H',data,pe+6)[0];opt=struct.unpack_from('<H',data,pe+20)[0]
    for i in range(ns):
        off=pe+24+opt+40*i
        vs,va,rs,raw=struct.unpack_from('<IIII',data,off+8)
        if va<=rva and rva+n<=va+rs:return data[raw+rva-va:raw+rva-va+n]
    return b''

if __name__=='__main__':
    s=StaticVM();result={}
    for kind,t in [('m102',26),('m103',27),('m104',28),('bastion',43),('maelstrom_candidate',44),('tanker',33)]:
        rows=[]
        for node in range(32):
            role=s.run(0x11957c0,t,node)
            if role:
                ptr=s.run(0x11966f0,t,node)
                raw=disk_read(ptr,20)
                action=s.run(0x119a6b0,t,node)&0xffffffff
                rows.append(dict(node=node,role=role,restore_action=action,next_array=hex(ptr),disk_ints=list(struct.unpack('<5i',raw)) if len(raw)==20 else None))
        routes=[]
        for src in range(len(rows)):
            row=[]
            for dst in range(len(rows)):
                s.vm.mem_write(0x10001000,struct.pack('<I',src))
                action=s.run(0x1196dc0,t,0x10001000,dst)&0xffffffff
                nxt=struct.unpack('<I',s.vm.mem_read(0x10001000,4))[0]
                row.append([nxt, action if action<0x80000000 else action-0x100000000])
            routes.append(row)
        result[kind]=dict(transition=t,seats=rows,routes=routes)
    Path('work/reverse/seat_roles_25327279.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
