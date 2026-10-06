from pathlib import Path
import collections
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
DEST = ROOT / 'work/seat_motion_research/capture-20261004-0220'
DEST.mkdir(parents=True, exist_ok=True)
names = ['VehicleSeatIntegrated-20261004-140118-14756-312019468.log',
         'VehicleSeatIntegratedDiagnostic.log', 'BingusSharedLoader.log']
files = []
for name in names:
    src, dest = SRC / name, DEST / name
    data = src.read_bytes()
    if dest.exists():
        assert dest.read_bytes() == data, 'existing frozen evidence changed'
    else:
        shutil.copyfile(src, dest)
    files.append({'name': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
rows = [json.loads(line) for line in (DEST / names[0]).read_text(encoding='utf-8-sig').splitlines() if line.strip()]
gaps = [r for r in rows if r['event'] == 'physics_motion_gap']
selected = [r for r in rows if r['event'] in {
    'input_priority_consumed', 'seat_input', 'integrated_request_attempt',
    'integrated_cancelled', 'integrated_stopped', 'integrated_state',
    'physics_motion_sample', 'ownership_loan_only_verified',
    'integrated_loan_operation_complete', 'input_priority_stopped', 'end'}]
summary = {
    'files': files, 'start': rows[0],
    'event_counts': dict(collections.Counter(r['event'] for r in rows)),
    'gap_reasons': dict(collections.Counter(r['reason'] for r in gaps)),
    'gap_stages': dict(collections.Counter(r['stage'] for r in gaps)),
    'first_gap': gaps[0] if gaps else None,
    'last_gap': gaps[-1] if gaps else None,
    'operations': selected,
    'user_observation': 'Installer host; no stop or switch; native lean observed. Physical preflight rejected, no loan issued. No guest run requested.'
}
(DEST / 'files.json').write_text(json.dumps(files, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(DEST / 'analysis.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in summary.items() if k != 'operations'}, ensure_ascii=False, indent=2))
for row in selected:
    print(json.dumps(row, ensure_ascii=False))
