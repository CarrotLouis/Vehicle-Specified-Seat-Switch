from pathlib import Path
import sys,struct,re,bisect,json,os
sys.path.insert(0,str(Path(__file__).parent/'python_deps'))
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
ROOT=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs\VehicleSeatDiagnostic')
OLD_CAPTURE=Path(__file__).parent/'reverse/capture-24826606'
# Default to the preserved source build until the next diagnostic is imported.
if OLD_CAPTURE.exists():ROOT=OLD_CAPTURE
NEW_CAPTURE=Path(__file__).parent/'reverse/capture-25327279'
if NEW_CAPTURE.exists():ROOT=NEW_CAPTURE
# Explicit offline sample selection; never connects to a running process.
if os.getenv('VSS_CAPTURE'):ROOT=Path(os.environ['VSS_CAPTURE'])
OUT=Path(__file__).parent/'reverse';OUT.mkdir(exist_ok=True)
class Module:
    def __init__(self,name='game.dll',root=None):
        root=Path(root) if root else ROOT
        self.name=name;self.sections=[]
        for p in root.glob(name+'.*.bin'):
            if '_' not in p.stem:continue
            rva=int(p.stem.split('_')[1],16)
            self.sections.append((rva,p.read_bytes()))
        self.sections.sort()
        self.code=self.sections[0][1];self.base=self.sections[0][0]
        header=root/(name+'.headers.bin')
        if header.exists():
            h=header.read_bytes();pe=struct.unpack_from('<I',h,0x3c)[0]
            pva,plen=struct.unpack_from('<II',h,pe+24+112+3*8)
            pdata=self.read(pva,plen)
        else:pdata=next(b for r,b in self.sections if r== (0x2ada000 if name=='game.dll' else 0x27d3000))
        self.functions=[(a,b,c) for a,b,c in struct.iter_unpack('<III',pdata) if a and a<b and b<=self.base+len(self.code)]
        self.functions.sort();self.starts=[f[0] for f in self.functions]
        self.roots={}
        def root_of(f,depth=0):
            if depth>10:return f
            u=self.read(f[2],4)
            if len(u)==4 and (u[0]>>3)&4:
                offset=(4+2*u[2]+3)&~3
                chain=self.read(f[2]+offset,12)
                if len(chain)==12:return root_of(struct.unpack('<III',chain),depth+1)
            return f
        self.root_ranges={}
        for f in self.functions:
            root=root_of(f);self.roots[f]=root
            previous=self.root_ranges.get(root[0],root)
            self.root_ranges[root[0]]=(root[0],max(previous[1],f[1]),root[2])
        self.md=Cs(CS_ARCH_X86,CS_MODE_64)
    def read(self,rva,n):
        for base,data in self.sections:
            if base<=rva and rva+n<=base+len(data):return data[rva-base:rva-base+n]
        return b''
    def function(self,address):
        i=bisect.bisect_right(self.starts,address)-1
        if i>=0 and self.functions[i][0]<=address<self.functions[i][1]:
            f=self.functions[i]
            return self.root_ranges[self.roots[f][0]]
        return None
    def dis(self,address,size=None):
        if size is None:
            f=self.function(address)
            if f:address,end,_=f;size=end-address
            else:size=256
        return '\n'.join(f'{i.address:08x}: {i.mnemonic:8} {i.op_str}' for i in self.md.disasm(self.read(address,size),address))
    def strings(self,query):
        rx=re.compile(query,re.I)
        return [(r+m.start(),m.group().decode('ascii')) for r,b in self.sections[:2] for m in re.finditer(rb'[ -~]{5,}',b) if rx.search(m.group())]
    def xrefs(self,targets):
        targets=set(targets);result=[]
        # RIP relative LEA/MOV, including REX.W/R and the general-purpose register set.
        for m in re.finditer(rb'[\x48\x4c][\x8d\x8b\x89][\x05\x0d\x15\x1d\x25\x2d\x35\x3d]',self.code):
            p=m.start();target=self.base+p+7+struct.unpack_from('<i',self.code,p+3)[0]
            if target in targets:result.append((self.base+p,target,self.function(self.base+p)))
        return result
    def callers(self,targets):
        targets=set(targets);result=[]
        for m in re.finditer(rb'[\xe8\xe9]',self.code):
            p=m.start()
            if p+5>len(self.code):continue
            target=self.base+p+5+struct.unpack_from('<i',self.code,p+1)[0]
            if target in targets:result.append((hex(self.base+p),hex(target),tuple(hex(x) for x in (self.function(self.base+p) or ()))) )
        return result
if __name__=='__main__':
    mod=Module(sys.argv[1])
    op=sys.argv[2]
    if op=='strings':
        ss=mod.strings(sys.argv[3].encode());print(json.dumps(ss,indent=2))
        print('XREFS',json.dumps(mod.xrefs([a for a,_ in ss]),indent=2))
    elif op=='dis':
        print(mod.dis(int(sys.argv[3],16),int(sys.argv[4],16) if len(sys.argv)>4 else None))
    elif op=='xrefs':print(json.dumps(mod.xrefs([int(x,16) for x in sys.argv[3:]]),indent=2))
    elif op=='callers':print(json.dumps(mod.callers([int(x,16) for x in sys.argv[3:]]),indent=2))
