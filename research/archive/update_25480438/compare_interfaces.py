from pathlib import Path
import sys,re,json,struct
WORK=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(WORK))
from reverse import Module
from capstone.x86_const import X86_OP_MEM,X86_REG_RIP

def normalized(module, address, length):
    module.md.detail=True
    raw=module.read(address,length);mask=bytearray(len(raw));refs=[]
    for i in module.md.disasm(raw,address):
        p=i.address-address
        if i.disp_size and any(o.type==X86_OP_MEM and o.mem.base==X86_REG_RIP for o in i.operands):
            mask[p+i.disp_offset:p+i.disp_offset+i.disp_size]=b'\1'*i.disp_size
            refs.append(dict(offset=p,kind='rip',disp=i.disp_offset,width=i.disp_size,size=i.size,target=i.address+i.size+i.disp))
        if i.imm_size and (i.mnemonic.startswith('j') or i.mnemonic=='call'):
            # Preserve local branches; only external relative destinations are relocatable.
            target=i.operands[0].imm
            if not address<=target<address+length:
                mask[p+i.imm_offset:p+i.imm_offset+i.imm_size]=b'\1'*i.imm_size
                refs.append(dict(offset=p,kind='branch',disp=i.imm_offset,width=i.imm_size,size=i.size,target=target))
    rx=b''.join(b'.' if m else re.escape(bytes([b])) for b,m in zip(raw,mask))
    return raw,mask,refs,rx

def main():
    profile=(WORK/'seat_switch/src/profile.lua').read_text()
    report={}
    for name,part in [('game.dll',profile.split('functions={',1)[1].split('},driver=',1)[0]),
                      ('helldivers2.exe',profile.split('engine_functions={',1)[1].split('},animation=',1)[0])]:
        old=Module(name,root=WORK/'reverse/capture-25327279');new=Module(name,root=WORK/'reverse/capture-25480438')
        rows={}
        for key,addr in re.findall(r"\['([^']+)'\]=\{rva=0x([0-9a-f]+)",part):
            a=int(addr,16);fn=old.function(a);full=fn[1]-a if fn else 64
            candidates=[];chosen=None
            for length in sorted(set([full,min(full,512),min(full,256),min(full,160),min(full,96),min(full,48)]),reverse=True):
                raw,mask,refs,rx=normalized(old,a,length)
                found=[m.start()+new.base for m in re.finditer(rx,new.code,re.S)]
                if len(found)==1 and new.function(found[0]) and new.function(found[0])[0]==found[0]:
                    candidates=found;chosen=length;break
            rows[key]=dict(old=hex(a),old_length=full,length=chosen,new=[hex(x) for x in candidates])
            if candidates:
                dest=candidates[0];nf=new.function(dest);rows[key]['new_length']=nf[1]-dest
                (Path(__file__).parent/f'{name}_{key}.txt').write_text(new.dis(dest),encoding='utf-8')
            print(name,key,rows[key])
        report[name]=rows
    (Path(__file__).parent/'interfaces.json').write_text(json.dumps(report,indent=2))

if __name__=='__main__':main()
