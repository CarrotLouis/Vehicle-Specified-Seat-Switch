from pathlib import Path
import struct,re,json
from reverse import Module

W=Path(__file__).resolve().parent;out=W/'input_priority_research';out.mkdir(exist_ok=True)
interesting={'GetRawInputData','GetRawInputBuffer','GetAsyncKeyState','GetKeyState','PeekMessageW','PeekMessageA','GetMessageW','GetMessageA','RegisterRawInputDevices','DefWindowProcW','DefWindowProcA','GetProcAddress'}
for capture in ['25327279','25480438']:
    root=W/'reverse'/('capture-'+capture)
    for name in ['helldivers2.exe','game.dll']:
        m=Module(name,root);h=(root/(name+'.headers.bin')).read_bytes()
        pe=struct.unpack_from('<I',h,0x3c)[0];oh=pe+24
        nr,size=struct.unpack_from('<H12xH',h,pe+6)
        imp,imp_size=struct.unpack_from('<II',h,oh+112+8)
        sections=[]
        for i in range(nr):
            o=oh+size+40*i;n=h[o:o+8].rstrip(b'\0').decode();vs,rva=struct.unpack_from('<II',h,o+8);flags=struct.unpack_from('<I',h,o+36)[0]
            sections.append(dict(name=n,rva=rva,size=vs,write=bool(flags&0x80000000)))
        def cstring(rva,limit=256):
            for r,b in m.sections:
                if r<=rva<r+len(b):return b[rva-r:rva-r+limit].split(b'\0',1)[0].decode('ascii',errors='replace')
            return ''
        rows=[]
        for o in range(0,min(imp_size,4096),20):
            d=m.read(imp+o,20)
            if not d or d==bytes(20):break
            original,_,_,dll,iat=struct.unpack('<IIIII',d)
            for i in range(2048):
                b=m.read(original+8*i,8)
                if not b:break
                value=struct.unpack('<Q',b)[0]
                if not value:break
                if value>>63:continue
                sym=cstring(value+2)
                if sym not in interesting:continue
                slot=iat+8*i;refs=[]
                for x in re.finditer(rb'\xff[\x15\x25]',m.code):
                    p=x.start()
                    if p+6<=len(m.code) and m.base+p+6+struct.unpack_from('<i',m.code,p+2)[0]==slot:
                        refs.append(dict(rva=hex(m.base+p),function=[hex(v) for v in m.function(m.base+p) or []]))
                rows.append(dict(dll=cstring(dll),name=sym,rva=hex(slot),refs=refs,section=[s['name'] for s in sections if s['rva']<=slot<s['rva']+s['size']],writable=any(s['write'] for s in sections if s['rva']<=slot<s['rva']+s['size'])))
        result=dict(capture=capture,module=name,imports=rows)
        (out/(capture+'-'+name+'.json')).write_text(json.dumps(result,indent=2))
        print(json.dumps(result,indent=2))
