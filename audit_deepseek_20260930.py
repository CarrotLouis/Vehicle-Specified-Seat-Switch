"""Preserve external research separately; never merge or execute its sync script."""
from pathlib import Path
import hashlib, json, re, shutil, sys

ROOT = Path(__file__).resolve().parent.parent
DS = Path(r'E:\Document\deepseek-harness\default-workspace\vss-project')
OUT = ROOT / 'work/deepseek_review_20260930'
OUT.mkdir(exist_ok=True)
diff = (DS / 'work/SYNC_DIFF.md').read_text(encoding='utf-8-sig')
authored = diff.split('## 验证夹具')[0]
paths = re.findall(r'^\| \d+ \| `([^`]+)`', authored, re.M)
paths += ['work/SYNC_DIFF.md']
rows = []
for name in dict.fromkeys(paths):
    src = DS / name
    assert src.resolve().is_relative_to(DS.resolve())
    if not src.is_file():
        rows.append({'path':name,'missing':True}); continue
    dst = OUT / 'external_snapshot' / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    data = src.read_bytes()
    if dst.exists(): assert dst.read_bytes() == data, f'External research changed: {name}'
    else: dst.write_bytes(data)
    old = ROOT / name
    rows.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
                 'primary_sha256':hashlib.sha256(old.read_bytes()).hexdigest() if old.is_file() else None})
(OUT/'external_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('Preserved external authored files:',len(rows),'without merging primary sources')

sys.path.insert(0,str(ROOT/'work'))
from reverse import Module
m=Module('game.dll',ROOT/'work/reverse/capture-25480438')
targets=[0xbee380,0x637990,0x63dc90,0x6349b0,0x11a7f80,0x7853d0,0x785de0,0xbe1640]
for addr in targets:
    (OUT/f'{addr:08x}.asm.txt').write_text(m.dis(addr),encoding='utf-8')
    if addr in (0x7853d0,0x785de0):
        print(hex(addr),'calls:',[line for line in m.dis(addr).splitlines() if ': call' in line])
# Record opcode occurrences with function boundaries, not guessed function starts.
for value in (0xc698216f,0x2671dec5):
    found=[]; start=0; needle=value.to_bytes(4,'little')
    while (at:=m.code.find(needle,start))>=0:
        rva=m.base+at; start=at+1; f=m.function(rva)
        found.append({'rva':hex(rva),'function':[hex(x) for x in f] if f else None})
    (OUT/f'hash-{value:08x}.json').write_text(json.dumps(found,indent=2))
    print(hex(value),found)
