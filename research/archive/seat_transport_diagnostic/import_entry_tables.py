"""Import a completed one-shot table log supplied by the user; no live access."""
from pathlib import Path
import hashlib, json, shutil, sys

R=Path(__file__).resolve().parent
OUT=R/'reservation-20260925'
source=Path(sys.argv[1])
events=[json.loads(s) for s in source.read_text(encoding='utf-8').splitlines()]
assert events[0]['event']=='start' and events[0]['version']=='entry-tables-0.1.0'
assert events[-1]['event']=='end' and events[-1]['reason']=='complete'
tables=[e for e in events if e['event']=='entry_tables']
assert len(tables)==1
capture=tables[0]
requirements=json.loads((OUT/'entry-table-requirements.json').read_text())
assert capture['game_sha256']==requirements['game_sha256'], 'Need matching static capture for this game build'
assert len(capture['tables'])==6 and capture['total_bytes']==424
for expected in requirements['ranges']:
    t=next(t for t in capture['tables'] if t['vehicle']==expected['vehicle'])
    assert all(t[k]==expected[k] for k in ['transition','rva','row','rows','seat_count'])
    raw=bytes.fromhex(t['hex'])
    assert len(raw)==expected['size']
    actual=[int.from_bytes(raw[i:i+4],'little',signed=True) for i in range(0,len(raw),4)]
    assert actual==t['values']
    for off in range(0,len(actual),t['row']//4):
        row=actual[off:off+t['row']//4]
        assert -1 in row
        assert all(0<=v<t['rows'] for v in row[:row.index(-1)])
dest=OUT/source.name
if dest.exists():assert dest.read_bytes()==source.read_bytes()
else:shutil.copyfile(source,dest)
capture['source']=source.name
capture['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
canonical=OUT/'entry-tables.json'
if canonical.exists():
    assert json.loads(canonical.read_text())==capture,'Preserve previous table evidence; do not overwrite different capture'
else:canonical.write_text(json.dumps(capture,indent=2))
print(json.dumps(dict(imported=str(canonical),bytes=capture['total_bytes'],source_sha256=capture['source_sha256'])))
