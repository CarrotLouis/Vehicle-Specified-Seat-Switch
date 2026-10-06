"""Freeze 0.27.0 runs and summarize actual operations without inventing W/turn input."""
from pathlib import Path
from collections import Counter
import hashlib
import json

R = Path(__file__).resolve().parent
D = R / 'capture-20261005-0270'
L = Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
names = ['VehicleSeatIntegrated-20261005-150559-30132-402300500.log',
         'VehicleSeatIntegrated-20261005-151315-2568-292796.log',
         'VehicleSeatIntegrated-20261005-152906-30240-1244140.log',
         'VehicleSeatIntegratedDiagnostic.log', 'BingusSharedLoader.log']
D.mkdir(exist_ok=True)
files = []
for name in names:
    path = D / name
    if not path.exists():
        path.write_bytes((L / name).read_bytes())
    data = path.read_bytes()
    files.append({'name': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
index = D / 'files.json'
if index.exists():
    assert json.loads(index.read_text()) == files
else:
    index.write_text(json.dumps(files, indent=2))

summary = []
for name in names[:3]:
    rows = [json.loads(line) for line in (D / name).read_text(encoding='utf-8').splitlines() if line.strip()]
    if not rows:
        summary.append({'name': name, 'classification': 'empty start; no test evidence'})
        continue
    counts = Counter(row['event'] for row in rows)
    requests = [row for row in rows if row['event'] == 'reservation_request']
    completed = [row for row in rows if row['event'] == 'reservation_operation_complete']
    states = [row for row in rows if row['event'] == 'state']
    operations = []
    for i, request in enumerate(requests):
        finish = next((row for row in completed if row['operation'] == request['operation']), None)
        # Exclude later normal exits/entries into a different vehicle.
        limit = finish['t'] + 1 if finish else (requests[i + 1]['t'] if i + 1 < len(requests) else request['t'] + 6000)
        mapping = next((row for row in reversed(rows) if row['event'] == 'reservation_entrance_mapping'
                        and row['t'] <= request['t']), {})
        context = next((row for row in reversed(states) if row['t'] <= request['t']), {})
        data = context.get('data', {})
        avatar = next((row for row in data.get('avatars', []) if row.get('is_local')), {})
        car = next((row for row in data.get('vehicles', []) if row['id'] == avatar.get('seat', {}).get('collection')), {})
        authority = [row for row in rows if row['event'] == 'authority_interface_preflight' and request['t'] - 50 <= row['t'] < limit]
        phys = [row for row in rows if row['event'] == 'reservation_physics_sample' and request['t'] <= row['t'] < limit]
        stages = [row for row in rows if request['t'] <= row['t'] < limit and
                  (row['event'].startswith('reservation_') or row['event'] in ('reserved_local_stage', 'reserved_local_calls_returned'))]
        wire = [{key: row.get(key) for key in ('t', 'event', 'message', 'values', 'peers')}
                for row in rows if row['event'] in ('native_send', 'native_receive_dispatch')
                and request['t'] - 2 <= row['t'] < limit]
        operations.append({'request': request, 'complete': finish,
                           'duration_ms': finish['t'] - request['t'] if finish else None,
                           'mapping': mapping, 'car': car,
                           'avatar': {key: avatar.get(key) for key in ('id', 'unit', 'network_unit', 'seat')},
                           'room': {key: data.get(key) for key in ('player_count', 'local_count', 'coordinator', 'selfpeer', 'peers')},
                           'authority': authority,
                           'physics_owners': sorted(set((row.get('owner'), row.get('owner_serial')) for row in phys)),
                           'installer_is_host': sorted(set(row['installer_is_host'] for row in phys if 'installer_is_host' in row)),
                           'physics_samples': len(phys), 'stages': stages, 'wire': wire})
    errors = [row for row in rows if any(word in row['event'] for word in ('stopped', 'cancelled', 'denied', 'gap', 'failed', 'overflow'))
              and row['event'] not in ('input_priority_stopped', 'transport_stopped')]
    item = {'name': name, 'classification': 'actual test' if requests else 'no reservation request',
            'start': rows[0], 'end': rows[-1], 'events': dict(counts), 'operations': operations,
            'error_events': errors, 'state_schema': list(states[0]['data']) if states else [],
            'authority_example': next((row for row in rows if row['event'] == 'authority_interface_preflight'), None),
            'room_segments': [(row['t'], row['data']['state'], row['data'].get('mission_value')) for i, row in enumerate(states)
                              if i == 0 or (row['data']['state'], row['data'].get('mission_value')) !=
                              (states[i - 1]['data']['state'], states[i - 1]['data'].get('mission_value'))]}
    summary.append(item)
    print(json.dumps({'name': name, 'start_version': rows[0].get('version'), 'end': rows[-1],
                      'requests': len(requests), 'completed': len(completed), 'errors': errors,
                      'room_segments': item['room_segments']}, ensure_ascii=False))
    for op in operations:
        print(json.dumps({'op': op['request']['operation'], 't': op['request']['t'],
                          'route': [op['request']['source'], op['request']['target']],
                          'vehicle': op['car'].get('name'), 'car': op['car'].get('id'),
                          'mapping': op['mapping'], 'duration_ms': op['duration_ms'],
                          'owners': op['physics_owners'],
                          'authority_contract': [{key: row.get('data',{}).get(key) for key in ('stage', 'local_identity_matches', 'coordinator_matches')}
                                        for row in op['authority'][:1]],
                          'wire': [(row['event'], row['message']) for row in op['wire']]}, ensure_ascii=False))
(D / 'analysis.json').write_text(json.dumps(summary, indent=2))
assert all(item['start']['version'] == '0.27.0' for item in summary if 'start' in item)
assert all(op['complete'] and op['complete']['chassis_authority_unchanged'] and op['complete']['old_slot_released']
           for item in summary for op in item.get('operations', []))
print('PASS captured actual completed grants and old-source releases; W/turn conditions remain user-reported')
