"""Summarize bounded input observations in already-frozen 0.23/0.24 tank baselines."""
from pathlib import Path
from collections import Counter
import json

R = Path(__file__).resolve().parent
W = R.parent
out = []
for directory in ['capture-20261004-0230', 'capture-20261004-0240']:
    for file in sorted((W / 'seat_motion_research' / directory).glob('VehicleSeatIntegrated-*.log')):
        rows = [json.loads(line) for line in file.read_text(encoding='utf-8').splitlines() if line.strip()]
        samples = [row for row in rows if row['event'] == 'steering_watch_sample' and row.get('spin')]
        for vehicle in ['bastion', 'maelstrom']:
            chosen = [row for row in samples if row['vehicle'] == vehicle]
            if not chosen:
                continue
            compact = []
            for row in chosen:
                spin = row['spin']
                compact.append({key: row.get(key) for key in ['t', 'owned_local', 'held_keys', 'local_seat']} |
                               {key: spin.get(key) for key in ['driver_backend_kind', 'driver_active', 'driver_command_steer',
                                  'driver_command_flags_offset_2c_to_2f', 'input_steer', 'replicated_steer',
                                  'driver_in_owned_partition', 'vehicle_in_owned_partition']})
            item = {'file': str(file), 'vehicle': vehicle, 'samples': compact,
                    'backend_kinds': dict(Counter(row['driver_backend_kind'] for row in compact)),
                    'inactive_nonzero': [row for row in compact if row['driver_active'] == 0 and
                                         (abs(row['input_steer']) > .01 or abs(row['replicated_steer']) > .01)]}
            out.append(item)
            print(json.dumps({'file': file.name, 'vehicle': vehicle, 'samples': len(chosen),
                              'backends': item['backend_kinds'], 'inactive_nonzero': len(item['inactive_nonzero']),
                              'examples': item['inactive_nonzero'][:2]}, ensure_ascii=False))
(R / 'latest-baseline-audit.json').write_text(json.dumps(out, indent=2))
