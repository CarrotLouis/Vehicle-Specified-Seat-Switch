"""Extract only the two user-named addon resources for local API comparison."""
from pathlib import Path
import struct, hashlib, json
root=Path(r'E:\game\mod copy\Helldiver2\Arsenal\Vanilla Plus Megapack 16294 36 2026-09-30T23-48Z QXOHm3LsT_AR558038\options')
out=Path(__file__).parent/'installed';out.mkdir(exist_ok=True)
report=[]
for name in ['ModOptionsMenu','ModBindingsMenu']:
    for path in sorted((root/name).glob('*.patch_*')):
        if path.suffix in ['.stream','.gpu_resources']:continue
        data=path.read_bytes();magic,types,count=struct.unpack_from('<III',data)
        assert magic==0xf0000011
        for i in range(count):
            entry=struct.unpack_from('<7Q6I',data,72+types*32+i*80)
            resource,kind,offset=entry[:3];length=entry[7]
            body=data[offset:offset+length]
            if kind==0xa14e8dfa2cd117e2:
                size,version=struct.unpack_from('<II',body)
                text=body[8:8+size]
                target=out/(name+'-'+f'{resource:016x}'+'.lua')
                target.write_bytes(text)
                report.append({'addon':name,'file':str(target.name),'bytes':len(text),'sha256':hashlib.sha256(text).hexdigest()})
            else:
                target=out/(name+'-'+f'{resource:016x}.{kind:016x}.bin')
                target.write_bytes(body)
                report.append({'addon':name,'file':str(target.name),'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()})
(out/'files.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
