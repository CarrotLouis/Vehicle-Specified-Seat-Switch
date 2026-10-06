"""Read immutable captures, never attach to the game. Small JSON index + bounded disassembly."""
from pathlib import Path
import json, struct, re, sys

R = Path(__file__).resolve().parent
W = R.parent
sys.path.insert(0, str(W))
from reverse import Module

O = R / 'native-return'
O.mkdir(exist_ok=True)
roots = ['capture-25327279', 'capture-25480438']
targets = [0xd0ce80, 0xd0cfa0, 0xdcffb0, 0x299890, 0x290040, 0x29c840]
report = {}
for capture in roots:
    m = Module('helldivers2.exe', W / 'reverse' / capture)
    h = (W / 'reverse' / capture / 'helldivers2.exe.headers.bin').read_bytes()
    pe = struct.unpack_from('<I', h, 0x3c)[0]
    image_base = struct.unpack_from('<Q', h, pe + 24 + 24)[0]
    references = {}
    # Captured pointer sections may contain relocated absolute addresses. Infer
    # live base from witnesses rather than assuming PE preferred image base.
    pairs = []
    for base, data in m.sections[1:]:
        for i in range(0, len(data)-0xe0, 8):
            a, b, c = (struct.unpack_from('<Q', data, i + off)[0] for off in [0x70, 0x88, 0x98])
            if a and b-a == 0x120 and c-a == 0xc3130:
                pairs.append({'vtable':hex(base+i), 'live_base':hex(a-0xd0ce80),
                              'slots':{hex(s):hex(struct.unpack_from('<Q', data, i+s)[0]-(a-0xd0ce80))
                                       for s in range(0, 0xe0, 8)}})
    live_bases = {int(p['live_base'],16) for p in pairs} | {image_base}
    for target in targets:
        refs = []
        for base, data in m.sections[1:]:
            for lb in live_bases:
                needle = struct.pack('<Q',lb+target)
                for hit in re.finditer(re.escape(needle),data):
                    if (base+hit.start())%8==0:refs.append(hex(base+hit.start()))
        references[hex(target)] = sorted(set(refs))
    report[capture] = {'preferred_base':hex(image_base),'physical_vtables':pairs,
                       'pointer_references':references}
    if capture == roots[-1]:
        funcs = {0x290040:0x3a4,0x299890:None,0x29c840:None}
        for p in pairs:
            for slot in [0x90,0x98,0xd0]:
                funcs[int(p['slots'][hex(slot)],16)] = None
        for addr,size in funcs.items():
            f=m.function(addr)
            # Avoid including broad chained exception ranges in unrelated code.
            n = size or (min(f[1]-addr,0x6000) if f else 0x180)
            (O / f'engine-{addr:x}.txt').write_text(m.dis(addr,n),encoding='utf-8')
        for p in pairs:
            refs=m.xrefs([int(p['vtable'],16)])
            report[capture]['vtable_references']=[{'at':hex(a),'table':hex(t),'fn':hex(f[0]) if f else None} for a,t,f in refs]
            for a,t,f in refs:
                if f and f[1]-f[0]<0x6000:(O/f'engine-{f[0]:x}.txt').write_text(m.dis(f[0]),encoding='utf-8')

(O/'native-index.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
