"""Preserve and validate the 0.5.0 run without invoking game code."""
from pathlib import Path
import collections
import hashlib
import json

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'analysis-20260927'
LOGS = Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
NAME = 'VehicleSeatAuthority-20260926-214355-3812-179493218.log'
OUT.mkdir(exist_ok=True)
manifest = {}
for name in [NAME, 'VehicleSeatAuthorityDiagnostic.log', 'VehicleSeatSwitch.log', 'BingusSharedLoader.log']:
    dest = OUT / name
    if not dest.exists():
        dest.write_bytes((LOGS / name).read_bytes())
    data = dest.read_bytes()
    manifest[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
events = [json.loads(line) for line in (OUT / NAME).read_text(encoding='utf-8').splitlines() if line.strip()]
assert events[0]['version'] == '0.5.0'
native = [e for e in events if e['event'].startswith('native_')]
stop = next(e for e in events if e['event'] == 'transport_stopped')
checks = {
    'sequence_contiguous': [e['sequence'] for e in native] == list(range(1, len(native) + 1)),
    'arguments_complete': all(e['valid_mask'] == (1 << e['argument_count']) - 1 for e in native),
    'event_count_matches': stop['events'] == len(native),
    'no_drops': stop['dropped_total'] == 0,
    'hooks_restored': stop['restore_flags'] == 0,
    'normal_shutdown': stop['reason'] == 'shutdown' and events[-1]['event'] == 'end',
}
probe = [e for e in events if e['event'].startswith('authority_probe_')]
summary = {
    'files': manifest, 'records': len(events), 'native_events': len(native), 'checks': checks,
    'read_gaps': [e for e in events if e['event'] == 'read_gap'],
    'probe_events': probe,
    'interface_preflight': [e for e in events if e['event'] == 'authority_interface_preflight'],
    'native_authority_events': [e for e in native if e['message'].startswith('authority')],
    'event_counts': dict(collections.Counter(e['event'] for e in events)),
    'conclusion': 'Recording usable to diagnose observer refusal; active ownership round-trip NOT exercised. Stop for user as requested.',
}
(OUT / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False, indent=2))
