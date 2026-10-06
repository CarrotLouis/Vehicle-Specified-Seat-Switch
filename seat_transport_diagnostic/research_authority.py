"""Locate native authority message evidence in the immutable module capture."""
from pathlib import Path
import os, sys, struct, json, hashlib
R=Path(__file__).resolve().parent;W=R.parent
os.environ['VSS_CAPTURE']=str(W/'reverse/capture-25480438')
sys.path.insert(0,str(W))
from reverse import Module
m=Module();out=R/'entry-analysis-20260926';out.mkdir(exist_ok=True)
result={}
for name,h in [('authority_owned',0xf8a9d630),('authority_request',0xe29b4d18)]:
    needle=struct.pack('<I',h);hits=[]
    for base,data in m.sections:
        start=0
        while True:
            p=data.find(needle,start)
            if p<0:break
            start=p+1;address=base+p;f=m.function(address)
            hits.append(dict(address=hex(address),function=hex(f[0]) if f else None))
            if f:(out/(name+'-'+hex(f[0])+'.asm.txt')).write_text(m.dis(f[0]))
    result[name]=dict(hash=hex(h),hits=hits)
for name,a in [('seat_authority',0x635710),('ownership_busy',0xfde390)]:
    f=m.function(a);body=m.read(a,f[1]-a)
    result[name]=dict(rva=hex(a),sha256=hashlib.sha256(body).hexdigest())
    (out/(name+'.asm.txt')).write_text(m.dis(a))
(out/'authority-locations.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
table=struct.unpack('<600Q',m.read(0x214c2e0,600*8))
candidates=[]
for index in list(range(514,560))+list(range(561,590)):
    addr=table[index]-0x7ffbf8760000
    f=m.function(addr)
    if not f or f[0]!=addr:continue
    ins=list(m.md.disasm(m.read(addr,f[1]-addr),addr))
    calls=[i.op_str for i in ins if i.mnemonic in ('call','jmp') and i.op_str.startswith('0x')
           and not f[0]<=int(i.op_str,16)<f[1]]
    if '0xfd9ba0' in calls:continue
    candidates.append(dict(index=index,rva=hex(addr),length=f[1]-addr,calls=calls))
    (out/('adapter-'+str(index)+'.asm.txt')).write_text(m.dis(addr))
(out/'authority-adapter-candidates.json').write_text(json.dumps(candidates,indent=2))
print(json.dumps(candidates,indent=2))
