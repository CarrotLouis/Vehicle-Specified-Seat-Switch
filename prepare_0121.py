from pathlib import Path
import hashlib,json
W=Path(__file__).resolve().parent
old=W/'seat_input_priority_test';out=W/'seat_input_thread_fix'
logs=Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
capture=old/'capture-20261001-0120';capture.mkdir(exist_ok=True)
names=['VehicleSeatIntegrated-20261001-154624-32348-59125593.log','VehicleSeatIntegratedDiagnostic.log','BingusSharedLoader.log']
manifest=[]
for name in names:
    src=logs/name;data=src.read_bytes();dest=capture/name
    if dest.exists():assert dest.read_bytes()==data,'frozen evidence must not change'
    else:dest.write_bytes(data)
    manifest.append(dict(name=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),source=str(src)))
records=[json.loads(s) for s in (capture/names[0]).read_text(encoding='utf-8').splitlines() if s.strip()]
failure=[r for r in records if r['event']=='input_priority_install_failure']
assert len(failure)==1 and failure[0]['code']==-4
assert records[0]['version']=='0.12.0'
assert not any(r['event'] in ('seat_input','integrated_request','integrated_operation_complete','input_priority_ready','input_priority_consumed') for r in records)
summary=dict(failure=failure[0],counts={e:sum(r['event']==e for r in records) for e in sorted({r['event'] for r in records})},files=manifest)
(capture/'analysis.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
assert not out.exists();out.mkdir()
for p in old.iterdir():
    if p.is_file() and p.suffix in ('.lua','.py','.txt','.json','.c') and p.name not in ('bundled.lua','check.lua','package.json','input_helper.lua','input-native-build.json'):
        (out/p.name).write_text(p.read_text(encoding='utf-8').replace('seat_input_priority_test','seat_input_thread_fix').replace('0.12.0','0.12.1'),encoding='utf-8')
print(json.dumps(summary,indent=2))
