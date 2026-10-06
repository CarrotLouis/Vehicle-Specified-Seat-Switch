from pathlib import Path
import sys,json,re,struct,shutil,hashlib
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
from reverse import Module
out=R/'preflight-20260925-141635';out.mkdir(exist_ok=True)
logs=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
name='VehicleSeatInterface-20260925-141635-28984-66253000.log'
for file in [name,'VehicleSeatInterfaceDiagnostic.log']:
 if not(out/file).exists():shutil.copyfile(logs/file,out/file)
events=[json.loads(line)for line in(out/name).read_text().splitlines()]
rows=[e['data']for e in events if e['event']=='routing_snapshot']
assert len(rows)==10 and all(r['state']=='observed'for r in rows)
assert all(r['callback']['matches_dispatch']and r['callback']['stable']and r['callback']['storage']['protection']==4 for r in rows)
assert all(r['messages']==rows[0]['messages']and r['registry_count']==592 for r in rows)
capture=W/'reverse/capture-25480438';m=Module(root=capture)
base=int(re.search(r'game.dll base=(0x[0-9a-f]+)',(capture/'capture.txt').read_text()).group(1),16)
# Dispatcher branch table is code-referenced, not a guessed index for future builds.
raw=m.read(0xbc2d10,17);assert raw[:9]==bytes.fromhex('418bc0498bd14c8d05')and raw[13:]==bytes.fromhex('49ff24c0')
table=0xbc2d1d+struct.unpack_from('<i',raw,9)[0]
assert table==0x214c2e0
messages=[]
for row in rows[0]['messages']:
 assert row['found']
 adapter=struct.unpack('<Q',m.read(table+row['index']*8,8))[0]-base
 assert m.function(adapter)or 0<adapter<0x2111000
 (out/(row['name']+'-adapter.txt')).write_text(m.dis(adapter))
 messages.append(dict(**row,adapter_rva=adapter))
summary=dict(source=name,source_sha256=hashlib.sha256((out/name).read_bytes()).hexdigest(),rounds=10,end=events[-1],callback=rows[0]['callback'],registry_count=592,messages=messages)
(out/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
